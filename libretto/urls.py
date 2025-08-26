from django.conf.urls import *
from .api.rest.routers import api_router
from libretto.views import TreeNode, EnsembleViewSet, EvenementExport
from .views import *


__all__ = ('urlpatterns',)


urlpatterns = [
    url(r'^', include(LieuViewSet().urls)),
    url(r'^', include(IndividuViewSet().urls)),
    url(r'^', include(EnsembleViewSet().urls)),
    url(r'^', include(OeuvreViewSet().urls)),
    url(r'^evenements/$', EvenementListView.as_view(), name='evenements'),
    url(r'^evenements/export$', EvenementExport.as_view(),
        name='evenements_export'),
    url(r'^evenements/geojson$', EvenementGeoJson.as_view(),
        name='evenements_geojson'),
    url(r'^evenements/id/(?P<pk>\d+)/$', EvenementDetailView.as_view(),
        name='evenement_pk'),
    url(r'^', include(SourceViewSet().urls)),
    url(r'^', include(PartieViewSet().urls)),
    url(r'^', include(ProfessionViewSet().urls)),
    url(r'^tree_node/(?P<app_label>[\w_]+)/(?P<model_name>\w+)/(?P<attr>[\w_]+)/(?P<pk>\d+)?$',
        TreeNode.as_view(), name='tree_node'),
    url(r'^api/', include(api_router.urls)),
]
