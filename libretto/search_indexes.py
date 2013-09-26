# coding: utf-8

from __future__ import unicode_literals
from django.conf import settings
from django.utils import translation
from celery_haystack.indexes import CelerySearchIndex as SearchIndex
from haystack.indexes import Indexable, CharField, \
    EdgeNgramField, DateField
from .models import Oeuvre, Source, Individu, Lieu, Evenement, Partie, \
    Profession


class CommonSearchIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def prepare(self, obj):
        translation.activate(settings.LANGUAGE_CODE)
        prepared_data = super(CommonSearchIndex, self).prepare(obj)
        prepared_data['boost'] = obj.get_related_count()
        return prepared_data


class PolymorphicCommonSearchIndex(CommonSearchIndex):
    def index_queryset(self, *args, **kwargs):
        return super(PolymorphicCommonSearchIndex,
                     self).index_queryset(*args, **kwargs).non_polymorphic()


class OeuvreIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='titre_descr_html')

    def get_model(self):
        return Oeuvre

    def prepare(self, obj):
        prepared_data = super(OeuvreIndex, self).prepare(obj)
        prepared_data['boost'] *= 1.0 / (obj.level + 1)
        return prepared_data


class SourceIndex(CommonSearchIndex, Indexable):
    date = DateField(model_attr='date')

    def get_model(self):
        return Source


class IndividuIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='related_label')

    def get_model(self):
        return Individu


class LieuIndex(PolymorphicCommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='html')

    def get_model(self):
        return Lieu


class EvenementIndex(CommonSearchIndex, Indexable):
    def get_model(self):
        return Evenement


class PartieIndex(PolymorphicCommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='html')

    def get_model(self):
        return Partie


class ProfessionIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='html')

    def get_model(self):
        return Profession
