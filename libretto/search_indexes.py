# coding: utf-8

from __future__ import unicode_literals, division
from django.conf import settings
from django.db.models import Q
from django.utils import translation
from haystack.indexes import (
    SearchIndex, Indexable, CharField, EdgeNgramField, DateField, BooleanField,
    IntegerField)
from haystack.query import SearchQuerySet
from .models import (
    Oeuvre, Source, Individu, Lieu, Evenement, Partie, Profession, Ensemble)
from typography.utils import replace


class CommonSearchIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    public = BooleanField(model_attr='etat__public')
    owner_id = IntegerField(model_attr='owner_id', null=True)

    def prepare(self, obj):
        translation.activate(settings.LANGUAGE_CODE)
        prepared_data = super(CommonSearchIndex, self).prepare(obj)
        # Booste chaque objet en fonction du nombre de données liées.
        # le plus petit boost possible est `min_boost`, et une racine de base
        # `root_base` est appliquée pour niveler les résultats.
        root_base = 5
        min_boost = 0.5
        prepared_data['boost'] = (
            (1 + obj.get_related_count()) ** (1 / root_base) - (1 - min_boost))
        return prepared_data


class PolymorphicCommonSearchIndex(CommonSearchIndex):
    def index_queryset(self, *args, **kwargs):
        return super(PolymorphicCommonSearchIndex,
                     self).index_queryset(*args, **kwargs).non_polymorphic()


class OeuvreIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='titre_html')

    def get_model(self):
        return Oeuvre

    def prepare(self, obj):
        prepared_data = super(OeuvreIndex, self).prepare(obj)
        prepared_data['boost'] *= 1.0 / (obj.level + 1)
        return prepared_data


class SourceIndex(CommonSearchIndex, Indexable):
    date = DateField(model_attr='date', null=True)

    def get_model(self):
        return Source


class IndividuIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='related_label')

    def get_model(self):
        return Individu


class EnsembleIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='related_label')

    def get_model(self):
        return Ensemble


class LieuIndex(PolymorphicCommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='html')

    def get_model(self):
        return Lieu

    def prepare(self, obj):
        prepared_data = super(LieuIndex, self).prepare(obj)
        prepared_data['boost'] *= 5.0 / (obj.level + 1)
        return prepared_data


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


def filter_published(sqs, request):
    user_id = request.user.id
    filters = Q(public=True)
    if user_id is not None:
        filters |= Q(user_id=user_id)
    return sqs.filter(filters)


def autocomplete_search(request, q, model=None, max_results=7):
    q = replace(q)
    sqs = SearchQuerySet()
    sqs = filter_published(sqs, request)
    if model is not None:
        sqs = sqs.models(model)
    sqs = sqs.autocomplete(content_auto=q).filter(content_auto__icontains=q)[:max_results]
    return [r.object for r in sqs]
