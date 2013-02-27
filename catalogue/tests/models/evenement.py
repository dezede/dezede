# coding: utf-8

from __future__ import unicode_literals
from django.test import TransactionTestCase
from django.utils.encoding import smart_text
from ...models import *


class EvenementTestCase(TransactionTestCase):
    fixtures = ['catalogue/tests/models/fixtures/auth.json',
                'catalogue/tests/models/fixtures/evenement.json']
    cleans_up_after_itself = True

    def setUp(self):
        self.nicolas = Evenement.objects.all()[0]

    def testProgrammeRendering(self):
        programme = self.nicolas.programme.all()
        self.assertEqual(smart_text(programme[0]),
                         '« Avez-vous été bien sages les enfants ? »')
        self.assertEqual(smart_text(programme[1]),
                         'Le père Fouettard, ou la correction méritée, '
                         'mélodrame [première représentation]')
        self.assertEqual(smart_text(programme[2]),
                         'Distribution de tatanées')
        self.assertEqual(smart_text(programme[3]),
                         'L’arrivée du père Noël, ou Le Saint Nicolas vengeur')
        self.assertEqual(smart_text(programme[4]),
                         'Distribution de pains d’épices')

    def testRendering(self):
        self.assertEqual(smart_text(self.nicolas),
                         'Jeudi 6 décembre 2012 > '
                         'Rouen, Théâtre des Arts, Saint-Nicolas')
