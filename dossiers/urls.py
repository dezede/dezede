# coding: utf-8

from __future__ import unicode_literals
from django.conf.urls import patterns, url
from dossiers.views import DossierDEvenementsList, DossierDEvenementsDetail,\
    DossierDEvenementsDataDetail


urlpatterns = patterns('',
    url(r'^$', DossierDEvenementsList.as_view(),
        name='dossierdevenements_index'),
    url(r'^(?P<pk>\d+)/$', DossierDEvenementsDetail.as_view(),
        name='dossierdevenements_detail'),
    url(r'^(?P<pk>\d+)/data$', DossierDEvenementsDataDetail.as_view(),
        name='dossierdevenements_data_detail'),
)
