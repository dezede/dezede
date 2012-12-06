# coding: utf-8

from __future__ import unicode_literals
from django.test import TestCase
from ...models import *


class EvenementTestCase(TestCase):
    fixtures = ['catalogue/tests/models/fixtures/auth.json',
                'catalogue/tests/models/fixtures/evenement.json']

    def setUp(self):
        self.nicolas = Evenement.objects.all()[0]

    def testProgrammeRendering(self):
        programme = self.nicolas.programme.all()
        self.assertEqual(unicode(programme[0]),
                         '« Avez-vous été bien sages les enfants ? »')
        self.assertEqual(unicode(programme[1]),
                         'Le père Fouettard, ou la correction méritée, '
                         'mélodrame [première représentation]')
        self.assertEqual(unicode(programme[2]),
                         'Distribution de tatanées')
        self.assertEqual(unicode(programme[3]),
                         'L’arrivée du père Noël, ou Le Saint Nicolas vengeur')
        self.assertEqual(unicode(programme[4]),
                         'Distribution de pains d’épices')

    def testRendering(self):
        self.assertEqual(unicode(self.nicolas),
                         'Jeudi 6 décembre 2012 > '
                         'Rouen, Théâtre des Arts, Saint-Nicolas')
