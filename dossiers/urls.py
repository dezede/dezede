# coding: utf-8

from __future__ import unicode_literals
from django.conf.urls import patterns, url
from django.views.generic import ListView, DetailView
from .models import DossierDEvenements


urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=DossierDEvenements),
        name='dossierdevenements_index'),
    url(r'^(?P<pk>\d+)/$', DetailView.as_view(model=DossierDEvenements),
        name='dossierdevenements_detail'),
)
