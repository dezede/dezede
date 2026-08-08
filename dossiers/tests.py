import json
import re
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase, override_settings
from django.urls import reverse

from libretto.models import (
    Etat, Evenement, Lieu, NatureDeLieu, Oeuvre, Source, TypeDeSource,
)
from .models import (
    Dossier, KIND_EVENEMENTS, KIND_OEUVRES, KIND_SOURCES, KINDS_ORDER,
)


# The real (PostgreSQL) search backend indexes every saved object through a
# background task whose separate connection conflicts with the test
# transaction; searching is not what is under test here, so it is swapped for
# the no-op fallback backend. A TransactionTestCase (truncation-based
# teardown) is used for the same reason: wagtail's ReferenceIndex writes
# from signal handlers clash with the in-transaction constraint check of a
# plain TestCase.
@override_settings(WAGTAILSEARCH_BACKENDS={
    'default': {
        'BACKEND': 'wagtail.search.backends.database.fallback',
    },
})
class DossierTestCase(TransactionTestCase):
    """A merged dossier presenting several kinds of data at once: shared
    dynamic criteria, per-kind querysets/counts, static freezing via the admin
    conversion actions, and the kind-scoped URL/API gating."""

    def setUp(self):
        cls = self  # per-test fixtures (truncated between tests)
        cls.etat = Etat.objects.create(nom='public', slug='public',
                                       public=True)
        User = get_user_model()
        cls.user = User.objects.create_superuser(
            'test_superuser', 'a@b.com', 'test_password')

        nature = NatureDeLieu.objects.create(nom='ville', slug='ville')
        cls.lieu = Lieu.objects.create(
            nom='Rouen', slug='rouen', nature=nature,
            etat=cls.etat, owner=cls.user)
        autre_lieu = Lieu.objects.create(
            nom='Paris', slug='paris', nature=nature,
            etat=cls.etat, owner=cls.user)

        cls.evenement = Evenement.objects.create(
            debut_date=date(1850, 3, 14), debut_lieu=cls.lieu,
            etat=cls.etat, owner=cls.user)
        cls.evenement_hors_criteres = Evenement.objects.create(
            debut_date=date(1950, 3, 14), debut_lieu=autre_lieu,
            etat=cls.etat, owner=cls.user)

        cls.oeuvre = Oeuvre.objects.create(
            titre='Carmen', slug='carmen', creation_date=date(1875, 3, 3),
            creation_lieu=cls.lieu, etat=cls.etat, owner=cls.user)
        cls.oeuvre_hors_criteres = Oeuvre.objects.create(
            titre='Ailleurs', slug='ailleurs', creation_date=date(1875, 3, 3),
            creation_lieu=autre_lieu, etat=cls.etat, owner=cls.user)

        type_de_source = TypeDeSource.objects.create(
            nom='programme', slug='programme')
        cls.source = Source.objects.create(
            type=type_de_source, date=date(1860, 1, 1),
            etat=cls.etat, owner=cls.user)
        cls.source.lieux.add(cls.lieu)
        Source.objects.create(  # hors critères (aucun lieu)
            type=type_de_source, date=date(1860, 1, 1),
            etat=cls.etat, owner=cls.user)

        cls.dossier = Dossier.objects.create(
            types_de_donnees=[KIND_EVENEMENTS, KIND_OEUVRES, KIND_SOURCES],
            titre='Multi', slug='multi', presentation='<p>x</p>',
            debut=date(1800, 1, 1), fin=date(1900, 12, 31),
            etat=cls.etat, owner=cls.user)
        cls.dossier.lieux.add(cls.lieu)
        self.client.force_login(self.user)

    def refreshed(self):
        return Dossier.objects.get(pk=self.dossier.pk)

    # -- Model ----------------------------------------------------------------

    def test_counts_and_querysets_per_kind(self):
        dossier = self.refreshed()
        self.assertEqual(dossier.active_kinds,
                         [KIND_EVENEMENTS, KIND_OEUVRES, KIND_SOURCES])
        self.assertEqual(dossier.counts(),
                         {KIND_EVENEMENTS: 1, KIND_OEUVRES: 1,
                          KIND_SOURCES: 1})
        self.assertQuerySetEqual(dossier.get_queryset(KIND_EVENEMENTS),
                                 [self.evenement])
        self.assertQuerySetEqual(dossier.get_queryset(KIND_OEUVRES),
                                 [self.oeuvre])
        self.assertQuerySetEqual(dossier.get_queryset(KIND_SOURCES),
                                 [self.source])

    def test_static_selection_wins_over_criteria(self):
        dossier = self.refreshed()
        dossier.evenements.add(self.evenement_hors_criteres)
        self.assertQuerySetEqual(dossier.get_queryset(KIND_EVENEMENTS),
                                 [self.evenement_hors_criteres])
        # The other kinds still follow the dynamic criteria.
        self.assertQuerySetEqual(dossier.get_queryset(KIND_OEUVRES),
                                 [self.oeuvre])
        # The dynamic queryset remains available explicitly.
        self.assertQuerySetEqual(
            dossier.get_queryset(KIND_EVENEMENTS, dynamic=True),
            [self.evenement])

    def test_unknown_kind(self):
        with self.assertRaises(ValueError):
            self.dossier.get_queryset('photos')

    # -- Admin conversion actions --------------------------------------------

    def test_convert_to_static_then_back_to_dynamic(self):
        convert_url = reverse('admin:dossiers_dossier_convert_static',
                              args=(self.dossier.pk,))
        response = self.client.get(convert_url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(convert_url)
        self.assertEqual(response.status_code, 302)
        dossier = self.refreshed()
        self.assertQuerySetEqual(dossier.evenements.all(), [self.evenement])
        self.assertQuerySetEqual(dossier.oeuvres.all(), [self.oeuvre])
        self.assertQuerySetEqual(dossier.sources.all(), [self.source])
        # Once frozen, changing the criteria does not change the selection.
        dossier.debut = date(1990, 1, 1)
        self.assertQuerySetEqual(dossier.get_queryset(KIND_EVENEMENTS),
                                 [self.evenement])
        # An already-static dossier cannot be converted again: the view
        # redirects back to the change form (and the button is hidden).
        response = self.client.get(convert_url)
        self.assertEqual(response.status_code, 302)

        revert_url = reverse('admin:dossiers_dossier_convert_dynamic',
                             args=(self.dossier.pk,))
        response = self.client.post(revert_url)
        self.assertEqual(response.status_code, 302)
        dossier = self.refreshed()
        self.assertFalse(dossier.evenements.exists())
        self.assertFalse(dossier.oeuvres.exists())
        self.assertFalse(dossier.sources.exists())

    # -- Django views ---------------------------------------------------------

    def test_detail_and_kind_scoped_pages(self):
        self.assertEqual(
            self.client.get('/dossiers/multi/').status_code, 200)
        for kind in (KIND_EVENEMENTS, KIND_OEUVRES, KIND_SOURCES):
            self.assertEqual(
                self.client.get(f'/dossiers/multi/{kind}/data').status_code,
                200, kind)
        for kind in (KIND_EVENEMENTS, KIND_OEUVRES):
            self.assertEqual(
                self.client.get(f'/dossiers/multi/{kind}/stats').status_code,
                200, kind)
            self.assertEqual(
                self.client.get(
                    f'/dossiers/multi/{kind}/geojson').status_code,
                200, kind)

    def test_permanent_pk_pages(self):
        pk = self.dossier.pk
        self.assertEqual(
            self.client.get(f'/dossiers/id/{pk}/').status_code, 200)
        self.assertEqual(
            self.client.get(f'/dossiers/id/{pk}/evenements/data').status_code,
            200)
        self.assertEqual(
            self.client.get(f'/dossiers/id/{pk}/oeuvres/stats').status_code,
            200)

    def test_kind_gating(self):
        Dossier.objects.filter(pk=self.dossier.pk).update(
            types_de_donnees=[KIND_OEUVRES])
        self.assertEqual(
            self.client.get('/dossiers/multi/evenements/data').status_code,
            404)
        self.assertEqual(
            self.client.get('/dossiers/multi/oeuvres/data').status_code, 200)

    def test_legacy_redirects(self):
        response = self.client.get('/dossiers/multi/data')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers['Location'],
                         '/dossiers/multi/evenements/data')
        response = self.client.get('/dossiers/multi/stats')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers['Location'],
                         '/dossiers/multi/evenements/stats')

    # -- Public API -----------------------------------------------------------

    def test_api_retrieve(self):
        response = self.client.get(f'/api/public/dossiers/{self.dossier.pk}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['kinds'],
                         [KIND_EVENEMENTS, KIND_OEUVRES, KIND_SOURCES])
        self.assertEqual(data['stats_kinds'], [KIND_EVENEMENTS, KIND_OEUVRES])
        self.assertEqual(data['counts'],
                         {KIND_EVENEMENTS: 1, KIND_OEUVRES: 1,
                          KIND_SOURCES: 1})

    def test_api_list_defers_counts(self):
        # The index renders cards fast by not computing counts inline: each
        # card carries counts=None and the frontend fetches them on demand.
        response = self.client.get('/api/public/dossiers/')
        self.assertEqual(response.status_code, 200)
        cards = response.json()['dossiers']
        card = next(c for c in cards if c['id'] == self.dossier.pk)
        self.assertEqual(card['kinds'],
                         [KIND_EVENEMENTS, KIND_OEUVRES, KIND_SOURCES])
        self.assertIsNone(card['counts'])

    def test_api_counts_action(self):
        # The on-demand counts endpoint returns the same live, static-wins
        # counts the index used to compute inline.
        response = self.client.get('/api/public/dossiers/counts/',
                                   {'ids': str(self.dossier.pk)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {str(self.dossier.pk): {KIND_EVENEMENTS: 1, KIND_OEUVRES: 1,
                                    KIND_SOURCES: 1}})
        # Unpublished/unknown ids are simply absent from the response.
        self.assertEqual(
            self.client.get('/api/public/dossiers/counts/',
                            {'ids': '999999999'}).json(), {})

    def test_api_kind_actions_are_gated(self):
        base = f'/api/public/dossiers/{self.dossier.pk}'
        self.assertEqual(
            self.client.get(f'{base}/evenements/').json()['count'], 1)
        self.assertEqual(self.client.get(f'{base}/oeuvres/').json()['count'],
                         1)
        self.assertEqual(self.client.get(f'{base}/sources/').json()['count'],
                         1)
        Dossier.objects.filter(pk=self.dossier.pk).update(
            types_de_donnees=[KIND_SOURCES])
        self.assertEqual(
            self.client.get(f'{base}/evenements/').json()['count'], 0)
        self.assertEqual(self.client.get(f'{base}/oeuvres/').json()['count'],
                         0)
        self.assertEqual(self.client.get(f'{base}/sources/').json()['count'],
                         1)

    def test_api_geojson_and_stats_kinds(self):
        base = f'/api/public/dossiers/{self.dossier.pk}'
        for kind in (KIND_EVENEMENTS, KIND_OEUVRES):
            response = self.client.get(f'{base}/geojson/', {'kind': kind})
            self.assertEqual(response.status_code, 200, kind)
            self.assertEqual(response.json()['type'], 'FeatureCollection')
            response = self.client.get(f'{base}/stats/', {'kind': kind})
            self.assertEqual(response.status_code, 200, kind)
        # Sources have no map/stats: empty payloads.
        self.assertEqual(
            self.client.get(f'{base}/geojson/',
                            {'kind': KIND_SOURCES}).json()['features'],
            [])
        self.assertEqual(
            self.client.get(f'{base}/stats/', {'kind': KIND_SOURCES}).json(),
            {})


@override_settings(WAGTAILSEARCH_BACKENDS={
    'default': {
        'BACKEND': 'wagtail.search.backends.database.fallback',
    },
})
class DossierWagtailPanelsTestCase(TransactionTestCase):
    """The Wagtail form hides the criteria and manual selections that do not
    apply to the ticked « types de données », the way ``js/dossier_admin.js``
    does in the Django admin. It relies on ``w-rules``, Wagtail's own
    conditional-visibility Stimulus controller, so these tests pin down the
    markup contract it needs."""

    def setUp(self):
        self.etat = Etat.objects.create(nom='public', slug='public',
                                        public=True)
        self.user = get_user_model().objects.create_superuser(
            'test_superuser', 'a@b.com', 'test_password')
        self.client.force_login(self.user)
        self.dossier = Dossier.objects.create(
            titre='Test', slug='test-panels', presentation='p',
            etat=self.etat, owner=self.user)

    def get_edit_html(self):
        response = self.client.get(reverse(
            'wagtailsnippets_dossiers_dossier:edit', args=(self.dossier.pk,)))
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    @staticmethod
    def rules(*kinds):
        # As rendered in the HTML attribute, i.e. with escaped quotes.
        return json.dumps(
            {'types_de_donnees': list(kinds)}).replace('"', '&quot;')

    def test_every_target_carries_its_own_controller(self):
        # ``w-rules`` only toggles targets inside its own element. Rather than
        # relying on a shared ancestor declaring the controller — which nothing
        # would keep in place — every panel carrying a rule is its own
        # controller, and this test is what enforces that.
        html = self.get_edit_html()
        tags = re.findall(r'<\w+[^>]*\bdata-w-rules=[^>]*>', html)
        self.assertTrue(tags)
        for tag in tags:
            self.assertIn('data-controller="w-rules"', tag)
            self.assertIn('data-w-rules-target="show"', tag)
            self.assertIn('data-action="change@document-&gt;w-rules#resolve"',
                          tag)
        self.assertEqual(html.count('data-controller="w-rules"'), len(tags))

    def test_each_kind_reveals_its_own_panels(self):
        html = self.get_edit_html()
        expected = {
            # « Sélection dynamique » as a whole: any kind ticked.
            self.rules(*KINDS_ORDER): 1,
            # circonstance, saisons, sélection manuelle.
            self.rules(KIND_EVENEMENTS): 3,
            # genres, sélection manuelle.
            self.rules(KIND_OEUVRES): 2,
            # types de source, sélection manuelle.
            self.rules(KIND_SOURCES): 2,
        }
        for rule, count in expected.items():
            self.assertEqual(html.count(rule), count, rule)
        self.assertEqual(html.count('data-w-rules-target="show"'),
                         sum(expected.values()))

    def test_rules_are_carried_by_collapsible_panel_elements(self):
        # ``w-rules`` hides a target by setting ``hidden``, which only has a
        # visible effect on the panel wrappers (a top-level ``.w-panel``
        # section, or a ``.w-panel__wrapper`` inside a MultiFieldPanel).
        for tag in re.findall(r'<\w+[^>]*data-w-rules-target="show"[^>]*>',
                              self.get_edit_html()):
            self.assertTrue(
                re.search(r'class="[^"]*w-panel(__wrapper)?[\s"]', tag), tag)
