from functools import cached_property

from django.core.exceptions import PermissionDenied, EmptyResultSet
from django.db import connection
from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from el_pagination.views import AjaxListView

from accounts.models import HierarchicUser
from common.utils.sql import get_raw_query
from .jobs import dossier_to_pdf, dossier_to_xlsx
from libretto.models import Source, Oeuvre, Individu
from libretto.views import (
    PublishedListView, PublishedDetailView, EvenementGeoJson, EvenementExport,
    BaseEvenementListView, MAX_MIN_PLACES, DEFAULT_MIN_PLACES)
from .models import (
    CategorieDeDossiers, Dossier, KIND_EVENEMENTS, KIND_OEUVRES, KIND_SOURCES,
)
from common.utils.export import launch_export

from .forms import ScenarioForm, ScenarioFormSet

DEFAULT_PERIOD = -1

PERIODS = {
    0: (-4713, 1580),
    1: (1580, 1730),
    2: (1730, 1780),
    3: (1780, 1880),
    4: (1880, 1920),
    5: (1920, 5874897),
}

PERIOD_NAMES = {
    -1: _('Indéterminé'),
    0: _('Né avant 1580'),
    1: _('Baroque'),
    2: _('Classique'),
    3: _('Romantique'),
    4: _('Moderne'),
    5: _('Né après 1920'),
}

PERIOD_COLORS = {
    -1: '#E6E6E6',
    0: '#75101C',
    1: '#FF6523',
    2: '#FFDD89',
    3: '#4D8E66',
    4: '#89B4FF',
    5: '#80138E',
}

PERIOD_TEXT_COLORS = {
    -1: 'black',
    0: 'white',
    1: 'white',
    2: 'black',
    3: 'white',
    4: 'black',
    5: 'white',
}

# Kinds that get a « Visualisations » page (map + statistics).
STATS_KINDS = (KIND_EVENEMENTS, KIND_OEUVRES)


class CategorieDeDossiersList(PublishedListView):
    model = CategorieDeDossiers
    has_frontend_admin = False


class DossierDetail(PublishedDetailView):
    model = Dossier
    # FIXME: Try to find out what to do with this.
    formset = ScenarioFormSet
    form = ScenarioForm

    def get_context_data(self, **kwargs):
        context = super(DossierDetail,
                        self).get_context_data(**kwargs)
        context.update(
            children=self.object.children.published(self.request),
            formset=self.formset(),
            form=self.form(),
        )
        return context


CHORD_DIAGRAM_SQL_SANS_AUTRES = """
WITH individus AS (%s)
SELECT individu1.id, individu2.id, COUNT(DISTINCT programme1.evenement_id) AS n
FROM individus AS individu1
LEFT OUTER JOIN individus AS individu2 ON (true)
LEFT OUTER JOIN libretto_auteur AS auteur1 ON (auteur1.individu_id = individu1.id)
LEFT OUTER JOIN libretto_auteur AS auteur2 ON (auteur2.individu_id = individu2.id AND auteur2.oeuvre_id != auteur1.oeuvre_id)
LEFT OUTER JOIN libretto_elementdeprogramme AS programme1 ON (programme1.oeuvre_id = auteur1.oeuvre_id)
LEFT OUTER JOIN libretto_elementdeprogramme AS programme2 ON (programme2.oeuvre_id = auteur2.oeuvre_id)
WHERE programme1.evenement_id = programme2.evenement_id AND programme1.evenement_id IN (%s)
GROUP BY individu1.id, individu2.id;
"""

CHORD_DIAGRAM_SQL_AVEC_AUTRES = """
WITH individus AS (%s)
SELECT individu1.id, individu2.id, COUNT(DISTINCT evenement.id) AS n
FROM (%s) AS evenement
INNER JOIN libretto_elementdeprogramme AS programme1 ON (programme1.evenement_id = evenement.id)
INNER JOIN libretto_elementdeprogramme AS programme2 ON (programme2.evenement_id = evenement.id AND programme2.oeuvre_id != programme1.oeuvre_id)
INNER JOIN libretto_auteur AS auteur1 ON (auteur1.oeuvre_id = programme1.oeuvre_id)
INNER JOIN libretto_auteur AS auteur2 ON (auteur2.oeuvre_id = programme2.oeuvre_id)
LEFT OUTER JOIN individus AS individu1 ON (individu1.id = auteur1.individu_id)
LEFT OUTER JOIN individus AS individu2 ON (individu2.id = auteur2.individu_id)
GROUP BY individu1.id, individu2.id;
"""

CHORD_DIAGRAM_SQL = CHORD_DIAGRAM_SQL_AVEC_AUTRES

# Co-authorship over a works queryset: how many works each pair of authors
# shares. The same « avec autres » convention as the events chord applies:
# authors outside the top-N CTE fall in the NULL bucket.
WORKS_CHORD_DIAGRAM_SQL = """
WITH individus AS (%s)
SELECT individu1.id, individu2.id, COUNT(DISTINCT oeuvre.id) AS n
FROM (%s) AS oeuvre
INNER JOIN libretto_auteur AS auteur1 ON (auteur1.oeuvre_id = oeuvre.id)
INNER JOIN libretto_auteur AS auteur2 ON (auteur2.oeuvre_id = oeuvre.id AND auteur2.individu_id != auteur1.individu_id)
LEFT OUTER JOIN individus AS individu1 ON (individu1.id = auteur1.individu_id)
LEFT OUTER JOIN individus AS individu2 ON (individu2.id = auteur2.individu_id)
GROUP BY individu1.id, individu2.id;
"""


class DossierStatsDetail(PublishedDetailView):
    model = Dossier
    template_name = 'dossiers/dossier_stats_detail.html'
    n_auteurs = 30

    @cached_property
    def kind(self):
        kind = self.kwargs['kind']
        if kind not in STATS_KINDS:
            raise Http404
        return kind

    def get_object(self, queryset=None):
        dossier = super().get_object(queryset=queryset)
        if not dossier.has_kind(self.kind):
            raise Http404
        return dossier

    def get_oeuvres_par_periode(self, oeuvres_qs):
        try:
            oeuvres_sql, oeuvres_params = get_raw_query(
                oeuvres_qs.order_by().values('pk'))
        except EmptyResultSet:
            return ()

        conditions = [
            'WHEN year >= %s AND year < %s THEN %s'
            % (min_year, max_year, k)
            for k, (min_year, max_year) in PERIODS.items()]
        conditions.insert(
            0, 'WHEN year IS NULL THEN %s' % DEFAULT_PERIOD)
        sql = """
        SELECT
            CASE %s END AS period,
            COUNT(oeuvre_id)
        FROM (
            SELECT
                extract(YEAR FROM MIN(individu.naissance_date)) AS year,
                oeuvre.id AS oeuvre_id
            FROM (%s) AS oeuvre
            INNER JOIN libretto_auteur AS auteur
                ON (auteur.oeuvre_id = oeuvre.id)
            INNER JOIN libretto_individu AS individu
                ON (individu.id = auteur.individu_id)
            GROUP BY oeuvre.id
        ) AS years_and_ids
        GROUP BY period
        ORDER BY period;
        """ % (' '.join(conditions), oeuvres_sql)

        with connection.cursor() as cursor:
            cursor.execute(sql, oeuvres_params)
            data = cursor.fetchall()
        return [(PERIOD_NAMES[k], PERIOD_COLORS[k], PERIOD_TEXT_COLORS[k],
                 count)
                for k, count in data]

    def get_individus(self):
        """Authors involved in the visualised queryset, one row per
        involvement so the annotate below ranks them by popularity."""
        if self.kind == KIND_EVENEMENTS:
            return self.object.queryset_for(KIND_EVENEMENTS).individus_auteurs()
        return Individu.objects.filter(
            auteurs__oeuvre__in=self.object.queryset_for(KIND_OEUVRES),
        ).distinct()

    def update_context_with_chord_diagram(self, context):
        objects = self.object.queryset_for(self.kind)
        individus = self.get_individus()

        n_auteurs = self.n_auteurs
        n_individus = individus.count()
        if n_individus == 0:
            return

        if n_individus == n_auteurs + 1:
            n_auteurs = n_individus

        individus_par_popularite = individus.annotate(
            n=Count('pk')).order_by('-n')
        individus_pks = [
            pk for pk, k in
            individus_par_popularite.values_list('pk', 'n')[:n_auteurs]]
        individus = Individu.objects.filter(
            pk__in=individus_pks).order_by('naissance_date')
        objects = objects.order_by().values('pk')
        OBJECTS_SQL, OBJECTS_PARAMS = get_raw_query(objects)
        INDIVIDUS_SQL, INDIVIDUS_PARAMS = get_raw_query(
            individus.order_by().values('pk'))

        chord_sql = (CHORD_DIAGRAM_SQL if self.kind == KIND_EVENEMENTS
                     else WORKS_CHORD_DIAGRAM_SQL)
        with connection.cursor() as cursor:
            cursor.execute(chord_sql % (INDIVIDUS_SQL, OBJECTS_SQL),
                           INDIVIDUS_PARAMS + OBJECTS_PARAMS)
            data = cursor.fetchall()

        if len(data) < 3:
            return

        has_autres = False
        pre_matrix = {}
        for id1, id2, k in data:
            has_autres |= id1 is None or id2 is None
            pre_matrix[(id1, id2)] = k

        individus = list(individus)
        if has_autres:
            individus.append(
                Individu(nom='%d autres auteurs' % (n_individus - n_auteurs)))

        matrix = []
        for individu1 in individus:
            row = []
            matrix.append(row)
            for individu2 in individus:
                row.append(pre_matrix.get((individu1.pk, individu2.pk), 0))

        colors = []
        for individu in individus:
            year = (None if individu.naissance_date is None
                    else individu.naissance_date.year)
            if year is None:
                colors.append(PERIOD_COLORS[DEFAULT_PERIOD])
                continue
            for k, (min_year, max_year) in PERIODS.items():
                if min_year <= year < max_year:
                    colors.append(PERIOD_COLORS[k])
                    break
        colors_by_period = []
        for k, (min_year, max_year) in PERIODS.items():
            color = PERIOD_COLORS[k]
            if color in colors:
                colors_by_period.append((min_year, max_year,
                                         color, PERIOD_NAMES[k]))

        context.update(
            matrix=matrix, individus=individus,
            colors=colors, colors_by_period=colors_by_period)

    def get_context_data(self, **kwargs):
        context = super(DossierStatsDetail,
                        self).get_context_data(**kwargs)

        evenements_par_territoire = None
        if self.kind == KIND_EVENEMENTS:
            ensemble = None
            ensembles = list(self.object.ensembles.all())
            if len(ensembles) == 1:
                ensemble = ensembles[0]
            else:
                saisons = list(self.object.saisons.all())
                if len(saisons) == 1:
                    ensemble = saisons[0].ensemble

            evenements_par_territoire = (
                None if ensemble is None
                else ensemble.evenements_par_territoire(
                    evenements_qs=self.object.queryset_for(KIND_EVENEMENTS)))
            oeuvres_qs = self.object.queryset_for(KIND_EVENEMENTS).oeuvres()
        else:
            oeuvres_qs = self.object.queryset_for(KIND_OEUVRES)

        oeuvres_par_periode = self.get_oeuvres_par_periode(oeuvres_qs)
        n_oeuvres = sum([count for _, _, _, count in oeuvres_par_periode])
        context.update(
            MAX_MIN_PLACES=MAX_MIN_PLACES,
            DEFAULT_MIN_PLACES=DEFAULT_MIN_PLACES,
            kind=self.kind,
            evenements_par_territoire=evenements_par_territoire,
            oeuvres_par_periode=oeuvres_par_periode,
            n_oeuvres=n_oeuvres,
            # Unit shown in the chord tooltips: pairs share events on an
            # events dossier, works on a works dossier.
            chord_unit=(_('événements') if self.kind == KIND_EVENEMENTS
                        else _('œuvres')),
            geojson_url=reverse('dossier_data_geojson',
                                kwargs={'slug': self.object.slug,
                                        'kind': self.kind}),
        )
        self.update_context_with_chord_diagram(context)
        return context


class DossierViewMixin:
    success_view_name = 'dossier_data_detail'
    enable_default_page = False
    kind = None

    def __init__(self, *args, dossier=None, **kwargs):
        super().__init__(*args, **kwargs)
        if dossier is not None:
            self.dossier = dossier

    @cached_property
    def dossier(self):
        if 'dossier' in self.kwargs:
            return self.kwargs['dossier']

        lookup = {key: value for key, value in self.kwargs.items()
                  if key in ('slug', 'pk')}
        dossier = get_object_or_404(Dossier, **lookup)
        if not dossier.can_be_viewed(self.request):
            raise PermissionDenied
        if self.kind is not None and not dossier.has_kind(self.kind):
            raise Http404
        return dossier

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['object'] = data['dossier'] = self.dossier
        return data

    def get_success_url(self):
        kwargs = {'slug': self.dossier.slug}
        if 'kind' in self.kwargs:
            kwargs['kind'] = self.kwargs['kind']
        return reverse(self.success_view_name, kwargs=kwargs)


class DossierDataDetail(DossierViewMixin, View):
    def get_child_view(self):
        return {
            KIND_EVENEMENTS: DossierEvenementsDataDetail,
            KIND_OEUVRES: DossierOeuvresDataDetail,
            KIND_SOURCES: DossierSourcesDataDetail,
        }[self.kwargs['kind']]

    def dispatch(self, request, *args, **kwargs):
        if not self.dossier.has_kind(self.kwargs['kind']):
            raise Http404
        view = self.get_child_view().as_view()
        view.view_initkwargs['dossier'] = self.dossier
        return view(request, *args, **kwargs)


class DossierEvenementsViewMixin(DossierViewMixin):
    kind = KIND_EVENEMENTS

    def get_queryset(self):
        return super().get_queryset(
            base_filter=Q(pk__in=self.dossier.queryset_for(KIND_EVENEMENTS)))

    # Always reverse the slug-based routes: the page may have been reached
    # through its permanent (pk) URL, whose kwargs would not match here.

    def get_export_url(self):
        return reverse('dossier_data_export',
                       kwargs={'slug': self.dossier.slug,
                               'kind': KIND_EVENEMENTS})

    def get_geojson_url(self):
        return reverse('dossier_data_geojson',
                       kwargs={'slug': self.dossier.slug,
                               'kind': KIND_EVENEMENTS})


class DossierEvenementsDataDetail(DossierEvenementsViewMixin,
                                  AjaxListView, BaseEvenementListView):
    template_name = 'dossiers/dossier_evenements_data_detail.html'


class DossierEvenementsDataExport(DossierEvenementsViewMixin,
                                  EvenementExport):
    pass


class DossierEvenementsDataGeoJson(DossierEvenementsViewMixin,
                                   EvenementGeoJson):
    pass


class DossierOeuvresDataGeoJson(DossierViewMixin, TemplateView):
    """GeoJSON of the dossier's works, aggregated by world-premiere place,
    mirroring what ``EvenementGeoJson`` does with the events' opening places."""
    kind = KIND_OEUVRES
    template_name = 'dossiers/oeuvre_list.geojson'
    content_type = 'application/json'

    def get_context_data(self, **kwargs):
        from django.contrib.gis.geos import Polygon

        context = super().get_context_data(**kwargs)
        bbox = self.request.GET.get('bbox')
        if bbox is not None:
            bbox = Polygon.from_bbox([float(coord)
                                      for coord in bbox.split(',')])
        min_places = self.request.GET.get('min_places',
                                          str(DEFAULT_MIN_PLACES))
        min_places = (int(min_places) if min_places.isdigit()
                      else DEFAULT_MIN_PLACES)
        context.update(
            oeuvres=self.dossier.queryset_for(KIND_OEUVRES)
                        .published(self.request),
            bbox=bbox,
            min_places=min(min_places, MAX_MIN_PLACES),
        )
        return context


class DossierDataGeoJson(View):
    """Kind-scoped map data: events by opening place, works by
    world-premiere place."""

    def dispatch(self, request, *args, **kwargs):
        kind = kwargs['kind']
        if kind == KIND_EVENEMENTS:
            view = DossierEvenementsDataGeoJson.as_view()
        elif kind == KIND_OEUVRES:
            view = DossierOeuvresDataGeoJson.as_view()
        else:
            raise Http404
        return view(request, *args, **kwargs)


class DossierSourcesDataDetail(DossierViewMixin, PublishedListView):
    kind = KIND_SOURCES
    model = Source
    context_object_name = 'sources'
    template_name = 'dossiers/dossier_sources_data_detail.html'

    def get_queryset(self):
        return self.dossier.queryset_for(KIND_SOURCES)


class DossierDetailXeLaTeX(DossierDetail):
    def get_object(self, queryset=None):
        if not self.request.user.is_authenticated:
            raise PermissionDenied
        return super(DossierDetailXeLaTeX, self).get_object(queryset)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        launch_export(dossier_to_pdf, request, self.object.pk, 'PDF',
                      'du dossier « %s »' % self.object)
        return redirect(self.object.get_absolute_url())


class DossierScenario(DossierDetail):
    def get_object(self, queryset=None):
        if not self.request.user.is_authenticated:
            raise PermissionDenied
        return super(DossierScenario, self).get_object(queryset)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ScenarioFormSet(data=request.POST)
        if form.is_valid():
            data = {
                'dossier': self.object.pk,
                'scenarios': form.cleaned_data
            }
            launch_export(dossier_to_xlsx, request, data, 'XLSX',
                          '%s' % self.object)
        return redirect(self.object.get_absolute_url())


class DossierOeuvresDataDetail(DossierViewMixin, PublishedListView):
    kind = KIND_OEUVRES
    model = Oeuvre
    context_object_name = 'oeuvres'
    template_name = 'dossiers/dossier_oeuvres_data_detail.html'

    def get_queryset(self):
        qs = self.dossier.queryset_for(KIND_OEUVRES).select_related(
            'genre', 'creation_lieu__parent__nature', 'creation_lieu__nature'
        ).prefetch_related(
            'auteurs__individu', 'auteurs__profession',
        )
        if self.request.GET.get('order_by') == 'creation_date':
            return qs.order_by('creation_date')
        return qs.order_by(*Oeuvre._meta.ordering)


class DossierLegacyDataRedirect(View):
    """Permanent redirects from the pre-merge, kind-less sub-resource URLs
    (``…/data``, ``…/stats``, ``…/geojson``, ``…/export``) to their kind-scoped
    equivalents, so old links keep working."""
    view_name = 'dossier_data_detail'
    # Route kind: None picks the dossier's first active kind (data lists);
    # the pre-merge stats/geojson/export routes only ever served events.
    kind = None

    def get(self, request, *args, **kwargs):
        lookup = {key: value for key, value in kwargs.items()
                  if key in ('slug', 'pk')}
        dossier = get_object_or_404(Dossier, **lookup)
        kind = self.kind
        if kind is None:
            kinds = dossier.active_kinds
            if not kinds:
                raise Http404
            kind = kinds[0]
        url = reverse(self.view_name, kwargs={**lookup, 'kind': kind})
        query = request.GET.urlencode(safe='|')
        return redirect(f'{url}?{query}' if query else url, permanent=True)
