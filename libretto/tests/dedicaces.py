from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import *
from ..models.oeuvre import Dedicace


__all__ = ('IndividuDedicacesTestCase',)


class IndividuDedicacesTestCase(TestCase):
    def setUp(self):
        self.proprietaire = get_user_model().objects.create_user(
            'proprietaire', 'p@x.fr')
        public = Etat.objects.create(nom='test public', public=True)
        prive = Etat.objects.create(nom='test privé', public=False)

        self.individu = Individu.objects.create(nom='Dédicataire', etat=public)
        self.oeuvre = Oeuvre.objects.create(titre='Œuvre publique', etat=public)
        self.oeuvre_privee = Oeuvre.objects.create(
            titre='Œuvre privée', etat=prive, owner=self.proprietaire)
        for oeuvre in (self.oeuvre, self.oeuvre_privee):
            Dedicace.objects.create(oeuvre=oeuvre, individu=self.individu)

        self.url = f'/api/public/individus/{self.individu.pk}/'

    def _get(self, url, user=None, **params):
        self.client.logout()
        if user is not None:
            self.client.force_login(user)
        return self.client.get(url, {'format': 'json', **params})

    def testDetailCountsOnlyTheDedicatedWorksTheViewerMaySee(self):
        for user, attendu in ((None, 1), (self.proprietaire, 2)):
            with self.subTest(user=user):
                response = self._get(self.url, user)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['dedicaces_count'], attendu)

    def testRelatedListsOnlyTheDedicatedWorksTheViewerMaySee(self):
        for user, attendus in (
            (None, {self.oeuvre.pk}),
            (self.proprietaire, {self.oeuvre.pk, self.oeuvre_privee.pk}),
        ):
            with self.subTest(user=user):
                response = self._get(
                    f'{self.url}related/', user, collection='dedicaces')
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data['count'], len(attendus))
                self.assertEqual(
                    {oeuvre['id'] for oeuvre in data['results']}, attendus)
