# coding: utf-8

from __future__ import unicode_literals

from rest_framework.routers import DefaultRouter

from .viewsets import *


router = DefaultRouter()
router.register(r'individus', IndividuViewSet)
router.register(r'ensembles', EnsembleViewSet)
router.register(r'lieux', LieuViewSet)
router.register(r'oeuvres', OeuvreViewSet)
