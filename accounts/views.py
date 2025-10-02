import datetime
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.db.models import Count
from django.db.models.expressions import RawSQL
from django.http import Http404
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, TemplateView, ListView
from libretto.models import Evenement
from .models import HierarchicUser


class GrantToAdmin(DetailView):
    model = get_user_model()
    template_name = 'accounts/grant_to_admin.html'

    def grant_user(self, user):
        user.is_active = True
        user.is_staff = True
        user.save()
        site_url = 'https://' + Site.objects.get_current(self.request).domain
        email_content = render_to_string(
            'accounts/granted_to_admin_email.txt',
            {'user': user, 'site_url': site_url})
        user.email_user(
            _('Accès autorisé à l’administration'),
            email_content)

    def get_context_data(self, **kwargs):
        context = super(GrantToAdmin, self).get_context_data(**kwargs)
        current_user = self.request.user
        user_to_be_granted = self.object
        if current_user != user_to_be_granted.mentor:
            raise PermissionDenied
        if user_to_be_granted.is_staff:
            context['already_staff'] = True
        else:
            self.grant_user(user_to_be_granted)
        return context


class EvenementsGraph(TemplateView):
    template_name = 'accounts/include/evenements_graph.svg'
    content_type = 'image/svg+xml'
    displayed_range = 150  # years
    row_length = 20  # years
    rect_size = 16  # pixels
    rect_margin = 4  # pixels
    # When we set the font size, the figures are smaller than
    # the specified size.
    figure_size_factor = 0.8
    hue = 17  # degrees
    legend_levels = 6

    def get_context_data(self, **kwargs):
        context = super(EvenementsGraph, self).get_context_data(**kwargs)

        qs = Evenement.objects.exclude(debut_date=None)

        username = self.request.GET.get('username')

        if username is not None:
            User = get_user_model()
            if not User.objects.filter(username=username).exists():
                raise Http404

            qs = qs.filter(owner__username=username)

        context['data'] = data = list(
            qs
            .annotate(year=RawSQL(*connection.ops.date_trunc_sql(
                'year', 'debut_date', [],
            )))
            .values('year').annotate(n=Count('pk'))
            .order_by('year'))

        for d in data:
            d['year'] = d['year'].year

        years = [d['year'] for d in data]
        current_year = datetime.datetime.now().year
        if not years:
            years = [current_year]
            data = [{'year': current_year, 'n': 0}]
        min_year = min(years)
        max_year = max(years)

        margin = max(0, (self.displayed_range - (max_year - min_year)) // 2)

        max_upper_margin = max(0, current_year - max_year)
        margin_offset = max(0, margin - max_upper_margin)

        context['min_year'] = min_year = min_year - (margin + margin_offset)
        context['max_year'] = max_year = max_year + (margin - margin_offset)

        counts = [d['n'] for d in data] + [0]
        context['max_n'] = max(counts)

        # Fill data with missing years between min_year and max_year.
        for year in range(min_year, max_year + 1):
            if year not in years:
                data.append({'year': year, 'n': 0})
        context['data'] = sorted(data, key=lambda d: d['year'])

        def get_float(attr):
            return float(self.request.GET.get(attr) or getattr(self, attr))

        row_length = self.row_length

        context['row_length'] = row_length
        context['size'] = get_float('rect_size')
        context['margin'] = get_float('rect_margin')
        context['figure_size_factor'] = get_float('figure_size_factor')
        context['hue'] = get_float('hue')

        isolated_starting_years = min_year % row_length
        isolated_ending_years = max_year % row_length
        min_year -= isolated_starting_years
        max_year -= isolated_ending_years

        n_rows = (max_year - min_year) // row_length
        if isolated_ending_years > 0:
            n_rows += 1
        context['n_rows'] = n_rows

        def levels_iterator(start, end, n_steps):
            step = (end - start) / (n_steps - 1)
            i = start
            while i <= end:
                yield i
                i += step

        context['legend_levels'] = list(
            levels_iterator(0, 1, self.legend_levels))

        return context


class HierarchicUserList(ListView):
    model = HierarchicUser
    title = _('Liste des utilisateurs')

    def get_context_data(self, **kwargs):
        context = super(HierarchicUserList, self).get_context_data(**kwargs)
        context['title'] = self.title
        return context


class EquipeView(HierarchicUserList):
    membres = ()

    def get_queryset(self):
        qs = super(EquipeView, self).get_queryset()
        return qs.filter(pk__in=self.membres)


class ComiteEditorialeView(EquipeView):
    membres = (
        5,  # Joann
        6,  # Yannick
        7,  # Patrick
    )
    title = _('Comité éditorial')


class ComiteScientifiqueView(EquipeView):
    membres = (
        5,  # Joann
        6,  # Yannick
        7,  # Patrick
        94,  # Étienne Jardin
        375,  # Frédéric Guérin
        602,  # Manuel Cornejo
        605,  # Déborah Livet
        724,  # Jonathan Parisi
        796,  # Lucia Pasini
        845,  # Yannaël Pasquier
        820,  # Arthur Macé
        843,  # Karine Boulanger
        1062,  # Sabine Le Hir
    )
    title = _('Comité scientifique')


class ContributeursView(EquipeView):
    membres = (
        5,  # Joann
        6,  # Yannick
        7,  # Patrick
        39,  # Claire Morvannou
        80,  # Lucille Brunel
        85,  # Denis Tchorek
        94,  # Étienne Jardin
        95,  # Christine Carrère-Saucède
        98,  # Julie Graine
        102,  # Thomas Bacquet
        168,  # Thomas Vernet
        206,  # Maxime Margollé
        330,  # Jean-Christophe Branger
        337,  # Naomie Charlier
        344,  # Stella Rollet
        375,  # Frédéric Guérin
        472,  # Gabriella Elgarrista
        474,  # Pierre Girod
        482,  # Marion Blanc
        566,  # Myriam Chimènes
        602,  # Manuel Cornejo
        605,  # Déborah Livet
        692,  # Sabine Teulon Lardic
        694,  # Jean-Sébastien Noël
        724,  # Jonathan Parisi
        740,  # Gilles Demonet
        776,  # Danieli Longo
        796,  # Lucia Pasini
        798,  # Jessie Gerbaud
        799,  # Màrius Bernadó
        820,  # Arthur Macé
        841,  # Apolline Gouzi
        843,  # Karine Boulanger
        844,  # Gaëlle Lafage
        845,  # Yannaël Pasquier
        856,  # Peter Asimov
        983,  # Pierrot Menuge
        1062,  # Sabine Le Hir
    )
    title = _('Principaux contributeurs')


class EquipeDeveloppementView(EquipeView):
    membres = (
        1,  # Bertrand
        5,  # Joann
        6,  # Yannick
        7,  # Patrick
    )
    title = _('Équipe de développement')


class ProprietairesView(EquipeView):
    membres = (
        194,  # Université de Rouen
        195,  # Université de Montpellier 3
        196,  # CÉRÉdI
        197,  # GRHis
        198,  # IRCL
    )
    title = _('Propriétaires')


class PartenairesView(EquipeView):
    membres = (
        157,  # AFO
        103,  # Opéra Comique
        297,  # Orchestre de l’Opéra de Rouen Normandie
        332,  # Fondation Royaumont
        871,  # CNSMDP
    )
    title = _('Partenaires')


class HierarchicUserDetail(DetailView):
    model = HierarchicUser
    slug_url_kwarg = 'username'
    slug_field = 'username'
