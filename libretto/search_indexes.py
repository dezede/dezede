from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet
from django.utils import translation
from haystack import connections
from haystack.exceptions import NotHandled
from haystack.indexes import (
    SearchIndex, Indexable, CharField, EdgeNgramField, DateField, BooleanField,
    IntegerField)
from tree.models import TreeModelMixin
from wagtail.models import Page
from wagtail.query import PageQuerySet
from wagtail.search.backends import get_search_backend
from wagtail.search.models import IndexEntry

from libretto.models.base import PublishedModel, PublishedQuerySet
from typography.utils import replace


class CommonSearchIndex(SearchIndex):
    content_auto = EdgeNgramField(model_attr='related_label')
    text = CharField(document=True, use_template=True)
    public = BooleanField(model_attr='etat__public')
    owner_id = IntegerField(model_attr='owner_id', null=True)
    BASE_BOOST = 0.5
    MAXIMUM_BOOST = 5.0
    BOOST_GROWTH = 100
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
        boost = (
            min_boost
            + (max_boost-min_boost) * (1 - 1 / (1 + n / self.BOOST_GROWTH)))
        prepared_data['boost'] = boost
        return prepared_data


class OeuvreIndex(CommonSearchIndex, Indexable):
    BASE_BOOST = 2.0
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
    BASE_BOOST = 3.0

    def get_model(self):
        return apps.get_model('libretto.Individu')

    def index_queryset(self, using=None):
        qs = super(IndividuIndex, self).index_queryset(using)
        return qs.prefetch_related('professions')


class EnsembleIndex(CommonSearchIndex, Indexable):
    BASE_BOOST = 2.0

    def get_model(self):
        return apps.get_model('libretto.Ensemble')

    def index_queryset(self, using=None):
        qs = super(EnsembleIndex, self).index_queryset(using)
        return qs.select_related('type')


class LieuIndex(CommonSearchIndex, Indexable):
    BASE_BOOST = 2.5

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
    def get_model(self):
        return apps.get_model('libretto.Partie')


class ProfessionIndex(CommonSearchIndex, Indexable):
    BASE_BOOST = 1.0

    def get_model(self):
        return apps.get_model('libretto.Profession')


def filter_sqs_published(sqs, request):
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


RATIO_BETWEEN_FIRST_AND_LAST = 1/5


def result_iterator(qs: QuerySet):
    results = list(qs)

    if results:
        min_score = results[0]._score * RATIO_BETWEEN_FIRST_AND_LAST
        for result in results:
            if result._score < min_score:
                break
            if isinstance(result, IndexEntry):
                yield result.content_object
            else:
                yield result


def autocomplete_search(request, q, model=None, max_results=5):
    q = replace(q)
    s = get_search_backend()

    if model is None:
        model = IndexEntry

    qs = model.objects.all()
    if isinstance(qs, PublishedQuerySet):
        qs = qs.published(request)
    elif isinstance(qs, PageQuerySet):
        qs = qs.live()
    elif qs.model is IndexEntry:
        qs = qs.filter(
            content_type__in=[
                ContentType.objects.get_for_model(m) for m in apps.get_models()
                if issubclass(m, (PublishedModel, Page))
            ]
        )

    qs = s.autocomplete(q, qs).annotate_score('_score').get_queryset()

    return list(result_iterator(qs[:max_results]))
