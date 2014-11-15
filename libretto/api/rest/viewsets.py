# coding: utf-8

from __future__ import unicode_literals
from rest_framework.viewsets import ReadOnlyModelViewSet
from ...models import *
from ...views import PublishedMixin
from .serializers import *


class IndividuViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Individu
    serializer_class = IndividuSerializer


class EnsembleViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Ensemble
    serializer_class = EnsembleSerializer


class LieuViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Lieu
    serializer_class = LieuSerializer


class OeuvreViewSet(PublishedMixin, ReadOnlyModelViewSet):
    model = Oeuvre
    serializer_class = OeuvreSerializer
