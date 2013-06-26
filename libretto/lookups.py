from ajax_select import LookupChannel
from django.template.defaultfilters import removetags
from .models import *
from haystack.query import SearchQuerySet


def search_in_model(Model, qs, search_query):
    sqs = SearchQuerySet().models(Model)
    sqs = sqs.autocomplete(content_auto=search_query)
    pk_list = sqs.values_list('pk', flat=True)
    return qs.filter(pk__in=pk_list)


class PublicLookup(LookupChannel):
    max_results = 7
    displayed_attr = 'html'

    def get_query(self, q, request):
        Model = self.model
        return search_in_model(
            Model, Model.objects.all(), q)[:self.max_results]

    def format_match(self, obj):
        out = getattr(obj, self.displayed_attr)
        if callable(out):
            out = out()
        return removetags(out, 'a')

    def check_auth(self, request):
        pass


class LieuLookup(PublicLookup):
    model = Lieu


class OeuvreLookup(PublicLookup):
    model = Oeuvre
    displayed_attr = 'titre_html'


class IndividuLookup(PublicLookup):
    model = Individu


class CharFieldLookupChannel(LookupChannel):
    attr = None

    def get_query(self, q, request):
        Model = self.model
        attr = self.attr
        filters = {attr + '__istartswith': q}
        all_results = Model.objects.filter(**filters) \
                                   .values_list(attr, flat=True) \
                                   .distinct().order_by(attr)
        results = sorted(all_results,
                       key=lambda r: Model.objects.filter(**{attr: r}).count())
        results.reverse()
        return results[:7]


class SourceNomLookup(CharFieldLookupChannel):
    model = Source
    attr = 'nom'


class OeuvrePrefixeTitreLookup(CharFieldLookupChannel):
    model = Oeuvre
    attr = 'prefixe_titre'


class OeuvreCoordinationLookup(CharFieldLookupChannel):
    model = Oeuvre
    attr = 'coordination'


class OeuvrePrefixeTitreSecondaireLookup(CharFieldLookupChannel):
    model = Oeuvre
    attr = 'prefixe_titre_secondaire'


class ElementDeProgrammeAutreLookup(CharFieldLookupChannel):
    model = ElementDeProgramme
    attr = 'autre'
