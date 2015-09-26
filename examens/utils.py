# coding: utf-8

from __future__ import unicode_literals, division

from collections import defaultdict
from difflib import SequenceMatcher
from itertools import izip_longest

from bs4 import BeautifulSoup, NavigableString
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
        text_index = 0
        old_chars = tuple(self)
        del self[:]

        def append_tag(tag, text_char):
            for tag_c in tag:
                self.append(HTMLAnnotatedChar(
                    tag_c, is_tag=True,
                    names=text_char.names, classes=text_char.classes))

        for c in old_chars:
            if c.is_tag:
                self.append(c)
                continue

            if text_index == start == end:
                append_tag(start_tag, c)
                append_tag(end_tag, c)

            if text_index == start != end:
                append_tag(start_tag, c)
            self.append(c)
            text_index += 1
            if text_index == end != start:
                append_tag(end_tag, c)


class AnnotatedDiff:
    IGNORED_FORMATTING_CHARACTERS = '   .,:;…?!¿¡«»"\'()[]{}/\\'

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
        else:
            self.annotated_a.annotate(i, i, start_tag, ERROR_END_TAG)
        self.errors[error_code] += n_chars

    def compare(self, ia, ib, sub_a, sub_b):
        if sub_a == sub_b:
            for inc, (ca, cb) in enumerate(zip(
                    self.annotated_a.get_chars(ia, ia+len(sub_a)),
                    self.annotated_b.get_chars(ib, ib+len(sub_b)))):
                names_differences = set(
                    ca.names).symmetric_difference(cb.names)
                names_differences.discard('span')
                classes_differences = set(
                    ca.classes).symmetric_difference(cb.classes)
                if names_differences or classes_differences:
                    if ca in self.IGNORED_FORMATTING_CHARACTERS:
                        continue
                    # Ignore small caps errors on upper case letters.
                    if ca == ca.upper() and not names_differences \
                            and classes_differences == {'sc'}:
                        continue
                    self.add_error(ia+inc, FORMATTING_ERROR, ca)
            return
        if not sub_b:
            self.add_error(ia, EXTRA_ERROR, sub_a, len(sub_a))
            return
        if not sub_a:
            if force_text(sub_b).strip() == '[sic]':
                self.add_error(ia, MISSING_SIC_ERROR, '')
                return
            self.add_error(ia, MISSING_ERROR, '', len(sub_b))
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
        score = float(max(score, 0))
        max_score = len(self.b_text)
        return score / max_score
