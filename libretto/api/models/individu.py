import re
from libretto.api import parse_ancrage
from .utils import update_or_create, clean_string
from ...models import Individu


PARTICULES = 'de|d’|d\'|di|da|van|van der|von|ben'
INDIVIDU_RE = re.compile(
    r'^'
    r'(?P<nom>[^,(]+?)'
    fr'(?:, (?P<prenoms>[^,(]+?)(?: (?P<particule_nom>{PARTICULES}))?)?'
    r'(?: \((?P<dates>[^)]+)\))?'
    r'(?:, dite? (?P<pseudonyme>.+?))?'
    r'$', flags=re.IGNORECASE)


def get_individu(individu_str, dates_sep='-', commit=True):
    individu_str = clean_string(individu_str)
    if individu_str.isdigit():
        return Individu.objects.get(pk=individu_str)
    else:
        match = INDIVIDU_RE.match(individu_str)
        if match is None:
            raise ValueError(f'Unable to parse "{individu_str}"')
        data = match.groupdict()
        for k, v in data.items():
            if v is None:
                del data[k]
            else:
                data[k] = v.strip()

        if 'dates' in data:
            date_strs = filter(bool, data['dates'].split(dates_sep))
            del data['dates']
            if len(date_strs) > 0:
                assert len(date_strs) <= 2
                data.update(parse_ancrage(date_strs[0],
                                          prefix='naissance', commit=commit))
                if len(date_strs) == 2:
                    data.update(parse_ancrage(date_strs[1],
                                              prefix='deces', commit=commit))
        return update_or_create(
            Individu, data, unique_keys=['nom', 'prenoms', 'particule_nom'],
            commit=commit)


def get_individus(individus_str, sep=';', dates_sep='-', commit=True):
    if not individus_str:
        return []
    individu_strs = [s.strip() for s in individus_str.split(sep)]
    return [get_individu(s, dates_sep=dates_sep, commit=commit)
            for s in individu_strs]
