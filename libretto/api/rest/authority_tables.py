"""
Shared field maps for the "autorité" list views.

Both the Django HTML tables (``libretto.views.*TableView``) and the public REST
API (``libretto.api.rest.public_viewsets``) drive their columns, sortings and
filters from the constants below, so the two front-ends cannot drift apart — the
same idea as ``libretto.api.rest.filters.filter_evenements_queryset`` for events.

This module is import-light on purpose (only ``common.utils.text`` lazily): it
must stay free of any ``libretto.views`` import to avoid a circular import.
"""

# Centuries used by the date filters (11th–21st), mirroring ``libretto.views``.
CENTURIES = tuple(range(11, 22))

# Map a century key ("19") to an inclusive ``(start, end)`` ISO date range, e.g.
# "19" -> ('1800-1-1', '1899-12-31').
CENTURIES_DATE_RANGES = {
    f'{i}': (f'{i - 1}00-1-1', f'{i - 1}99-12-31') for i in CENTURIES
}


def centuries_options():
    """``[{'value': '19', 'label': 'XIXe siècle'}, …]`` newest-first.

    Plain-text labels (no ``<sup>`` HTML) for the JSON filter UI, unlike the
    Django-side ``CENTURIES_VERBOSES``.
    """
    from common.utils.text import to_roman
    return [
        {'value': str(i), 'label': f'{to_roman(i)}e siècle'}
        for i in CENTURIES
    ][::-1]


def data_type_options():
    """Plain labels for ``Source`` content-type filtering (the "icons" column)."""
    return [
        {'value': 'video', 'label': 'Vidéo'},
        {'value': 'audio', 'label': 'Audio'},
        {'value': 'image', 'label': 'Image'},
        {'value': 'other', 'label': 'Autre'},
        {'value': 'text', 'label': 'Texte'},
        {'value': 'link', 'label': 'Lien'},
    ]


# -- Sortings ---------------------------------------------------------------
# Per public-API key: the sortable column name -> the ORM field/lookup to
# ``order_by``. These mirror the ``orderings`` dicts on the matching
# ``*TableView`` classes exactly (so the same columns are sortable here).

ORDERING_MAPS = {
    'oeuvres': {
        'titre': 'titre',
        'auteurs': 'auteurs__individu',
        'creation': 'creation_date',
    },
    'individus': {
        'nom': 'nom',
        'professions': 'professions',
        'naissance': 'naissance_date',
        'deces': 'deces_date',
    },
    'ensembles': {
        'nom': 'nom',
    },
    'parties': {
        'nom': 'nom',
    },
    'professions': {
        'nom': 'nom',
    },
    'sources': {
        'ancrage': 'date',
    },
}


# -- Filters ----------------------------------------------------------------
# Per public-API key: the query param -> a spec describing how to filter.
#   kind='century'   -> ``<field>__range = CENTURIES_DATE_RANGES[value]``
#   kind='fk'        -> ``<field>_id = value`` (exact related pk)
#   kind='choice'    -> ``<field> = value`` (exact integer choice)
#   kind='data_type' -> ``Source.objects.with_data_type(value)`` membership
# These mirror the ``filters`` dicts / ``filter_*`` methods on the matching
# ``*TableView`` classes.

FILTER_SPECS = {
    'oeuvres': {
        'creation': {'kind': 'century', 'field': 'creation_date'},
    },
    'individus': {
        'naissance': {'kind': 'century', 'field': 'naissance_date'},
        'deces': {'kind': 'century', 'field': 'deces_date'},
    },
    'ensembles': {
        'type': {'kind': 'fk', 'field': 'type'},
    },
    'parties': {
        'type': {'kind': 'choice', 'field': 'type'},
    },
    'professions': {},
    'sources': {
        'ancrage': {'kind': 'century', 'field': 'date'},
        'type': {'kind': 'fk', 'field': 'type'},
        'icons': {'kind': 'data_type'},
    },
}
