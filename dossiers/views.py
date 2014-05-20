# coding: utf-8

from __future__ import unicode_literals
from django.contrib.sites.models import get_current_site
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from libretto.views import (
    PublishedListView, PublishedDetailView, EvenementListView)
from .models import CategorieDeDossiers, DossierDEvenements


class CategorieDeDossiersList(PublishedListView):
    model = CategorieDeDossiers
    has_frontend_admin = False


class DossierDEvenementsDetail(PublishedDetailView):
    model = DossierDEvenements


class DossierDEvenementsDataDetail(EvenementListView):
    template_name = 'dossiers/dossierdevenements_data_detail.html'
    view_name = 'dossierdevenements_data_detail'
    enable_default_page = False

    def get_queryset(self):
        self.object = get_object_or_404(DossierDEvenements,
                                        pk=self.kwargs['pk'])
        return super(DossierDEvenementsDataDetail, self).get_queryset(
            base_filter=Q(pk__in=self.object.get_queryset()))

    def get_context_data(self, **kwargs):
        data = super(DossierDEvenementsDataDetail, self) \
            .get_context_data(**kwargs)
        data['object'] = self.object
        return data

    def get_success_view(self):
        return self.view_name, int(self.kwargs['pk'])


class DossierDEvenementsDetailXeLaTeX(DossierDEvenementsDetail):
    template_name = 'dossiers/dossierdevenements_detail.tex'
    content_type = 'text/plain'

    def get_context_data(self, **kwargs):
        context = super(DossierDEvenementsDetailXeLaTeX, self) \
            .get_context_data(**kwargs)
        context['SITE'] = get_current_site(self.request)
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super(DossierDEvenementsDetailXeLaTeX,
                         self).render_to_response(context, **response_kwargs)
        response['Content-Disposition'] = 'filename="%s.tex"' \
                                          % slugify(self.object.titre)
        return response
