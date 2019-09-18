from rest_framework.routers import DefaultRouter

from .viewsets import *


router = DefaultRouter()
router.register(r'ensembles', EnsembleViewSet)
router.register(r'evenements', EvenementViewSet)
router.register(r'individus', IndividuViewSet)
router.register(r'lieux', LieuViewSet)
router.register(r'oeuvres', OeuvreViewSet)
router.register(r'parties', PartieViewSet)
router.register(r'sources', SourceViewSet)
router.register(r'users', UserViewSet)
