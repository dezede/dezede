from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from dossiers.models import DossierDOeuvres
from dossiers.views import DossierDOeuvresDataDetail
from ..models import *

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
        self.evenement = self._evenement(public, None)
        self.evenement_prive = self._evenement(prive, self.proprietaire)

        Auteur.objects.create(oeuvre=self.oeuvre_privee,
                              individu=Individu.objects.create(
                                  nom='Auteur test', etat=public))

    def _evenement(self, etat, owner):
        evenement = Evenement.objects.create(
            debut_date=date(2000, 1, 1), debut_lieu=self.lieu, etat=etat,
            owner=owner, notes_privees='secret')
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
