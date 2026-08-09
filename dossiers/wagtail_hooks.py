from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from wagtail import hooks
from wagtail.admin.views.generic.base import WagtailAdminTemplateMixin
from wagtail.admin.widgets import Button
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from common.utils.text import capfirst
from libretto.wagtail_hooks import CommonEditView, CommonViewSet, scope_to_owner

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


@hooks.register('register_log_actions')
def register_dossier_log_actions(actions):
    # ``ModelLogEntry.save()`` full-cleans the action against this registry, so
    # an unregistered action raises rather than silently vanishing from the
    # History tab. Wagtail core already maps ``models.Model`` to
    # ``ModelLogEntry``, so only the two actions need declaring.
    actions.register_action(
        'dossiers.convert_to_static',
        _('Conversion en dossier statique'),
        _('Converti en dossier statique'))
    actions.register_action(
        'dossiers.convert_to_dynamic',
        _('Reconversion en dossier dynamique'),
        _('Reconverti en dossier dynamique'))


class DossierConversionView(WagtailAdminTemplateMixin, View):
    """Confirmation page + action for the static <-> dynamic conversions.

    The behaviour itself lives on ``Dossier``; this only handles permissions,
    the confirmation page and the messages.
    """
    header_icon = 'folder-open'
    # All injected by ``DossierViewSet.get_conversion_view_kwargs()``.
    permission_policy = None
    edit_url_name = None
    index_url_name = None

    def dispatch(self, request, *args, pk=None, **kwargs):
        self.object = self.get_object(pk)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, pk):
        dossier = get_object_or_404(
            scope_to_owner(Dossier.objects.all(), self.request.user), pk=pk)
        if not self.permission_policy.user_has_permission_for_instance(
                self.request.user, 'change', dossier):
            raise PermissionDenied
        if not dossier.active_kinds:
            raise Http404
        return dossier

    def get_edit_url(self):
        return reverse(self.edit_url_name, args=(self.object.pk,))

    def get_breadcrumbs_items(self):
        return self.breadcrumbs_items + [
            {'url': reverse(self.index_url_name),
             'label': capfirst(Dossier._meta.verbose_name_plural)},
            {'url': self.get_edit_url(), 'label': str(self.object)},
            {'url': '', 'label': self.get_page_title()},
        ]

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            object=self.object,
            rows=self.object.conversion_rows(),
            edit_url=self.get_edit_url(),
            **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.convert(request.user)
        messages.success(request, self.success_message % self.object)
        return redirect(self.get_edit_url())


class ConvertToStaticView(DossierConversionView):
    page_title = _('Convertir en dossier statique')
    template_name = 'wagtailadmin/dossiers/dossier/convert_to_static.html'
    success_message = _('« %s » a été converti en dossier statique.')

    def get(self, request, *args, **kwargs):
        if self.object.is_fully_static:
            # Reached by URL although the button is hidden: nothing to do.
            messages.info(
                request,
                _('« %s » est déjà un dossier statique.') % self.object)
            return redirect(self.get_edit_url())
        return super().get(request, *args, **kwargs)

    def convert(self, user):
        self.object.convert_to_static(user)


class ConvertToDynamicView(DossierConversionView):
    page_title = _('Reconvertir en dossier dynamique')
    template_name = 'wagtailadmin/dossiers/dossier/convert_to_dynamic.html'
    success_message = _('« %s » a été reconverti en dossier dynamique.')

    def convert(self, user):
        self.object.convert_to_dynamic(user)


class DossierEditView(CommonEditView):
    # Injected by ``DossierViewSet.get_edit_view_kwargs()``.
    convert_static_url_name = None
    convert_dynamic_url_name = None

    def get_header_more_buttons(self):
        buttons = super().get_header_more_buttons()
        dossier = self.object
        if dossier.active_kinds and self.user_has_permission('change'):
            if not dossier.is_fully_static:
                buttons.append(Button(
                    _('Convertir en dossier statique'),
                    url=reverse(self.convert_static_url_name,
                                args=(dossier.pk,)),
                    icon_name='folder-open',
                    priority=20))
            if dossier.has_static_selection:
                buttons.append(Button(
                    _('Reconvertir en dossier dynamique'),
                    url=reverse(self.convert_dynamic_url_name,
                                args=(dossier.pk,)),
                    icon_name='folder-open',
                    priority=25))
        return sorted(buttons)


class CategorieDeDossiersViewSet(CommonViewSet):
    model = CategorieDeDossiers
    icon = 'folder-open'
    list_display = ['nom', 'position', 'etat', *CommonViewSet.list_display]
    filterset_fields = ['etat', *CommonViewSet.filterset_fields]


class DossierViewSet(CommonViewSet):
    model = Dossier
    icon = 'folder-open'
    edit_view_class = DossierEditView
    list_display = ['__str__', 'categorie', 'etat', *CommonViewSet.list_display]
    filterset_fields = ['etat', *CommonViewSet.filterset_fields]

    def get_conversion_view_kwargs(self):
        return {
            'permission_policy': self.permission_policy,
            'edit_url_name': self.get_url_name('edit'),
            'index_url_name': self.get_url_name('list'),
        }

    def get_edit_view_kwargs(self, **kwargs):
        return super().get_edit_view_kwargs(
            convert_static_url_name=self.get_url_name('convert_static'),
            convert_dynamic_url_name=self.get_url_name('convert_dynamic'),
            **kwargs,
        )

    def get_urlpatterns(self):
        conversion_kwargs = self.get_conversion_view_kwargs()
        return super().get_urlpatterns() + [
            path('convertir-statique/<int:pk>/',
                 ConvertToStaticView.as_view(**conversion_kwargs),
                 name='convert_static'),
            path('reconvertir-dynamique/<int:pk>/',
                 ConvertToDynamicView.as_view(**conversion_kwargs),
                 name='convert_dynamic'),
        ]


@register_snippet
class DossierViewSetGroup(SnippetViewSetGroup):
    menu_label = _('Dossiers')
    add_to_admin_menu = True
    items = [DossierViewSet, CategorieDeDossiersViewSet]
