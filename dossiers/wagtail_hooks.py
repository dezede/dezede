from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from libretto.wagtail_hooks import CommonViewSet

from .forms import DossierWagtailForm
from .models import CategorieDeDossiers, Dossier


# ``DossierWagtailForm`` redeclares ``types_de_donnees`` (a postgres ``ArrayField``
# of choices) as a checkbox multi-select; wire it here rather than on the model
# to avoid a models <-> forms circular import (same pattern as libretto).
Dossier.base_form_class = DossierWagtailForm


@hooks.register('register_icons')
def register_dossier_icons(icons):
    return icons + [
        'wagtailfontawesomesvg/solid/folder-open.svg',
    ]


class CategorieDeDossiersViewSet(CommonViewSet):
    model = CategorieDeDossiers
    icon = 'folder-open'
    list_display = ['nom', 'position', 'etat', *CommonViewSet.list_display]
    filterset_fields = ['etat', *CommonViewSet.filterset_fields]


class DossierViewSet(CommonViewSet):
    model = Dossier
    icon = 'folder-open'
    list_display = ['__str__', 'categorie', 'etat', *CommonViewSet.list_display]
    filterset_fields = ['etat', *CommonViewSet.filterset_fields]


@register_snippet
class DossierViewSetGroup(SnippetViewSetGroup):
    menu_label = _('Dossiers')
    add_to_admin_menu = True
    items = [DossierViewSet, CategorieDeDossiersViewSet]
