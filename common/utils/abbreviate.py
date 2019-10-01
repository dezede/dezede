import re

from .html import hlp
from .text import remove_diacritics


VOWELS = 'AEIOUYaeiouy'


def abbreviate(text, min_len=1, tags=True, enabled=True):
    """
    Abrège les mots avec une limite de longueur (par défaut 1).

    >>> print(abbreviate('amélie'))
    <span title="Amélie">a.</span>
    >>> print(abbreviate('jeanöõ-françois du puy du fou', tags=False))
    j.-fr. du p. du f.
    >>> print(abbreviate('autéeur dramatique de la tour de babel', 1,
    ...                  tags=False))
    aut. dram. de la tour de bab.
    >>> print(abbreviate('adaptateur', 4, tags=False))
    adapt.
    >>> print(abbreviate('Fait à Quincampoix', 2, tags=False))
    Fait à Quinc.
    >>> print(abbreviate('ceci est un test bidon', enabled=False))
    ceci est un test bidon
    >>> print(abbreviate('A.-J.'))
    A.-J.
    """

    if not enabled:
        return text

    pattern = (
        fr'([A-Za-z]{{{min_len},}}?(?<=[^{VOWELS}])(?=[{VOWELS}]))'
    )
    if min_len == 1:  # Handles the special case for a single vowel.
        pattern = fr'([{VOWELS}]|{pattern})'
    short = ''
    last_end = 0
    for match in re.finditer(
        pattern + r'[A-Za-z]{2,}',
        remove_diacritics(text).decode(),
    ):
        start = match.start()
        short += text[last_end:start]
        short += text[start:start + len(match.group(1))] + '.'
        last_end = match.end()
    short += text[last_end:]
    if short == text:
        return text
    return hlp(short, text, tags)
