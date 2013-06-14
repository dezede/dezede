# coding: utf-8

from __future__ import unicode_literals
from django.test import TransactionTestCase
from libretto.api.models.utils import update_or_create
from libretto.models import *


class UpdateOrCreateTestCase(TransactionTestCase):
    def setUp(self):
        self.data = data = dict(nom='Dezède', pseudonyme='Dezède')
        self.objects = []
        self.objects.append(update_or_create(Individu, data))
        data.update(nom_naissance='inconnu')
        self.objects.append(update_or_create(Individu, data, unique_keys=['nom']))

    def testComputedNames(self):
        reference_pk = self.objects[0].pk
        for obj in self.objects[1:]:
            self.assertEqual(reference_pk, obj.pk)

        self.assertDictContainsSubset(self.data, self.objects[-1].__dict__)
