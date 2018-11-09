from collections import OrderedDict
import json

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.utils.encoding import smart_text
from django.views.generic import ListView, TemplateView
from haystack.views import SearchView
from libretto.models import Oeuvre, Lieu, Individu
from libretto.search_indexes import autocomplete_search, filter_published
from typography.utils import replace
from .models import Diapositive


# Taken from https://gist.github.com/justinfx/3095246
def cache_generics(queryset):
    generics = {}
    for item in queryset:
        if item.object_id is not None:
            generics.setdefault(item.content_type_id, set()).add(item.object_id)

    content_types = ContentType.objects.in_bulk(generics.keys())

    relations = {}
    for ct, fk_list in generics.items():
        ct_model = content_types[ct].model_class()
        relations[ct] = ct_model.objects.in_bulk(list(fk_list))

    for item in queryset:
        try:
            cached_val = relations[item.content_type_id][item.object_id]
        except KeyError:
            cached_val = None
        setattr(item, '_content_object_cache', cached_val)


class HomeView(ListView):
    model = Diapositive
    template_name = 'home.html'

    def get_queryset(self):
        qs = super(HomeView, self).get_queryset().published(self.request)
        cache_generics(qs)
        return qs


# TODO: Use the search engine filters to do this
def clean_query(q):
    return (q.lower().replace('(', '').replace(')', '').replace(',', '')
            .replace('-', ' '))


class CustomSearchView(SearchView):
    """
    Custom SearchView to fix spelling suggestions.
    """

    def build_form(self, form_kwargs=None):
        self.request.GET = GET = self.request.GET.copy()
        GET['q'] = replace(GET.get('q', ''))
        return super(CustomSearchView, self).build_form(form_kwargs)

    def extra_context(self):
        context = {'suggestion': None}

        if self.results.query.backend.include_spelling:
            q = self.query or ''
            suggestion = self.form.searchqueryset.spelling_suggestion(q) or ''
            if clean_query(suggestion) != clean_query(q):
                context['suggestion'] = suggestion

        return context

    def get_results(self):
        sqs = super(CustomSearchView, self).get_results()
        return filter_published(sqs, self.request)


def autocomplete(request):
    q = request.GET.get('q', '')
    model = None
    if 'model' in request.GET:
        model = apps.get_model('libretto', request.GET.get('model'))
        if model is None:
            return HttpResponse('Invalid “model” argument.', status=400)
    suggestions = autocomplete_search(request, q, model=model) if q else []
    suggestions = [
        OrderedDict((
            ('id', s.pk),
            ('str', (s.related_label() if hasattr(s, 'related_label')
                     else smart_text(s))),
            ('url', s.get_absolute_url()))) for s in suggestions
        if s is not None]
    data = json.dumps(suggestions)
    return HttpResponse(data, content_type='application/json')


class ErrorView(TemplateView):
    status = 200

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['status'] = self.status
        self.template_name = '%s.html' % self.status
        return super(ErrorView, self).render_to_response(context,
                                                         **response_kwargs)


class BibliographieView(TemplateView):
    template_name = 'pages/bibliographie.html'

    def get_context_data(self, **kwargs):
        context = super(BibliographieView, self).get_context_data(**kwargs)
        context.update(
            oeuvres=Oeuvre.objects.all(),
            individus=Individu.objects.all(),
            lieux=Lieu.objects.all(),
        )
        return context
