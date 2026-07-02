"""
Public, read-only DRF API for the Next.js (musicaLetters) frontend's dossiers
section: the category index, a dossier's presentation, its events/works data
list, the map GeoJSON and the statistics (period distribution + chord diagram).

The statistics replicate ``DossierDEvenementsStatsDetail`` in ``views.py`` so the
React visualisations match the Django ones.
"""
import json

from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.contrib.sites.models import Site
from django.core.exceptions import EmptyResultSet
from django.db import connection
from django.db.models import Count, F
from django.db.models.functions import ExtractYear
from django.utils.html import strip_tags
from django.utils.text import capfirst
from django.utils.translation import get_language, gettext as _
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from common.utils.cache import is_user_locked, lock_user
from common.utils.sql import get_raw_query
from libretto.api.rest import public_serializers as ps
from libretto.api.rest.authority_tables import (
    centuries_options, data_type_options,
)
from libretto.api.rest.filters import (
    evenement_facets, filter_evenements_queryset, filter_oeuvres_queryset,
    filter_sources_queryset,
)
from libretto.api.rest.public_viewsets import lookup_autocomplete
from libretto.api.rest.viewsets import (
    EVENEMENT_PUBLIC_SELECT, EVENEMENT_PUBLIC_PREFETCH,
)
from libretto.models import GenreDOeuvre, Individu, TypeDeSource
from libretto.templatetags.extras import get_data
from libretto.views import DEFAULT_MIN_PLACES, MAX_MIN_PLACES

from .forms import SCENARIOS
from .jobs import dossier_to_pdf, dossier_to_xlsx
from .models import (
    CategorieDeDossiers, Dossier, DossierDEvenements, DossierDOeuvres,
    DossierDeSources,
)
from .views import (
    PERIODS, PERIOD_NAMES, PERIOD_COLORS, PERIOD_TEXT_COLORS, DEFAULT_PERIOD,
    CHORD_DIAGRAM_SQL,
)


def dossier_kind(dossier):
    if isinstance(dossier, DossierDEvenements):
        return 'evenements'
    if isinstance(dossier, DossierDOeuvres):
        return 'oeuvres'
    if isinstance(dossier, DossierDeSources):
        return 'sources'
    return None


def serialize_user(user):
    """A dossier editor/contributor for the sidebar: display name plus the URL
    of the user's (always public) Django profile page, so the frontend chip can
    link to it."""
    return {'name': str(user), 'url': user.get_absolute_url()}


def excerpt(html, word_count=30):
    """Plain-text excerpt of a rich-text field: its first ``word_count`` words,
    with a trailing "[…]" when the text was actually truncated."""
    words = strip_tags(html).split()
    if not words:
        return ''
    text = ' '.join(words[:word_count])
    if len(words) > word_count:
        text += ' […]'
    return text


def serialize_card(dossier):
    """Light card for the index/children lists."""
    specific = dossier.specific
    return {
        'id': specific.pk,
        'meta': {'type': f'{specific._meta.app_label}.'
                         f'{specific._meta.object_name}'},
        'titre': specific.titre,
        'titre_court': specific.titre_court,
        'slug': specific.slug,
        'kind': dossier_kind(specific),
        'count': specific.get_count(),
        'children_count': specific.children.count(),
        'cover_image': (specific.image_couverture.url
                        if specific.image_couverture else None),
        'excerpt': excerpt(specific.presentation),
        'categorie_id': specific.categorie_id,
    }


# -- Statistics (ported from DossierDEvenementsStatsDetail) ------------------

def get_oeuvres_par_periode(oeuvres_qs):
    try:
        oeuvres_sql, oeuvres_params = get_raw_query(
            oeuvres_qs.order_by().values('pk'))
    except EmptyResultSet:
        return []

    conditions = [
        'WHEN year >= %s AND year < %s THEN %s' % (min_year, max_year, k)
        for k, (min_year, max_year) in PERIODS.items()]
    conditions.insert(0, 'WHEN year IS NULL THEN %s' % DEFAULT_PERIOD)
    sql = """
    SELECT CASE %s END AS period, COUNT(oeuvre_id)
    FROM (
        SELECT extract(YEAR FROM MIN(individu.naissance_date)) AS year,
               oeuvre.id AS oeuvre_id
        FROM (%s) AS oeuvre
        INNER JOIN libretto_auteur AS auteur ON (auteur.oeuvre_id = oeuvre.id)
        INNER JOIN libretto_individu AS individu
            ON (individu.id = auteur.individu_id)
        GROUP BY oeuvre.id
    ) AS years_and_ids
    GROUP BY period ORDER BY period;
    """ % (' '.join(conditions), oeuvres_sql)

    with connection.cursor() as cursor:
        cursor.execute(sql, oeuvres_params)
        data = cursor.fetchall()
    return [{'name': str(PERIOD_NAMES[k]), 'color': PERIOD_COLORS[k],
             'text_color': PERIOD_TEXT_COLORS[k], 'count': count}
            for k, count in data]


def get_chord_diagram(dossier, n_auteurs=30):
    evenements = dossier.queryset
    individus = evenements.individus_auteurs()
    n_individus = individus.count()
    if n_individus == 0:
        return None
    if n_individus == n_auteurs + 1:
        n_auteurs = n_individus

    individus_par_popularite = individus.annotate(n=Count('pk')).order_by('-n')
    individus_pks = [
        pk for pk, _ in
        individus_par_popularite.values_list('pk', 'n')[:n_auteurs]]
    individus = Individu.objects.filter(
        pk__in=individus_pks).order_by('naissance_date')
    evenements = evenements.order_by().values('pk')
    evenements_sql, evenements_params = get_raw_query(evenements)
    individus_sql, individus_params = get_raw_query(
        individus.order_by().values('pk'))

    with connection.cursor() as cursor:
        cursor.execute(CHORD_DIAGRAM_SQL % (individus_sql, evenements_sql),
                       individus_params + evenements_params)
        data = cursor.fetchall()

    if len(data) < 3:
        return None

    has_autres = False
    pre_matrix = {}
    for id1, id2, k in data:
        has_autres |= id1 is None or id2 is None
        pre_matrix[(id1, id2)] = k

    individus = list(individus)
    if has_autres:
        individus.append(
            Individu(nom='%d autres auteurs' % (n_individus - n_auteurs)))

    matrix = [[pre_matrix.get((a.pk, b.pk), 0) for b in individus]
              for a in individus]

    def period_color(individu):
        year = (None if individu.naissance_date is None
                else individu.naissance_date.year)
        if year is None:
            return PERIOD_COLORS[DEFAULT_PERIOD]
        for k, (min_year, max_year) in PERIODS.items():
            if min_year <= year < max_year:
                return PERIOD_COLORS[k]
        return PERIOD_COLORS[DEFAULT_PERIOD]

    nodes = [{'id': individu.pk,
              'individu': ps.PersonSerializer(individu).data,
              'color': period_color(individu)} for individu in individus]
    colors = [node['color'] for node in nodes]
    legend = [{'name': str(PERIOD_NAMES[k]), 'color': PERIOD_COLORS[k]}
              for k in PERIODS if PERIOD_COLORS[k] in colors]
    return {'nodes': nodes, 'matrix': matrix, 'legend': legend}


class DossierPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


# First-page size of each source-type group on a dossier de sources. The frontend
# (DossierData) appends further pages with this same limit, so the two must match.
SOURCES_GROUP_PAGE_SIZE = 40


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Session auth without CSRF enforcement, for the dossier export POST
    actions. Those only enqueue an export emailed to the *requesting* user (no
    data mutation, no destructive effect, guarded by per-user locking + DRF
    throttling), so the SPA can POST with just the session cookie rather than
    plumbing a CSRF token. Read actions are GET and unaffected."""

    def enforce_csrf(self, request):
        return


class DossierViewSet(ReadOnlyModelViewSet):
    """Public dossiers API. ``list`` returns the category index; ``retrieve``
    a dossier's presentation; plus events/works/geojson/stats sub-resources and
    the PDF/statistics export POST actions."""
    authentication_classes = [CsrfExemptSessionAuthentication]
    queryset = Dossier.objects.all()

    def get_queryset(self):
        return Dossier.objects.published(request=self.request)

    def list(self, request, *args, **kwargs):
        # Flat list, most recently published first, so the frontend can render
        # a single masonry grid and filter it client-side by category chip
        # (children never carry a category of their own, see the model's
        # help_text, so this naturally only surfaces top-level dossiers).
        dossiers = self.get_queryset().filter(parent__isnull=True).order_by(
            F('date_publication').desc(nulls_last=True), '-pk')
        categories = CategorieDeDossiers.objects.published(request=request)
        return Response({
            'categories': [{'id': c.pk, 'nom': c.nom} for c in categories],
            'dossiers': [serialize_card(d) for d in dossiers],
        })

    def retrieve(self, request, *args, **kwargs):
        dossier = self.get_object().specific
        children = dossier.children.published(request)
        is_evenements = isinstance(dossier, DossierDEvenements)
        # Sidebar actions, mirroring the Django template gates: PDF export for any
        # authenticated user on any dossier type (see the XeLaTeX templates in
        # dossiers/templates/dossiers/), the statistics scenario export for
        # superusers on event dossiers only (see ``dossierdevenements_sidebar.html``).
        can_export_pdf = request.user.is_authenticated
        can_export_stats = request.user.is_superuser and is_evenements
        data = {
            'id': dossier.pk,
            'meta': {'type': f'{dossier._meta.app_label}.'
                             f'{dossier._meta.object_name}'},
            'titre': dossier.titre,
            'titre_court': dossier.titre_court,
            'slug': dossier.slug,
            'kind': dossier_kind(dossier),
            'count': dossier.get_count(),
            'children_count': children.count(),
            'categorie_id': dossier.categorie_id,
            'presentation': dossier.presentation,
            'contexte': dossier.contexte,
            'sources_et_protocole': dossier.sources_et_protocole,
            'bibliographie': dossier.bibliographie,
            'publications': dossier.publications,
            # Sidebar metadata. The musicaLetters frontend has no profile pages
            # of its own, so each user carries the URL of the existing Django
            # profile page (``/utilisateurs/<username>``) to link the chip to.
            'editeurs_scientifiques': [
                serialize_user(u) for u in dossier.editeurs_scientifiques.all()],
            'contributors': [serialize_user(u) for u in dossier.contributors],
            'date_publication': (dossier.date_publication.isoformat()
                                 if dossier.date_publication else None),
            'developpements': dossier.developpements,
            'can_export_pdf': can_export_pdf,
            'can_export_stats': can_export_stats,
            'cover_image': (dossier.image_couverture.url
                            if dossier.image_couverture else None),
            'children': [serialize_card(c) for c in children],
            'citation': self.get_citation(dossier),
            **ps.admin_link_data(dossier, request),
        }
        if can_export_stats:
            # Expose the already-translated scenario labels so the export dialog
            # need not duplicate them in the frontend i18n catalogue.
            data['scenario_choices'] = [
                {'value': value, 'label': str(label)}
                for value, label in SCENARIOS]
        return Response(data)

    @staticmethod
    def get_citation(dossier):
        """Academic reference for the « Pour citer ce dossier » block, mirroring
        the source citation (see ``SourceDetailSerializer.get_citation``). The
        ``url`` is a relative path; the frontend prefixes the canonical
        dezede.org domain."""
        return {
            'title': str(dossier),
            'url': dossier.permalien(),
            'editeurs': [str(u)
                         for u in dossier.editeurs_scientifiques.all()],
        }

    @action(detail=True)
    def evenements(self, request, pk=None):
        dossier = self.get_object().specific
        if not isinstance(dossier, DossierDEvenements):
            return Response({'count': 0, 'results': []})
        # Apply the same filters as the global event list (free text, dates,
        # lieu/oeuvre/individu/ensemble…) before the eager-loading, mirroring
        # EvenementViewSet.filter_queryset so the semantics cannot drift.
        qs = filter_evenements_queryset(dossier.queryset, request.query_params)
        qs = qs.select_related(*EVENEMENT_PUBLIC_SELECT) \
            .prefetch_related(*EVENEMENT_PUBLIC_PREFETCH)
        paginator = DossierPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        data = ps.EvenementSerializer(
            page, many=True, context={'request': request}).data
        return paginator.get_paginated_response(data)

    @action(detail=True)
    def facets(self, request, pk=None):
        # Filter-form facets (date-slider bounds + filtered count + auth flag)
        # for this dossier's events, scoped to dossier.queryset. Mirrors
        # EvenementViewSet.facets via the shared helper.
        dossier = self.get_object().specific
        if not isinstance(dossier, DossierDEvenements):
            return Response({
                'date_range': {'min_year': 1600, 'max_year': 1600},
                'total_count': 0,
                'is_authenticated': request.user.is_authenticated,
            })
        return Response(evenement_facets(
            dossier.queryset, request.query_params,
            request.user.is_authenticated))

    @action(detail=True)
    def oeuvres(self, request, pk=None):
        dossier = self.get_object().specific
        if not isinstance(dossier, DossierDOeuvres):
            return Response({'count': 0, 'results': []})
        qs = dossier.queryset.select_related(
            'genre', 'creation_lieu__parent__nature', 'creation_lieu__nature',
        ).prefetch_related(
            'pupitres__partie', 'auteurs__individu', 'auteurs__ensemble',
            'auteurs__profession')
        # Same list filters as the standalone œuvres index, scoped to this
        # dossier (free text, genre, author).
        qs = filter_oeuvres_queryset(qs, request.query_params)
        # Mirror DossierDOeuvresDataDetail: order by world-premiere date when
        # asked, otherwise keep the default tree (path) ordering.
        if request.query_params.get('order_by') == 'creation_date':
            qs = qs.order_by('creation_date')
        paginator = DossierPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        data = ps.DossierWorkSerializer(
            page, many=True, context={'request': request}).data
        return paginator.get_paginated_response(data)

    @action(detail=True)
    def genres(self, request, pk=None):
        """Type-ahead options for the dossier d'œuvres ``genre`` filter, scoped
        to the genres actually present in the dossier's works (the full genre
        list is too long for a plain ``<select>``). Authors use the shared
        ``/api/evenements/{individus,ensembles}/`` type-ahead."""
        dossier = self.get_object().specific
        if not isinstance(dossier, DossierDOeuvres):
            return Response([])
        return lookup_autocomplete(request, GenreDOeuvre.objects.filter(
            pk__in=dossier.queryset.values('genre_id')))

    @action(detail=True)
    def sources(self, request, pk=None):
        dossier = self.get_object().specific
        if not isinstance(dossier, DossierDeSources):
            return Response({'count': 0, 'groups': []})
        qs = dossier.queryset.select_related('type')
        # Same list filters as the standalone sources index, scoped to this
        # dossier (free text, content type, century). The source-type (`type`)
        # filter is the per-group key handled just below, so it is excluded here.
        qs = filter_sources_queryset(qs, request.query_params)
        # Order by the ancrage date when asked, otherwise keep the queryset's
        # default ordering.
        if request.query_params.get('order_by') == 'date':
            qs = qs.order_by('date', 'pk')

        by_date = request.query_params.get('order_by') == 'date'

        type_id = request.query_params.get('type')
        if not by_date and type_id is not None:
            # Load-more within a single source-type group: a flat paginated list
            # of that type's rows (the frontend's per-group infinite scroll).
            paginator = DossierPagination()
            page = paginator.paginate_queryset(
                qs.filter(type_id=type_id), request, view=self)
            data = ps.SourceRowSerializer(
                page, many=True, context={'request': request}).data
            return paginator.get_paginated_response(data)

        if by_date:
            # "Par date": group by year (mirroring the per-type grouping) so the
            # chronological order reads as clearly-boxed year blocks.
            year = request.query_params.get('year')
            if year is not None:
                # Load-more within a single year group.
                year_qs = (qs.filter(date__isnull=True) if year == ''
                           else qs.filter(date__year=year))
                paginator = DossierPagination()
                page = paginator.paginate_queryset(year_qs, request, view=self)
                data = ps.SourceRowSerializer(
                    page, many=True, context={'request': request}).data
                return paginator.get_paginated_response(data)
            return Response(self._year_groups(qs, request))

        # Initial load: one block per source type (slug-ordered, the TypeDeSource
        # default), each with its total count and first page of rows. Mirrors the
        # related-sources panels (``grouped_sources``), but paginated per group.
        groups = []
        total = 0
        types = TypeDeSource.objects.filter(
            pk__in=qs.values('type_id')).order_by('slug')
        for type_obj in types:
            type_qs = qs.filter(type_id=type_obj.pk)
            count = type_qs.count()
            total += count
            label = type_obj.pluriel() if count > 1 else type_obj.nom
            groups.append({
                'type': capfirst(label),
                'type_id': type_obj.pk,
                'count': count,
                'results': ps.SourceRowSerializer(
                    type_qs[:SOURCES_GROUP_PAGE_SIZE], many=True,
                    context={'request': request}).data,
            })
        return Response({'count': total, 'groups': groups})

    def _year_groups(self, qs, request):
        """Build one block per ``date`` year (chronological, undated last) for
        the "Par date" view, in the same ``{count, groups}`` shape as the
        per-type grouping. Each group's ``type_id`` is the year (or '' for
        undated rows), used by the frontend's per-group load-more (``?year=``)."""
        years = (qs.order_by().annotate(year=ExtractYear('date'))
                 .values_list('year', flat=True).distinct())
        years = sorted(y for y in years if y is not None)
        # Undated rows go in a trailing « Sans date » block.
        if qs.filter(date__isnull=True).exists():
            years.append(None)
        groups = []
        total = 0
        for year in years:
            if year is None:
                year_qs = qs.filter(date__isnull=True)
                label = _('Sans date')
            else:
                year_qs = qs.filter(date__year=year)
                label = str(year)
            count = year_qs.count()
            total += count
            groups.append({
                'type': label,
                'type_id': year if year is not None else '',
                'count': count,
                'results': ps.SourceRowSerializer(
                    year_qs[:SOURCES_GROUP_PAGE_SIZE], many=True,
                    context={'request': request}).data,
            })
        return {'count': total, 'groups': groups}

    @action(detail=True)
    def sources_filters(self, request, pk=None):
        """Option lists for the dossier de sources filter bar. ``icons`` and
        ``ancrage`` reuse the standalone-index static option lists; the source
        ``type`` filter is a type-ahead (see ``source_types``), so it needs no
        option list here."""
        dossier = self.get_object().specific
        if not isinstance(dossier, DossierDeSources):
            return Response({'icons': [], 'ancrage': []})
        return Response({
            'icons': data_type_options(),
            'ancrage': centuries_options(),
        })

    @action(detail=True)
    def source_types(self, request, pk=None):
        """Type-ahead options for the dossier de sources ``type`` filter, scoped
        to the source types actually present in the dossier (the full source-type
        list is too long for a plain ``<select>``)."""
        dossier = self.get_object().specific
        if not isinstance(dossier, DossierDeSources):
            return Response([])
        return lookup_autocomplete(request, TypeDeSource.objects.filter(
            pk__in=dossier.queryset.values('type_id')))

    @action(detail=True)
    def geojson(self, request, pk=None):
        dossier = self.get_object().specific
        if not isinstance(dossier, DossierDEvenements):
            return Response({'type': 'FeatureCollection', 'features': []})
        qs = dossier.queryset
        bbox = request.query_params.get('bbox')
        bbox = (Polygon.from_bbox([float(c) for c in bbox.split(',')])
                if bbox else None)
        min_places = request.query_params.get('min_places',
                                              str(DEFAULT_MIN_PLACES))
        min_places = (int(min_places) if min_places.isdigit()
                      else DEFAULT_MIN_PLACES)
        min_places = min(min_places, MAX_MIN_PLACES)
        features = []
        for lieu_pk, nom, geometry, n in get_data(qs, min_places, bbox):
            point = GEOSGeometry(geometry).point_on_surface
            features.append({
                'type': 'Feature',
                'properties': {'lieu_pk': lieu_pk, 'tooltip': f'{nom} ({n})',
                               'n': n},
                'geometry': json.loads(point.json),
            })
        return Response({'type': 'FeatureCollection', 'features': features})

    @action(detail=True)
    def stats(self, request, pk=None):
        dossier = self.get_object().specific
        if not isinstance(dossier, DossierDEvenements):
            return Response({})
        oeuvres_par_periode = get_oeuvres_par_periode(dossier.queryset.oeuvres())
        return Response({
            'oeuvres_par_periode': oeuvres_par_periode,
            'n_oeuvres': sum(p['count'] for p in oeuvres_par_periode),
            'chord': get_chord_diagram(dossier),
        })

    def _enqueue_export(self, request, export_job, data, file_extension):
        """Shared body of the export actions: replicate ``launch_export`` (per-user
        lock + ``job.delay``) but return JSON the SPA can act on instead of the
        Django ``messages`` framework's redirect flow. Each response carries a
        stable ``code`` (and ``format`` for the success case) so the frontend can
        localise the snackbar itself; ``detail`` is a French fallback."""
        if not request.user.is_authenticated:
            return Response(
                {'code': 'export_not_authenticated',
                 'detail': _('Vous devez être connecté pour lancer un '
                             'export.')},
                status=403)
        if is_user_locked(request.user):
            return Response(
                {'code': 'export_in_progress',
                 'detail': _('Un export de votre part est déjà en cours. '
                             'Veuillez attendre la fin de celui-ci avant d’en '
                             'lancer un autre.')},
                status=409)
        lock_user(request.user)
        site = Site.objects.get_current(request)
        # LocaleMiddleware sets LANGUAGE_CODE on a real request; fall back to the
        # active language so the action never 500s outside that middleware.
        language_code = getattr(request, 'LANGUAGE_CODE', None) or get_language()
        export_job.delay(data, request.user.pk, site.pk, language_code)
        return Response(
            {'code': 'export_started',
             'format': file_extension,
             'detail': _('La génération de l’export %s est en cours. Un '
                         'courriel le contenant vous sera envoyé d’ici quelques '
                         'minutes.') % file_extension},
            status=202)

    @action(detail=True, methods=['post'])
    def export_pdf(self, request, pk=None):
        dossier = self.get_object().specific
        return self._enqueue_export(request, dossier_to_pdf, dossier.pk, 'PDF')

    @action(detail=True, methods=['post'])
    def export_scenario(self, request, pk=None):
        dossier = self.get_object().specific
        if not request.user.is_superuser:
            return Response(
                {'code': 'export_no_permission',
                 'detail': _('Vous n’avez pas la permission de lancer cet '
                             'export.')},
                status=403)
        if not isinstance(dossier, DossierDEvenements):
            return Response(
                {'code': 'export_unavailable',
                 'detail': _('Export indisponible pour ce dossier.')},
                status=400)
        # Normalise the posted list to the ``[{'scenario': 'scenario-N'}, …]``
        # shape ``dossier_to_xlsx`` expects, dropping anything not in SCENARIOS.
        valid = {value for value, label in SCENARIOS}
        scenarios = [
            {'scenario': item['scenario']}
            for item in (request.data.get('scenarios') or [])
            if isinstance(item, dict) and item.get('scenario') in valid]
        if not scenarios:
            return Response(
                {'code': 'export_no_scenario',
                 'detail': _('Veuillez sélectionner au moins un scénario.')},
                status=400)
        data = {'dossier': dossier.pk, 'scenarios': scenarios}
        return self._enqueue_export(request, dossier_to_xlsx, data, 'XLSX')
