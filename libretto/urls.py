# coding: utf-8

from __future__ import unicode_literals
from django.conf.urls import *
from .api.rest import router as api_router
from .views import *


__all__ = (b'urlpatterns',)


urlpatterns = patterns('',
    url(br'^', include(LieuViewSet().urls)),
    url(br'^', include(IndividuViewSet().urls)),
    url(br'^', include(OeuvreViewSet().urls)),
    url(br'^evenements/$', EvenementListView.as_view(), name=b'evenements'),
    url(br'^evenements/id/(?P<pk>\d+)/$', EvenementDetailView.as_view(),
        name=b'evenement_pk'),
    url(br'^', include(SourceViewSet().urls)),
    url(br'^', include(PartieViewSet().urls)),
    url(br'^', include(ProfessionViewSet().urls)),
    url(br'^api/', include(api_router.urls)),
)
