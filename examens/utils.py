# coding: utf-8

from __future__ import unicode_literals, print_function
from difflib import SequenceMatcher
import re
import string
from bs4 import BeautifulSoup
from common.utils.text import remove_diacritics


class Translatable(object):
    def __init__(self, pos):
        self.pos = pos
        self.translations = []
        self.translations_offset = 0

    @property
    def current_pos(self):
        return self.pos + self.translations_offset

    def add(self, *translations):
        for translation in translations:
            self.translations.append(translation)
            if translation.pos <= self.current_pos:
                self.translations_offset += translation.offset


class Translation(Translatable):
    def __init__(self, pos, offset):
        self.offset = offset
        super(Translation, self).__init__(pos)

    def __repr__(self):
        return '<Translation: at %d add %d>' % (self.current_pos, self.offset)

    def __lt__(self, other):
        return self.pos < other.pos

    def __gt__(self, other):
        return self.pos > other.pos


class Diff(Translatable):
    """
    >>> d = Diff('teatre', 'theatre', (1, 1, 1, 2))
    >>> d.diff_a, d.diff_b
    (u'', u'h')
    >>> d.offset
    1
    >>> d.translations_offset
    0
    >>> d.current_a0, d.current_a1
    (1, 1)
    >>> d.add(Translation(0, 3))
    >>> d.offset
    1
    >>> d.translations_offset
    3
    >>> d.current_a0, d.current_a1
    (4, 4)
    >>> d.diff_a, d.diff_b
    (u'', u'h')
    >>> print(d.apply_to('le téâtre'))
    le théâtre
    >>> d.to_translation()
    <Translation: at 4 add 1>
    >>> d
    <Diff: at 4 insert 'h'>
    >>> d = Diff('teatre', 'theatre', (1, 1, 1, 2))
    >>> print(d.apply_to('le téâtre', [Translation(0, 3)]))
    le théâtre
    >>> d
    <Diff: at 1 insert 'h'>
    >>> Diff("'", '', (0, 1, 0, 0))
    <Diff: at 0 delete '\\''>
    >>> d = Diff('théâtre  des arts ', 'théâtre  des arts,', (17, 17, 17, 18))
    >>> print(d.apply_to('théâtre des arts', [Translation(7, -1)]))
    théâtre des arts,
    >>> print(d.apply_to('théâtre des arts', [Translation(17, -1), Translation(7, -1)]))
    théâtre des arts,
    """
    def __init__(self, a, b, diff_positions):
        self.a = a
        self.b = b
        self.diff_positions = diff_positions
        super(Diff, self).__init__(self.pos)

    @property
    def diff_positions(self):
        return self.a0, self.a1, self.b0, self.b1

    @diff_positions.setter
    def diff_positions(self, diff_positions):
        self.a0, self.a1, self.b0, self.b1 = diff_positions

    @property
    def diff_a(self):
        return self.a[self.a0:self.a1]

    @property
    def diff_b(self):
        return self.b[self.b0:self.b1]

    @property
    def a0(self):
        return self.pos

    @a0.setter
    def a0(self, value):
        self.pos = value

    @property
    def current_a0(self):
        return self.a0 + self.translations_offset

    @property
    def current_a1(self):
        return self.a1 + self.translations_offset

    @property
    def offset(self):
        return (self.b1 - self.b0) - (self.a1 - self.a0)

    def copy(self, initial_translations):
        d = Diff(self.a, self.b, self.diff_positions)
        d.add(*sorted(initial_translations))
        d.add(*self.translations)
        return d

    def apply_to(self, c, initial_translations=()):
        c_list = list(c)
        if initial_translations:
            d = self.copy(initial_translations)
        else:
            d = self
        c_list[d.current_a0:d.current_a1] = d.diff_b
        return ''.join(c_list)

    def to_translation(self):
        return Translation(self.current_a0, self.offset)

    def __repr__(self):
        diff_a = self.diff_a.replace("'", "\\'")
        diff_b = self.diff_b.replace("'", "\\'")
        if self.a0 == self.a1:
            msg = "insert '%s'" % diff_b
        elif self.b0 == self.b1:
            msg = "delete '%s'" % diff_a
        else:
            msg = "replace '%s' with '%s'" % (diff_a, diff_b)
        return ('<Diff: at %d %s>' % (self.current_a0, msg)).encode('utf-8')


class Comparator(object):
    """
    >>> comparator = Comparator('teatr', 'le theatre')
    >>> print(comparator.apply_to('Téâtr'))
    le Théâtre
    >>> comparator.to_translations()
    [<Translation: at 0 add 3>, <Translation: at 4 add 1>, <Translation: at 9 add 1>]
    >>> comparator = Comparator('il gran teatro', 'il gran téâtro')
    >>> print(comparator.apply_to('le theatre',
    ...                           [Translation(0, -8), Translation(0, 3), Translation(4, 1)]))
    le théâtre
    >>> comparator = Comparator('theatre  des arts ', 'theatre  des arts, ')
    >>> comparator.to_translations()
    [<Translation: at 17 add 1>]
    >>> print(comparator.apply_to('Theatre des arts',
    ... [Translation(7, -1)]))
    Theatre des arts,
    >>> print(comparator.apply_to('Theatre des arts',
    ... [Translation(17, -1), Translation(7, -1)]))
    Theatre des arts,
    """
    def __init__(self, a, b):
        self.a = a
        self.b = b
        matcher = SequenceMatcher()
        matcher.set_seqs(a, b)
        self.diffs = [Diff(a, b, (a0, a1, b0, b1))
                      for op, a0, a1, b0, b1 in matcher.get_opcodes()
                      if op != 'equal']
        translations = []
        for diff in self.diffs:
            for translation in translations:
                diff.add(translation)
            translations.append(diff.to_translation())

    def apply_to(self, c, initial_translations=()):
        for diff in self.diffs:
            c = diff.apply_to(c, initial_translations)
        return c

    def to_translations(self):
        translations = [d.to_translation() for d in self.diffs]
        return [t for t in translations if t.offset != 0]

    def add(self, *translations):
        for diff in self.diffs:
            diff.add(*translations)

    def add_before(self, *translations):
        self.diffs = [diff.copy(translations) for diff in self.diffs]


PUNCTUATION_RE = re.compile(r'[^\s  \w]')
normalize_punctuation = lambda text: PUNCTUATION_RE.sub(b'', text)
MULTI_WHITESPACE_RE = re.compile(r'[\s  ]{2,}')
normalize_spaces = lambda text: MULTI_WHITESPACE_RE.sub(b' ', text)


def striptags_n_chars(text):
    return unicode(BeautifulSoup(text, 'html.parser').get_text())


def normalize(a, b):
    """
    >>> from pprint import pprint
    >>> pprint(normalize('<p>Théâtre des arts.</p>', '<div> tèatre  des atrs, </div>'))
    [(u'texte', 'theatre des arts', ' teatre des atrs '),
     (u'majuscules', 'Theatre des arts', ' teatre des atrs '),
     (u'espaces', 'Theatre des arts', ' teatre  des atrs '),
     (u'ponctuation', 'Theatre des arts.', ' teatre  des atrs, '),
     (u'accents', u'Th\\xe9\\xe2tre des arts.', u' t\\xe8atre  des atrs, '),
     (u'mise en forme',
      u'<p>Th\\xe9\\xe2tre des arts.</p>',
      u'<div> t\\xe8atre  des atrs, </div>')]
    """
    NORMALIZERS = (
        ('mise en forme', lambda text: text),
        ('accents', striptags_n_chars),
        ('ponctuation', remove_diacritics),
        ('espaces', normalize_punctuation),
        ('majuscules', normalize_spaces),
        ('texte', string.lower),
    )

    out = []
    for name, normalizer in NORMALIZERS:
        a, b = normalizer(a), normalizer(b)
        out.insert(0, (name, a, b))
    return out


def get_diffs_per_normalizer(a, b):
    """
    >>> from pprint import pprint
    >>> pprint(get_diffs_per_normalizer('<p>Théâtre des arts.</p>', '<div> tèatre  des atrs, </div>'))
    [(u'texte',
      [<Diff: at 5 delete ' '>,
       <Diff: at 6 insert 'h'>,
       <Diff: at 19 insert 'r'>,
       <Diff: at 21 delete 'r'>,
       <Diff: at 23 delete ' '>]),
     (u'majuscules', [<Diff: at 5 replace 't' with 'T'>]),
     (u'espaces', [<Diff: at 12 delete ' '>]),
     (u'ponctuation', [<Diff: at 21 delete ','>, <Diff: at 21 insert '.'>]),
     (u'accents', [<Diff: at 7 replace 'èa' with 'éâ'>]),
     (u'mise en forme',
      [<Diff: at 1 replace 'div' with 'p'>,
       <Diff: at 22 replace 'div' with 'p'>])]
    """
    m = None
    left_translations = []
    reverse_left_translations = []
    lcs = []
    for name, a, b in normalize(a, b):
        if m is None:
            m = b
        else:
            rc = Comparator(previous_b, b)
            m = rc.apply_to(previous_a, left_translations)
            # for translation in reverse_left_translations:
            #     translation.add(*rc.to_translations())
            for _, comparator in lcs:
                comparator.add(*sorted(rc.to_translations()))
        # print(left_translations)
        # print(name.ljust(20).encode('utf-8'), a.ljust(25).encode('utf-8'), b'|', m.ljust(30).encode('utf-8'), b'|', b.encode('utf-8'))
        lc = Comparator(m, a)
        lcs.append((name, lc))
        # for _, lc in lcs:
        #     lc.add(*lc.to_translations())
        left_translations.extend(lc.to_translations())
        # lc.add(*reverse_left_translations)
        # reverse_left_translations.extend(Comparator(a, m).to_translations())
        previous_a = a
        previous_b = b

    return [(name, c.diffs) for name, c in lcs]


def highlight_diffs(a, b):
    """
    >>> print(highlight_diffs('<p><span class="sc">théâtre des arts.</span></p>',
    ...                       '<p>Théâtre des arts.</p>'))
    <p><mark title="majuscules t">T</mark>héâtre des arts.</p>
    >>> print(highlight_diffs('<p>Aujourd’hui, relâche.</p>',
    ...                       '<p>aujourd’hui, relache.</p>'))
    <p><mark title="majuscules A">a</mark>ujourd’hui, rel<mark title="accents â">a</mark>che.</p>
    >>> print(highlight_diffs(
    ...     '<p><span class="sc">théâtre des arts.</span></p>\\n'
    ...     '<p>Aujourd’hui, relâche.</p>',
    ...     '<p>Théâtre des arts.</p>\\n<p>aujourd’hui, relache.</p>'))
    <p><mark title="majuscules t">T</mark>héâtre des arts.</p>
    <p><mark title="majuscules A">a</mark>ujourd’hui, rel<mark title="accents â">a</mark>che.</p>
    """
    translations = []
    diffs = [(name, diff) for name, diffs in
             get_diffs_per_normalizer(a, b)[:-1] for diff in diffs]
    for name, diff in sorted(diffs):
        diff.add(*sorted(translations))
        diff.b = ('<mark title="%s">%s</mark>'
                  % (name + ' ' + diff.diff_b,
                     diff.diff_a.replace(' ', ' ')))
        diff.b0 = 0
        diff.b1 += len(diff.b)
        b = diff.apply_to(b)
        translations.append(diff.to_translation())
    return b


if __name__ == '__main__':
    import doctest
    doctest.testmod()
