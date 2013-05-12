# coding: utf-8

from __future__ import unicode_literals
from libretto.views import PublishedListView, PublishedDetailView
from .models import DossierDEvenements


class DossierDEvenementsList(PublishedListView):
    model = DossierDEvenements

    def get_queryset(self):
        qs = super(DossierDEvenementsList, self).get_queryset()
        return qs.filter(level=0)


class DossierDEvenementsDetail(PublishedDetailView):
    model = DossierDEvenements


class DossierDEvenementsDataDetail(DossierDEvenementsDetail):
    template_name_suffix = '_data_detail'
