# coding: utf-8

from __future__ import unicode_literals
from django.test import TransactionTestCase
from django.utils.encoding import smart_text
from ...models import *
from datetime import date
from .utils import new


class SourceTestCase(TransactionTestCase):
    cleans_up_after_itself = True

    def setUp(self):
        type_de_source = new(TypeDeSource, nom='compte rendu',
                             nom_pluriel='comptes rendus')
        self.journal = new(Source, nom='Journal de Rouen',
                           date=date(1828, 1, 15),
                           type=type_de_source)

    def testComputedNames(self):
        self.assertEqual(smart_text(self.journal),
                         'Journal de Rouen, mardi 15 janvier 1828')
