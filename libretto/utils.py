# coding: utf-8

from __future__ import unicode_literals
import re
from unicodedata import normalize
from .models.functions import hlp


__all__ = (
    'abbreviate',
)


def remove_diacritics(string):
    return normalize('NFKD', string).encode('ASCII', 'ignore')


def is_vowel(string):
    return remove_diacritics(string) in b'AEIOUYaeiouy'


def is_vowel_iterator(s):
    i0 = 0
    is_vowel0 = is_vowel(s[0])
    i1 = 1
    for c1 in s[1:-1]:
        is_vowel1 = is_vowel(c1)
        yield i0, is_vowel0, i1, is_vowel1
        i0 = i1
        is_vowel0 = is_vowel1
        i1 += 1


# TODO: créer un catalogue COMPLET de ponctuations de séparation.
ABBREVIATION_RE = re.compile('(-|\.|\s)')


def abbreviate(string, min_vowels=0, min_len=1, tags=True, enabled=True):
    """
    Abrège les mots avec une limite de longueur (par défaut 0).

    >>> print(abbreviate('amélie'))
    <span title="Amélie">a.</span>
    >>> print(abbreviate('jeanöõ-françois du puy du fou', tags=False))
    j.-fr. du p. du f.
    >>> print(abbreviate('autéeur dramatique de la tour de babel', 1,
    ...                  tags=False))
    a. dram. de la tour de bab.
    >>> print(abbreviate('adaptateur', 1, 4, tags=False))
    adapt.
    >>> print(abbreviate('Fait à Quincampoix', 2, tags=False))
    Fait à Quincamp.
    >>> print(abbreviate('ceci est un test bidon', enabled=False))
    ceci est un test bidon
    """

    if not enabled:
        return string

    out = ''
    is_word = True
    for sub in ABBREVIATION_RE.split(string):
        if is_word:
            if not sub:
                continue

            vowels_count = 0
            for j0, is_vowel0, j1, is_vowel1 in is_vowel_iterator(sub):
                general_case = is_vowel1 and not is_vowel0
                particular_case = j0 == 0 and is_vowel0
                if general_case or particular_case:
                    if particular_case:
                        vowels_count += 1
                    if vowels_count >= min_vowels and j1 >= min_len:
                        sub = sub[:j1] + '.'
                        break
                    if general_case:
                        vowels_count += 1

            is_word = False
        else:
            is_word = True
        out += sub
    return hlp(out, string, tags)
