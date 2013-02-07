# coding: utf-8

from __future__ import unicode_literals
from datetime import datetime
import re
from ...models import NatureDeLieu, Lieu, AncrageSpatioTemporel
from ...templatetags.extras import multiword_replace
from ..exceptions import ParseError
from .utils import get_or_create, update_or_create


MONTH_BINDINGS_FR = {
    'janvier': 'January', 'février':  'February', 'mars': 'March',
    'avril':   'April',   'mai':      'May',      'juin': 'June',
    'juillet': 'July',    'août':     'August',   'septembre': 'September',
    'octobre': 'October', 'novembre': 'November', 'décembre': 'December',
}


def translate_date_month(date_str, language='fr'):
    var_name = 'MONTH_BINDINGS_' + language.upper()
    month_bindings = globals().get(var_name, {})
    return multiword_replace(date_str, month_bindings)


NATURE_DE_LIEU_NOMS = ('ville', 'institution', 'salle')


LIEU_RE_PATTERNS = (
    r'.+',
)

SEPARATORS = (
    ',',
    ';',
)

DATE_RE_PATTERNS = (
    # Matches format "1/9/1841".
    r'\d{1,2}/\d{1,2}/\d{4}',
    # Matches format "1841-9-1".
    r'\d{4}-\d{1,2}-\d{1,2}',
    # Matches format "1 septembre 1841".
    r'\d{1,2}\s+\S+\s+\d{4}',
    # Matches anything else.
    r'.+',
)
DATE_STRP_PATTERNS = (
    # Matches format "1/9/1841".
    r'%d/%m/%Y',
    # Matches format "1841-9-1".
    r'%Y-%m-%d',
    # Matches format "1 septembre 1841".
    r'%d %B %Y',
    # Matches anything else.
    None,
)


def ancrage_re_iterator():
    DATE_PATTERNS = zip(DATE_RE_PATTERNS, DATE_STRP_PATTERNS)
    for date_re_pattern, date_strp_pattern in DATE_PATTERNS:
        for lieu_re_pattern in LIEU_RE_PATTERNS:
            for separator in SEPARATORS:
                ancrage_re = re.compile(
                    r'^'                  # Begin of string.
                    r'(?:\([^)]+\)\s+)?'  # Matches "(something and so on...) "
                    r'(?P<lieux>%s)'
                    r'%s\s+'              # Matches ", ".
                    r'(?P<date>%s)'
                    r'$'                  # End of string.
                    % (lieu_re_pattern, separator, date_re_pattern)
                )
                yield ancrage_re, date_strp_pattern


def build_lieu(lieu_str, commit=True):
    lieux = [l.strip() for l in lieu_str.split(',') if l]
    assert 1 <= len(lieux) <= 3
    natures = [get_or_create(NatureDeLieu, {'nom': s}, commit=commit)
               for s in NATURE_DE_LIEU_NOMS]
    lieu = None
    for i, lieu_nom in enumerate(lieux):
        lieu = update_or_create(Lieu, {
            'nom': lieu_nom,
            'nature': natures[i],
            'parent':lieu,
        }, unique_keys=['nom', 'parent'], commit=commit)
    return lieu


def build_date(date_str, date_strp_pattern=None):
    if date_strp_pattern is not None:
        date_str = translate_date_month(date_str)
        return datetime.strptime(date_str, date_strp_pattern).date()


def parse_ancrage_inner(ancrage_str, ancrage_re, date_strp_pattern,
                        commit=False):
    match = ancrage_re.match(ancrage_str)
    kwargs = {}

    lieu_str = match.group('lieux')
    lieu = build_lieu(lieu_str, commit=commit)
    if lieu is None:
        kwargs['lieu_approx'] = lieu_str
    else:
        kwargs['lieu'] = lieu

    date_str = match.group('date')
    date = build_date(date_str, date_strp_pattern)
    if date is None:
        kwargs['date_approx'] = date_str
    else:
        kwargs['date'] = date

    return kwargs


def parse_ancrage(ancrage_str, commit=False):
    r"""
    >>> repr(parse_ancrage('Paris, Opéra-comique, 1852'))
    "{u'date_approx': u'1852', u'lieu': <Lieu: Paris, Op\xc3\xa9ra-comique>}"
    """
    for ancrage_re, date_strp_pattern in ancrage_re_iterator():
        try:
            return parse_ancrage_inner(ancrage_str, ancrage_re,
                                       date_strp_pattern, commit=commit)
        except AttributeError:
            continue
    raise ParseError('Impossible d’analyser « %s »' % ancrage_str)


def build_ancrage(ancrage_str, commit=True):
    kwargs = parse_ancrage(ancrage_str, commit=commit)
    ancrage = AncrageSpatioTemporel(**kwargs)
    if commit:
        ancrage.save()
    return ancrage
