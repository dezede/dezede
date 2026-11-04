from datetime import date
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.template import Context
from django.test import RequestFactory, TestCase
from django.urls import reverse

from dossiers.models import DossierDOeuvres
from dossiers.views import DossierDOeuvresDataDetail
from ..models import *
from ..templatetags.routines import evenement_list_def

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
