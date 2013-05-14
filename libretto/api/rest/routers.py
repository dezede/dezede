# coding: utf-8

from __future__ import unicode_literals
from rest_framework.routers import DefaultRouter
from .viewsets import *


router = DefaultRouter()
router.register(br'individus', IndividuViewSet)
router.register(br'lieux', LieuViewSet)
router.register(br'oeuvres', OeuvreViewSet)
