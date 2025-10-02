from django.urls import path, include, re_path
from .api.rest.routers import api_router
from libretto.views import TreeNode, EnsembleViewSet, EvenementExport
from .views import *


__all__ = ('urlpatterns',)


urlpatterns = [
    path('', include(LieuViewSet().urls)),
    path('', include(IndividuViewSet().urls)),
    path('', include(EnsembleViewSet().urls)),
    path('', include(OeuvreViewSet().urls)),
    path('evenements/', EvenementListView.as_view(), name='evenements'),
    path('evenements/export', EvenementExport.as_view(), name='evenements_export'),
    path('evenements/geojson', EvenementGeoJson.as_view(), name='evenements_geojson'),
    path('evenements/id/<int:pk>/', EvenementDetailView.as_view(),
        name='evenement_pk'),
    path(r'', include(SourceViewSet().urls)),
    path(r'', include(PartieViewSet().urls)),
    path('', include(ProfessionViewSet().urls)),
    re_path(
        r'^tree_node/(?P<app_label>[\w_]+)/(?P<model_name>\w+)/(?P<attr>[\w_]+)/(?P<pk>\d+)?$',
        TreeNode.as_view(), name='tree_node',
    ),
    path('api/', include(api_router.urls)),
]
