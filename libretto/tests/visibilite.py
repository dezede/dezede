import json
import re
from datetime import date
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase
from django.urls import reverse

from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from bs4 import BeautifulSoup
from dossiers.export import ScenariosExporter
from dossiers.jobs import dossier_to_xlsx
from dossiers.models import (
    CategorieDeDossiers, Dossier, DossierDEvenements, DossierDOeuvres,
)
from dezede.models import IndexEntryExtension
from dezede.search_backend import refresh_visibility
from dezede.views import SearchView, autocomplete_search
from dossiers.views import DossierDOeuvresDataDetail
from ..models import *
from ..signals import refresh_search_visibility
from wagtail.coreutils import get_supported_content_language_variant
from wagtail.models import Locale, Page
from wagtail.search.backends import get_search_backend
from wagtail.search.models import IndexEntry

__all__ = ('VisibiliteTestCase',)


class VisibiliteTestCase(TestCase):
    """Anonymous, owner, other user and superuser must each get the right
    counts and lists."""

    def setUp(self):
        User = get_user_model()
        self.proprietaire = User.objects.create_user('proprietaire', 'p@x.fr')
        self.autre = User.objects.create_user('autre', 'a@x.fr')
        self.super = User.objects.create_superuser('super', 's@x.fr', 'pw')

        public = Etat.objects.create(nom='test public', public=True)
        prive = Etat.objects.create(nom='test privé', public=False)

        nature = NatureDeLieu.objects.create(nom='nature test')
        self.lieu = Lieu.objects.create(
            nom='Lieu test', nature=nature, etat=public)
        self.ensemble = Ensemble.objects.create(
            nom='Ensemble test', siege=self.lieu, etat=public)
        self.oeuvre = Oeuvre.objects.create(titre='Œuvre publique',
                                            etat=public)
        self.oeuvre_privee = Oeuvre.objects.create(
            titre='Œuvre privée', etat=prive, owner=self.proprietaire)
        self.evenement = self._evenement(public, None, 'Circonstance publique')
        self.evenement_prive = self._evenement(
            prive, self.proprietaire, 'Circonstance privée')

        Auteur.objects.create(oeuvre=self.oeuvre_privee,
                              individu=Individu.objects.create(
                                  nom='Auteur test', etat=public))

    def _evenement(self, etat, owner, circonstance):
        evenement = Evenement.objects.create(
            debut_date=date(2000, 1, 1), debut_lieu=self.lieu, etat=etat,
            owner=owner, circonstance=circonstance, notes_privees='secret')
        ElementDeProgramme.objects.create(
            evenement=evenement, oeuvre=self.oeuvre, position=1)
        ElementDeDistribution.objects.create(
            evenement=evenement, ensemble=self.ensemble)
        return evenement

    def _request(self, user=None):
        request = RequestFactory().get('/')
        request.user = AnonymousUser() if user is None else user
        return request

    def _viewers(self):
        return {
            'anonyme': (None, 1),
            'autre': (self.autre, 1),
            'proprietaire': (self.proprietaire, 2),
            'super': (self.super, 2),
        }

    def _api_status(self, url, user=None):
        self.client.logout()
        if user is not None:
            self.client.force_login(user)
        return self.client.get(url, {'format': 'json'})

    def testApiHidesPrivateNotes(self):
        response = self._api_status(f'/api/evenements/{self.evenement.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('notes_privees', response.content.decode())

    def testApiAuteurs(self):
        url = f'/api/auteurs/{Auteur.objects.get(oeuvre=self.oeuvre_privee).pk}/'
        self.assertEqual(self._api_status(url).status_code, 404)
        self.assertEqual(self._api_status(url, self.autre).status_code, 404)
        self.assertEqual(
            self._api_status(url, self.proprietaire).status_code, 200)

    def testApiProfessionsArePublished(self):
        profession = Profession.objects.create(
            nom='Profession test', etat=Etat.objects.get(nom='test privé'),
            owner=self.proprietaire)
        url = f'/api/professions/{profession.pk}/'
        self.assertEqual(self._api_status(url).status_code, 404)
        self.assertEqual(
            self._api_status(url, self.proprietaire).status_code, 200)

    def testDossierDOeuvresIsPublished(self):
        dossier = DossierDOeuvres.objects.create(
            titre='Dossier test', slug='dossier-test',
            etat=Etat.objects.get(nom='test public'))
        dossier.oeuvres.add(self.oeuvre, self.oeuvre_privee)
        for nom, (user, _) in self._viewers().items():
            with self.subTest(nom):
                vue = DossierDOeuvresDataDetail(dossier=dossier)
                vue.request = self._request(user)
                pks = set(vue.get_queryset().values_list('pk', flat=True))
                self.assertEqual(
                    self.oeuvre_privee.pk in pks,
                    user in (self.proprietaire, self.super))

    def _search_visibles(self, user):
        request = RequestFactory().get(
            '/recherche/', {'models': 'libretto.Oeuvre'})
        request.user = self._request(user).user
        vue = SearchView()
        vue.request = request
        vue.args = vue.kwargs = ()
        pks = [str(self.oeuvre.pk), str(self.oeuvre_privee.pk)]
        return set(vue.get_queryset().filter(object_id__in=pks)
                   .values_list('object_id', flat=True))

    def testSearchHidesUnpublished(self):
        pks = {str(self.oeuvre.pk), str(self.oeuvre_privee.pk)}
        self.assertEqual(IndexEntry.objects.filter(
            content_type=ContentType.objects.get_for_model(Oeuvre),
            object_id__in=pks).count(), 2)
        for nom, (user, _) in self._viewers().items():
            with self.subTest(nom):
                self.assertEqual(
                    self._search_visibles(user),
                    pks if user in (self.proprietaire, self.super)
                    else {str(self.oeuvre.pk)})

    def testAutocompleteWithoutModelHidesUnpublished(self):
        for nom, (user, _) in self._viewers().items():
            with self.subTest(nom):
                request = self._request(user)
                pks = {o.pk for o in autocomplete_search(request, 'Œuvre')}
                self.assertEqual(
                    pks,
                    {self.oeuvre.pk, self.oeuvre_privee.pk}
                    if user in (self.proprietaire, self.super)
                    else {self.oeuvre.pk})

    def testAutocompleteWithoutModelExcludesPages(self):
        Locale.objects.get_or_create(
            language_code=get_supported_content_language_variant(
                settings.LANGUAGE_CODE))
        racine = Page.get_first_root_node() or Page.add_root(
            instance=Page(title='Racine', slug='racine'))
        publiee = racine.add_child(
            instance=Page(title='Pagetest publiée', slug='pagetest-publiee'))
        racine.add_child(instance=Page(
            title='Pagetest brouillon', slug='pagetest-brouillon', live=False))

        # Guard against a vacuous pass: the page is indexed and the search
        # does find it once a model is given.
        self.assertTrue(IndexEntry.objects.filter(
            content_type=ContentType.objects.get_for_model(Page),
            object_id=str(publiee.pk)).exists())
        self.assertEqual(
            [p.pk for p in autocomplete_search(
                self._request(self.super), 'Pagetest', Page)],
            [publiee.pk])

        for nom, (user, _) in self._viewers().items():
            with self.subTest(nom):
                resultats = autocomplete_search(self._request(user), 'Pagetest')
                self.assertEqual(resultats, [])

    def testAutocompleteViewWithoutModelHidesUnpublished(self):
        self.client.logout()
        response = self.client.get('/autocomplete', {'q': 'Œuvre'})
        self.assertEqual(response.status_code, 200)
        # The view escapes non-ASCII characters, so compare parsed values.
        titres = {s['str'] for s in response.json()}
        self.assertTrue(any('Œuvre publique' in t for t in titres))
        self.assertFalse(any('Œuvre privée' in t for t in titres))

    def testSearchFollowsEtatChange(self):
        # Saving an Etat doesn't reindex the objects that use it.
        etat = self.oeuvre_privee.etat
        etat.public = True
        etat.save()
        refresh_visibility(etat.pk)
        self.assertEqual(self._search_visibles(None),
                         {str(self.oeuvre.pk), str(self.oeuvre_privee.pk)})
        etat.public = False
        etat.save()
        refresh_visibility(etat.pk)
        self.assertEqual(self._search_visibles(None), {str(self.oeuvre.pk)})

    def testSavingEtatEnqueuesSearchRefresh(self):
        etat = self.oeuvre_privee.etat
        with patch('libretto.signals.django_rq.enqueue') as enqueue:
            with self.captureOnCommitCallbacks(execute=True):
                etat.save()
        calls = [c for c in enqueue.call_args_list
                 if c.args and c.args[0] is refresh_search_visibility]
        self.assertEqual([c.kwargs['args'] for c in calls], [(etat.pk,)])

    def testSearchFollowsOwnerChange(self):
        self.oeuvre_privee.owner = self.autre
        self.oeuvre_privee.save()
        self.assertIn(str(self.oeuvre_privee.pk),
                      self._search_visibles(self.autre))
        self.assertNotIn(str(self.oeuvre_privee.pk),
                         self._search_visibles(self.proprietaire))

    def _extension(self, objet):
        return IndexEntryExtension.objects.get(
            index_entry_ptr__content_type=ContentType.objects.get_for_model(
                objet),
            index_entry_ptr__object_id=str(objet.pk))

    def testRowBoostsCopyVisibility(self):
        index = get_search_backend().get_index_for_model(Oeuvre)
        IndexEntryExtension.objects.all().update(public=True, owner_pk=None)
        index.update_row_boosts(Oeuvre, [self.oeuvre, self.oeuvre_privee])
        extension = self._extension(self.oeuvre)
        self.assertEqual((extension.public, extension.owner_pk), (True, None))
        extension = self._extension(self.oeuvre_privee)
        self.assertEqual(
            (extension.public, extension.owner_pk),
            (False, self.proprietaire.pk))

    def testRowBoostsHideDeletedObject(self):
        individu = Individu.objects.create(
            nom='Individu test', etat=self.lieu.etat)
        self.assertTrue(self._extension(individu).public)
        # Skips the signals, so the index entry outlives its object.
        Individu.objects.filter(pk=individu.pk)._raw_delete(
            Individu.objects.db)
        get_search_backend().get_index_for_model(Individu).update_row_boosts(
            Individu, [individu])
        self.assertFalse(self._extension(individu).public)

    def testTreeBoostsKeepVisibility(self):
        enfant = Lieu.objects.create(
            nom='Lieu enfant', nature=self.lieu.nature, parent=self.lieu,
            etat=self.lieu.etat)
        # Values the tree pass must not touch.
        IndexEntryExtension.objects.filter(
            pk=self._extension(self.lieu).pk,
        ).update(boost=1.0, public=False, owner_pk=self.autre.pk)
        IndexEntryExtension.objects.filter(
            pk=self._extension(enfant).pk).update(boost=100.0)
        get_search_backend().get_index_for_model(
            Lieu).update_tree_boosts_from_descendants(Lieu, [self.lieu])
        extension = self._extension(self.lieu)
        self.assertEqual(extension.boost, 100.0)
        self.assertEqual(
            (extension.public, extension.owner_pk), (False, self.autre.pk))

    def _dossier_prive(self, classe=DossierDEvenements):
        public = Etat.objects.get(nom='test public')
        prive = Etat.objects.get(nom='test privé')
        return (
            classe.objects.create(titre='Dossier public', slug=f'd-pub-{classe.__name__}',
                                  etat=public),
            classe.objects.create(titre='Dossier privé', slug=f'd-priv-{classe.__name__}',
                                  etat=prive, owner=self.proprietaire),
        )

    def _search_dossiers(self, user, dossiers):
        request = RequestFactory().get(
            '/recherche/', {'models': 'dossiers.Dossier'})
        request.user = self._request(user).user
        vue = SearchView()
        vue.request = request
        vue.args = vue.kwargs = ()
        return set(vue.get_queryset().filter(
            object_id__in=[str(d.pk) for d in dossiers],
        ).values_list('object_id', flat=True))

    def _entries(self, dossier, classe=Dossier):
        return IndexEntry.objects.filter(
            content_type=ContentType.objects.get_for_model(classe),
            object_id=str(dossier.pk))

    def testDossierSubclassIsIndexedOnceUnderDossier(self):
        for classe in (DossierDEvenements, DossierDOeuvres):
            with self.subTest(classe.__name__):
                public, prive = self._dossier_prive(classe)
                for dossier in (public, prive):
                    self.assertEqual(self._entries(dossier).count(), 1)
                    self.assertEqual(
                        self._entries(dossier, classe).count(), 0)
                extension = self._entries(prive).get().extension
                self.assertEqual(
                    (extension.public, extension.owner_pk),
                    (False, self.proprietaire.pk))
                self.assertTrue(self._entries(public).get().extension.public)

    def testDossierSubclassesAreNotRebuilt(self):
        self._dossier_prive()
        self.assertFalse(DossierDEvenements.get_indexed_objects().exists())

    def testSearchHidesPrivateDossierSubclasses(self):
        for classe in (DossierDEvenements, DossierDOeuvres):
            with self.subTest(classe.__name__):
                public, prive = self._dossier_prive(classe)
                for nom, (user, _) in self._viewers().items():
                    with self.subTest(nom):
                        self.assertEqual(
                            self._search_dossiers(user, (public, prive)),
                            {str(public.pk), str(prive.pk)}
                            if user in (self.proprietaire, self.super)
                            else {str(public.pk)})

    def testSearchFollowsDossierEtatChange(self):
        public, prive = self._dossier_prive()
        etat = prive.etat
        etat.public = True
        etat.save()
        refresh_visibility(etat.pk)
        self.assertEqual(self._search_dossiers(None, (public, prive)),
                         {str(public.pk), str(prive.pk)})

    def _dossier_d_evenements(self):
        ElementDeProgramme.objects.create(
            evenement=self.evenement, oeuvre=self.oeuvre_privee, position=2)
        dossier = DossierDEvenements.objects.create(
            titre='Dossier événements test', slug='dossier-evenements-test',
            etat=Etat.objects.get(nom='test public'))
        dossier.evenements.add(self.evenement, self.evenement_prive)
        return dossier

    def testScenariosExportHidesUnpublished(self):
        dossier = self._dossier_d_evenements()
        for nom, (user, attendu) in self._viewers().items():
            with self.subTest(nom):
                request = self._request(user)
                exporters = ScenariosExporter(
                    dossier, [{'scenario': 'scenario-1'},
                              {'scenario': 'scenario-7'}],
                    request=request).exporters
                self.assertEqual(len(exporters), 2)
                self.assertEqual(exporters[0].queryset.count(), attendu)
                oeuvres = {e.oeuvre for e in exporters[1].queryset}
                self.assertEqual('Œuvre privée' in oeuvres,
                                 user in (self.proprietaire, self.super))

    def testScenariosExportersDontAccumulate(self):
        dossier = self._dossier_d_evenements()
        scenarios = [{'scenario': 'scenario-1'}]
        ScenariosExporter(dossier, scenarios)
        self.assertEqual(len(ScenariosExporter(dossier, scenarios).exporters), 1)

    def testPdfExportHidesUnpublished(self):
        dossier = self._dossier_d_evenements()
        for nom, (user, attendu) in self._viewers().items():
            with self.subTest(nom):
                request = self._request(user)
                tex = render_to_string(
                    'dossiers/dossierdevenements_detail.tex',
                    {'object': dossier, 'request': request,
                     'user': request.user, 'SITE': Site.objects.get_current(),
                     'source_dict': {}})
                self.assertIn('Circonstance publique', tex)
                self.assertEqual('Circonstance privée' in tex, attendu == 2)

    def testXlsxJobFiltersByTheExportingUser(self):
        dossier = self._dossier_d_evenements()
        for user, attendu in ((self.autre, 1), (self.proprietaire, 2),
                              (self.super, 2)):
            with self.subTest(user.username):
                data = {'dossier': dossier.pk,
                        'scenarios': [{'scenario': 'scenario-1'}]}
                with patch('dossiers.jobs.send_export') as send_export:
                    dossier_to_xlsx(data, user.pk, 1, 'fr')
                exporter = send_export.call_args.args[0]
                self.assertEqual(
                    exporter.exporters[0].queryset.count(), attendu)

    def _get(self, url, user=None):
        self.client.logout()
        if user is not None:
            self.client.force_login(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response

    def _dossier_avec_contributeurs(self):
        dossier = self._dossier_d_evenements()
        source = Source.objects.create(
            type=TypeDeSource.objects.create(nom='type test'),
            titre='Source privée', etat=Etat.objects.get(nom='test privé'),
            owner=self.autre)
        source.evenements.add(self.evenement)
        return dossier

    def testDossierContributorsAreVisibleOnesOnly(self):
        dossier = self._dossier_avec_contributeurs()
        # The public event has no owner, so only the private event and the
        # private source bring contributors.
        attendus = {
            'anonyme': set(),
            'autre': {self.autre.pk},
            'proprietaire': {self.proprietaire.pk},
            'super': {self.proprietaire.pk, self.autre.pk},
        }
        for nom, (user, _) in self._viewers().items():
            with self.subTest(nom):
                contributeurs = dossier.get_contributors(self._request(user))
                self.assertEqual({u.pk for u in contributeurs}, attendus[nom])

    def testDossierContributorsAreComputedOncePerViewer(self):
        dossier = self._dossier_avec_contributeurs()
        request = self._request(self.autre)
        first = dossier.get_contributors(request)
        with self.assertNumQueries(0):
            self.assertIs(dossier.get_contributors(request), first)
        self.assertIsNot(
            dossier.get_contributors(self._request(self.super)), first)

    def testDossierContributorsDefaultToPublicData(self):
        dossier = self._dossier_avec_contributeurs()
        self.assertFalse(dossier.get_contributors().exists())

    def testDossierPageShowsVisibleContributorsOnly(self):
        dossier = self._dossier_avec_contributeurs()
        url = reverse('dossier_detail', args=(dossier.slug,))
        for nom, (user, _) in self._viewers().items():
            with self.subTest(nom):
                html = self._get(url, user).content.decode()
                self.assertEqual(
                    re.search(r'<dt>\s*Contributeurs?\s*</dt>', html)
                    is not None,
                    user is not None)

    def testUserPageListsVisibleDossiersOnly(self):
        publie = self._dossier_d_evenements()
        prive = DossierDEvenements.objects.create(
            titre='Dossier privé test', slug='dossier-prive-test',
            etat=Etat.objects.get(nom='test privé'), owner=self.proprietaire)
        for dossier in (publie, prive):
            dossier.editeurs_scientifiques.add(self.autre)
        url = reverse('user_profile', args=(self.autre.username,))
        attendus = {
            'anonyme': (True, False),
            'autre': (True, False),
            'proprietaire': (True, True),
            'super': (True, True),
        }
        for nom, (user, _) in self._viewers().items():
            with self.subTest(nom):
                html = self._get(url, user).content.decode()
                self.assertEqual(
                    (publie.titre in html, prive.titre in html),
                    attendus[nom])

    def testUserPageHidesSectionWithoutVisibleDossier(self):
        prive = DossierDEvenements.objects.create(
            titre='Dossier privé test', slug='dossier-prive-test',
            etat=Etat.objects.get(nom='test privé'), owner=self.proprietaire)
        prive.editeurs_scientifiques.add(self.autre)
        url = reverse('user_profile', args=(self.autre.username,))
        html = self._get(url).content.decode()
        self.assertNotIn('À consulter dans Dezède', html)

    def testDossierPdfShowsVisibleContributorsOnly(self):
        dossier = self._dossier_avec_contributeurs()
        for nom, (user, _) in self._viewers().items():
            with self.subTest(nom):
                request = self._request(user)
                tex = render_to_string(
                    'dossiers/dossierdevenements_detail.tex',
                    {'object': dossier, 'request': request,
                     'user': request.user, 'SITE': Site.objects.get_current(),
                     'source_dict': {}})
                self.assertEqual(
                    self.proprietaire.username in tex,
                    user in (self.proprietaire, self.super))

    def _tree(self, path, user=None):
        self.client.logout()
        if user is not None:
            self.client.force_login(user)
        return self.client.get(f'/tree_node/{path}')

    def _tree_nodes(self, path, user=None):
        response = self._tree(path, user)
        self.assertEqual(response.status_code, 200)
        # The view serves JSON as text/html, so `response.json()` refuses it.
        return {int(n['id']): n['label'] for n in json.loads(response.content)}

    def _trees(self):
        """Every tree of the site: its parent, the URL listing the children of
        that parent, and a public and a private (owned) child."""
        public = Etat.objects.get(nom='test public')
        prive = Etat.objects.get(nom='test privé')

        def enfants(creer):
            return {'public': creer('public', public, None),
                    'prive': creer('prive', prive, self.proprietaire)}

        categorie = CategorieDeDossiers.objects.create(
            nom='Catégorie test', etat=public)
        autre_categorie = CategorieDeDossiers.objects.create(
            nom='Autre catégorie test', etat=public)
        partie = Partie.objects.create(
            nom='Partie parent', type=Partie.INSTRUMENT, etat=public)
        profession = Profession.objects.create(
            nom='profession parent', etat=public)
        dossier = DossierDEvenements.objects.create(
            titre='Dossier parent', slug='dossier-parent',
            categorie=autre_categorie, etat=public)
        return {
            'lieu': {
                'parent': self.lieu,
                'url': f'libretto/lieu/nom/{self.lieu.pk}',
                'enfants': enfants(lambda s, etat, owner: Lieu.objects.create(
                    nom=f'Lieu enfant {s}', nature=self.lieu.nature,
                    parent=self.lieu, etat=etat, owner=owner)),
            },
            'oeuvre': {
                'parent': self.oeuvre,
                'url': f'libretto/oeuvre/short_html/{self.oeuvre.pk}',
                'enfants': enfants(lambda s, etat, owner: Oeuvre.objects.create(
                    titre=f'Extrait {s}', extrait_de=self.oeuvre, etat=etat,
                    owner=owner)),
            },
            'partie': {
                'parent': partie,
                'url': f'libretto/partie/__str__/{partie.pk}',
                'enfants': enfants(lambda s, etat, owner: Partie.objects.create(
                    nom=f'Partie enfant {s}', type=Partie.INSTRUMENT,
                    parent=partie, etat=etat, owner=owner)),
            },
            'profession': {
                'parent': profession,
                'url': f'libretto/profession/__str__/{profession.pk}',
                'enfants': enfants(
                    lambda s, etat, owner: Profession.objects.create(
                        nom=f'profession enfant {s}', parent=profession,
                        etat=etat, owner=owner)),
            },
            'categorie': {
                'parent': categorie,
                'url': f'dossiers/categoriededossiers/short_link/'
                       f'{categorie.pk}',
                'enfants': enfants(
                    lambda s, etat, owner: DossierDEvenements.objects.create(
                        titre=f'Dossier de catégorie {s}',
                        slug=f'dossier-categorie-{s}', categorie=categorie,
                        etat=etat, owner=owner)),
            },
            # `node` swaps the category for the dossier it names.
            'dossier': {
                'parent': dossier,
                'url': f'dossiers/categoriededossiers/short_link/'
                       f'{categorie.pk}?node={dossier.pk}',
                'enfants': enfants(
                    lambda s, etat, owner: DossierDEvenements.objects.create(
                        titre=f'Sous-dossier {s}', slug=f'sous-dossier-{s}',
                        parent=dossier, etat=etat, owner=owner)),
            },
        }

    def testTreeNodeRejectsUnlistedModelsAndAttributes(self):
        for combinaison in (
            'accounts/hierarchicuser/password',
            'accounts/hierarchicuser/email',
            'libretto/lieu/delete',
            'libretto/lieu/notes_privees',
            'libretto/oeuvre/notes_privees',
            'libretto/individu/nom',
            # A listed model and a listed attribute, but not together.
            'libretto/lieu/short_html',
            'libretto/oeuvre/nom',
        ):
            for nom, user in (('anonyme', None), ('super', self.super)):
                with self.subTest(combinaison=combinaison, viewer=nom):
                    response = self._tree(combinaison + '/', user)
                    self.assertEqual(response.status_code, 404)
        self.assertTrue(Lieu.objects.filter(pk=self.lieu.pk).exists())

    def testTreeNodeHasNoRootForModelsThatAreNotTrees(self):
        for chemin in ('libretto/partie/__str__/',
                       'libretto/profession/__str__/'):
            for nom, user in (('anonyme', None), ('super', self.super)):
                with self.subTest(chemin=chemin, viewer=nom):
                    self.assertEqual(self._tree(chemin, user).status_code, 404)

    def testTreeNodeServesWhatThePagesAsk(self):
        trees = self._trees()
        pages = [
            trees['lieu']['parent'].get_absolute_url(),
            reverse('lieu_index'),
            trees['oeuvre']['parent'].get_absolute_url(),
            trees['partie']['parent'].get_absolute_url(),
            trees['profession']['parent'].get_absolute_url(),
            reverse('dossier_index'),
        ]
        urls = set()
        for page in pages:
            with self.subTest(page):
                html = self._get(page).content.decode()
                trouvees = re.findall(r'data-url="(/tree_node/[^"]*)"', html)
                self.assertTrue(trouvees)
                urls.update(trouvees)
        for url in urls:
            with self.subTest(url):
                self.client.logout()
                self.assertEqual(self.client.get(url).status_code, 200)

    def testTreeNodeRootsHideUnpublished(self):
        lieu_prive = Lieu.objects.create(
            nom='Lieu racine privé', nature=self.lieu.nature,
            etat=Etat.objects.get(nom='test privé'), owner=self.proprietaire)
        racines = {
            'libretto/lieu/nom/': (self.lieu, lieu_prive),
            'libretto/oeuvre/short_html/': (self.oeuvre, self.oeuvre_privee),
        }
        for chemin, (visible, cache) in racines.items():
            for nom, (user, attendu) in self._viewers().items():
                with self.subTest(chemin=chemin, viewer=nom):
                    pks = set(self._tree_nodes(chemin, user))
                    self.assertIn(visible.pk, pks)
                    self.assertEqual(cache.pk in pks, attendu == 2)

    def testTreeNodeHidesUnpublishedChildren(self):
        for tree_name, tree in self._trees().items():
            enfants = tree['enfants']
            for nom, (user, attendu) in self._viewers().items():
                with self.subTest(tree=tree_name, viewer=nom):
                    noeuds = self._tree_nodes(tree['url'], user)
                    self.assertEqual(
                        set(noeuds),
                        {e.pk for e in enfants.values()} if attendu == 2
                        else {enfants['public'].pk})
                    self.assertIn(
                        'public', noeuds[enfants['public'].pk].lower())

    def testEvenementFilterWidgetHidesUnpublishedNames(self):
        individu = Individu.objects.create(
            nom='Nom secret', etat=Etat.objects.get(nom='test privé'),
            owner=self.proprietaire)
        url = reverse('evenements') + f'?individu=|{individu.pk}|'
        for nom, (user, attendu) in self._viewers().items():
            with self.subTest(viewer=nom):
                self.client.logout()
                if user is not None:
                    self.client.force_login(user)
                contenu = self.client.get(url).content.decode()
                self.assertEqual('Nom secret' in contenu, attendu == 2)

    def testEvenementFilterIgnoresUnpublishedObjects(self):
        ElementDeProgramme.objects.create(
            evenement=self.evenement, oeuvre=self.oeuvre_privee, position=2)
        self._evenement(Etat.objects.get(nom='test public'), None, 'Autre')
        url = reverse('evenements') + f'?oeuvre=|{self.oeuvre_privee.pk}|'
        # Le filtre n'agit que pour qui voit l'œuvre.
        attendus = {'anonyme': 2, 'autre': 2, 'proprietaire': 1, 'super': 1}
        for nom, (user, _) in self._viewers().items():
            with self.subTest(viewer=nom):
                self.client.logout()
                if user is not None:
                    self.client.force_login(user)
                response = self.client.get(url)
                self.assertEqual(
                    len(response.context['object_list']), attendus[nom])

    def testChoosersShowWhichAutoritesAreNotPublished(self):
        public = Etat.objects.get(nom='test public')
        prive = Etat.objects.get(nom='test privé')
        Individu.objects.create(nom='Zzzchoix publié', etat=public)
        Individu.objects.create(nom='Zzzchoix caché', etat=prive)
        self.client.force_login(self.super)
        response = self.client.get(
            reverse('wagtailsnippetchoosers_libretto_individu:choose_results'),
            {'q': 'Zzzchoix'})
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('Zzzchoix publié', html)
        self.assertIn('Zzzchoix caché', html)
        soup = BeautifulSoup(html, 'html.parser')

        def icone_et_etat(nom):
            ligne = next(tr for tr in soup.select('tr') if nom in tr.text)
            (icone,) = [
                svg['class'] for svg in ligne.select('svg')
                if {'w-text-positive-100', 'w-text-text-error'}
                & set(svg['class'])
            ]
            return icone, ligne.text

        # A green tick for the published états, a red cross for the others.
        icone, ligne = icone_et_etat('Zzzchoix publié')
        self.assertIn('w-text-positive-100', icone)
        self.assertIn('test public', ligne)
        icone, ligne = icone_et_etat('Zzzchoix caché')
        self.assertIn('w-text-text-error', icone)
        self.assertIn('test privé', ligne)
