from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.views.generic import ListView, DetailView
from endless_pagination.views import AjaxListView
from .models import *
from .forms import *
from .tables import OeuvreTable, IndividuTable, ProfessionTable, PartieTable
from django_tables2 import SingleTableView
from haystack.query import SearchQuerySet


class SourceDetailView(DetailView):
    model = Source
    context_object_name = 'source'


class EvenementListView(AjaxListView):
    model = Evenement
    context_object_name = 'evenements'

    def get_queryset(self):
        Model = self.model
        qs = Model.objects.all()
        data = self.request.GET
        self.form = EvenementListForm(data)
        search_query = data.get('q')
        if search_query:
            sqs = SearchQuerySet().models(Model)
            sqs = sqs.auto_query(search_query)
            pk_list = sqs.values_list('pk', flat=True)
            qs = qs.filter(pk__in=pk_list)
        bindings = {
          'lieu': 'ancrage_debut__lieu__pk',
          'annee': 'ancrage_debut__date__year',
          'mois': 'ancrage_debut__date__month',
          'jour': 'ancrage_debut__date__day',
          'oeuvre': 'programme__oeuvre__pk',
        }
        filters = {}
        for key, value in data.iteritems():
            if value and key in bindings:
                filters[bindings[key]] = value
        return qs.filter(**filters).distinct()

    def get_context_data(self, **kwargs):
        context = super(EvenementListView, self).get_context_data(**kwargs)
        context['form'] = self.form
        return context


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
