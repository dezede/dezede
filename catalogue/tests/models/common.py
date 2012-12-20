# coding: utf-8

from __future__ import unicode_literals
from django.test import TransactionTestCase
from ...models import *
from .utils import new


class EtatTestCase(TransactionTestCase):
    cleans_up_after_itself = True

    def setUp(self):
        self.brouillon = new(Etat, nom='brouillon', public=False)
        self.nouveau = new(Etat, nom='nouveau', nom_pluriel='nouveaux')

    def testComputedNames(self):
        self.assertEqual(unicode(self.brouillon),  'brouillon')
        self.assertEqual(self.brouillon.pluriel(), 'brouillons')
        self.assertEqual(unicode(self.nouveau),    'nouveau')
        self.assertEqual(self.nouveau.pluriel(),   'nouveaux')
