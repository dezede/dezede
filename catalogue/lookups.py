from ajax_select import LookupChannel
from django.template.defaultfilters import removetags
from .models import *
from haystack.query import SearchQuerySet


def search_in_model(Model, qs, search_query):
   sqs = SearchQuerySet().models(Model)
   sqs = sqs.autocomplete(content_auto=search_query)
   pk_list = sqs.values_list('pk', flat=True)
   return qs.filter(pk__in=pk_list)


class LieuLookup(LookupChannel):
    model = Lieu

    def get_query(self, q, request):
        Model = self.model
        return search_in_model(Model, Model.objects.all(), q)[:7]

    def format_match(self, obj):
        return removetags(obj.html(), 'a')

    def check_auth(self,request):
        pass


class OeuvreLookup(LookupChannel):
    model = Oeuvre

    def get_query(self, q, request):
        Model = self.model
        return search_in_model(Model, Model.objects.all(), q)[:7]

    def format_match(self, obj):
        return removetags(obj.titre_html(), 'a')

    def check_auth(self,request):
        pass
