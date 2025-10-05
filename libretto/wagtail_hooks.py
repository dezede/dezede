from typing import List
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.ui.tables import BaseColumn, BooleanColumn, Column
from wagtail.permissions import ModelPermissionPolicy
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.chooser import SnippetChooserViewSet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.snippets.wagtail_hooks import SnippetsMenuItem
from wagtail_linksnippet.richtext_utils import add_snippet_link_button

from common.utils.text import capfirst

from .models import Individu, Lieu, Oeuvre, Evenement, Partie, Ensemble


@hooks.register('register_icons')
def register_icons(icons):
    return icons + [
        'wagtailfontawesomesvg/solid/calendar-day.svg',
        'wagtailfontawesomesvg/solid/child.svg',
        'wagtailfontawesomesvg/solid/location-dot.svg',
        'wagtailfontawesomesvg/solid/book.svg',
        'wagtailfontawesomesvg/solid/guitar.svg',
        'wagtailfontawesomesvg/solid/people-group.svg',
    ]

@hooks.register('construct_main_menu')
def hide_snippets_menu_item(request, menu_items):
    menu_items[:] = [item for item in menu_items if not isinstance(item, SnippetsMenuItem)]


class AutoritePermissionPolicy(ModelPermissionPolicy):
    def user_has_permission(self, user, action):
        if action in {'add', 'change', 'delete'}:
            return False
        return super().user_has_permission(user, action)


class AutoriteViewSet(SnippetViewSet):
    list_filter = ['etat']

    @property
    def permission_policy(self):
        return AutoritePermissionPolicy(self.model)

    def get_chooser_extra_columns(self):
        return []

    def get_chooser_columns(self, original_columns: List[BaseColumn]):
        return [
            Column('id', 'ID'),
            *original_columns,
            *self.get_chooser_extra_columns(),
            Column('link', label=_('Lien')),
        ]

    @property
    def chooser_viewset_class(self):
        get_columns = self.get_chooser_columns
        class CustomChooseView(SnippetChooserViewSet.choose_view_class):
            @property
            def columns(self):
                return get_columns([self.title_column])


        class CustomChooseResultsView(SnippetChooserViewSet.choose_results_view_class):
            @property
            def columns(self):
                return get_columns([self.title_column])

        class CustomChooserViewSet(SnippetChooserViewSet):
            choose_view_class = CustomChooseView
            choose_results_view_class = CustomChooseResultsView

        return CustomChooserViewSet

    @property
    def chooser_viewset(self):
        viewset = super().chooser_viewset
        add_snippet_link_button(viewset, feature_name=f'{self.model._meta.model_name}-link')
        return viewset


@register_snippet
class EvenementViewSet(AutoriteViewSet):
    model = Evenement
    icon = 'calendar-day'
    list_display = [
        '__str__', BooleanColumn('relache'), 'circonstance',
        BooleanColumn('has_source'), BooleanColumn('has_program'),
    ]
    list_filter = ['relache', *AutoriteViewSet.list_filter]

    def get_queryset(self, request):
        return Evenement.objects.select_related(
            'debut_lieu', 'debut_lieu__nature',
            'debut_lieu__parent', 'debut_lieu__parent__nature',
        ).annotate_has_program_and_source()


@register_snippet
class IndividuViewSet(AutoriteViewSet):
    model = Individu
    icon = 'child'
    list_display = [
        '__str__', 'naissance', 'deces', 'calc_professions',
    ]
    list_filter = ['titre', *AutoriteViewSet.list_filter]

    def get_queryset(self, request):
        return Individu.objects.select_related(
            'naissance_lieu', 'deces_lieu',
        ).prefetch_related('professions')

    def get_chooser_extra_columns(self):
        return [
            Column('prenoms', label=capfirst(_('prénoms'))),
            Column('naissance', label=capfirst(_('naissance'))),
        ]


@register_snippet
class LieuViewSet(AutoriteViewSet):
    model = Lieu
    icon = 'location-dot'
    list_display = ['__str__', 'nature']
    list_filter = ['nature', *AutoriteViewSet.list_filter]

    def get_queryset(self, request):
        return Lieu.objects.select_related('nature')

    def get_chooser_extra_columns(self):
        return [Column('nature', label=capfirst(_('nature')))]


@register_snippet
class OeuvreViewSet(AutoriteViewSet):
    model = Oeuvre
    icon = 'book'
    list_display = ['__str__', 'auteurs_html', 'creation']
    list_filter = [
        'genre', 'tonalite', 'arrangement', 'type_extrait', *AutoriteViewSet.list_filter,
    ]

    def get_queryset(self, request):
        return Oeuvre.objects.select_related(
            'genre', 'extrait_de__genre', 'creation_lieu',
        ).prefetch_related(
            'pupitres__partie',
            'auteurs__individu',
            'auteurs__profession',
            'extrait_de__pupitres__partie',
        )

    def get_chooser_extra_columns(self):
        return [
            Column('auteurs_html', label=_('Auteurs')),
            Column('creation', label=_('Création')),
        ]


@register_snippet
class PartieViewSet(AutoriteViewSet):
    model = Partie
    icon = 'guitar'
    list_display = [
        '__str__', 'parent', 'oeuvre', 'classement',
        'premier_interprete',
    ]
    list_filter = ['type', *AutoriteViewSet.list_filter]

    def get_queryset(self, request):
        return Partie.objects.select_related('parent', 'oeuvre', 'premier_interprete')


@register_snippet
class EnsembleViewSet(AutoriteViewSet):
    model = Ensemble
    icon = 'people-group'
    list_display = ['__str__', 'type', 'membres_count']

    def get_queryset(self, request):
        return Ensemble.objects.select_related('type')
