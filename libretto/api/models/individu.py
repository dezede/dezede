# coding: utf-8

from __future__ import unicode_literals
import re
from .utils import update_or_create
from ...models import Individu


PARTICULES = 'de|d’|d\'|di|da|van|von|ben'
INDIVIDU_RE = re.compile(
    r'^'
    r'(?P<nom>[^,]+?), '
    r'(?:(?P<prenoms>[^,]+?)(?: (?P<particule_nom>%s))?)'
    r'(?:, dite? (?P<pseudonyme>[^,]+))?'
    r'$'
    % PARTICULES, flags=re.IGNORECASE)


def get_individu(individu_str, commit=True):
    if individu_str.isdigit():
        return Individu.objects.get(pk=individu_str)
    else:
        match = INDIVIDU_RE.match(individu_str)
        if match is None:
            data = {'nom': individu_str}
        else:
            data = match.groupdict()
        for k, v in data.items():
            if v is None:
                del data[k]
            else:
                data[k] = v.strip()
        return update_or_create(Individu, data, commit=commit)


def get_individus(individus_str, separator=';', commit=True):
    if not individus_str:
        return []
    individu_strs = [s.strip() for s in individus_str.split(separator)]
    return [get_individu(s, commit=commit) for s in individu_strs]
