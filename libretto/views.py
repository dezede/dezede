import re

from django.apps import apps
from django.contrib.gis.geos import Polygon
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView
from el_pagination.views import AjaxListView
from haystack.query import SearchQuerySet
from tree.query import TreeQuerySetMixin
from viewsets.model import ModelViewSet

from common.utils.export import launch_export
from common.utils.text import to_roman
from tablature.views import TableView
from .jobs import events_to_csv, events_to_xlsx, events_to_json
from .models import *
from .models.base import PublishedQuerySet
from .forms import *


__all__ = (
    'PublishedDetailView', 'PublishedListView',
    'EvenementListView', 'EvenementGeoJson', 'EvenementDetailView',
    'SourceViewSet', 'PartieViewSet', 'ProfessionViewSet',
    'LieuViewSet', 'IndividuViewSet', 'OeuvreViewSet'
)


DEFAULT_MIN_PLACES = 10
MAX_MIN_PLACES = 100


class PublishedMixin(object):
    has_frontend_admin = False

    def get_queryset(self):
        qs = super(PublishedMixin, self).get_queryset()
        if self.has_frontend_admin:
            qs = qs.select_related('owner', 'etat')
        return qs.published(request=self.request) \
                 .order_by(*self.model._meta.ordering)


class PublishedDetailView(PublishedMixin, DetailView):
    pass


class PublishedListView(PublishedMixin, ListView):
    pass


class BaseEvenementListView(PublishedListView):
    model = Evenement
    context_object_name = 'evenements'
    view_name = 'evenements'
    has_frontend_admin = True
    enable_default_page = True
    filter_re = re.compile(r'^\|?\d+(?:\|\d+)*\|?$')

    BINDINGS = {
        'lieu': ('debut_lieu__in', 'fin_lieu__in'),
        'oeuvre': 'programme__oeuvre__in',
        'individu': ('distribution__individu__in',
                     'programme__distribution__individu__in',
                     'programme__oeuvre__auteurs__individu__in'),
        'ensemble': ('distribution__ensemble__in',
                     'programme__distribution__ensemble__in',
                     'programme__oeuvre__auteurs__ensemble__in'),
        'source': ('sources__in',),
    }

    @classmethod
    def get_filters(cls, data):
        filters = Q()
        for key, value in data.items():
            if key not in cls.BINDINGS:
                continue
            # Sépare les différents objets à partir d'une liste de pk.
            Model = apps.get_model('libretto', key)
            pk_list = value.strip('|').split('|')
            objects = Model._default_manager.filter(pk__in=pk_list)
            # Inclus tous les événements impliquant les descendants
            # éventuels de chaque objet de value.
            if isinstance(objects, TreeQuerySetMixin):
                objects = objects.get_descendants(include_self=True)
            value = objects
            if value.exists():
                accessors = cls.BINDINGS[key]
                if not isinstance(accessors, (tuple, list)):
                    accessors = [accessors]
                subfilter = Q()
                for accessor in accessors:
                    subfilter |= Q(**{accessor: value})
                filters &= subfilter
        return filters

    def get_queryset(self, base_filter=None):
        qs = super(BaseEvenementListView, self).get_queryset()
        if base_filter is not None:
            qs = qs.filter(base_filter)

        data = self.request.GET
        self.form = EvenementListForm(data, queryset=qs)
        try:
            self.valid_form = self.form.is_valid()
        except:
            self.form = EvenementListForm(queryset=qs)
            self.valid_form = False
            data = {}
        if self.enable_default_page and not data:
            self.default_page = True
            return qs.none()
        else:
            self.default_page = False

        if not self.valid_form:
            return qs

        search_query = data.get('q')
        if search_query:
            sqs = SearchQuerySet().models(self.model)
            sqs = sqs.auto_query(search_query)
            qs = qs.filter(pk__in=sqs.values_list('pk', flat=True))

        filters = self.get_filters(data)
        qs = qs.filter(filters).distinct()
        try:
            start, end = int(data.get('dates_0')), int(data.get('dates_1'))
            if data.get('par_saison', 'False') == 'True':
                qs &= Saison.objects.between_years(start, end).evenements()
            else:
                qs = qs.filter(debut_date__range=(f'{start}-1-1',
                                                  f'{end}-12-31'))
        except (TypeError, ValueError):
            pass

        if data.get('order_by') == 'reversed':
            qs = qs.reverse()

        return qs

    def get_export_url(self):
        return reverse('evenements_export')

    def get_geojson_url(self):
        return reverse('evenements_geojson')

    def get_context_data(self, **kwargs):
        context = super(BaseEvenementListView, self).get_context_data(**kwargs)
        context.update(
            form=self.form,
            default_page=self.default_page,
            by_season=(self.request.GET.get('par_saison', 'False') == 'True'),
            export_url=self.get_export_url(),
            geojson_url=self.get_geojson_url(),
            DEFAULT_MIN_PLACES=DEFAULT_MIN_PLACES,
            MAX_MIN_PLACES=MAX_MIN_PLACES,
        )
        return context

    def get_success_url(self):
        return reverse(self.view_name)

    def get_cleaned_GET(self):
        new_qd = self.request.GET.copy()
        for k, v in tuple(new_qd.items()):
            if not v:
                del new_qd[k]
            elif k in self.BINDINGS and self.filter_re.match(v) is None:
                del new_qd[k]
        return new_qd

    def get(self, request, *args, **kwargs):
        new_GET = self.get_cleaned_GET()
        if new_GET.dict() != self.request.GET.dict():
            return HttpResponseRedirect('?' + new_GET.urlencode(safe='|'))
        return super(BaseEvenementListView, self).get(request, *args, **kwargs)


class EvenementListView(AjaxListView, BaseEvenementListView):
    pass


class EvenementExport(BaseEvenementListView):
    def get_queryset(self, base_filter=None):
        if not self.request.user.is_authenticated():
            raise PermissionDenied
        qs = super(EvenementExport, self).get_queryset(base_filter=base_filter)
        if self.request.user.is_superuser:
            return qs
        return qs.filter(owner=self.request.user)

    def get_cleaned_GET(self):
        query_dict = super(EvenementExport, self).get_cleaned_GET()
        del query_dict['format']
        return query_dict

    def get(self, request, *args, **kwargs):
        if 'format' not in request.GET:
            raise Http404
        export_format = request.GET['format']
        jobs = {'csv': events_to_csv, 'xlsx': events_to_xlsx,
                'json': events_to_json}
        pk_list = list(self.get_queryset().values_list('pk', flat=True))
        if self.valid_form and export_format in jobs:
            launch_export(jobs[export_format], request, pk_list,
                          export_format, _('de %s événements') % len(pk_list))
        return redirect(self.get_success_url()
                        + '?' + self.get_cleaned_GET().urlencode())


class EvenementGeoJson(BaseEvenementListView):
    template_name = 'libretto/lieu_list.geojson'
    content_type = 'application/json'

    def get_context_data(self, **kwargs):
        context = super(EvenementGeoJson, self).get_context_data(**kwargs)
        bbox = self.request.GET.get('bbox')
        if bbox is not None:
            bbox = Polygon.from_bbox([float(coord)
                                      for coord in bbox.split(',')])
        context['bbox'] = bbox
        min_places = self.request.GET.get('min_places',
                                          str(DEFAULT_MIN_PLACES))
        min_places = (int(min_places) if min_places.isdigit()
                      else DEFAULT_MIN_PLACES)
        context['min_places'] = min(min_places, MAX_MIN_PLACES)
        return context


class EvenementDetailView(PublishedDetailView):
    model = Evenement

    def get_queryset(self):
        qs = super(EvenementDetailView, self).get_queryset()
        return qs.prefetch_all(create_subquery=False)


class CommonTableView(TableView):
    def search(self, queryset, q):
        if not q:
            return queryset
        sqs = SearchQuerySet().models(self.model).auto_query(q)
        pk_list = [r.pk for r in sqs[:10 ** 6]]
        return queryset.filter(pk__in=pk_list)


class CommonViewSet(ModelViewSet):
    list_view = CommonTableView
    views = {
        'list_view': {
            'view': None,
            'pattern': r'',
            'name': 'index',
        },
        'detail_view': {
            'view': PublishedDetailView,
            'pattern': r'(?P<slug>[\w-]+)/',
            'name': 'detail',
        },
        'permanent_detail_view': {
            'view': PublishedDetailView,
            'pattern': r'id/(?P<pk>\d+)/',
            'name': 'permanent_detail',
        },
    }

    def __init__(self):
        self.views['list_view']['view'] = self.list_view
        super(CommonViewSet, self).__init__()


CENTURIES = tuple(range(11, 22))

CENTURIES_VERBOSES = [
    (str(i), to_roman(i) + force_text(_('<sup>e</sup> siècle')))
    for i in CENTURIES
][::-1]

CENTURIES_DATE_RANGES = {
    f'{i}': (f'{i-1}00-1-1', f'{i-1}99-12-31') for i in CENTURIES
}


class SourceTableView(PublishedMixin, CommonTableView):
    model = Source
    columns = ('icons', 'html', 'ancrage', 'type')
    columns_widths = {
        'icons': '70px',
        'html': '599px',
        'ancrage': '130px',
        'type': '140px',
    }
    verbose_columns = {
        'icons': _('Type de contenu'),
        'html': _('Titre'),
        'ancrage': _('Date'),
    }
    orderings = {'ancrage': 'date'}
    filters = {
        'icons': Source.DATA_TYPES_WITH_ICONS,
        'ancrage': CENTURIES_VERBOSES,
        'type': TypeDeSource.objects.values_list('pk', 'nom')
    }
    queryset = Source.objects.prefetch()

    def filter_ancrage(self, queryset, value):
        return queryset.filter(date__range=CENTURIES_DATE_RANGES[value])

    def filter_icons(self, queryset, value):
        return Source.objects.filter(
            pk__in=queryset.with_data_type(value)).prefetch()


class SourceModalView(PublishedDetailView):
    def get(self, request, *args, **kwargs):
        if not request.is_ajax():
            return redirect('source_permanent_detail', kwargs['pk'])
        return super(SourceModalView, self).get(request, *args, **kwargs)


class SourceViewSet(CommonViewSet):
    model = Source
    base_url_name = 'source'
    excluded_views = ('detail_view',)
    list_view = SourceTableView

    def __init__(self):
        self.views['content_view'] = {
            'view': SourceModalView,
            'pattern': r'modal/(?P<pk>\d+)/',
            'name': 'modal',
            'kwargs': {
                'template_name': 'libretto/source_modal.html'
            },
        }
        super(SourceViewSet, self).__init__()


class PartieTableView(PublishedMixin, CommonTableView):
    model = Partie
    columns = ('html', 'type')
    columns_widths = {
        'html': '839px',
        'type': '100px',
    }
    verbose_columns = {'html': ''}
    orderings = {'html': 'nom'}
    filters = {'type': Partie.TYPES}


class PartieViewSet(CommonViewSet):
    model = Partie
    base_url_name = 'partie'
    list_view = PartieTableView


class ProfessionTableView(PublishedMixin, CommonTableView):
    model = Profession
    columns = ('html', 'individus_count', 'oeuvres_count')
    columns_widths = {
        'html': '639px',
        'individus_count': '150px',
        'oeuvres_count': '150px'
    }
    verbose_columns = {'html': ''}
    orderings = {'html': 'nom'}


class ProfessionViewSet(CommonViewSet):
    model = Profession
    base_url_name = 'profession'
    list_view = ProfessionTableView


class LieuViewSet(CommonViewSet):
    model = Lieu
    base_url_name = 'lieu'

    def __init__(self):
        super(LieuViewSet, self).__init__()
        self.views['list_view']['view'] = PublishedListView


class IndividuTableView(PublishedMixin, CommonTableView):
    model = Individu
    columns = ('related_label_html', 'calc_professions', 'naissance', 'deces')
    columns_widths = {
        'related_label_html': '300px',
        'calc_professions': '299px',
        'naissance': '170px',
        'deces': '170px',
    }
    verbose_columns = {'related_label_html': '',
                       'calc_professions': _('Profession(s)')}
    orderings = {
        'related_label_html': 'nom',
        'calc_professions': 'professions',
        'naissance': 'naissance_date',
        'deces': 'deces_date',
    }
    filters = {'naissance': CENTURIES_VERBOSES, 'deces': CENTURIES_VERBOSES}
    queryset = Individu.objects.select_related(
        'naissance_lieu', 'deces_lieu'
    ).prefetch_related('professions')

    def filter_naissance(self, queryset, value):
        return queryset.filter(
            naissance_date__range=CENTURIES_DATE_RANGES[value])

    def filter_deces(self, queryset, value):
        return queryset.filter(
            deces_date__range=CENTURIES_DATE_RANGES[value])


class IndividuViewSet(CommonViewSet):
    model = Individu
    base_url_name = 'individu'
    list_view = IndividuTableView


class EnsembleTableView(PublishedMixin, CommonTableView):
    model = Ensemble
    columns = ('html', 'type', 'siege')
    columns_widths = {
        'html': '559px',
        'type': '190px',
        'siege': '190px',
    }
    verbose_columns = {'html': ''}
    orderings = {'html': 'nom'}
    filters = {'type': TypeDEnsemble.objects.values_list('pk', 'nom')}
    values_per_filter = 20
    queryset = Ensemble.objects.select_related('type', 'siege')


class EnsembleViewSet(CommonViewSet):
    model = Ensemble
    base_url_name = 'ensemble'
    list_view = EnsembleTableView


class OeuvreTableView(PublishedMixin, CommonTableView):
    model = Oeuvre
    columns = ('titre_html', 'genre', 'auteurs_html', 'creation')
    columns_widths = {
        'titre_html': '299px',
        'genre': '120px',
        'auteurs_html': '280px',
        'creation': '240px',
    }
    verbose_columns = {'titre_html': '', 'creation': _('Genèse et création')}
    orderings = {
        'titre_html': 'titre',
        'auteurs_html': 'auteurs__individu',
        'creation': 'creation_date',
    }
    filters = {
        'creation': CENTURIES_VERBOSES
    }
    queryset = (
        Oeuvre.objects.filter(extrait_de=None)
        .select_related('genre', 'creation_lieu')
        .prefetch_related(
            'pupitres__partie',
            'auteurs__individu', 'auteurs__ensemble', 'auteurs__profession')
    )

    def filter_creation(self, queryset, value):
        return queryset.filter(
            creation_date__range=CENTURIES_DATE_RANGES[value])


class OeuvreViewSet(CommonViewSet):
    model = Oeuvre
    base_url_pattern = 'oeuvres'
    base_url_name = 'oeuvre'
    list_view = OeuvreTableView


class TreeNode(PublishedDetailView):
    template_name = 'routines/tree_node.json'

    def get_context_data(self, **kwargs):
        context = super(TreeNode, self).get_context_data(**kwargs)

        if self.object is None:
            children = self.model.get_roots()
        else:
            children = self.object.get_children()

        if isinstance(children, PublishedQuerySet):
            children = list(children.published(self.request))
            for child in children:
                child.is_leaf_node = not (child.get_children()
                                          .published(self.request).exists())

        context.update(children=children, attr=self.kwargs['attr'])
        return context

    def get(self, request, *args, **kwargs):
        app_label = self.kwargs['app_label']
        model_name = self.kwargs['model_name']

        # FIXME: Ceci est un hack laid pour gérer les DossierDEvenements
        #        enfants de CategorieDeDossiers.
        if app_label == 'dossiers' and model_name == 'categoriededossiers' \
                and 'node' in self.request.GET:
            model_name = 'dossierdevenements'

        self.model = apps.get_model(app_label, model_name)
        if 'node' in self.request.GET:
            self.kwargs['pk'] = self.request.GET['node']
        try:
            self.object = self.get_object()
        except AttributeError:
            self.object = None
        context = self.get_context_data()
        return self.render_to_response(context)
