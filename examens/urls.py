# coding: utf-8

from __future__ import unicode_literals
from django.conf.urls import patterns, url
from .views import SourceExamen


urlpatterns = patterns('',
    url(r'^source$', SourceExamen.as_view(), name='source_examen'),
)
