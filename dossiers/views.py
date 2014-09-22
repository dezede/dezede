# coding: utf-8

from __future__ import unicode_literals
from django.contrib import messages
from django.contrib.sites.models import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from libretto.views import (
    PublishedListView, PublishedDetailView, EvenementListView)
from .jobs import send_pdf
from .models import CategorieDeDossiers, DossierDEvenements
from .utils import is_user_locked, lock_user


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
        if not self.object.can_be_viewed(self.request):
            raise PermissionDenied
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
    def get_object(self, queryset=None):
        if not self.request.user.is_authenticated():
            raise PermissionDenied
        return super(DossierDEvenementsDetailXeLaTeX,
                     self).get_object(queryset)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if is_user_locked(request.user):
            messages.error(request,
                           'Un export de votre part est déjà en cours. '
                           'Veuillez attendre la fin de celui-ci avant d’en '
                           'lancer un autre.')
        else:
            lock_user(request.user)
            site = get_current_site(request)
            send_pdf.delay(self.object.pk, request.user.pk, site.pk,
                           request.LANGUAGE_CODE)
            messages.info(request,
                          'La génération de l’export PDF du dossier « %s » '
                          'est en cours. Un courriel le contenant vous sera '
                          'envoyé d’ici quelques minutes.' % self.object)
        return redirect(reverse('dossierdevenements_detail',
                                args=(self.object.pk,)))
