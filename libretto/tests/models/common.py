# coding: utf-8

from __future__ import unicode_literals
from django.utils.encoding import smart_text
from ...models import *
from .utils import new, CommonTestCase


class EtatTestCase(CommonTestCase):
    model = Etat

    def setUp(self):
        self.brouillon = new(Etat, nom='brouillon', public=False)
        self.nouveau = new(Etat, nom='nouveau', nom_pluriel='nouveaux')

    def testComputedNames(self):
        self.assertEqual(smart_text(self.brouillon), 'brouillon')
        self.assertEqual(self.brouillon.pluriel(),   'brouillons')
        self.assertEqual(smart_text(self.nouveau), 'nouveau')
        self.assertEqual(self.nouveau.pluriel(),   'nouveaux')
