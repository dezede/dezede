import datetime
import json
from collections import OrderedDict
from mimetypes import guess_type

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.contrib.sitemaps import Sitemap
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.syndication.views import Feed
from django.http import HttpResponse
from django.utils.encoding import smart_text
from django.utils.feedgenerator import DefaultFeed, Enclosure
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, TemplateView
from haystack.views import SearchView

from common.utils.html import sanitize_html
from dossiers.models import DossierDEvenements
from libretto.models import (
    Oeuvre, Lieu, Individu, Source, Evenement, Ensemble, Profession, Partie,
)
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
        self.template_name = f'{self.status}.html'
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


class ImageRssFeedGenerator(DefaultFeed):
    def add_root_elements(self, handler):
        super(ImageRssFeedGenerator, self).add_root_elements(handler)
        handler.startElement('image', {})
        handler.addQuickElement('url', self.feed['image_url'])
        handler.addQuickElement('title', self.feed['title'])
        handler.addQuickElement('link', self.feed['link'])
        handler.endElement('image')


class RssFeed(Feed):
    feed_type = ImageRssFeedGenerator
    title = 'Dezède'
    link = ''
    description = _(
        'Derniers travaux importants de chronologie des spectacles.'
    )

    def get_feed(self, obj, request):
        self.request = request
        return super().get_feed(obj, request)

    def get_absolute_url(self, relative_url):
        return self.request.build_absolute_uri(relative_url)

    def items(self):
        return Diapositive.objects.published()

    def item_title(self, item):
        return strip_tags(item.title) + ' ' + strip_tags(item.subtitle)

    def item_description(self, item: Diapositive):
        if isinstance(item.content_object, DossierDEvenements):
            return sanitize_html(
                item.content_object.presentation, include_links=False,
            )

    def item_link(self, item: Diapositive):
        return item.content_object.get_absolute_url()

    def item_pubdate(self, item: Diapositive):
        if isinstance(item.content_object, DossierDEvenements):
            return datetime.datetime.combine(
                item.content_object.date_publication,
                datetime.time.min,
            )

    def item_enclosures(self, item: Diapositive):
        thumbnail = item.thumbnail_instance(item.size_lg(), item.box_lg())
        return [
            Enclosure(
                self.get_absolute_url(thumbnail.url),
                str(thumbnail.size),
                guess_type(thumbnail.url)[0],
            )
        ]

    def feed_extra_kwargs(self, obj):
        return {
            'image_url': self.get_absolute_url(
                staticfiles_storage.url('images/logo-large.png')
            ),
        }


class GlobalSitemap(Sitemap):
    changefreq = 'monthly'

    def items(self):
        items = []
        for model in (
            DossierDEvenements, Individu, Ensemble, Oeuvre,
            Lieu, Profession, Partie, Source, Evenement,
        ):
            items.extend(model.objects.published().only('pk'))
        return items

    def location(self, obj):
        return obj.permalien()

    def priority(self, obj):
        if isinstance(obj, DossierDEvenements):
            return 1.0
        if isinstance(obj, (Individu, Ensemble)):
            return 0.7
        if isinstance(obj, Profession):
            return 0.2
        if isinstance(obj, (Source, Evenement, Partie)):
            return 0.1
        return 0.5
