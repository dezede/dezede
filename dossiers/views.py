# coding: utf-8

from __future__ import unicode_literals
from django.views.generic import ListView, DetailView
from .models import DossierDEvenements


class DossierDEvenementsList(ListView):
    model = DossierDEvenements

    def get_queryset(self):
        qs = super(DossierDEvenementsList, self).get_queryset()
        return qs.filter(level=0)


class DossierDEvenementsDetail(DetailView):
    model = DossierDEvenements
