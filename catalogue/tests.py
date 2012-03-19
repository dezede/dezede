# coding: utf-8
from django.utils import unittest
from musicologie.catalogue.models import *

class OeuvreTestCase(unittest.TestCase):
    def setUp(self):
        self.opera = Oeuvre.objects.create(titre='Carmen')
    def testComputedName(self):
        self.assertEqual(self.opera.__unicode__(), 'Carmen')

