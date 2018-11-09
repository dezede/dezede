from django.apps import apps
from django.conf import settings
from django.db.models import Q
from django.utils import translation
from haystack import connections
from haystack.exceptions import NotHandled
from haystack.indexes import (
    SearchIndex, Indexable, CharField, EdgeNgramField, DateField, BooleanField,
    IntegerField)
from haystack.query import SearchQuerySet
from tree.models import TreeModelMixin

from typography.utils import replace


class CommonSearchIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    public = BooleanField(model_attr='etat__public')
    owner_id = IntegerField(model_attr='owner_id', null=True)
    BASE_BOOST = 0.5
    MAXIMUM_BOOST = 5.0
    LEVEL_ATTENUATION = 0.1

    def prepare(self, obj):
        translation.activate(settings.LANGUAGE_CODE)
        prepared_data = super(CommonSearchIndex, self).prepare(obj)
        # Booste chaque objet en fonction du nombre de données liées.
        # `growth` est le nombre d’objets liés nécessaires pour atteindre
        # les 2/3 de la distance entre `min_boost` et `max_boost`.
        n = obj.get_related_count()

        if isinstance(obj, TreeModelMixin):
            # Sligthly reduces the number of related objects if highly nested.
            n /= 1 + (obj.get_level() - 1) * self.LEVEL_ATTENUATION

        min_boost, max_boost = self.BASE_BOOST, self.MAXIMUM_BOOST
        growth = 100
        boost = (
            min_boost + (max_boost-min_boost) * (1 - 1 / (1 + n / growth)))
        prepared_data['boost'] = boost
        return prepared_data


class OeuvreIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='titre_html')
    BASE_BOOST = 1.5
    LEVEL_ATTENUATION = 1

    def get_model(self):
        return apps.get_model('libretto.Oeuvre')

    def index_queryset(self, using=None):
        qs = super(OeuvreIndex, self).index_queryset(using)
        return qs.select_related('genre').prefetch_related(
            'pupitres__partie',
            'auteurs__individu', 'auteurs__ensemble', 'auteurs__profession')


class SourceIndex(CommonSearchIndex, Indexable):
    date = DateField(model_attr='date', null=True)
    BASE_BOOST = 0.25

    def get_model(self):
        return apps.get_model('libretto.Source')


class IndividuIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='related_label')
    BASE_BOOST = 2.0

    def get_model(self):
        return apps.get_model('libretto.Individu')

    def index_queryset(self, using=None):
        qs = super(IndividuIndex, self).index_queryset(using)
        return qs.prefetch_related('professions')


class EnsembleIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='related_label')
    BASE_BOOST = 2.0

    def get_model(self):
        return apps.get_model('libretto.Ensemble')

    def index_queryset(self, using=None):
        qs = super(EnsembleIndex, self).index_queryset(using)
        return qs.select_related('type')


class LieuIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='html')
    BASE_BOOST = 1.5

    def get_model(self):
        return apps.get_model('libretto.Lieu')

    def index_queryset(self, using=None):
        qs = super(LieuIndex, self).index_queryset(using)
        return qs.select_related('nature', 'parent', 'parent__nature')


class EvenementIndex(CommonSearchIndex, Indexable):
    def get_model(self):
        return apps.get_model('libretto.Evenement')

    def index_queryset(self, using=None):
        qs = super(EvenementIndex, self).index_queryset(using)
        return qs.prefetch_all().defer(None)


class PartieIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='html')
    BASE_BOOST = 1.0

    def get_model(self):
        return apps.get_model('libretto.Partie')


class ProfessionIndex(CommonSearchIndex, Indexable):
    content_auto = EdgeNgramField(model_attr='html')
    BASE_BOOST = 1.0

    def get_model(self):
        return apps.get_model('libretto.Profession')


def filter_published(sqs, request):
    user_id = request.user.id
    if request.user.is_superuser:
        return sqs
    filters = Q(public='true')
    if user_id is not None:
        filters |= Q(owner_id=user_id)
    return sqs.filter(filters)


def get_haystack_unified_index():
    return connections['default'].get_unified_index()


def get_haystack_index(model):
    try:
        return get_haystack_unified_index().get_index(model)
    except NotHandled:
        return


MINIMUM_SCORE = 5.0
RATIO_BETWEEN_FIRST_AND_LAST = 1/3


def result_iterator(sqs):
    results = list(sqs)

    if results:
        min_score = max(results[0].score * RATIO_BETWEEN_FIRST_AND_LAST,
                        MINIMUM_SCORE)
        for result in results:
            if result.score < min_score:
                break
            yield result.object


def autocomplete_search(request, q, model=None, max_results=5):
    q = replace(q)
    sqs = SearchQuerySet()
    if model is None:
        unified_index = get_haystack_unified_index()
        models = unified_index.get_indexed_models()
        models = [model for model in models
                  if 'content_auto' in unified_index.get_index(model).fields]
        sqs = sqs.models(*models)
    else:
        sqs = sqs.models(model)
    sqs = filter_published(sqs, request)
    sqs = sqs.autocomplete(content_auto=q)[:max_results]

    return list(result_iterator(sqs))
