from django.contrib import messages
from django.contrib.admin import register
from django.core.exceptions import PermissionDenied
from django.db.models import TextField
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
import reversion
from reversion.admin import VersionAdmin
from tinymce.widgets import TinyMCE
from libretto.admin import PublishedAdmin
from .forms import DossierForm
from .models import CategorieDeDossiers, Dossier, KIND_CHOICES


@register(CategorieDeDossiers)
class CategorieDeDossierAdmin(VersionAdmin, PublishedAdmin):
    list_display = ('__str__', 'position')
    list_editable = ('position',)
    fieldsets = (
        (None, {
            'fields': ('nom', 'position')
        }),
    )


@register(Dossier)
class DossierAdmin(VersionAdmin, PublishedAdmin):
    form = DossierForm
    list_display = ('__str__',)
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ('get_counts_display',)
    change_form_template = 'admin/dossiers/dossier/change_form.html'
    raw_id_fields = (
        'editeurs_scientifiques', 'saisons', 'lieux', 'filtre_oeuvres',
        'individus', 'ensembles', 'filtre_sources', 'genres',
        'types_de_sources', 'evenements', 'oeuvres', 'sources',
    )
    autocomplete_lookup_fields = {
        'm2m': ('editeurs_scientifiques', 'lieux', 'filtre_oeuvres',
                'individus', 'ensembles', 'genres', 'types_de_sources'),
    }
    fieldsets = (
        (None, {
            'fields': ('titre', 'titre_court', 'categorie',
                       ('parent', 'position'),
                       'slug')
        }),
        (_('Métadonnées'), {
            'fields': (
                ('editeurs_scientifiques', 'date_publication'),
                'publications', 'developpements', 'image_couverture'),
            'classes': ('grp-collapse grp-open',),
        }),
        (_('Article'), {
            'fields': (
                'presentation', 'contexte', 'sources_et_protocole',
                'bibliographie'
            ),
            'classes': ('grp-collapse grp-open',),
        }),
        (_('Types de données'), {
            'fields': ('types_de_donnees', 'get_counts_display'),
            'classes': ('grp-collapse grp-open',),
        }),
        (_('Sélection dynamique'), {
            'fields': (
                'saisons', ('debut', 'fin'), 'lieux', 'filtre_oeuvres',
                'individus', 'ensembles', 'filtre_sources', 'circonstance',
                'genres', 'types_de_sources',
            ),
            'classes': ('grp-collapse grp-open', 'dossier-selection-dynamique'),
        }),
        (_('Sélection manuelle des événements'), {
            'fields': ('evenements',),
            'classes': ('grp-collapse grp-open', 'dossier-kind-evenements'),
        }),
        (_('Sélection manuelle des œuvres'), {
            'fields': ('oeuvres',),
            'classes': ('grp-collapse grp-open', 'dossier-kind-oeuvres'),
        }),
        (_('Sélection manuelle des sources'), {
            'fields': ('sources',),
            'classes': ('grp-collapse grp-open', 'dossier-kind-sources'),
        }),
    )
    formfield_overrides = {
        **PublishedAdmin.formfield_overrides,
        TextField: {'widget': TinyMCE},
    }

    def get_urls(self):
        return [
            path('<int:object_id>/convertir-statique/',
                 self.admin_site.admin_view(self.convert_to_static_view),
                 name='dossiers_dossier_convert_static'),
            path('<int:object_id>/reconvertir-dynamique/',
                 self.admin_site.admin_view(self.convert_to_dynamic_view),
                 name='dossiers_dossier_convert_dynamic'),
            *super().get_urls(),
        ]

    def _get_conversion_object(self, request, object_id):
        dossier = get_object_or_404(Dossier, pk=object_id)
        if not self.has_change_permission(request, dossier):
            raise PermissionDenied
        if not dossier.active_kinds:
            raise Http404
        return dossier

    @staticmethod
    def _kind_labels():
        return dict(KIND_CHOICES)

    def convert_to_static_view(self, request, object_id):
        """Snapshots each active kind's dynamic queryset into its manual
        selection, after a confirmation page detailing what will be frozen."""
        dossier = self._get_conversion_object(request, object_id)
        if self._is_fully_static(dossier):
            # Reached by URL although the button is hidden: nothing to do.
            self.message_user(
                request,
                _('« %s » est déjà un dossier statique.') % dossier,
                messages.INFO)
            return redirect('admin:dossiers_dossier_change', dossier.pk)
        labels = self._kind_labels()
        if request.method == 'POST':
            with reversion.create_revision():
                reversion.set_user(request.user)
                reversion.set_comment('Conversion en dossier statique')
                for kind in dossier.active_kinds:
                    getattr(dossier, kind).set(
                        dossier.get_queryset(kind, dynamic=True))
            self.message_user(
                request,
                _('« %s » a été converti en dossier statique.') % dossier,
                messages.SUCCESS)
            return redirect('admin:dossiers_dossier_change', dossier.pk)
        rows = [
            {'label': labels[kind],
             'count': dossier.get_queryset(kind, dynamic=True).count(),
             'static_count': getattr(dossier, kind).count()}
            for kind in dossier.active_kinds]
        context = {
            **self.admin_site.each_context(request),
            'title': _('Convertir en dossier statique'),
            'object': dossier,
            'opts': self.opts,
            'rows': rows,
        }
        return TemplateResponse(
            request, 'admin/dossiers/dossier/convert_to_static.html', context)

    def convert_to_dynamic_view(self, request, object_id):
        """Clears every kind's manual selection so the dossier goes back to
        being computed live from its dynamic criteria."""
        dossier = self._get_conversion_object(request, object_id)
        labels = self._kind_labels()
        if request.method == 'POST':
            with reversion.create_revision():
                reversion.set_user(request.user)
                reversion.set_comment('Reconversion en dossier dynamique')
                for kind in dossier.active_kinds:
                    getattr(dossier, kind).clear()
            self.message_user(
                request,
                _('« %s » a été reconverti en dossier dynamique.') % dossier,
                messages.SUCCESS)
            return redirect('admin:dossiers_dossier_change', dossier.pk)
        rows = [
            {'label': labels[kind],
             'count': dossier.get_queryset(kind, dynamic=True).count(),
             'static_count': getattr(dossier, kind).count()}
            for kind in dossier.active_kinds]
        context = {
            **self.admin_site.each_context(request),
            'title': _('Reconvertir en dossier dynamique'),
            'object': dossier,
            'opts': self.opts,
            'rows': rows,
        }
        return TemplateResponse(
            request, 'admin/dossiers/dossier/convert_to_dynamic.html', context)

    @staticmethod
    def _is_fully_static(dossier):
        """Whether every active kind already carries a manual selection —
        i.e. the dossier is already static and converting it again would
        change nothing."""
        return all(getattr(dossier, kind).exists()
                   for kind in dossier.active_kinds)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        try:
            dossier = Dossier.objects.get(pk=object_id)
        except (Dossier.DoesNotExist, ValueError):
            dossier = None
        if dossier is not None and dossier.active_kinds:
            has_static = any(
                getattr(dossier, kind).exists()
                for kind in dossier.active_kinds)
            extra_context.update(
                show_convert_to_static=not self._is_fully_static(dossier),
                show_convert_to_dynamic=has_static,
                convert_static_url=reverse(
                    'admin:dossiers_dossier_convert_static',
                    args=(dossier.pk,)),
                convert_dynamic_url=reverse(
                    'admin:dossiers_dossier_convert_dynamic',
                    args=(dossier.pk,)),
            )
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)
