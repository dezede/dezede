# coding: utf-8

from __future__ import unicode_literals
from django.conf.urls import patterns, url
from dossiers.views import (
    CategorieDeDossiersList, DossierDEvenementsDetail,
    DossierDEvenementsDataDetail, DossierDEvenementsDetailXeLaTeX)


urlpatterns = patterns('',
    url(r'^$', CategorieDeDossiersList.as_view(),
        name='dossierdevenements_index'),
    url(r'^(?P<pk>\d+)/$', DossierDEvenementsDetail.as_view(),
        name='dossierdevenements_detail'),
    url(r'^(?P<pk>\d+)/data$', DossierDEvenementsDataDetail.as_view(),
        name='dossierdevenements_data_detail'),
    url(r'^(?P<pk>\d+)/export',
        DossierDEvenementsDetailXeLaTeX.as_view(),
        name='dossierdevenements_detail_xelatex'),
)
