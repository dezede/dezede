# coding: utf-8

from __future__ import unicode_literals
from django.conf.urls import *
from .api.rest import router as api_router
from libretto.views import TreeNode, EnsembleViewSet
from .views import *


__all__ = (b'urlpatterns',)


urlpatterns = patterns('',
    url(br'^', include(LieuViewSet().urls)),
    url(br'^', include(IndividuViewSet().urls)),
    url(br'^', include(EnsembleViewSet().urls)),
    url(br'^', include(OeuvreViewSet().urls)),
    url(br'^evenements/$', EvenementListView.as_view(), name=b'evenements'),
    url(br'^evenements/id/(?P<pk>\d+)/$', EvenementDetailView.as_view(),
        name=b'evenement_pk'),
    url(br'^', include(SourceViewSet().urls)),
    url(br'^', include(PartieViewSet().urls)),
    url(br'^', include(ProfessionViewSet().urls)),
    url(r'^tree_node/(?P<model_name>\w+)/(?P<attr>[\w_]+)/(?P<pk>\d+)?$', TreeNode.as_view(),
        name='tree_node'),
    url(br'^api/', include(api_router.urls)),
)
