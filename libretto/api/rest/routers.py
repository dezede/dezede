from rest_framework.routers import DefaultRouter

from .viewsets import *
from . import public_viewsets as pub


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

# Public index/detail endpoints for the Next.js standalone entity pages.
api_router.register(r'public/oeuvres', pub.PublicOeuvreViewSet,
                    basename='public-oeuvre')
api_router.register(r'public/individus', pub.PublicIndividuViewSet,
                    basename='public-individu')
api_router.register(r'public/ensembles', pub.PublicEnsembleViewSet,
                    basename='public-ensemble')
api_router.register(r'public/lieux', pub.PublicLieuViewSet,
                    basename='public-lieu')
api_router.register(r'public/parties', pub.PublicPartieViewSet,
                    basename='public-partie')
api_router.register(r'public/professions', pub.PublicProfessionViewSet,
                    basename='public-profession')
api_router.register(r'public/sources', pub.PublicSourceViewSet,
                    basename='public-source')

# Global, entity-type-faceted search across all catalogue models.
from .public_search import PublicSearchViewSet  # noqa: E402
api_router.register(r'public/search', PublicSearchViewSet,
                    basename='public-search')

# Dossiers (separate app) — index, detail, data, geojson and statistics.
from dossiers.rest import DossierViewSet  # noqa: E402
api_router.register(r'public/dossiers', DossierViewSet,
                    basename='public-dossier')
