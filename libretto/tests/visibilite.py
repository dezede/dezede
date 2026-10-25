from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from dossiers.export import ScenariosExporter
from dossiers.jobs import dossier_to_xlsx
from dossiers.models import Dossier, DossierDEvenements, DossierDOeuvres
from dezede.models import IndexEntryExtension
from dezede.search_backend import refresh_visibility
from dezede.views import SearchView
from dossiers.views import DossierDOeuvresDataDetail
from ..models import *
from ..signals import refresh_search_visibility
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
