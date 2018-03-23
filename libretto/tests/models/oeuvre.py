# coding: utf-8

from __future__ import unicode_literals
import os
from django.utils.encoding import force_text
from ...models import *
from .utils import CommonTestCase


PATH = os.path.abspath(os.path.dirname(__file__))


class OeuvreTestCase(CommonTestCase):
    model = Oeuvre
    fixtures = [
        os.path.join(PATH, 'fixtures/oeuvre.yaml'),
    ]

    def setUp(self):
        # Force save to rebuild slug & tree fields
        for oeuvre in Oeuvre.objects.all():
            oeuvre.save()

    def test_str(self):
        def test_oeuvre(pk, n_queries, n_queries_prefetched, result):
            oeuvre = Oeuvre.objects.get(pk=pk)
            with self.assertNumQueries(n_queries):
                self.assertEqual(force_text(oeuvre), result)
            oeuvre = Oeuvre.objects.prefetch_all().get(pk=pk)
            with self.assertNumQueries(n_queries_prefetched):
                self.assertEqual(force_text(oeuvre), result)

        test_oeuvre(1, 0, 0, 'Carmen')
        test_oeuvre(2, 1, 1, 'Carmen, Acte I')
        test_oeuvre(3, 5, 2, 'Carmen, I, № 5 Habanera de Carmen '
                             '« L’amour est un oiseau rebelle »')
        test_oeuvre(4, 3, 0, 'Sonate pour violon')
        test_oeuvre(5, 2, 0, 'Symphonie n° 5')
        test_oeuvre(6, 0, 0, 'Le Tartuffe, ou l’Imposteur')

    def test_titre_descr(self):
        def test_oeuvre(pk, n_queries, n_queries_prefetched, result):
            oeuvre = Oeuvre.objects.get(pk=pk)
            with self.assertNumQueries(n_queries):
                self.assertEqual(oeuvre.titre_descr(), result)
            oeuvre = Oeuvre.objects.prefetch_all().get(pk=pk)
            with self.assertNumQueries(n_queries_prefetched):
                self.assertEqual(oeuvre.titre_descr(), result)

        test_oeuvre(1, 1, 0, 'Carmen, opéra')
        test_oeuvre(2, 1, 1, 'Carmen, Acte I')
        test_oeuvre(3, 5, 2, 'Carmen, I, № 5 Habanera de Carmen '
                             '« L’amour est un oiseau rebelle »')
        test_oeuvre(4, 3, 0, 'Sonate pour violon')
        test_oeuvre(5, 2, 0, 'Symphonie n° 5, op. 107')
        test_oeuvre(6, 1, 0, 'Le Tartuffe, ou l’Imposteur, '
                             'comédie en cinq actes et en vers')

    def test_titre_html(self):
        def test_oeuvre(pk, n_queries, n_queries_prefetched, result):
            oeuvre = Oeuvre.objects.get(pk=pk)
            with self.assertNumQueries(n_queries):
                self.assertEqual(oeuvre.titre_html(), result)
            oeuvre = Oeuvre.objects.prefetch_all().get(pk=pk)
            with self.assertNumQueries(n_queries_prefetched):
                self.assertEqual(oeuvre.titre_html(), result)

        test_oeuvre(1, 0, 0,
                    '<a href="/oeuvres/carmen/"><cite>Carmen</cite></a>')
        test_oeuvre(
            2, 1, 1,
            '<a href="/oeuvres/carmen/"><cite>Carmen</cite></a>, '
            '<a href="/oeuvres/carmen-acte-i/">Acte I</a>')
        test_oeuvre(
            3, 5, 2,
            '<a href="/oeuvres/carmen/"><cite>Carmen</cite></a>, '
            '<a href="/oeuvres/carmen-acte-i/">I</a>, '
            '<a href="/oeuvres/carmen-i-'
            '5-habanera-de-carmen-l-amour-est-un/">'
            '№ 5 Habanera de Carmen <span title="Incipit">'
            '« L’amour est un oiseau rebelle »</span></a>')
        test_oeuvre(4, 3, 0,
                    '<a href="/oeuvres/sonate-pour-violon/">'
                    'Sonate pour violon</a>')
        test_oeuvre(5, 2, 0,
                    '<a href="/oeuvres/symphonie-n-5/">Symphonie n° 5</a>')
        test_oeuvre(
            6, 0, 0,
            '<a href="/oeuvres/le-tartuffe-ou-l-imposteur/">'
            '<cite>Le Tartuffe, ou l’Imposteur</cite></a>')

    def test_description_html(self):
        def test_oeuvre(pk, n_queries, n_queries_prefetched, result):
            oeuvre = Oeuvre.objects.get(pk=pk)
            with self.assertNumQueries(n_queries):
                self.assertEqual(oeuvre.description_html(), result)
            oeuvre = Oeuvre.objects.prefetch_all().get(pk=pk)
            with self.assertNumQueries(n_queries_prefetched):
                self.assertEqual(oeuvre.description_html(), result)

        test_oeuvre(1, 1, 0, 'opéra')
        test_oeuvre(2, 0, 0, '')
        test_oeuvre(3, 0, 0, '')
        test_oeuvre(4, 0, 0, '')
        test_oeuvre(5, 0, 0, '<span title="Opus">op. 107</span>')
        test_oeuvre(
            6, 1, 0,
            'comédie <span title="Coupe">en cinq actes et en vers</span>')

    def test_html(self):
        def test_oeuvre(pk, n_queries, n_queries_prefetched, result):
            oeuvre = Oeuvre.objects.get(pk=pk)
            with self.assertNumQueries(n_queries):
                self.assertEqual(oeuvre.html(), result)
            oeuvre = Oeuvre.objects.prefetch_all().get(pk=pk)
            with self.assertNumQueries(n_queries_prefetched):
                self.assertEqual(oeuvre.html(), result)

        test_oeuvre(
            1, 2, 1,
            '<a href="/oeuvres/carmen/"><cite>Carmen</cite></a>, opéra')
        test_oeuvre(
            2, 2, 2,
            '<cite>Carmen</cite>, '
            '<a href="/oeuvres/carmen-acte-i/">Acte I</a>')
        test_oeuvre(
            3, 6, 3,
            '<cite>Carmen</cite>, I, <a href="/oeuvres/carmen-i-'
            '5-habanera-de-carmen-l-amour-est-un/">'
            '№ 5 Habanera de Carmen <span title="Incipit">'
            '« L’amour est un oiseau rebelle »</span></a>')
        test_oeuvre(4, 4, 1,
                    '<a href="/oeuvres/sonate-pour-violon/">'
                    'Sonate pour violon</a>')
        test_oeuvre(5, 3, 1,
                    '<a href="/oeuvres/symphonie-n-5/">Symphonie n° 5</a>, '
                    '<span title="Opus">op. 107</span>')
        test_oeuvre(
            6, 2, 1,
            '<a href="/oeuvres/le-tartuffe-ou-l-imposteur/">'
            '<cite>Le Tartuffe, ou l’Imposteur</cite></a>, '
            'comédie <span title="Coupe">en cinq actes et en vers</span>')
