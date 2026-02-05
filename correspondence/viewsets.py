from functools import cached_property
from typing import List, Union
from django.db.models import QuerySet, Q, Count, F
from django.urls import path
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from correspondence.models import Letter, LetterCorpus
from dezede.viewsets import CustomPagesAPIViewSet
from dezede.search_backend import FixedPostgresSearchResults
from libretto.models.espace_temps import Lieu
from libretto.models.individu import Individu


def get_only(model_name: str, lookup: Union[str, None] = None) -> List[str]:
    only_lookups = {
        'libretto.Individu': [
            'particule_nom', 'nom', 'particule_nom_naissance', 'nom_naissance',
            'prenoms', 'pseudonyme', 'designation', 'titre',
        ],
        'libretto.Lieu': ['nom', 'parent__nom', 'nature__nom', 'nature__referent'],
    }[model_name]
    if lookup is not None:
        only_lookups = [f'{lookup}__{field}' for field in only_lookups]
    return only_lookups


class LetterCorpusAPIViewSet(CustomPagesAPIViewSet):
    model = Letter
    known_query_parameters = {
        *CustomPagesAPIViewSet.known_query_parameters,
        'year',
        'person',
        'writing_place',
        'tab',
    }

    @cached_property
    def corpus(self) -> LetterCorpus:
        try:
            return LetterCorpus.objects.live().select_related('person').only(
                'body', *get_only('libretto.Individu', 'person'),
            ).get(pk=self.pk)
        except LetterCorpus.DoesNotExist:
            raise NotFound

    def corpus_view(self, request: Request, pk: int):
        self.pk = pk
        corpus = self.corpus
        letters = self.filter_queryset(self.get_queryset())
        person_choices = Individu.objects.filter(
            Q(sent_letters__in=letters) | Q(received_letters__in=letters)
        ).distinct().only(*get_only('libretto.Individu'))
        place_choices = Lieu.objects.filter(
            letter_writing_set__in=letters,
        ).distinct().order_by('nature__nom', 'nom').select_related('parent', 'nature').only(
            *get_only('libretto.Lieu'),
        )
        return Response({
            'person': self.serialize_instance('person', corpus.person),
            'body': corpus.body.stream_block.get_api_representation(corpus.body, {'view': self}),
            'first_published_at': corpus.first_published_at,
            'owner': self.serialize_instance('owner', corpus.owner),
            'year_choices': letters.annotate(
                year=F('writing_date__year'),
            ).values('year').order_by('year').annotate(
                count=Count('pk'),
            ),
            'person_choices': self.serialize_queryset('person_choices', person_choices),
            'writing_place_choices': self.serialize_queryset('writing_place_choices', place_choices),
            'total_count': letters.count(),
            'from_count': letters.filter(sender_persons=corpus.person_id).count(),
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
            qs = qs.filter(Q(sender_persons=person) | Q(recipient_persons=person))

        writing_place = self.request.GET.get('writing_place', '')
        if writing_place.isdigit():
            qs = qs.filter(writing_lieu=writing_place)

        if self.action == 'listing_view':
            tab = self.request.GET.get('tab', 'all')
            if tab == 'from':
                qs = qs.filter(sender_persons=corpus.person_id)
            elif tab == 'to':
                qs = qs.filter(recipient_persons=corpus.person_id)
            elif tab == 'other':
                qs = qs.exclude(
                    sender_persons=corpus.person_id,
                ).exclude(
                    recipient_persons=corpus.person_id,
                )
        qs = super().filter_queryset(qs)
        if isinstance(qs, FixedPostgresSearchResults):
            qs = qs.get_queryset()
        return (
            qs.order_by('writing_date')
            .select_related(
                'writing_lieu__nature', 'writing_lieu__parent',
            ).prefetch_related(
                'senders__person', 'recipients__person', 'letter_images__image',
            ).distinct()
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
