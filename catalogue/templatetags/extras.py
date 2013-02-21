# coding: utf-8

from __future__ import unicode_literals
import re
from unicodedata import normalize
from BeautifulSoup import BeautifulStoneSoup
from django.template import Library
from ..models.functions import hlp


register = Library()


@register.filter
def stripchars(text):
    return unicode(
        BeautifulStoneSoup(
            text,
            convertEntities=BeautifulStoneSoup.HTML_ENTITIES
        )
    )


TYPOGRAPHIC_REPLACEMENTS = {
    "'": '’',        ' :': '\u00A0:', ' ;': '\u00A0;',
    ' !': '\u202F!', ' ?': '\u202F?', '« ': '«\u00A0',
    ' »': '\u00A0»', '“ ': '“\u00A0', ' ”': '\u00A0”',
    ' /': '\u00A0/',
    '&laquo; ': '«\u00A0', ' &raquo;': '\u00A0»',
    '&ldquo; ': '“\u00A0', ' &rdquo;': '\u00A0”',
}

TYPOGRAPHIC_REPLACEMENTS_RE = re.compile(
    '|'.join(map(re.escape, TYPOGRAPHIC_REPLACEMENTS)))

def typographic_translation(match):
    return TYPOGRAPHIC_REPLACEMENTS[match.group(0)]


@register.filter
def replace(string):
    """
    >>> print(replace("L'horloge dit : &laquo; Quinze heures ? &raquo;."))
    L’horloge dit\u00A0: «\u00A0Quinze heures\u202F?\u00A0».
    >>> print(replace(" ; !«  »“  ” /&ldquo;  &rdquo;"))
    \u00A0;\u202F!«\u00A0\u00A0»“\u00A0\u00A0”\u00A0/“\u00A0\u00A0”
    """
    return TYPOGRAPHIC_REPLACEMENTS_RE.sub(typographic_translation, string)


def remove_diacritics(string):
    return normalize('NFKD', string).encode('ASCII', 'ignore')


def is_vowel(string):
    return remove_diacritics(string) in 'AEIOUYaeiouy'


def chars_iterator(s):
    i0 = 0
    c0 = s[0]
    i1 = 1
    for c1 in s[1:-1]:
        yield i0, c0, i1, c1
        i0 = i1
        c0 = c1
        i1 += 1


@register.filter
def abbreviate(string, min_vowels=0, min_len=1, tags=True):
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
    """
    out = ''
    # TODO: créer un catalogue COMPLET de ponctuations de séparation.
    for i, sub in enumerate(re.split('(-|\.|\s)', string)):
        if not i % 2:
            if not sub:
                continue
            vowels_count = min_vowels
            vowel_first = is_vowel(sub[0])
            if vowel_first:
                vowels_count -= 1
            for j0, c0, j1, c1 in chars_iterator(sub):
                general_case = is_vowel(c1) and not is_vowel(c0)
                particular_case = j0 == 0 and vowel_first
                if general_case or particular_case:
                    if vowels_count <= 0:
                        if min_len <= j1:
                            sub = sub[:j1] + '.'
                            break
                    if general_case:
                        vowels_count -= 1
        out += sub
    return hlp(out, string, tags)
