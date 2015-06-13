# coding: utf-8

from __future__ import unicode_literals

from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import connection
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from endless_pagination.views import AjaxListView

from accounts.models import HierarchicUser
from common.utils.sql import get_raw_query
from .jobs import dossier_to_pdf
from libretto.models import Source, Oeuvre, Individu
from libretto.views import (
    PublishedListView, PublishedDetailView, EvenementGeoJson, EvenementExport,
    BaseEvenementListView)
from .models import CategorieDeDossiers, DossierDEvenements
from common.utils.export import launch_export


class CategorieDeDossiersList(PublishedListView):
    model = CategorieDeDossiers
    has_frontend_admin = False


class DossierDEvenementsDetail(PublishedDetailView):
    model = DossierDEvenements

    def get_context_data(self, **kwargs):
        context = super(DossierDEvenementsDetail,
                        self).get_context_data(**kwargs)
        context['SITE'] = get_current_site(self.request)
        return context


class DossierDEvenementsViewMixin(object):
    view_name = 'dossierdevenements_data_detail'
    enable_default_page = False

    def get_queryset(self):
        self.object = get_object_or_404(DossierDEvenements, **self.kwargs)
        if not self.object.can_be_viewed(self.request):
            raise PermissionDenied
        return super(DossierDEvenementsViewMixin, self).get_queryset(
            base_filter=Q(pk__in=self.object.get_queryset()))

    def get_export_url(self):
        return reverse('dossierdevenements_data_export', kwargs=self.kwargs)

    def get_geojson_url(self):
        return reverse('dossierdevenements_data_geojson', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        data = super(DossierDEvenementsViewMixin,
                     self).get_context_data(**kwargs)
        data['object'] = self.object
        return data

    def get_success_url(self):
        return reverse(self.view_name, kwargs=self.kwargs)


class DossierDEvenementsDataDetail(DossierDEvenementsViewMixin,
                                   AjaxListView, BaseEvenementListView):
    template_name = 'dossiers/dossierdevenements_data_detail.html'


class DossierDEvenementsDataExport(DossierDEvenementsViewMixin,
                                   EvenementExport):
    pass


class DossierDEvenementsDataGeoJson(DossierDEvenementsViewMixin,
                                    EvenementGeoJson):
    pass


class DossierDEvenementsDetailXeLaTeX(DossierDEvenementsDetail):
    def get_object(self, queryset=None):
        if not self.request.user.is_authenticated():
            raise PermissionDenied
        return super(DossierDEvenementsDetailXeLaTeX,
                     self).get_object(queryset)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        launch_export(dossier_to_pdf, request, self.object.pk, 'PDF',
                      'du dossier « %s »' % self.object)
        return redirect(self.object.get_absolute_url())


class OperaComiquePresentation(TemplateView):
    template_name = 'dossiers/opera_comique_presentation.html'

    def get_context_data(self, **kwargs):
        context = super(OperaComiquePresentation,
                        self).get_context_data(**kwargs)
        context['oc_user'] = HierarchicUser.objects.get(pk=103)
        return context


class OperaComiqueListView(PublishedListView):
    model = Source
    template_name = 'dossiers/opera_comique.html'

    def get_queryset(self):
        qs = super(OperaComiqueListView, self).get_queryset()
        return qs.filter(owner_id=103)

    def get_context_data(self, **kwargs):
        context = super(OperaComiqueListView, self).get_context_data(**kwargs)
        qs = context['object_list']
        oeuvres = (
            Oeuvre.objects.filter(sources__in=qs).distinct()
            .select_related('genre', 'creation_lieu', 'creation_lieu__nature')
            .prefetch_related('auteurs__individu', 'auteurs__profession'))
        if self.request.GET.get('order_by') == 'creation_date':
            oeuvres = oeuvres.order_by('creation_date')
        else:
            oeuvres = oeuvres.order_by(*Oeuvre._meta.ordering)
        context['oeuvres'] = oeuvres
        return context


SQL_SANS_AUTRES = """
WITH individus AS (%s)
SELECT individu1.id, individu2.id, COUNT(DISTINCT programme1.evenement_id) AS n
FROM individus AS individu1
LEFT OUTER JOIN individus AS individu2 ON (true)
LEFT OUTER JOIN libretto_auteur AS auteur1 ON (auteur1.individu_id = individu1.id)
LEFT OUTER JOIN libretto_auteur AS auteur2 ON (auteur2.individu_id = individu2.id AND auteur2.oeuvre_id != auteur1.oeuvre_id)
LEFT OUTER JOIN libretto_elementdeprogramme AS programme1 ON (programme1.oeuvre_id = auteur1.oeuvre_id)
LEFT OUTER JOIN libretto_elementdeprogramme AS programme2 ON (programme2.oeuvre_id = auteur2.oeuvre_id)
WHERE programme1.evenement_id = programme2.evenement_id AND programme1.evenement_id IN (%s)
GROUP BY individu1.id, individu2.id;
"""

SQL_AVEC_AUTRES = """
WITH individus AS (%s)
SELECT individu1.id, individu2.id, COUNT(DISTINCT evenement.id) AS n
FROM (%s) AS evenement
INNER JOIN libretto_elementdeprogramme AS programme1 ON (programme1.evenement_id = evenement.id)
INNER JOIN libretto_elementdeprogramme AS programme2 ON (programme2.evenement_id = evenement.id AND programme2.oeuvre_id != programme1.oeuvre_id)
INNER JOIN libretto_auteur AS auteur1 ON (auteur1.oeuvre_id = programme1.oeuvre_id)
INNER JOIN libretto_auteur AS auteur2 ON (auteur2.oeuvre_id = programme2.oeuvre_id)
LEFT OUTER JOIN individus AS individu1 ON (individu1.id = auteur1.individu_id)
LEFT OUTER JOIN individus AS individu2 ON (individu2.id = auteur2.individu_id)
GROUP BY individu1.id, individu2.id;
"""

SQL = SQL_AVEC_AUTRES


class ChordDiagramView(PublishedDetailView):
    model = DossierDEvenements
    template_name = 'dossiers/chord_diagram.html'
    n_auteurs = 30
    colors_by_period = (
        (float('-inf'), 1580, '#75101C', _('Né avant 1580')),
        (1580, 1730, '#FF6523', _('Baroque')),
        (1730, 1780, '#FFDD89', _('Classique')),
        (1780, 1880, '#4D8E66', _('Romantique')),
        (1880, 1930, '#89B4FF', _('Moderne')),
        (1930, float('+inf'), '#80138E', _('Né après 1930')),
        (None, None, '#E6E6E6', _('Indéterminé')),
    )

    def get_context_data(self, **kwargs):
        context = super(ChordDiagramView, self).get_context_data(**kwargs)

        evenements = self.object.get_queryset()
        individus = evenements.individus_auteurs()

        n_auteurs = self.n_auteurs
        n_individus = individus.count()
        if n_individus == 0:
            return

        if n_individus == n_auteurs + 1:
            n_auteurs = n_individus

        individus_par_popularite = individus.annotate(n=Count('pk')).order_by('-n')
        individus_pks = [pk for pk, n in individus_par_popularite.values_list('pk', 'n')[:n_auteurs]]
        individus = Individu.objects.filter(pk__in=individus_pks).order_by('naissance_date')
        evenements = evenements.order_by().values('pk')
        EVENEMENTS_SQL, EVENEMENTS_PARAMS = get_raw_query(evenements)
        INDIVIDUS_SQL, INDIVIDUS_PARAMS = get_raw_query(individus.order_by().values('pk'))

        with connection.cursor() as cursor:
            cursor.execute(SQL % (INDIVIDUS_SQL, EVENEMENTS_SQL), INDIVIDUS_PARAMS + EVENEMENTS_PARAMS)
            data = cursor.fetchall()

        if len(data) < 3:
            return

        has_autres = False
        pre_matrix = {}
        for id1, id2, n in data:
            has_autres |= id1 is None or id2 is None
            pre_matrix[(id1, id2)] = n

        individus = list(individus)
        if has_autres:
            individus.append(
                Individu(nom='%d autres auteurs' % (n_individus - n_auteurs)))

        matrix = []
        for individu1 in individus:
            row = []
            matrix.append(row)
            for individu2 in individus:
                row.append(pre_matrix.get((individu1.pk, individu2.pk), 0))

        colors = []
        for individu in individus:
            year = (None if individu.naissance_date is None
                    else individu.naissance_date.year)
            for min_year, max_year, color, _ in self.colors_by_period:
                if ((year is not None and (min_year <= year < max_year))
                    or (year is None
                        and min_year is None and max_year is None)):
                    colors.append(color)
                    break
        colors_by_period = []
        for min_year, max_year, color, verbose in self.colors_by_period:
            if color in colors:
                colors_by_period.append((min_year, max_year, color, verbose))

        context.update(
            matrix=matrix, individus=individus,
            colors=colors, colors_by_period=colors_by_period)
        return context
