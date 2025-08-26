from rest_framework.routers import DefaultRouter

from .viewsets import *


api_router = DefaultRouter()
api_router.register(r'auteurs', AuteurViewSet)
api_router.register(r'ensembles', EnsembleViewSet)
api_router.register(r'evenements', EvenementViewSet)
api_router.register(r'individus', IndividuViewSet)
api_router.register(r'lieux', LieuViewSet)
api_router.register(r'oeuvres', OeuvreViewSet)
api_router.register(r'parties', PartieViewSet)
api_router.register(r'professions', ProfessionViewSet)
api_router.register(r'sources', SourceViewSet)
api_router.register(r'users', UserViewSet)
