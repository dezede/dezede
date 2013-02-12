# coding: utf-8

from __future__ import unicode_literals
from datetime import date
from django.db.models import get_model
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView
from endless_pagination.views import AjaxListView
from django_tables2 import SingleTableView
from haystack.query import SearchQuerySet
from viewsets import ModelViewSet
from .models import *
from .forms import *
from .tables import OeuvreTable, IndividuTable, ProfessionTable, PartieTable


__all__ = (b'EvenementListView', b'EvenementDetailView', b'SourceViewSet',
           b'PartieViewSet', b'ProfessionViewSet', b'LieuViewSet',
           b'IndividuViewSet', b'OeuvreViewSet')


def cleaned_querydict(qd):
    new_qd = qd.copy()
    for k, v in new_qd.items():
        if not v or v == '|':
            del new_qd[k]
    return new_qd


def get_filters(bindings, data):
    filters = {}
    for key, value in data.items():
        if value and key in bindings:
            if '|' in value:
                # Sépare les différents objets à partir d'une liste de pk.
                Model = get_model('catalogue', key)
                pk_list = value.split('|')
                objects = []
                for pk in pk_list:
                    if pk:
                        try:
                            objects.append(Model.objects.get(pk=pk))
                        except Model.DoesNotExist:
                            continue
                # Inclus tous les événements impliquant les descendants
                # éventuels de chaque objet de value.
                for obj in objects:
                    if hasattr(obj, 'get_descendants'):
                        objects.extend(obj.get_descendants())
                value = objects
            if value:
                filters[bindings[key]] = value
    return filters


class EvenementListView(AjaxListView):
    model = Evenement
    context_object_name = 'evenements'

    def get_queryset(self):
        Model = self.model
        qs = Model.objects.all()
        data = self.request.GET
        self.form = form = EvenementListForm(data)
        try:
            self.valid_form = form.is_valid()
        except:
            self.form = EvenementListForm()
            self.valid_form = False
            data = {}
        if self.valid_form:
            search_query = data.get('q')
            if search_query:
                sqs = SearchQuerySet().models(Model)
                sqs = sqs.auto_query(search_query)
                pk_list = sqs.values_list('pk', flat=True)
                qs = qs.filter(pk__in=pk_list)
            bindings = {
                'lieu': 'ancrage_debut__lieu__in',
                'oeuvre': 'programme__oeuvre__in',
            }
            filters = get_filters(bindings, data)
            qs = qs.filter(**filters).distinct()
            try:
                start, end = int(data.get('dates_0')), int(data.get('dates_1'))
                qs = qs.filter(ancrage_debut__date__gte=date(start, 1, 1),
                               ancrage_debut__date__lte=date(end, 12, 31))
            except (TypeError, ValueError):
                pass
        return qs

    def get_context_data(self, **kwargs):
        context = super(EvenementListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context

    def get(self, request, *args, **kwargs):
        response = super(EvenementListView, self).get(request, *args, **kwargs)
        data = self.request.GET
        new_data = cleaned_querydict(data)
        if new_data.dict() != data.dict() or not self.valid_form:
            response = redirect('evenements')
            if self.valid_form:
                response['Location'] += '?' + new_data.urlencode(safe=b'|')
        return response


class EvenementDetailView(DetailView):
    model = Evenement


class CommonViewSet(ModelViewSet):
    views = {
        b'list_view': {
            b'view': SingleTableView,
            b'pattern': br'',
            b'name': b'index',
            b'kwargs': {
                b'template_name': b'catalogue/tableau.html',
            },
        },
        b'detail_view': {
            b'view': DetailView,
            b'pattern': br'(?P<slug>[\w-]+)/',
            b'name': b'detail',
        },
        b'permanent_detail_view': {
            b'view': DetailView,
            b'pattern': br'id/(?P<pk>\d+)/',
            b'name': b'permanent_detail',
        },
    }
    table_class = None

    def __init__(self):
        if self.table_class is not None:
            self.views[b'list_view'][b'kwargs'][b'table_class'] \
                = self.table_class
        super(CommonViewSet, self).__init__()


class GETDetailView(DetailView):
    def get_object(self, queryset=None):
        pk = self.request.REQUEST.get(b'pk', None)
        if pk is None:
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
                b'template_name': 'catalogue/source_ajax_content.html'
            },
        }
        super(SourceViewSet, self).__init__()


class PartieViewSet(CommonViewSet):
    model = Partie
    base_url_name = b'partie'
    table_class = PartieTable


class ProfessionViewSet(CommonViewSet):
    model = Profession
    base_url_name = b'profession'
    table_class = ProfessionTable


class LieuViewSet(CommonViewSet):
    model = Lieu
    base_url_name = b'lieu'

    def __init__(self):
        super(LieuViewSet, self).__init__()
        self.views[b'list_view'][b'view'] = ListView
        del self.views[b'list_view'][b'kwargs']


class IndividuViewSet(CommonViewSet):
    model = Individu
    base_url_name = b'individu'
    table_class = IndividuTable


class OeuvreViewSet(CommonViewSet):
    model = Oeuvre
    base_url_pattern = b'oeuvres'
    base_url_name = b'oeuvre'
    table_class = OeuvreTable
