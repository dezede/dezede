# coding: utf-8

from __future__ import unicode_literals
from collections import OrderedDict

from django.contrib.gis.geos import Polygon
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import get_model, Q, FieldDoesNotExist
from django.db.models.query import QuerySet
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.encoding import force_text
from django.views.generic import ListView, DetailView, TemplateView
from endless_pagination.views import AjaxListView
from eztables.forms import DatatablesForm
from eztables.views import DatatablesView
from haystack.query import SearchQuerySet
from polymorphic import PolymorphicQuerySet
from viewsets import ModelViewSet

from common.utils.export import launch_export
from common.utils.html import href
from .jobs import events_to_csv, events_to_xlsx, events_to_json
from .models import *
from .models.base import PublishedQuerySet
from .forms import *


__all__ = (
    b'PublishedDetailView', b'PublishedListView',
    b'EvenementListView', b'EvenementGeoJson', b'EvenementDetailView',
    b'SourceViewSet', b'PartieViewSet', b'ProfessionViewSet',
    b'LieuViewSet', b'IndividuViewSet', b'OeuvreViewSet'
)


DEFAULT_MIN_PLACES = 10
MAX_MIN_PLACES = 100


class PublishedMixin(object):
    has_frontend_admin = False

    def get_queryset(self):
        qs = super(PublishedMixin, self).get_queryset()
        if isinstance(qs, PolymorphicQuerySet):
            qs = qs.non_polymorphic()
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

    BINDINGS = {
        'lieu': ('debut_lieu__in', 'fin_lieu__in'),
        'oeuvre': 'programme__oeuvre__in',
        'individu': ('distribution__individu__in',
                     'programme__distribution__individu__in',
                     'programme__oeuvre__auteurs__individu__in'),
        'ensemble': ('distribution__ensemble__in',
                     'programme__distribution__ensemble__in'),
        'source': ('sources__in',),
    }

    @classmethod
    def get_filters(cls, data):
        filters = Q()
        for key, value in data.items():
            if not value or value == '|' or key not in cls.BINDINGS:
                continue
            if '|' in value:
                # Sépare les différents objets à partir d'une liste de pk.
                Model = get_model('libretto', key)
                pk_list = [pk for pk in value.split('|') if pk]
                objects = Model._default_manager.filter(pk__in=pk_list)
                # Inclus tous les événements impliquant les descendants
                # éventuels de chaque objet de value.
                if hasattr(objects, 'get_descendants'):
                    objects = objects.get_descendants(include_self=True)
                value = objects
            if (isinstance(value, QuerySet) and value.exists()) or value:
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
            # Le slicing est là pour compenser un bug de haystack, qui va
            # chercher les valeurs par paquets de 10, faisant parfois ainsi
            # des centaines de requêtes à elasticsearch.
            # FIXME: Utiliser une values_list quand cette issue sera résolue :
            # https://github.com/toastdriven/django-haystack/issues/1019
            pk_list = [r.pk for r in sqs[:10**6]]
            qs = qs.filter(pk__in=pk_list)

        filters = self.get_filters(data)
        qs = qs.filter(filters).distinct()
        try:
            start, end = int(data.get('dates_0')), int(data.get('dates_1'))
            qs = qs.filter(debut_date__range=('%s-1-1' % start,
                                              '%s-12-31' % end))
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
        for k, v in new_qd.items():
            if not v or v == '|':
                del new_qd[k]
        return new_qd

    def get(self, request, *args, **kwargs):
        response = super(BaseEvenementListView, self).get(request, *args, **kwargs)
        new_GET = self.get_cleaned_GET()
        if new_GET.dict() != self.request.GET.dict() or not self.valid_form:
            response = HttpResponseRedirect(self.get_success_url())
            if self.valid_form:
                response['Location'] += '?' + new_GET.urlencode(safe=b'|')
        return response


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
        data = self.request.GET.copy()
        export_format = data.get('format')
        jobs = {'csv': events_to_csv, 'xlsx': events_to_xlsx,
                'json': events_to_json}
        pk_list = list(self.get_queryset().values_list('pk', flat=True))
        if self.valid_form and export_format in jobs:
            launch_export(jobs[export_format], request, pk_list,
                          export_format, 'de %s événements' % len(pk_list))
        return super(EvenementExport, self).get(request, *args, **kwargs)


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


class CommonTableView(TemplateView):
    template_name = 'libretto/tableau.html'
    fields = None
    model = None

    def _get_verbose_name(self, field):
        try:
            return self.model._meta.get_field(field).verbose_name
        except FieldDoesNotExist:
            try:
                return getattr(self.model, field).short_description
            except AttributeError:
                return field

    def get_context_data(self, **kwargs):
        context = super(CommonTableView, self).get_context_data(**kwargs)
        context.update(
            fields_verbose=[self._get_verbose_name(f) for f in self.fields],
            fieldnames=self.fields,
            model=self.model,
        )
        return context


class CommonDatatablesView(PublishedMixin, DatatablesView):
    undefined_str = '−'
    link_on_column = 0
    select_related = ()
    prefetch_related = ()

    def get_queryset(self):
        qs = super(CommonDatatablesView, self).get_queryset()
        return (qs.select_related(*self.select_related)
                .prefetch_related(*self.prefetch_related))

    def process_dt_response(self, data):
        self.form = DatatablesForm(data)
        if self.form.is_valid():
            self.object_list = self.get_queryset().order_by(*self.get_orders())
            return self.render_to_response(self.form)
        return HttpResponseBadRequest()

    def get_db_fields(self):
        raise NotImplementedError

    def _get_value(self, obj, attr):
        out = getattr(obj, attr)
        if callable(out):
            out = out()
        return force_text(out or self.undefined_str)

    def get_row(self, obj):
        out = {}
        for i, attr in enumerate(self.fields):
            v = self._get_value(obj, attr)
            if self.link_on_column is not None and i == self.link_on_column:
                v = href(obj.get_absolute_url(), v)
            out[attr] = v
        return out

    def global_search(self, queryset):
        q = self.dt_data['sSearch']
        if not q:
            return queryset
        sqs = SearchQuerySet().models(self.model).auto_query(q)
        # Le slicing est là pour compenser un bug de haystack, qui va
        # chercher les valeurs par paquets de 10, faisant parfois ainsi
        # des centaines de requêtes à elasticsearch.
        # FIXME: Utiliser une values_list quand cette issue sera résolue :
        #        https://github.com/toastdriven/django-haystack/issues/1019
        pk_list = [r.pk for r in sqs[:10**6]]
        return queryset.filter(pk__in=pk_list).order_by(*self.get_orders())

    def column_search(self, queryset):
        return queryset


class CommonViewSet(ModelViewSet):
    views = {
        b'list_view': {
            b'view': CommonTableView,
            b'pattern': br'',
            b'name': b'index',
        },
        b'list_view_data': {
            b'view': CommonDatatablesView,
            b'pattern': br'ajax',
            b'name': b'ajax',
        },
        b'detail_view': {
            b'view': PublishedDetailView,
            b'pattern': br'(?P<slug>[\w-]+)/',
            b'name': b'detail',
        },
        b'permanent_detail_view': {
            b'view': PublishedDetailView,
            b'pattern': br'id/(?P<pk>\d+)/',
            b'name': b'permanent_detail',
        },
    }
    table_fields = ()
    table_select_related = ()
    table_prefetch_related = ()

    def __init__(self):
        fields = OrderedDict(self.table_fields)
        self.views[b'list_view'][b'kwargs'] = {b'fields': fields}
        self.views[b'list_view_data'][b'kwargs'] = {
            b'model': self.model, b'fields': fields,
            b'select_related': self.table_select_related,
            b'prefetch_related': self.table_prefetch_related}
        super(CommonViewSet, self).__init__()


class SourceModalView(PublishedDetailView):
    def get(self, request, *args, **kwargs):
        is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
        if not is_ajax:
            return redirect('source_permanent_detail', kwargs['pk'])
        return super(SourceModalView, self).get(request, *args, **kwargs)


class SourceViewSet(CommonViewSet):
    model = Source
    base_url_name = b'source'
    excluded_views = (b'list_view', b'detail_view')

    def __init__(self):
        self.views[b'content_view'] = {
            b'view': SourceModalView,
            b'pattern': br'modal/(?P<pk>\d+)/',
            b'name': b'modal',
            b'kwargs': {
                b'template_name': 'libretto/source_modal.html'
            },
        }
        super(SourceViewSet, self).__init__()


class PartieViewSet(CommonViewSet):
    model = Partie
    base_url_name = b'partie'
    table_fields = (
        ('nom', 'nom'),
        ('interpretes_html', None),
    )


class ProfessionViewSet(CommonViewSet):
    model = Profession
    base_url_name = b'profession'
    table_fields = (
        ('nom', 'nom'),
        ('parent', 'parent'),
        ('individus_count', None),
        ('oeuvres_count', None),
    )


class LieuViewSet(CommonViewSet):
    model = Lieu
    base_url_name = b'lieu'

    def __init__(self):
        super(LieuViewSet, self).__init__()
        self.views[b'list_view'][b'view'] = PublishedListView
        del self.views[b'list_view'][b'kwargs']


class IndividuViewSet(CommonViewSet):
    model = Individu
    base_url_name = b'individu'
    table_fields = (
        ('related_label', '{nom} {prenoms}'),
        ('calc_professions', 'professions'),
        ('naissance', '{naissance_date}'),
        ('deces', '{deces_date}')
    )
    table_select_related = ('naissance_lieu', 'deces_lieu')
    table_prefetch_related = ('professions',)


class EnsembleViewSet(CommonViewSet):
    model = Ensemble
    base_url_name = b'ensemble'
    table_fields = (
        ('nom', 'nom'),
        ('membres_html', 'membres'),
    )


class OeuvreTableView(CommonTableView):
    def get_queryset(self):
        return super(OeuvreTableView,
                     self).get_queryset().filter(contenu_dans=None)


class OeuvreViewSet(CommonViewSet):
    model = Oeuvre
    base_url_pattern = b'oeuvres'
    base_url_name = b'oeuvre'
    table_fields = (
        ('_str', '{titre} {genre}'),
        ('genre', 'genre'),
        ('auteurs_html', 'auteurs__individu'),
        ('creation', '{creation_date}'),
    )
    table_select_related = (
        'genre', 'creation_lieu')
    table_prefetch_related = (
        'caracteristiques__type', 'auteurs__individu', 'auteurs__profession')

    def __init__(self):
        super(OeuvreViewSet, self).__init__()
        self.views[b'list_view'][b'view'] = OeuvreTableView


class TreeNode(PublishedDetailView):
    template_name = 'routines/tree_node.json'

    def get_context_data(self, **kwargs):
        context = super(TreeNode, self).get_context_data(**kwargs)

        if self.object is None:
            children = self.model._tree_manager.root_nodes()
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

        self.model = get_model(app_label, model_name)
        if 'node' in self.request.GET:
            self.kwargs['pk'] = self.request.GET['node']
        try:
            self.object = self.get_object()
        except AttributeError:
            self.object = None
        context = self.get_context_data()
        return self.render_to_response(context)
