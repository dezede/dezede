# coding: utf-8
from __future__ import unicode_literals
import re
from common.utils.html import hlp
from common.utils.text import remove_diacritics

VOWELS = frozenset(b'AEIOUYaeiouy')


def abbreviate_word(word, min_vowels, min_len):
    ascii_word = remove_diacritics(word)
    prev_is_vowel = ascii_word[0] in VOWELS

    if prev_is_vowel:
        if min_vowels <= 1 and min_len <= 1:
            return word[0] + '.'
        vowels_count = 1
    else:
        vowels_count = 0

    i = 1
    for c in ascii_word[1:-1]:
        is_vowel = c in VOWELS
        if is_vowel and not prev_is_vowel:
            if vowels_count >= min_vowels and i >= min_len:
                return word[:i] + '.'
            vowels_count += 1
        prev_is_vowel = is_vowel
        i += 1

    return word


# TODO: créer un catalogue COMPLET de ponctuations de séparation.
SEPARATOR_RE = re.compile(r'([-\s]+)')


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
    >>> print(abbreviate('A.-J.'))
    A.-J.
    """

    if not enabled:
        return string

    out = ''
    is_word = True
    for sub in SEPARATOR_RE.split(string):
        if is_word:
            if sub:
                out += abbreviate_word(sub, min_vowels, min_len)
        else:
            out += sub
        is_word = not is_word

    if out == string:
        return string
    return hlp(out, string, tags)