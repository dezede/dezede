# coding: utf-8

from __future__ import unicode_literals
from datetime import date
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_text
from ...models import *
from .utils import new, log_as_superuser, TransactionTestCase


class LieuTestCase(TransactionTestCase):
    def setUp(self):
        theatre = new(NatureDeLieu, nom='théâtre')
        ville = new(NatureDeLieu, nom='ville')
        self.rouen = new(LieuDivers, nom='Rouen', nature=ville)
        self.theatre_des_arts = new(Institution,
                                    nom='Théâtre des Arts', nature=theatre,
                                    parent=self.rouen)
        # Test client
        log_as_superuser(self)

    def testComputedNames(self):
        self.assertEqual(smart_text(self.rouen), 'Rouen')
        self.assertEqual(smart_text(self.theatre_des_arts),
                         'Rouen, Théâtre des Arts')

    def testTemplateRenders(self):
        for lieu in Lieu.objects.all():
            self.fetch_page(lieu.get_absolute_url())

    def testAdminRenders(self):
        self.fetch_page(reverse('admin:libretto_lieu_changelist'))
        self.fetch_page(reverse('admin:libretto_lieu_add'))
        for lieu in Lieu.objects.all():
            self.fetch_page(
                reverse('admin:libretto_lieu_history', args=[lieu.pk]))
            self.fetch_page(
                reverse('admin:libretto_lieu_delete', args=[lieu.pk]))
            self.fetch_page(
                reverse('admin:libretto_lieu_change', args=[lieu.pk]))


class SaisonTestCase(TransactionTestCase):
    def setUp(self):
        theatre = new(NatureDeLieu, nom='théâtre')
        ville = new(NatureDeLieu, nom='ville')
        rouen = new(Lieu, nom='Rouen', nature=ville)
        theatre_des_arts = new(
            Lieu, nom='Théâtre des Arts', nature=theatre, parent=rouen)
        self.saison = new(
            Saison, lieu=theatre_des_arts, debut=date(2011, 9, 1),
            fin=date(2012, 8, 31))
        # Test client
        log_as_superuser(self)

    def testComputedNames(self):
        self.assertEqual(smart_text(self.saison),
                         'Rouen, Théâtre des Arts, 2011–2012')

    def testAdminRenders(self):
        self.fetch_page(reverse('admin:libretto_saison_changelist'))
        self.fetch_page(
            reverse('admin:libretto_saison_change', args=[self.saison.pk]))
