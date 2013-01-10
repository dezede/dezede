# coding: utf-8

from __future__ import unicode_literals
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.views.generic import ListView, DetailView
from endless_pagination.views import AjaxListView
from .models import *
from .forms import *
from .tables import OeuvreTable, IndividuTable, ProfessionTable, PartieTable
from django_tables2 import SingleTableView
from haystack.query import SearchQuerySet
from django.db.models import get_model
from datetime import date


class SourceDetailView(DetailView):
    model = Source
    context_object_name = 'source'


def cleaned_querydict(qd):
    new_qd = qd.copy()
    for k, v in new_qd.iteritems():
        if not v or v == '|':
            del new_qd[k]
    return new_qd


def get_filters(bindings, data):
    filters = {}
    for key, value in data.iteritems():
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
                for object in objects:
                    if hasattr(object, 'get_descendants'):
                        objects.extend(object.get_descendants())
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
                response['Location'] += '?' + new_data.urlencode(safe='|')
        return response


class EvenementDetailView(DetailView):
    model = Evenement


class PartieListView(SingleTableView):
    model = Partie
    table_class = PartieTable
    template_name = 'catalogue/tableau.html'


class PartieDetailView(DetailView):
    model = Partie


class ProfessionListView(SingleTableView):
    model = Profession
    table_class = ProfessionTable
    template_name = 'catalogue/tableau.html'


class ProfessionDetailView(DetailView):
    model = Profession
    context_object_name = 'profession'


class LieuListView(ListView):
    model = Lieu
    context_object_name = 'lieux'


class LieuDetailView(DetailView):
    model = Lieu
    context_object_name = 'lieu'


class IndividuListView(SingleTableView):
    model = Individu
    table_class = IndividuTable
    template_name = 'catalogue/tableau.html'


class IndividuDetailView(DetailView):
    model = Individu
    context_object_name = 'individu'


class OeuvreListView(SingleTableView):
    model = Oeuvre
    table_class = OeuvreTable
    template_name = 'catalogue/tableau.html'


class OeuvreDetailView(DetailView):
    model = Oeuvre
    context_object_name = 'oeuvre'


def saisie_source(request, source_id=None):
    if source_id is not None:
        source = get_object_or_404(Source, pk=source_id)
    else:
        source = None
    if request.method == 'POST':
        form = SourceForm(request.POST, instance=source)
        if form.is_valid():
            form.save()
            return redirect('saisie_sources')
    else:
        form = SourceForm(instance=source)
    c = RequestContext(
            request,
            {
                'form': form,
                'sources': Source.objects.all(),
                'source': source,
            }
        )
    return render_to_response('catalogue/saisie_source.html', c)
