"""
Shared event-list filtering, used by both the public HTML list view
(``libretto.views.BaseEvenementListView``) and the REST API
(``EvenementViewSet``) so their semantics cannot drift.

Filter GET/query params (all optional):
- ``q``: free-text Wagtail search.
- ``lieu``/``oeuvre``/``individu``/``ensemble``: pipe-delimited pk lists
  (e.g. ``|12|34|``); tree models also match descendants. See
  ``BaseEvenementListView.BINDINGS``.
- ``dates_0``/``dates_1``: inclusive year range.
- ``par_saison``: ``True`` to filter by season instead of civil year.
- ``order_by=reversed``: reverse the default ordering.

It also hosts the dossier de sources / dossier d'œuvres list filtering
(``filter_sources_queryset`` / ``filter_oeuvres_queryset``), mirroring the public
authority API's column filters (``authority_tables``) so a dossier's "Données"
tab and the standalone sources/œuvres index pages cannot drift apart.
"""
import datetime

from django.db.models import Max, Min, Q
from rest_framework.filters import BaseFilterBackend
from wagtail.search.backends import get_search_backend

from .authority_tables import CENTURIES_DATE_RANGES
from ...models import Saison, Source


def filter_evenements_queryset(qs, data):
    # Imported lazily to avoid a circular import (views imports this module).
    from ...views import BaseEvenementListView

    search_query = data.get('q')
    if search_query:
        s = get_search_backend()
        qs = s.autocomplete(search_query, qs).get_queryset()

    qs = qs.filter(BaseEvenementListView.get_filters(data)).distinct()

    try:
        start, end = int(data.get('dates_0')), int(data.get('dates_1'))
        if data.get('par_saison', 'False') == 'True':
            qs &= Saison.objects.between_years(start, end).evenements()
        else:
            qs = qs.filter(
                debut_date__range=(f'{start}-1-1', f'{end}-12-31'))
    except (TypeError, ValueError):
        pass

    if data.get('order_by') == 'reversed':
        qs = qs.reverse()

    return qs


class EvenementFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return filter_evenements_queryset(queryset, request.query_params)


def evenement_facets(base_qs, query_params, is_authenticated):
    """Filter-form facets for an event queryset, shared by the global event API
    and the per-dossier event API so the two cannot drift.

    The date-slider bounds come from the *unfiltered* ``base_qs`` published range
    (as in ``range_slider.fields.RangeSliderWidget.get_default_range``); the count
    reflects the current filters.
    """
    agg = base_qs.aggregate(min=Min('debut_date'), max=Max('debut_date'),
                            max_fin=Max('fin_date'))
    min_date, max_date, max_fin = agg['min'], agg['max'], agg['max_fin']
    if max_fin is not None and max_date is not None:
        max_date = max(max_date, max_fin)
    min_year = min_date.year if min_date is not None else 1600
    max_year = (max_date.year if max_date is not None
                else datetime.date.today().year)
    total = filter_evenements_queryset(base_qs, query_params).count()
    return {
        'date_range': {'min_year': min_year, 'max_year': max_year},
        'total_count': total,
        'is_authenticated': is_authenticated,
    }


def parse_pk_list(value):
    """``"|12|34|"`` -> ``['12', '34']`` (the events pipe-delimited convention,
    see ``BaseEvenementListView.get_filters``). Returns ``[]`` for an empty/None
    value."""
    if not value:
        return []
    return [pk for pk in value.strip('|').split('|') if pk]


def filter_sources_queryset(qs, params):
    """Apply the dossier de sources list filters to an (already dossier-scoped)
    ``Source`` queryset, mirroring the public ``sources`` column filters
    (``authority_tables.FILTER_SPECS['sources']``):

    - ``q``: free-text Wagtail prefix autocomplete (the queryset's own order
      survives);
    - ``icons``: a ``Source.DATA_TYPES`` content type (image/audio/video/text/
      link/other);
    - ``ancrage``: a century key ("19"), filtering the ancrage ``date``.

    The ``type`` source-type filter and ``order_by`` sort are intentionally left
    to the caller (the dossier ``sources`` action owns per-type grouping and
    pagination, so ``type`` carries a different meaning there).
    """
    q = params.get('q')
    if q:
        backend = get_search_backend()
        qs = backend.autocomplete(q, qs).get_queryset()

    icons = params.get('icons')
    if icons and icons in Source.DATA_TYPES:
        qs = qs.filter(pk__in=Source.objects.with_data_type(icons))

    ancrage = params.get('ancrage')
    if ancrage:
        date_range = CENTURIES_DATE_RANGES.get(ancrage)
        if date_range is not None:
            qs = qs.filter(date__range=date_range)

    return qs


def filter_oeuvres_queryset(qs, params):
    """Apply the dossier d'œuvres list filters to an (already dossier-scoped)
    ``Oeuvre`` queryset:

    - ``q``: free-text Wagtail prefix autocomplete (the default tree order
      survives when no explicit sort is asked);
    - ``genre``: a ``GenreDOeuvre`` pk;
    - ``individu`` / ``ensemble``: pipe-delimited author pk lists (``|12|34|``,
      the events convention), matched against the work's ``auteurs``.

    ``order_by`` (name vs world-premiere date) is left to the caller.
    """
    q = params.get('q')
    if q:
        backend = get_search_backend()
        qs = backend.autocomplete(q, qs).get_queryset()

    genre = params.get('genre')
    if genre:
        qs = qs.filter(genre_id=genre)

    individus = parse_pk_list(params.get('individu'))
    ensembles = parse_pk_list(params.get('ensemble'))
    if individus or ensembles:
        author_q = Q()
        if individus:
            author_q |= Q(auteurs__individu_id__in=individus)
        if ensembles:
            author_q |= Q(auteurs__ensemble_id__in=ensembles)
        qs = qs.filter(author_q).distinct()

    return qs
