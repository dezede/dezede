# coding: utf-8

from __future__ import unicode_literals
from datetime import datetime
import re
from ...models import NatureDeLieu, Lieu
from .utils import get_or_create, update_or_create, clean_string


MONTH_BINDINGS_FR = {
    'janvier': 'January', 'février':  'February', 'mars': 'March',
    'avril':   'April',   'mai':      'May',      'juin': 'June',
    'juillet': 'July',    'août':     'August',   'septembre': 'September',
    'octobre': 'October', 'novembre': 'November', 'décembre': 'December',
}


def multiple_replace(text, replacement_dict):
    rc = re.compile('|'.join(map(re.escape, replacement_dict)))

    def translate(match):
        return replacement_dict[match.group(0)]

    return rc.sub(translate, text)


def translate_date_month(date_str, language='fr'):
    var_name = 'MONTH_BINDINGS_' + language.upper()
    month_bindings = globals().get(var_name, {})
    return multiple_replace(date_str, month_bindings)


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
    # Matches format "1841/9/1".
    r'\d{4}/\d{1,2}/\d{1,2}',
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
    # Matches format "1841/9/1".
    r'%Y/%m/%d',
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
    natures = [get_or_create(NatureDeLieu, {'nom': s}, commit=commit)[0]
               for s in NATURE_DE_LIEU_NOMS]
    lieu = None
    for i, lieu_nom in enumerate(lieux):
        data = {
            'nom': lieu_nom,
            'nature': natures[i],
        }
        unique_keys = ['nom']
        if lieu is not None:
            data['parent'] = lieu
            unique_keys.append('parent')
        lieu = update_or_create(Lieu, data, unique_keys=unique_keys,
                                commit=commit)
    return lieu


def build_date(date_str, date_strp_pattern=None):
    if date_strp_pattern is not None:
        date_str = translate_date_month(date_str)
        try:
            return datetime.strptime(date_str, date_strp_pattern).date()
        except ValueError:
            raise ValueError('Unable to parse "%s"' % date_str)


def parse_ancrage_inner(ancrage_str, ancrage_re, date_strp_pattern,
                        prefix, commit=False):
    match = ancrage_re.match(ancrage_str)
    if match is None:
        return
    kwargs = {}

    lieu_str = match.group('lieux')
    lieu = build_lieu(lieu_str, commit=commit)
    if lieu is None:
        kwargs[prefix + 'lieu_approx'] = lieu_str
    else:
        kwargs[prefix + 'lieu'] = lieu

    date_str = match.group('date')
    date = build_date(date_str, date_strp_pattern)
    if date is None:
        kwargs[prefix + 'date_approx'] = date_str
    else:
        kwargs[prefix + 'date'] = date

    return kwargs


def parse_ancrage(ancrage_str, prefix='', commit=False):
    ancrage_str = clean_string(ancrage_str)
    if prefix:
        prefix += '_'
    if ancrage_str.isdigit():
        return {prefix + 'date_approx': ancrage_str}

    for ancrage_re, date_strp_pattern in ancrage_re_iterator():
        if date_strp_pattern is not None:
            try:
                return {prefix + 'date': build_date(ancrage_str,
                                                    date_strp_pattern)}
            except ValueError:
                pass
        data = parse_ancrage_inner(ancrage_str, ancrage_re,
                                   date_strp_pattern, prefix, commit=commit)
        if data is not None:
            return data

    return {prefix + 'date_approx': ancrage_str}


def build_ancrage(ancrage, ancrage_str, commit=True):
    kwargs = parse_ancrage(ancrage_str, commit=commit)
    for k, v in kwargs.items():
        setattr(ancrage, k, v)
    if commit:
        ancrage.instance.save()
