# coding: utf-8

from __future__ import unicode_literals
from django.conf import settings
from django.utils import translation
from haystack import site
from haystack.indexes import SearchIndex, CharField, EdgeNgramField, \
    DateField
from .models import Oeuvre, Source, Individu, Lieu, Evenement, Partie, \
    Profession


class CommonSearchIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    suggestions = CharField()

    def index_queryset(self):
        return self.get_model().objects.all()

    def prepare(self, obj):
        translation.activate(settings.LANGUAGE_CODE)
        prepared_data = super(CommonSearchIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data    


class PolymorphicCommonSearchIndex(CommonSearchIndex):
    def index_queryset(self):
        return self.get_model().objects.non_polymorphic()


class OeuvreIndex(CommonSearchIndex):
    content_auto = EdgeNgramField(model_attr='titre_html')

    def get_model(self):
        return Oeuvre

    def prepare(self, obj):
        prepared_data = super(OeuvreIndex, self).prepare(obj)
        prepared_data['boost'] = 1.0 / (obj.level + 1)
        return prepared_data
site.register(Oeuvre, OeuvreIndex)


class SourceIndex(CommonSearchIndex):
    date = DateField(model_attr='date')

    def get_model(self):
        return Source
site.register(Source, SourceIndex)


class IndividuIndex(CommonSearchIndex):
    content_auto = EdgeNgramField(model_attr='html')

    def get_model(self):
        return Individu
site.register(Individu, IndividuIndex)


class LieuIndex(PolymorphicCommonSearchIndex):
    content_auto = EdgeNgramField(model_attr='html')

    def get_model(self):
        return Lieu
site.register(Lieu, LieuIndex)


class EvenementIndex(CommonSearchIndex):
    def get_model(self):
        return Evenement
site.register(Evenement, EvenementIndex)


class PartieIndex(PolymorphicCommonSearchIndex):
    content_auto = EdgeNgramField(model_attr='html')

    def get_model(self):
        return Partie
site.register(Partie, PartieIndex)


class ProfessionIndex(CommonSearchIndex):
    content_auto = EdgeNgramField(model_attr='html')

    def get_model(self):
        return Profession
site.register(Profession, ProfessionIndex)
