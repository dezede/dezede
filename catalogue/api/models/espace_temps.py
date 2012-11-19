# coding: utf-8

from ...models import NatureDeLieu, Lieu, AncrageSpatioTemporel
from ...templatetags.extras import multiword_replace
from .utils import update_or_create
from datetime import datetime
import re


MONTH_BINDINGS_FR = {
    'janvier': 'January', 'février': 'February',  'mars': 'March',
    'avril': 'April',     'mai': 'May',           'juin': 'June',
    'juillet': 'July',    'août': 'August',       'septembre': 'September',
    'octobre': 'October', 'novembre': 'November', 'décembre': 'December',
}


def translate_date_month(date_str, language='fr'):
    var_name = 'MONTH_BINDINGS_' + language.upper()
    month_bindings = globals().get(var_name, {})
    return multiword_replace(date_str, month_bindings)


DATE_RE_PATTERNS = (
    # Matches format "1/9/1841".
    r'\d{1,2}/\d{1,2}/\d{4}',
    # Matches format "1 septembre 1841".
    r'\d{1,2}\s+\S+\s+\d{4}',
)
DATE_STRP_PATTERNS = (
    # Matches format "1/9/1841".
    r'%d/%I/%Y',
    # Matches format "1 septembre 1841".
    r'%d %B %Y',
)

LIEU_RE_PATTERNS = (
    r'.+',
)


#from catalogue.api import build_ancrage; ancrage = build_ancrage('Paris, 30/01/1989')

def ancrage_re_iterator():
    DATE_PATTERNS = zip(DATE_RE_PATTERNS, DATE_STRP_PATTERNS)
    for date_re_pattern, date_strp_pattern in DATE_PATTERNS:
        for lieu_re_pattern in LIEU_RE_PATTERNS:
            ancrage_re = re.compile(
                r'^'  # Begin of string.
                r'(?:\([^)]+\)\s+)?'  # Matches "(something and so on...) "
                r'(?P<lieux>%s)'
                r',\s+'  # Matches ", ".
                r'(?P<date>%s)'
                r'$'  # End of string.
                % (lieu_re_pattern, date_re_pattern)
            )
            yield ancrage_re, date_strp_pattern


def build_ancrage_inner(str, ancrage_re, date_strp_pattern):
    match = ancrage_re.match(str.split(' // ')[0])
    lieux = [l.strip() for l in match.group('lieux').split(',') if l]
    assert 1 <= len(lieux) <= 3
    nature_noms = ['ville', 'institution', 'salle']
    natures = [NatureDeLieu.objects.get_or_create(nom=s)[0]
               for s in nature_noms]
    lieu = None
    for i, lieu_nom in enumerate(lieux):
        lieu = update_or_create(Lieu, ['nom'], nom=lieu_nom, nature=natures[i],
                                parent=lieu)
    date_str = match.group('date')
    date_str = translate_date_month(date_str)
    date = datetime.strptime(date_str, date_strp_pattern)
    return AncrageSpatioTemporel.objects.create(lieu=lieu, date=date)


def build_ancrage(ancrage_str):
    for ancrage_re, date_strp_pattern in ancrage_re_iterator():
        try:
            return build_ancrage_inner(ancrage_str,
                                       ancrage_re, date_strp_pattern)
        except AttributeError:
            continue
    raise Exception('Impossible d’analyser « %s »' % ancrage_str)
