# coding: utf-8

from django.utils.unittest import TestCase
from ...models import *
from datetime import date
from .utils import new


class LieuTestCase(TestCase):
    def setUp(self):
        theatre = new(NatureDeLieu, nom=u'théâtre')
        ville = new(NatureDeLieu, nom='ville')
        self.rouen = new(Lieu, nom='Rouen', nature=ville)
        self.theatre_des_arts = new(Lieu,
                                    nom=u'Théâtre des Arts', nature=theatre,
                                    parent=self.rouen)

    def testComputedNames(self):
        self.assertEqual(unicode(self.rouen), 'Rouen')
        self.assertEqual(unicode(self.theatre_des_arts),
                         u'Rouen, Théâtre des Arts')


class SaisonTestCase(TestCase):
    def setUp(self):
        theatre = new(NatureDeLieu, nom=u'théâtre')
        ville = new(NatureDeLieu, nom='ville')
        rouen = new(Lieu, nom='Rouen', nature=ville)
        theatre_des_arts = new(Lieu,
            nom=u'Théâtre des Arts', nature=theatre, parent=rouen)
        self.saison = new(Saison,
            lieu=theatre_des_arts, debut=date(2011, 9, 1),
            fin=date(2012, 8, 31))

    def testComputedNames(self):
        self.assertEqual(unicode(self.saison),
                         u'Rouen, Théâtre des Arts, 2011–2012')
