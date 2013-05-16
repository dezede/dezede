# coding: utf-8

from __future__ import unicode_literals
from django.contrib.sites.models import get_current_site
from django.utils.text import slugify
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


class DossierDEvenementsDetailXeLaTeX(DossierDEvenementsDetail):
    template_name = 'dossiers/dossierdevenements_detail.tex'
    content_type = 'text/plain'

    def get_context_data(self, **kwargs):
        context = super(DossierDEvenementsDetailXeLaTeX, self).get_context_data(**kwargs)
        context['SITE'] = get_current_site(self.request)
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super(DossierDEvenementsDetailXeLaTeX,
                         self).render_to_response(context, **response_kwargs)
        response['Content-Disposition'] = 'filename="%s.tex"' \
                                          % slugify(self.object.titre)
        return response
