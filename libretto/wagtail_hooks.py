from functools import cached_property
from typing import List
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist
from django.db.models import BooleanField, ForeignKey
from django.forms import NumberInput
from django.utils.translation import gettext_lazy as _
from django_filters import RangeFilter
from django_filters.filterset import filterset_factory
from wagtail import hooks
from wagtail.admin.filters import SuffixedMultiWidget, WagtailFilterSet
from wagtail.admin.ui.tables import BaseColumn, BooleanColumn, Column, UserColumn
from wagtail.models import ReferenceIndex
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.chooser import SnippetChooserViewSet
from wagtail.snippets.views.snippets import IndexView, SnippetViewSet, SnippetViewSetGroup
from wagtail_linksnippet.richtext_utils import add_snippet_link_button

from common.utils.text import capfirst
from libretto.models.base import CommonModel

from .models import (
    Individu, Lieu, Oeuvre, Evenement, Partie, Ensemble, Source,
    NatureDeLieu, Etat, CaracteristiqueDeProgramme, GenreDOeuvre,
    Profession, Saison, Audio, Video,
    TypeDEnsemble, TypeDeCaracteristiqueDeProgramme, TypeDeParenteDIndividus,
    TypeDeParenteDOeuvres, TypeDeSource,
)


@hooks.register('register_icons')
def register_icons(icons):
    return icons + [
        'wagtailfontawesomesvg/solid/calendar-day.svg',
        'wagtailfontawesomesvg/solid/child.svg',
        'wagtailfontawesomesvg/solid/location-dot.svg',
        'wagtailfontawesomesvg/solid/book.svg',
        'wagtailfontawesomesvg/solid/book-open.svg',
        'wagtailfontawesomesvg/solid/guitar.svg',
        'wagtailfontawesomesvg/solid/people-group.svg',
        'wagtailfontawesomesvg/solid/book-open.svg',
        'wagtailfontawesomesvg/solid/tools.svg',
        'wagtailfontawesomesvg/solid/file-audio.svg',
        'wagtailfontawesomesvg/solid/file-video.svg',
    ]


@hooks.register('after_create_snippet')
def add_owner(request, instance):
    if isinstance(instance, CommonModel):
        instance.owner = request.user
        instance.save()


# FIXME: Replace with the one from wagtail.admin.filters in >=7.4
class NumberRangeWidget(SuffixedMultiWidget):
    template_name = "wagtailadmin/widgets/range_input.html"
    suffixes = ["min", "max"]

    def __init__(self, attrs=None):
        widgets = (
            NumberInput(attrs={"placeholder": _("Minimum"), "min": "0"}),
            NumberInput(attrs={"placeholder": _("Maximum"), "min": "0"}),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.start, value.stop]
        return [None, None]


class CommonFilterSet(WagtailFilterSet):
    usage_count = RangeFilter(
        field_name="usage_count",
        label=_("Usage count"),
        widget=NumberRangeWidget(),
    )


class CommonIndexView(IndexView):
    def improve_column(self, column: BaseColumn):
        if column.__class__ != Column:
            return column

        attr = getattr(self.model, column.name)
        if callable(attr) and getattr(attr, 'boolean', False):
            return BooleanColumn(
                column.name,
                label=capfirst(getattr(attr, 'short_description', column.name)),
                sort_key=getattr(attr, 'admin_order_field', None),
            )

        try:
            field = self.model._meta.get_field(column.name)
        except FieldDoesNotExist:
            return column

        label = capfirst(field.verbose_name)

        if isinstance(field, BooleanField):
            return BooleanColumn(
                column.name,
                label=label,
                sort_key=column.name,
            )

        if isinstance(field, ForeignKey) and field.related_model is get_user_model():
            return UserColumn(column.name, label=label, sort_key=column.name)

        return column

    @cached_property
    def columns(self):
        return [self.improve_column(col) for col in super().columns]


class CommonViewSet(SnippetViewSet):
    index_view_class = CommonIndexView
    list_display = ['owner']
    filterset_fields = ['owner']

    @property
    def filterset_class(self):
        return filterset_factory(
            self.model, filterset=CommonFilterSet, fields=self.filterset_fields,
        )

    def get_queryset(self, request):
        user = request.user
        qs = self.model.objects.all()
        if not user.is_superuser:
            return qs.filter(owner__in=user.get_descendants(include_self=True))
        qs = qs.annotate(
            usage_count=ReferenceIndex.usage_count_subquery(self.model)
        )
        return qs

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


class AutoriteViewSet(CommonViewSet):
    list_display = ['link', 'etat', *CommonViewSet.list_display]
    filterset_fields = ['etat', *CommonViewSet.filterset_fields]


class EvenementViewSet(AutoriteViewSet):
    model = Evenement
    icon = 'calendar-day'
    list_display = [
        '__str__', 'relache', 'circonstance', 'has_source', 'has_program',
        *AutoriteViewSet.list_display,
    ]
    filterset_fields = ['relache', *AutoriteViewSet.filterset_fields]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'debut_lieu', 'debut_lieu__nature',
            'debut_lieu__parent', 'debut_lieu__parent__nature',
        ).annotate_has_program_and_source()


class IndividuViewSet(AutoriteViewSet):
    model = Individu
    icon = 'child'
    list_display = [
        '__str__', 'naissance', 'deces', 'calc_professions',
        *AutoriteViewSet.list_display,
    ]
    filterset_fields = ['titre', *AutoriteViewSet.filterset_fields]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'naissance_lieu', 'deces_lieu',
        ).prefetch_related('professions')

    def get_chooser_extra_columns(self):
        return [
            Column('prenoms', label=capfirst(_('prénoms'))),
            Column('naissance', label=capfirst(_('naissance'))),
        ]


class LieuViewSet(AutoriteViewSet):
    model = Lieu
    icon = 'location-dot'
    list_display = ['__str__', 'nature', *AutoriteViewSet.list_display]
    filterset_fields = ['nature', *AutoriteViewSet.filterset_fields]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('nature')

    def get_chooser_extra_columns(self):
        return [Column('nature', label=capfirst(_('nature')))]


class OeuvreViewSet(AutoriteViewSet):
    model = Oeuvre
    icon = 'book'
    list_display = [
        '__str__', 'auteurs_html', 'creation', *AutoriteViewSet.list_display,
    ]
    filterset_fields = [
        'genre', 'tonalite', 'arrangement', 'type_extrait', *AutoriteViewSet.filterset_fields,
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
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


class PartieViewSet(AutoriteViewSet):
    model = Partie
    icon = 'guitar'
    list_display = [
        '__str__', 'parent', 'oeuvre', 'classement',
        'premier_interprete', *AutoriteViewSet.list_display,
    ]
    filterset_fields = ['type', *AutoriteViewSet.filterset_fields]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'parent', 'oeuvre', 'premier_interprete'
        )


class EnsembleViewSet(AutoriteViewSet):
    model = Ensemble
    icon = 'people-group'
    list_display = [
        '__str__', 'type', 'membres_count', *AutoriteViewSet.list_display
    ]
    filterset_fields = ['type', *AutoriteViewSet.filterset_fields]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('type')


class SourceViewSet(AutoriteViewSet):
    model = Source
    icon = 'book-open'
    list_display = [
        'titre', 'parent', 'position', 'date', 'type', 'has_events',
        'has_program', 'link', *AutoriteViewSet.list_display,
    ]
    filterset_fields = ['type', *AutoriteViewSet.filterset_fields]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('type')

    def get_chooser_extra_columns(self):
        return [Column('type', label=capfirst(_('type')))]


class EtatViewSet(CommonViewSet):
    model = Etat
    icon = 'view'
    list_display = ['nom', 'nom_pluriel', 'public', *CommonViewSet.list_display]


class CaracteristiqueDeProgrammeViewSet(CommonViewSet):
    model = CaracteristiqueDeProgramme
    icon = 'book-open'
    list_display = ['__str__', 'classement', *CommonViewSet.list_display]


class GenreDOeuvreViewSet(CommonViewSet):
    model = GenreDOeuvre
    icon = 'book'
    list_display = [
        '__str__', 'nom_pluriel', 'has_related_objects', *CommonViewSet.list_display,
    ]


class NatureDeLieuViewSet(CommonViewSet):
    model = NatureDeLieu
    icon = 'location-dot'
    list_display = ['nom', 'nom_pluriel', 'referent', *CommonViewSet.list_display]
    filterset_fields = ['referent', *CommonViewSet.filterset_fields]


class ProfessionViewSet(AutoriteViewSet):
    model = Profession
    icon = 'tools'
    list_display = [
        'nom', 'nom_pluriel', 'nom_feminin', 'nom_feminin_pluriel', 'parent',
        'classement', *AutoriteViewSet.list_display,
    ]


class SaisonViewSet(CommonViewSet):
    model = Saison
    list_display = [
        '__str__', 'lieu', 'ensemble', 'debut', 'fin', 'evenements_count',
        *CommonViewSet.list_display,
    ]


class TypeDEnsembleViewSet(CommonViewSet):
    model = TypeDEnsemble
    icon = 'people-group'
    list_display = ['nom', 'nom_pluriel', 'parent', *CommonViewSet.list_display]


class TypeDeSourceViewSet(CommonViewSet):
    model = TypeDeSource
    icon = 'book-open'
    list_display = ['nom', 'nom_pluriel', *CommonViewSet.list_display]


class TypeDeCaracteristiqueDeProgrammeViewSet(CommonViewSet):
    model = TypeDeCaracteristiqueDeProgramme
    icon = 'book-open'
    list_display = [
        'nom', 'nom_pluriel', 'classement', *CommonViewSet.list_display,
    ]


class TypeDeParenteDIndividuViewSet(CommonViewSet):
    model = TypeDeParenteDIndividus
    icon = 'child'
    list_display = [
        'nom', 'nom_pluriel', 'nom_relatif', 'nom_relatif_pluriel',
        'classement', *CommonViewSet.list_display,
    ]


class TypeDeParenteDOeuvreViewSet(CommonViewSet):
    model = TypeDeParenteDOeuvres
    icon = 'book'
    list_display = [
        'nom', 'nom_pluriel', 'nom_relatif', 'nom_relatif_pluriel',
        'classement', *CommonViewSet.list_display,
    ]


class AudioViewSet(SourceViewSet):
    model = Audio
    icon = 'file-audio'


class VideoViewSet(SourceViewSet):
    model = Video
    icon = 'file-video'


@register_snippet
class EverydayInputViewSetGroup(SnippetViewSetGroup):
    menu_label = _('Saisie courante')
    add_to_admin_menu = True
    items = [
        SourceViewSet, EvenementViewSet, IndividuViewSet, EnsembleViewSet,
        LieuViewSet, OeuvreViewSet,
    ]


@register_snippet
class OccasionalInputSnippetViewSetGroup(SnippetViewSetGroup):
    menu_label = _('Saisie occasionnelle')
    add_to_admin_menu = True
    items = [
        EtatViewSet, CaracteristiqueDeProgrammeViewSet, GenreDOeuvreViewSet,
        PartieViewSet, NatureDeLieuViewSet, ProfessionViewSet, SaisonViewSet,
        TypeDeSourceViewSet, TypeDEnsembleViewSet,
        TypeDeCaracteristiqueDeProgrammeViewSet,
        TypeDeParenteDIndividuViewSet, TypeDeParenteDOeuvreViewSet,
        AudioViewSet, VideoViewSet,
    ]
