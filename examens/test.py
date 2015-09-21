# coding: utf-8

from __future__ import unicode_literals, division

from collections import defaultdict
from difflib import SequenceMatcher
from itertools import izip_longest

from bs4 import BeautifulSoup, NavigableString
from django.test import TestCase
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.six import text_type
from django.utils.translation import ungettext, ugettext_lazy as _

from common.utils.text import remove_diacritics


ERROR_START_TAG = '<span class="error %s" title="%s">'
ERROR_END_TAG = '</span>'

FORMATTING_ERROR = 'formatting'
EXTRA_ERROR = 'extra'
MISSING_ERROR = 'missing'
MISSING_SIC_ERROR = 'missing sic'
CASE_ERROR = 'case'
DIACRITIC_ERROR = 'diacritic'
CASE_AND_DIACRITIC_ERROR = 'case diacritic'
TEXT_ERROR = 'text'

PENALITIES = {
    FORMATTING_ERROR: 2,
    EXTRA_ERROR: 4,
    MISSING_ERROR: 4,
    MISSING_SIC_ERROR: 6,
    CASE_ERROR: 2,
    DIACRITIC_ERROR: 2,
    CASE_AND_DIACRITIC_ERROR: 4,
    TEXT_ERROR: 3,
}
PENALITIES_MESSAGES = {
    FORMATTING_ERROR: _('Bad formatting'),
    EXTRA_ERROR: lambda n: ungettext('Extra character', 'Extra characters', n),
    MISSING_ERROR: lambda n: ungettext('Missing character',
                                       'Missing characters', n),
    MISSING_SIC_ERROR: _('Missing sic'),
    CASE_ERROR: _('Wrong case'),
    DIACRITIC_ERROR: _('Wrong diacritic'),
    CASE_AND_DIACRITIC_ERROR: _('Wrong case and diacritic'),
    TEXT_ERROR: _('Erroneous character'),
}


@python_2_unicode_compatible
class HTMLAnnotatedChar(text_type):
    def __new__(cls, c='', is_tag=False, names=(), classes=()):
        self = super(HTMLAnnotatedChar, cls).__new__(cls, force_text(c))
        self.is_tag = is_tag
        self.names = names
        self.classes = classes
        return self

    def __repr__(self):
        return b"<HTMLChar %s is_tag=%s names=%s classes=%s>" % (
            super(HTMLAnnotatedChar, self).__repr__(),
            self.is_tag, self.names, self.classes)

    def __str__(self):
        return self


@python_2_unicode_compatible
class HTMLAnnotatedCharList(list):
    def __init__(self, html):
        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        self.parse()
        super(list, self).__init__()

    def parse(self, tag=None, parent_names=(), parent_classes=()):
        if tag is None:
            tag = self.soup
        for el in tag.contents:
            if isinstance(el, NavigableString):
                for c in el:
                    self.append(HTMLAnnotatedChar(
                        c, False, parent_names, parent_classes))
            else:
                tag_inside = '%s %s' % (el.name, ' '.join([
                    '%s="%s"' % (k, ' '.join(v) if isinstance(v, list) else v)
                    for k, v in el.attrs.items()]))
                template = '<%s />' if el.is_empty_element else '<%s>'
                start_tag = template % tag_inside.strip()
                for c in start_tag:
                    self.append(HTMLAnnotatedChar(
                        c, True, parent_names, parent_classes))
                names = parent_names + (el.name,)
                classes = parent_classes + tuple(el.get('class', ()))
                self.parse(el, names, classes)
                end_tag = '</%s>' % el.name
                for c in end_tag:
                    self.append(HTMLAnnotatedChar(
                        c, True, parent_names, parent_classes))

    def __str__(self):
        return ''.join(map(force_text, self))

    def __eq__(self, other):
        assert (isinstance(self, HTMLAnnotatedCharList)
                and isinstance(other, HTMLAnnotatedCharList))
        if len(self) != len(other):
            return False
        return all(c1 == c2 and c1.is_tag == c2.is_tag
                   and c1.names == c2.names and c1.classes == c2.classes
                   for c1, c2 in zip(self, other))

    def __getitem__(self, key):
        l = super(HTMLAnnotatedCharList, self).__getitem__(key)
        new = HTMLAnnotatedCharList(self.html)
        del new[:]
        new.extend(l)
        return new

    def __getslice__(self, i, j):
        return self.__getitem__(slice(i, j))

    def get_text_only(self):
        return ''.join([c for c in self if not c.is_tag])

    def get_chars(self, start, end):
        l = []
        i = 0
        for c in self:
            if c.is_tag:
                continue
            if start <= i < end:
                l.append(c)
            i += 1
        return l

    def annotate(self, start, end, start_tag, end_tag):
        if start == end:
            return

        text_index = 0
        old_chars = tuple(self)
        del self[:]
        for c in old_chars:
            if c.is_tag:
                self.append(c)
                continue

            if text_index == start:
                for tag_c in start_tag:
                    self.append(HTMLAnnotatedChar(
                        tag_c, is_tag=True, names=c.names, classes=c.classes))
            self.append(c)
            text_index += 1
            if text_index == end:
                for tag_c in end_tag:
                    self.append(HTMLAnnotatedChar(
                        tag_c, is_tag=True, names=c.names, classes=c.classes))


class AnnotatedDiff:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.annotated_a = HTMLAnnotatedCharList(a)
        self.annotated_b = HTMLAnnotatedCharList(b)
        self.a_text = self.annotated_a.get_text_only()
        self.b_text = self.annotated_b.get_text_only()
        self.errors = defaultdict(int)
        self.parsed = False

    def get_html(self):
        self.parse()
        return force_text(self.annotated_a)

    def parse(self):
        if self.parsed:
            return
        sm = SequenceMatcher(a=self.a_text, b=self.b_text)
        for tag, ia1, ia2, ib1, ib2 in sm.get_opcodes():
            sub_a = self.a_text[ia1:ia2]
            sub_b = self.b_text[ib1:ib2]
            self.compare(ia1, ib1, sub_a, sub_b)
        self.parsed = True

    def add_error(self, i, error_code, s, n_chars=1):
        error_message = PENALITIES_MESSAGES[error_code]
        if callable(error_message):
            error_message = error_message(n_chars)
        start_tag = ERROR_START_TAG % (error_code, error_message)
        for inc, c in enumerate(s, start=1):
            self.annotated_a.annotate(i, i+inc, start_tag, ERROR_END_TAG)
        self.errors[error_code] += n_chars

    def compare(self, ia, ib, sub_a, sub_b):
        if sub_a == sub_b:
            for inc, (ca, cb) in enumerate(zip(
                    self.annotated_a.get_chars(ia, ia+len(sub_a)),
                    self.annotated_b.get_chars(ib, ib+len(sub_b)))):
                if not (ca.names == cb.names and ca.classes == cb.classes):
                    self.add_error(ia+inc, FORMATTING_ERROR, ca)
            return
        if not sub_b:
            self.add_error(ia, EXTRA_ERROR, sub_a, len(sub_a))
            return
        if not sub_a:
            if force_text(sub_b).strip() == '[sic]':
                self.add_error(ia, MISSING_SIC_ERROR, '&nbsp;' * len(sub_b))
                return
            self.add_error(ia, MISSING_ERROR,
                           '&nbsp;' * len(sub_b), len(sub_b))
            return
        if len(sub_a) == len(sub_b) == 1:
            if sub_a.lower() == sub_b.lower():
                self.add_error(ia, CASE_ERROR, sub_a)
            elif remove_diacritics(sub_a) == remove_diacritics(sub_b):
                self.add_error(ia, DIACRITIC_ERROR, sub_a)
            elif remove_diacritics(sub_a).lower() == remove_diacritics(sub_b).lower():
                self.add_error(ia, CASE_AND_DIACRITIC_ERROR, sub_a)
            else:
                self.add_error(ia, TEXT_ERROR, sub_a)
        else:
            for inc, (ca, cb) in enumerate(
                    izip_longest(sub_a, sub_b, fillvalue=HTMLAnnotatedChar())):
                self.compare(ia+inc, ib+inc, ca, cb)

    def get_score(self):
        self.parse()
        score = len(self.a_text) - sum([PENALITIES[e] * n
                                        for e, n in self.errors.items()])
        if score < 0:
            score = 0
        max_score = len(self.b_text)
        return '%d/20' % round((score / max_score) * 20)


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
                         '<p><span class="sc"><b>b</b></span>labla</p>')
        self.html_annotated_char_list.annotate(5, 6,
                                               '<i>', '</i>')
        self.assertEqual(str(self.html_annotated_char_list),
                         '<p><span class="sc"><b>b</b></span>labl<i>a</i></p>')


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


if __name__ == '__main__':
    import os
    from unittest import main
    import django

    os.environ['DJANGO_SETTINGS_MODULE'] = 'dezede.settings'
    django.setup()
    main()
