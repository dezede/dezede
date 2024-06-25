import re
from string import ascii_letters

from .html import hlp
from .text import remove_diacritics


VOWELS = 'AEIOUYaeiouy'
CONSONANTS = ''.join([letter for letter in ascii_letters if letter not in VOWELS])


def abbreviate(text, min_len=1, tags=True, enabled=True):
    """
    Abrège les mots avec une limite de longueur (par défaut 1).

    >>> print(abbreviate('amélie'))
    <span title="Amélie">a.</span>
    >>> print(abbreviate('jeanöõ-françois du puy du fou', tags=False))
    j.-fr. du p. du f.
    >>> print(abbreviate('autéeur dramatique de la tour de babel', 1,
    ...                  tags=False))
    aut. dr. de la t. de b.
    >>> print(abbreviate('adaptateur', 4, tags=False))
    adapt.
    >>> print(abbreviate('Fait à Quincampoix', 2, tags=False))
    Fait à Quinc.
    >>> print(abbreviate('ceci est un test bidon', enabled=False))
    ceci est un test bidon
    >>> print(abbreviate('A.-J.'))
    A.-J.
    >>> print(abbreviate('Wolgang “Wolfie” Amadeus Mozart', tags=False))
    W. “W.” A. M.
    """

    if not enabled:
        return text

    pattern = fr'[A-Za-z]{{{min_len - 1},}}?[{CONSONANTS}](?P<consonant_case>[{VOWELS}][A-Za-z]+)'
    if min_len == 1:  # Handles the special case for a single vowel.
        pattern = fr'(?:[{VOWELS}](?P<vowel_case>[{CONSONANTS}][A-Za-z]+)|{pattern})'

    matches = []

    def gather_matches(match):
        start, end = match.span('consonant_case')
        if start == -1 or end == -1:
            start, end = match.span('vowel_case')
        matches.append((start, end))
        return ''

    re.sub(pattern, gather_matches, remove_diacritics(text))

    if not matches:
        return text

    short = list(text)
    for start, end in reversed(matches):
        short[start:end] = ['.']

    return hlp(''.join(short), text, tags)
