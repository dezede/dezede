# coding: utf-8

from __future__ import unicode_literals
from collections import OrderedDict
from datetime import date
from django.db.models import get_model, Q, FieldDoesNotExist
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect
from django.utils.encoding import force_text
from django.views.generic import ListView, DetailView, TemplateView
from endless_pagination.views import AjaxListView
from eztables.forms import DatatablesForm
from eztables.views import DatatablesView
from haystack.query import SearchQuerySet
from polymorphic import PolymorphicQuerySet
from viewsets import ModelViewSet
from libretto.models.functions import href
from .models import *
from .models.common import PublishedQuerySet
from .forms import *


__all__ = (b'PublishedDetailView', b'PublishedListView',
           b'EvenementListView', b'EvenementDetailView',
           b'SourceViewSet', b'PartieViewSet', b'ProfessionViewSet',
           b'LieuViewSet', b'IndividuViewSet', b'OeuvreViewSet')


class PublishedDetailView(DetailView):
    def get_queryset(self):
        qs = super(PublishedDetailView, self).get_queryset()
        if isinstance(qs, PolymorphicQuerySet):
            qs = qs.non_polymorphic()
        return qs.published(request=self.request)


class PublishedListView(ListView):
    has_frontend_admin = False

    def get_queryset(self):
        qs = super(PublishedListView, self).get_queryset()
        if self.has_frontend_admin:
            qs = qs.select_related('owner', 'etat')
        return qs.published(request=self.request) \
                 .order_by(*self.model._meta.ordering)


class EvenementListView(AjaxListView, PublishedListView):
    model = Evenement
    context_object_name = 'evenements'
    view_name = 'evenements'
    has_frontend_admin = True

    BINDINGS = {
        'lieu': ('ancrage_debut__lieu__in', 'ancrage_fin__lieu__in'),
        'oeuvre': 'programme__oeuvre__in',
        'individu': ('distribution__individus__in',
                     'programme__distribution__individus__in',
                     'programme__oeuvre__auteurs__individu__in'),
    }

    @classmethod
    def get_filters(cls, data):
        filters = Q()
        for key, value in data.items():
            if not value or key not in cls.BINDINGS:
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
            if value:
                accessors = cls.BINDINGS[key]
                if not isinstance(accessors, (tuple, list)):
                    accessors = [accessors]
                subfilter = Q()
                for accessor in accessors:
                    subfilter |= Q(**{accessor: value})
                filters &= subfilter
        return filters

    def get_queryset(self, base_filter=None):
        qs = super(EvenementListView, self).get_queryset()
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

        if not self.valid_form:
            return qs

        search_query = data.get('q')
        if search_query:
            sqs = SearchQuerySet().models(self.model)
            sqs = sqs.auto_query(search_query)
            # Le slicing est là pour compenser un bug de haystack, qui va
            # chercher les valeurs par paquets de 10, faisant parfois ainsi
            # des centaines de requêtes à elasticsearch.
            pk_list = sqs.values_list('pk', flat=True)[:10 ** 6]
            qs = qs.filter(pk__in=pk_list)

        filters = self.get_filters(data)
        qs = qs.filter(filters).distinct()
        try:
            start, end = int(data.get('dates_0')), int(data.get('dates_1'))
            qs = qs.filter(ancrage_debut__date__range=(
                date(start, 1, 1), date(end, 12, 31)))
        except (TypeError, ValueError):
            pass
        return qs

    def get_context_data(self, **kwargs):
        context = super(EvenementListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

    def get_success_view(self):
        return self.view_name,

    def get_cleaned_GET(self):
        new_qd = self.request.GET.copy()
        for k, v in new_qd.items():
            if not v or v == '|':
                del new_qd[k]
        return new_qd

    def get(self, request, *args, **kwargs):
        response = super(EvenementListView, self).get(request, *args, **kwargs)
        new_GET = self.get_cleaned_GET()
        if new_GET.dict() != self.request.GET.dict() or not self.valid_form:
            response = redirect(*self.get_success_view())
            if self.valid_form:
                response['Location'] += '?' + new_GET.urlencode(safe=b'|')
        return response


class EvenementDetailView(PublishedDetailView):
    model = Evenement


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


class CommonDatatablesView(DatatablesView):
    undefined_str = '−'
    link_on_column = 0

    def process_dt_response(self, data):
        self.form = DatatablesForm(data)
        if self.form.is_valid():
            self.object_list = self.get_queryset()
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
        pk_list = sqs.values_list('pk', flat=True)[:10 ** 6]
        return queryset.filter(pk__in=pk_list)

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

    def __init__(self):
        fields = OrderedDict(self.table_fields)
        self.views[b'list_view'][b'kwargs'] = {b'fields': fields}
        self.views[b'list_view_data'][b'kwargs'] = {
            b'model': self.model, b'fields': fields}
        super(CommonViewSet, self).__init__()


class GETDetailView(PublishedDetailView):
    def get_object(self, queryset=None):
        try:
            pk = int(self.request.REQUEST[b'pk'])
        except (KeyError, ValueError):
            raise Http404
        self.kwargs[self.pk_url_kwarg] = pk
        return super(GETDetailView, self).get_object(queryset=queryset)


class SourceViewSet(CommonViewSet):
    model = Source
    base_url_name = b'source'
    excluded_views = (b'list_view', b'detail_view')

    def __init__(self):
        self.views[b'content_view'] = {
            b'view': GETDetailView,
            b'pattern': br'content',
            b'name': b'content',
            b'kwargs': {
                b'template_name': 'libretto/source_ajax_content.html'
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
        ('ancrage_naissance', 'ancrage_naissance'),
        ('ancrage_deces', 'ancrage_deces')
    )


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
    )

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
            children = children.published(self.request)

        context.update(children=children, attr=self.kwargs['attr'])
        return context

    def get(self, request, *args, **kwargs):
        self.model = get_model('libretto', self.kwargs['model_name'])
        if 'node' in self.request.GET:
            self.kwargs['pk'] = self.request.GET['node']
        try:
            self.object = self.get_object()
        except AttributeError:
            self.object = None
        context = self.get_context_data()
        return self.render_to_response(context)
