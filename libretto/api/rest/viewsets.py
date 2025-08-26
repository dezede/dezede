from rest_framework.viewsets import ReadOnlyModelViewSet

from accounts.models import HierarchicUser
from accounts.serializers import UserSerializer
from ...models import *
from ...views import PublishedMixin
from .serializers import (
    IndividuSerializer, EnsembleSerializer, LieuSerializer, OeuvreSerializer,
    SourceSerializer, EvenementSerializer, PartieSerializer,
    AuteurSerializer, ProfessionSerializer,
)


class IndividuViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Individu
    queryset = model.objects.prefetch_related('professions', 'parents')
    serializer_class = IndividuSerializer


class EnsembleViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Ensemble
    queryset = model.objects.select_related('type')
    serializer_class = EnsembleSerializer


class LieuViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Lieu
    queryset = model.objects.select_related('parent__nature', 'nature')
    serializer_class = LieuSerializer


class OeuvreViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Oeuvre
    queryset = model.objects.prefetch_related('extrait_de',
                                              'auteurs__profession')
    serializer_class = OeuvreSerializer


class SourceViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Source
    queryset = Source.objects.prefetch_related(
        'evenements', 'oeuvres', 'individus', 'ensembles', 'lieux', 'parties',
        'editeurs_scientifiques', 'auteurs',
    )
    serializer_class = SourceSerializer


class AuteurViewSet(ReadOnlyModelViewSet):
    model = Auteur
    queryset = Auteur.objects.all()
    serializer_class = AuteurSerializer


class ProfessionViewSet(ReadOnlyModelViewSet):
    model = Profession
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer


class EvenementViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Evenement
    queryset = Evenement.objects.select_related(
        'debut_lieu', 'debut_lieu__nature',
        'debut_lieu__parent', 'debut_lieu__parent__nature',
        'fin_lieu', 'fin_lieu__nature',
    ).prefetch_related('caracteristiques')
    serializer_class = EvenementSerializer


class PartieViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Partie
    queryset = Partie.objects.all()
    serializer_class = PartieSerializer


class UserViewSet(ReadOnlyModelViewSet):
    model = HierarchicUser
    queryset = HierarchicUser.objects.all()
    serializer_class = UserSerializer
