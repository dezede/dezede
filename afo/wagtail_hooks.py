from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from libretto.wagtail_hooks import CommonViewSet

from .models import EvenementAFO, LieuAFO


@hooks.register('register_icons')
def register_icons(icons):
    return icons + ['wagtailfontawesomesvg/solid/music.svg']


class EvenementAFOViewSet(CommonViewSet):
    model = EvenementAFO
    icon = 'calendar-day'
    menu_label = _('événements AFO')
    menu_name = 'evenements-afo'
    add_to_admin_menu = False
    list_display = [
        '__str__', 'code_programme', 'frequentation',
        *CommonViewSet.list_display,
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'evenement__debut_lieu__nature',
            'evenement__debut_lieu__parent__nature',
            'owner',
        )


class LieuAFOViewSet(CommonViewSet):
    model = LieuAFO
    icon = 'location-dot'
    menu_label = _('lieux et institutions AFO')
    menu_name = 'lieux-afo'
    add_to_admin_menu = False
    list_display = [
        '__str__', 'code_postal', 'type_de_scene', 'type_de_salle',
        *CommonViewSet.list_display,
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'lieu__parent__nature', 'lieu__nature', 'owner',
        )


@register_snippet
class AFOViewSetGroup(SnippetViewSetGroup):
    menu_label = _('AFO')
    menu_icon = 'music'
    add_to_admin_menu = True
    items = (EvenementAFOViewSet, LieuAFOViewSet)
