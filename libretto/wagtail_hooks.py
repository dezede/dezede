from wagtail.admin.ui.tables import BooleanColumn
from wagtail.permissions import ModelPermissionPolicy
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Individu, Lieu, Oeuvre, Evenement, Partie, Ensemble


class AutoritePermissionPolicy(ModelPermissionPolicy):
    def user_has_permission(self, user, action):
        # if action in {'add', 'change', 'delete'}:
        #     return False
        return super().user_has_permission(user, action)


class AutoriteViewSet(SnippetViewSet):
    list_filter = ['etat']

    @property
    def permission_policy(self):
        return AutoritePermissionPolicy(self.model)


@register_snippet
class EvenementViewSet(AutoriteViewSet):
    model = Evenement
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
    list_display = [
        '__str__', 'naissance', 'deces', 'calc_professions',
    ]
    list_filter = ['titre', *AutoriteViewSet.list_filter]

    def get_queryset(self, request):
        return Individu.objects.select_related(
            'naissance_lieu', 'deces_lieu',
        ).prefetch_related('professions')


@register_snippet
class LieuViewSet(AutoriteViewSet):
    model = Lieu
    list_display = ['__str__', 'nature']
    list_filter = ['nature', *AutoriteViewSet.list_filter]

    def get_queryset(self, request):
        return Lieu.objects.select_related('nature')


@register_snippet
class OeuvreViewSet(AutoriteViewSet):
    model = Oeuvre
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


@register_snippet
class PartieViewSet(AutoriteViewSet):
    model = Partie
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
    list_display = ['__str__', 'type', 'membres_count']

    def get_queryset(self, request):
        return Ensemble.objects.select_related('type')
