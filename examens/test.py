# coding: utf-8

from __future__ import unicode_literals

from django.test import TestCase

from .utils import HTMLAnnotatedCharList, AnnotatedDiff


class HTMLAnnotatedCharListTestCase(TestCase):
    def setUp(self):
        self.html_annotated_char_list = HTMLAnnotatedCharList('<p>blabla</p>')

    def test_annotate(self):
        self.html_annotated_char_list.annotate(0, 1,
                                               '<span class="sc">', '</span>')
        self.assertEqual(str(self.html_annotated_char_list),
                         '<p><span class="sc">b</span>labla</p>')
        self.html_annotated_char_list.annotate(0, 1,
                                               '<b>', '</b>')
        self.assertEqual(str(self.html_annotated_char_list),
                         '<p><span class="sc"><b>b</b></span>labla</p>')
        self.html_annotated_char_list.annotate(5, 5,
                                               '<i>', '</i>')
        self.assertEqual(str(self.html_annotated_char_list),
                         '<p><span class="sc"><b>b</b></span>labl<i></i>a</p>')
        self.html_annotated_char_list.annotate(5, 6,
                                               '<i>', '</i>')
        self.assertEqual(
            str(self.html_annotated_char_list),
            '<p><span class="sc"><b>b</b></span>labl<i></i><i>a</i></p>')


class AnnotatedDiffTestCase(TestCase):
    def assertScore(self, a, b, score):
        self.assertEqual(AnnotatedDiff(a, b).get_score(), score)

    def test_perfect_score(self):
        self.assertScore(
            'abcdefghijklmnopqrstuvwxyz',
            'abcdefghijklmnopqrstuvwxyz',
            '20/20')

    def test_score_missing_char(self):
        self.assertScore(
            'bcdefghijklmnopqrstuvwxyz',
            'abcdefghijklmnopqrstuvwxyz',
            '16/20')
        self.assertScore(
            'abcdefghijklmnopqrstuvwxy',
            'abcdefghijklmnopqrstuvwxyz',
            '16/20')
        self.assertScore(
            'abcdefghijklnopqrstuvwxyz',
            'abcdefghijklmnopqrstuvwxyz',
            '16/20')

    def test_score_missing_diacritic(self):
        self.assertScore(
            'abcdefghijklmnopqrstuvwxyz',
            'âbcdefghijklmnopqrstuvwxyz',
            '18/20')
        self.assertScore(
            'abcdefghijklmnopqrstuvwxyz',
            'abcdéfghijklmnopqrstuvwxyz',
            '18/20')
        self.assertScore(
            'abcdefghijklmnopqrstuvwxyz',
            'abcdefghïjklmnopqrstuvwxyz',
            '18/20')

        # Missing several diacritics
        self.assertScore(
            'abcdefghijklmnopqrstuvwxyz',
            'âbcdéfghïjklmnopqrstuvwxyz',
            '15/20')

    def test_score_extra_diacritic(self):
        self.assertScore(
            'âbcdefghijklmnopqrstuvwxyz',
            'abcdefghijklmnopqrstuvwxyz',
            '18/20')
        self.assertScore(
            'abcdéfghijklmnopqrstuvwxyz',
            'abcdefghijklmnopqrstuvwxyz',
            '18/20')
        self.assertScore(
            'abcdefghïjklmnopqrstuvwxyz',
            'abcdefghijklmnopqrstuvwxyz',
            '18/20')

        # Multiple extra diacritics
        self.assertScore(
            'âbcdéfghïjklmnopqrstuvwxyz',
            'abcdefghijklmnopqrstuvwxyz',
            '15/20')
