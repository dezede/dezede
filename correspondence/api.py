from functools import cached_property
from typing import Type
from django.db.models import QuerySet, Q, Count, F, Model
from django.urls import path
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from wagtail.api.v2.utils import parse_fields_parameter
from wagtail.api.v2.views import PagesAPIViewSet, BaseAPIViewSet

from correspondence.models import Letter, LetterCorpus
from dezede.search_backend import FixedPostgresSearchResults
from libretto.models.espace_temps import Lieu
from libretto.models.individu import Individu


class LetterCorpusAPIViewSet(PagesAPIViewSet):
    model = Letter
    known_query_parameters = {
        *PagesAPIViewSet.known_query_parameters,
        'year',
        'person',
        'writing_place',
        'tab',
    }

    @cached_property
    def corpus(self) -> LetterCorpus:
        try:
            return LetterCorpus.objects.live().only('pk', 'person_id').get(pk=self.pk)
        except LetterCorpus.DoesNotExist:
            raise NotFound

    def get_related_serializer_class(self, name: str, request: Request, model: Type[Model]):
        router = request.wagtailapi_router
        endpoint_class = router.get_model_endpoint(model)
        endpoint_class = (
            endpoint_class[1] if endpoint_class else BaseAPIViewSet
        )
        fields_config = []
        for field, _, children in parse_fields_parameter(request.GET.get('fields')):
            if field == name:
                fields_config = children
        return endpoint_class._get_serializer_class(
            request.wagtailapi_router, model, fields_config=fields_config, nested=True,
        )

    def serialize_instance(self, name: str, request: Request, instance: Model):
        serializer_class = self.get_related_serializer_class(name, request, type(instance))
        return serializer_class(instance, context=self.get_serializer_context()).data

    def serialize_queryset(self, name: str, request: Request, queryset: QuerySet):
        serializer_class = self.get_related_serializer_class(name, request, queryset.model)
        return serializer_class(queryset, many=True, context=self.get_serializer_context()).data

    def corpus_view(self, request: Request, pk: int):
        self.pk = pk
        corpus = self.corpus
        letters = self.filter_queryset(self.get_queryset())
        person_choices = Individu.objects.filter(
            Q(sent_letters__in=letters) | Q(received_letters__in=letters)
        ).distinct()
        place_choices = Lieu.objects.filter(
            letter_writing_set__in=letters,
        ).distinct().order_by('nature__nom', 'nom')
        return Response({
            'person': self.serialize_instance('person', request, corpus.person),
            'year_choices': letters.annotate(
                year=F('writing_date__year'),
            ).values('year').order_by('year').annotate(
                count=Count('pk'),
            ),
            'person_choices': self.serialize_queryset('person_choices', request, person_choices),
            'writing_place_choices': self.serialize_queryset('writing_place_choices', request, place_choices),
            'total_count': letters.count(),
            'from_count': letters.filter(sender=corpus.person_id).count(),
            'to_count': letters.filter(recipient_persons=corpus.person_id).count(),
        })

    def filter_queryset(self, qs: QuerySet):
        corpus = self.corpus
        qs = qs.child_of(corpus)
        year = self.request.GET.get('year', '')
        if year.isdigit():
            qs = qs.filter(writing_date__year=year)
        elif year == 'null':
            qs = qs.filter(writing_date__isnull=True)

        person = self.request.GET.get('person', '')
        if person.isdigit():
            qs = qs.filter(Q(sender=person) | Q(recipient_persons=person))

        writing_place = self.request.GET.get('writing_place', '')
        if writing_place.isdigit():
            qs = qs.filter(writing_lieu=writing_place)

        if self.action == 'listing_view':
            tab = self.request.GET.get('tab', 'all')
            if tab == 'from':
                qs = qs.filter(sender_id=corpus.person_id)
            elif tab == 'to':
                qs = qs.filter(recipient_persons=corpus.person_id)
            elif tab == 'other':
                qs = qs.exclude(
                    sender_id=corpus.person_id,
                ).exclude(
                    recipient_persons=corpus.person_id,
                )
        qs = super().filter_queryset(qs)
        if isinstance(qs, FixedPostgresSearchResults):
            qs = qs.get_queryset()
        return (
            qs.order_by('writing_date')
            .select_related(
                'sender', 'writing_lieu__nature', 'writing_lieu__parent',
            ).prefetch_related(
                'recipients__person', 'letter_images__image',
            )
        )

    def listing_view(self, request, pk: int):
        self.pk = pk
        return super().listing_view(request)

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("<int:pk>/", cls.as_view({"get": "corpus_view"}), name="corpus"),
            path("<int:pk>/lettres/", cls.as_view({"get": "listing_view"}), name="letters"),
        ]
