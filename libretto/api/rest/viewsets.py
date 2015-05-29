# coding: utf-8

from __future__ import unicode_literals

from rest_framework.viewsets import ReadOnlyModelViewSet

from ...models import *
from ...views import PublishedMixin
from .serializers import (IndividuSerializer, EnsembleSerializer,
                          LieuSerializer, OeuvreSerializer)


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
