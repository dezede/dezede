# coding: utf-8
from django.conf.urls import *
from .views import *


urlpatterns = patterns('',
    url(r'^lieux/$', LieuListView.as_view(), name='lieux'),
    url(r'^lieux/id/(?P<pk>\d+)/$', LieuDetailView.as_view(), name='lieu_pk'),
    url(r'^lieux/(?P<slug>[-\w]+)/$', LieuDetailView.as_view(), name='lieu'),
    url(r'^', include(IndividuViewSet().urls)),
    url(r'^', include(OeuvreViewSet().urls)),
    url(r'^evenements/$', EvenementListView.as_view(), name='evenements'),
    url(r'^evenements/id/(?P<pk>\d+)/$', EvenementDetailView.as_view(),
        name='evenement_pk'),
    url(r'^sources/(?P<pk>\d+)/$', SourceDetailView.as_view(),
        name='source_pk'),
    url(r'^', include(PartieViewSet().urls)),
    url(r'^', include(ProfessionViewSet().urls)),
#    url(r'^saisie/source/$', saisie_source,
#        name='saisie_sources'),
#    url(r'^saisie/source/(?P<source_id>\d+)/$', saisie_source,
#        name='saisie_source'),
)
