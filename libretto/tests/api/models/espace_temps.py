# coding: utf-8

from __future__ import unicode_literals
from django.test import TestCase
from django.utils.encoding import force_text
import johnny.cache
from ....api import build_ancrage


class BuildAncrageTestCase(TestCase):
    cleans_up_after_itself = True

    def setUp(self):
        johnny.cache.disable()

    def test_function(self):
        with self.assertNumQueries(24):
            a = build_ancrage('Paris, Concert Spirituel, ca. 1852')
        self.assertIsNotNone(a.pk)
        self.assertEqual(force_text(a), 'Concert Spirituel, ca. 1852')

        with self.assertNumQueries(15):
            a = build_ancrage('Concert Spirituel, 5/7/1852')
        self.assertIsNotNone(a.pk)
        self.assertEqual(force_text(a), 'Concert Spirituel, 5 juillet 1852')

        with self.assertNumQueries(14):
            a = build_ancrage('Concert Spirituel, 1852-7-5')
        self.assertIsNotNone(a.pk)
        self.assertEqual(force_text(a), 'Concert Spirituel, 5 juillet 1852')

        with self.assertNumQueries(14):
            a = build_ancrage('Concert Spirituel, 5 juillet 1852')
        self.assertIsNotNone(a.pk)
        self.assertEqual(force_text(a), 'Concert Spirituel, 5 juillet 1852')

        with self.assertNumQueries(1):
            a = build_ancrage('5/7/1852')
        self.assertIsNotNone(a.pk)
        self.assertEqual(force_text(a), '5 juillet 1852')

        with self.assertNumQueries(1):
            a = build_ancrage('1852')
        self.assertIsNotNone(a.pk)
        self.assertEqual(force_text(a), '1852')

        with self.assertNumQueries(0):
            a = build_ancrage('18..', commit=False)
        self.assertIsNone(a.pk)
        self.assertEqual(force_text(a), '18..')
