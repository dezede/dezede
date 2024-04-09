from ajax_select import LookupChannel
from bs4 import BeautifulSoup
from django.db.models import Count
from django.utils.encoding import force_text
from django.utils.html import strip_tags

from libretto.search_indexes import autocomplete_search
from common.utils.html import hlp
from .models import *


#
# Ajax-select lookups
#


class PublicLookup(LookupChannel):
    max_results = 7
    displayed_attr = 'html'

    def get_query(self, q, request):
        return autocomplete_search(request, q, self.model, self.max_results)

    def format_match(self, obj):
        if obj is None:
            return ''
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


class EnsembleLookup(PublicLookup):
    model = Ensemble


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
        all_results = (model.objects.filter(**filters)
                       .values_list(attr).order_by(attr)
                       .annotate(n=Count('pk')).order_by('-n'))
        return [v for v, n in all_results[:7]]


class SourceTitreLookup(CharFieldLookupChannel):
    model = Source
    attr = 'titre'


class SourceLieuConservationLookup(CharFieldLookupChannel):
    model = Source
    attr = 'lieu_conservation'


class IndividuPrenomsLookup(CharFieldLookupChannel):
    model = Individu
    attr = 'prenoms'


class EnsembleParticuleNomLookup(CharFieldLookupChannel):
    model = Ensemble
    attr = 'particule_nom'


class OeuvrePrefixeTitreLookup(CharFieldLookupChannel):
    model = Oeuvre
    attr = 'prefixe_titre'


class OeuvreCoordinationLookup(CharFieldLookupChannel):
    model = Oeuvre
    attr = 'coordination'


class OeuvrePrefixeTitreSecondaireLookup(CharFieldLookupChannel):
    model = Oeuvre
    attr = 'prefixe_titre_secondaire'


class OeuvreCoupeLookup(CharFieldLookupChannel):
    model = Oeuvre
    attr = 'coupe'


class OeuvreTempoLookup(CharFieldLookupChannel):
    model = Oeuvre
    attr = 'tempo'


class ElementDeProgrammeAutreLookup(CharFieldLookupChannel):
    model = ElementDeProgramme
    attr = 'autre'
