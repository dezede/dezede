# coding: utf-8

from __future__ import unicode_literals
import json
from django.http import HttpResponse
from django.utils.encoding import smart_text
from django.views.generic import TemplateView
from haystack.query import SearchQuerySet
from haystack.views import SearchView
from libretto.views import PublishedListView
from .models import Diapositive


class HomeView(PublishedListView):
    model = Diapositive
    template_name = 'home.html'


class CustomSearchView(SearchView):
    """
    Custom SearchView to fix spelling suggestions.
    """
    def extra_context(self):
        context = {'suggestion': None}

        if self.results.query.backend.include_spelling:
            suggestion = self.form.get_suggestion()
            if suggestion != self.query:
                context['suggestion'] = suggestion

        return context


def autocomplete(request):
    q = request.GET.get('q', '')
    sqs = SearchQuerySet().autocomplete(content_auto=q)[:5]
    suggestions = [smart_text(result.object) for result in sqs]
    data = json.dumps(suggestions)
    return HttpResponse(data, content_type='application/json')


class ErrorView(TemplateView):
    status = 200

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['status'] = self.status
        self.template_name = '%s.html' % self.status
        return super(ErrorView, self).render_to_response(context,
                                                         **response_kwargs)
