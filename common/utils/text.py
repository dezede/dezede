from unicodedata import combining, normalize

from django.utils.encoding import force_text
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import pgettext, ugettext_lazy as _

from .base import OrderedDefaultDict


def remove_windows_newlines(text):
    return text.replace('\r\n', '\n').replace('\r', '\n')


def remove_diacritics(string):
    return ''.join([c for c in normalize('NFKD', string) if combining(c) == 0])


def capfirst(text):
    out = force_text(text)
    if not out:
        return out
    return f'{out[0].upper()}{out[1:]}'


def str_list(iterable, infix=None, last_infix=None):
    """
    Concatène une liste de chaîne de caractères avec des virgules.

    >>> l = ['Jeanne', 'Lola', 'Perrine', 'Marion']
    >>> print(str_list(l))
    Jeanne, Lola, Perrine, Marion
    """

    if infix is None:
        infix = pgettext('infix d’une liste', ', ')

    l = [e for e in iterable if e]

    if last_infix is None:
        return infix.join(l)

    suffix = ''
    if len(l) > 1:
        suffix = f'{last_infix}{l.pop()}'
    return f'{infix.join(l)}{suffix}'


def str_list_w_last(iterable, infix=None, last_infix=None):
    """
    Concatène une liste de chaîne de caractères avec des virgules
    et un «,\u00A0et\u00A0» final («\u00A0et\u00A0» pour deux éléments).
    Pour désactiver la virgule d’Oxford, passer oxford_comma=False en argument.

    >>> l = ['Jeanne', 'Marion', 'Lola', 'Perrine']
    >>> print(str_list_w_last(l))
    Jeanne, Marion, Lola et\u00A0Perrine
    >>> print(str_list_w_last(l[:2]))
    Jeanne et\u00A0Marion
    """

    l = [e for e in iterable if e]

    if infix is None:
        infix = pgettext('infix d’une liste', ', ')

    if last_infix is None:
        # Unfortunately, we cannot put a leading breaking space, as it gets
        # automatically stripped by Transifex for no good reason…
        # So we force `last_infix` to not have any leading space, then add a
        # breaking space manually.
        last_infix = pgettext(
            'dernier infix pour 2 éléments', 'et ',
        ).lstrip(' ')
        last_infix = ' ' + last_infix

    return str_list(l, infix, last_infix)


def ex(txt, pre='', post=''):
    """
    >>> print(force_text(ex('30/01/1989')))
    Exemple : « 30/01/1989 ».
    """
    return _('Exemple : %(pre)s« %(txt)s »%(post)s.') % {
        'pre': pre,
        'txt': txt,
        'post': post,
    }
ex = lazy(ex, str)


ROMAN_BINDINGS = (
    (1000, 'M'),
    (900, 'CM'),
    (500,  'D'),
    (400, 'CD'),
    (100,  'C'),
    (90,  'XC'),
    (50,   'L'),
    (40,  'XL'),
    (10,   'X'),
    (9,   'IX'),
    (5,    'V'),
    (4,   'IV'),
    (1,    'I'),
)


def to_roman(integer):
    """
    >>> for s in map(to_roman, (1, 2, 4, 5, 6, 7, 9,
    ...                         10, 11, 40, 49, 50, 55, 100, 900)):
    ...     print(s)
    I
    II
    IV
    V
    VI
    VII
    IX
    X
    XI
    XL
    XLIX
    L
    LV
    C
    CM
    """
    if integer < 1:
        raise ValueError(f'{integer} is not strictly positive.')
    roman = ''
    for n, s in ROMAN_BINDINGS:
        while integer >= n:
            integer -= n
            roman += s
    return roman


def from_roman(roman):
    """
    >>> map(from_roman, ('I', 'II', 'IV', 'V', 'VI', 'VII', 'IX', 'X', 'XI',
    ...                  'XL', 'XLIX', 'L', 'LV', 'C', 'CM'))
    [1, 2, 4, 5, 6, 7, 9, 10, 11, 40, 49, 50, 55, 100, 900]
    >>> for i in range(1, 1500):
    ...     assert from_roman(to_roman(i)) == i
    """
    integer = 0
    for n, s in ROMAN_BINDINGS:
        while roman[:len(s)] == s:
            integer += n
            roman = roman[len(s):]
    return integer


class BiGrouper(object):
    def __init__(self, iterator):
        self.iterator = iterator

    def get_key(self, obj):
        raise NotImplementedError

    def get_value(self, obj):
        raise NotImplementedError

    def get_verbose_key(self, key, values):
        raise NotImplementedError

    def get_verbose_value(self, value, keys):
        raise NotImplementedError

    def __str__(self):
        keys_grouper = OrderedDefaultDict()
        for obj in self.iterator:
            value = self.get_value(obj)
            keys_grouper[value].append(self.get_key(obj))
        values_grouper = OrderedDefaultDict()
        for value, keys in keys_grouper.items():
            values_grouper[tuple(keys)].append(value)
        return mark_safe(str_list([
            (f'{values} [{keys}]' if keys else values)
            for values, keys in [(
                str_list_w_last([self.get_verbose_value(value, keys)
                                 for value in values]),
                str_list_w_last(['' if key is None
                                 else self.get_verbose_key(key, values)
                                 for key in keys]))
                for keys, values in values_grouper.items()]]))
