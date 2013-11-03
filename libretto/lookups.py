import operator
from ajax_select import LookupChannel
from bs4 import BeautifulSoup
from django.utils.encoding import force_text
from django.utils import six
from django.utils.html import strip_tags
from haystack.backends import SQ
from haystack.query import SearchQuerySet
from typography.utils import replace
from .models.functions import hlp
from .models import *


# Application de https://github.com/toastdriven/django-haystack/pull/732
def autocomplete(self, **kwargs):
    clone = self._clone()
    query_bits = []

    for field_name, query in kwargs.items():
        for word in query.split(' '):
            bit = clone.query.clean(word.strip())
            if bit:
                kwargs = {
                    field_name: bit,
                }
                query_bits.append(SQ(**kwargs))

    return clone.filter(six.moves.reduce(operator.__and__, query_bits))


SearchQuerySet.autocomplete = autocomplete


def search_in_model(model, q, max_results):
    q = replace(q)
    sqs = SearchQuerySet().models(model)
    sqs = sqs.autocomplete(content_auto=q).boost(q+'*', 10)[:max_results]
    q = q.lower()
    return [r.object for r in sqs
            if q in r.get_stored_fields()['content_auto'].lower()]


class PublicLookup(LookupChannel):
    max_results = 7
    displayed_attr = 'html'

    def get_query(self, q, request):
        return search_in_model(self.model, q, self.max_results)

    def format_match(self, obj):
        out = getattr(obj, self.displayed_attr)
        if callable(out):
            out = out()

        soup = BeautifulSoup(out, 'html.parser')

        # Retire les attributs title.
        for with_title in soup.find_all(title=True):
            del(with_title['title'])

        # Retire les liens hypertexte.
        for link in soup.find_all('a'):
            link.unwrap()

        out = force_text(soup)
        return hlp(out, strip_tags(out))

    def format_item_display(self, obj):
        return self.format_match(obj)

    def check_auth(self, request):
        pass


class LieuLookup(PublicLookup):
    model = Lieu


class OeuvreLookup(PublicLookup):
    model = Oeuvre
    displayed_attr = 'titre_descr_html'


class IndividuLookup(PublicLookup):
    model = Individu
    displayed_attr = 'related_label_html'


class CharFieldLookupChannel(LookupChannel):
    attr = None

    def get_query(self, q, request):
        model = self.model
        attr = self.attr
        filters = {attr + '__istartswith': q}
        all_results = model.objects.filter(**filters) \
                                   .values_list(attr, flat=True) \
                                   .distinct().order_by(attr)
        results = sorted(all_results,
                       key=lambda r: model.objects.filter(**{attr: r}).count())
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
