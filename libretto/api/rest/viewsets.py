# coding: utf-8

from __future__ import unicode_literals
from rest_framework.viewsets import ReadOnlyModelViewSet
from libretto.models import *
from .serializers import *


class IndividuViewSet(ReadOnlyModelViewSet):
    model = Individu
    serializer_class = IndividuSerializer


class LieuViewSet(ReadOnlyModelViewSet):
    model = Lieu
    serializer_class = LieuSerializer


class OeuvreViewSet(ReadOnlyModelViewSet):
    model = Oeuvre
    serializer_class = OeuvreSerializer
