import re


__all__ = ('replace', 'TYPOGRAPHIC_REPLACEMENTS',
           'TYPOGRAPHIC_REPLACEMENTS_RE')


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

TYPOGRAPHIC_REPLACEMENTS_RE_SUB = TYPOGRAPHIC_REPLACEMENTS_RE.sub


def typographic_translation(match):
    return TYPOGRAPHIC_REPLACEMENTS[match.group(0)]


def replace(string):
    """
    >>> print(replace("L'horloge dit : &laquo; Quinze heures ? &raquo;."))
    L’horloge dit\u00A0: «\u00A0Quinze heures\u202F?\u00A0».
    >>> print(replace(" ; !«  »“  ” /&ldquo;  &rdquo;"))
    \u00A0;\u202F!«\u00A0\u00A0»“\u00A0\u00A0”\u00A0/“\u00A0\u00A0”
    """
    return TYPOGRAPHIC_REPLACEMENTS_RE_SUB(typographic_translation, string)
