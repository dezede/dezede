from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Permission
from django.test import TestCase
from django.urls import resolve

from ..admin_urls import get_admin_urls
from ..models import *


__all__ = ('AdminUrlsTestCase',)


class AdminUrlsTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.super = User.objects.create_superuser('super', 's@x.fr', 'pw')
        self.autre = User.objects.create_user('autre', 'a@x.fr')

        self.etat = etat = Etat.objects.create(nom='test public', public=True)
        self.lieu = lieu = Lieu.objects.create(
            nom='Lieu test', etat=etat,
            nature=NatureDeLieu.objects.create(nom='nature test'))
        # The models whose Django admin page no longer exists, with the API
        # route of their detail page.
        self.objets = {
            'événement': (
                Evenement.objects.create(
                    debut_date=date(2000, 1, 1), debut_lieu=lieu, etat=etat,
                    circonstance='Circonstance test'),
                '/api/evenements/{}/'),
            'individu': (
                Individu.objects.create(nom='Individu test', etat=etat),
                '/api/public/individus/{}/'),
            'œuvre': (
                Oeuvre.objects.create(titre='Œuvre test', etat=etat),
                '/api/public/oeuvres/{}/'),
            'partie': (
                Partie.objects.create(
                    nom='Partie test', type=Partie.INSTRUMENT, etat=etat),
                '/api/public/parties/{}/'),
            'source': (
                Source.objects.create(
                    type=TypeDeSource.objects.create(nom='type test'),
                    titre='Source test', etat=etat),
                '/api/public/sources/{}/'),
        }

    def assertWagtailUrl(self, url, obj, url_name):
        match = resolve(url)
        self.assertEqual(
            match.namespace, f'wagtailsnippets_libretto_{obj._meta.model_name}')
        self.assertEqual(match.url_name, url_name)

    def testSuperuserGetsWagtailUrls(self):
        for nom, (obj, _) in self.objets.items():
            with self.subTest(nom):
                change_url, delete_url = get_admin_urls(self.super, obj)
                self.assertWagtailUrl(change_url, obj, 'edit')
                self.assertWagtailUrl(delete_url, obj, 'delete')

    def testOthersGetNoUrls(self):
        for nom, (obj, _) in self.objets.items():
            for user in (None, AnonymousUser(), self.autre):
                with self.subTest(nom, user=user):
                    self.assertEqual(get_admin_urls(user, obj), (None, None))

    def testOnlyTheOwnerGetsUrlsWithTheSamePermissions(self):
        User = get_user_model()
        proprietaire = User.objects.create_user('proprietaire', 'p@x.fr')
        voisin = User.objects.create_user('voisin', 'v@x.fr')
        permissions = Permission.objects.filter(
            content_type__app_label='libretto',
            codename__in=('change_evenement', 'delete_evenement'))
        for user in (proprietaire, voisin):
            user.user_permissions.add(*permissions)
        evenement = Evenement.objects.create(
            debut_date=date(2000, 1, 1), debut_lieu=self.lieu, etat=self.etat,
            circonstance='Circonstance du propriétaire', owner=proprietaire)

        change_url, delete_url = get_admin_urls(proprietaire, evenement)
        self.assertWagtailUrl(change_url, evenement, 'edit')
        self.assertWagtailUrl(delete_url, evenement, 'delete')
        self.assertEqual(get_admin_urls(voisin, evenement), (None, None))

    def testApiDetailsGiveWagtailUrlsToSuperuser(self):
        self.client.force_login(self.super)
        for nom, (obj, route) in self.objets.items():
            with self.subTest(nom):
                response = self.client.get(
                    route.format(obj.pk), {'format': 'json'})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertTrue(data['can_change'])
                self.assertTrue(data['can_delete'])
                self.assertWagtailUrl(data['change_url'], obj, 'edit')
                self.assertWagtailUrl(data['delete_url'], obj, 'delete')

    def testApiDetailsGiveNoUrlToAnonymous(self):
        for nom, (obj, route) in self.objets.items():
            with self.subTest(nom):
                response = self.client.get(
                    route.format(obj.pk), {'format': 'json'})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertFalse(data['can_change'])
                self.assertFalse(data['can_delete'])
                self.assertIsNone(data['change_url'])
                self.assertIsNone(data['delete_url'])
