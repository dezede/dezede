from django.contrib import messages
from django.contrib.admin import register
from django.contrib.admin.checks import ModelAdminChecks
from django.contrib.admin.widgets import ManyToManyRawIdWidget
from django.core.exceptions import PermissionDenied
from django.db.models import TextField
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin
from tinymce.widgets import TinyMCE
from libretto.admin import PublishedAdmin
from .forms import DossierForm
from .models import CategorieDeDossiers, Dossier


@register(CategorieDeDossiers)
class CategorieDeDossierAdmin(VersionAdmin, PublishedAdmin):
    list_display = ('__str__', 'position')
    list_editable = ('position',)
    fieldsets = (
        (None, {
            'fields': ('nom', 'position')
        }),
    )


# Dossier's ManyToManyFields go through explicit models so the Wagtail admin can
# offer searchable choosers (``MultipleChooserPanel``). Django's admin then
# raises ``admin.E013``, which forbids a manually-``through`` M2M in ``fields``
# /``fieldsets``, and ``formfield_for_manytomany()`` builds no form field for
# one at all. Both guard against through models carrying extra data the admin
# would silently ignore; ours carry none beyond their two foreign keys, so
# ``ModelForm._save_m2m()`` can still ``set()`` them and the historical raw-id
# widgets keep working. Lifting the two restrictions below for these fields
# only leaves the rest of this admin — fieldsets, widgets, JS — untouched.
DOSSIER_M2M_FIELDS = frozenset((
    'editeurs_scientifiques', 'saisons', 'lieux', 'filtre_oeuvres',
    'individus', 'ensembles', 'filtre_sources', 'genres',
    'types_de_sources', 'evenements', 'oeuvres', 'sources',
))


class DossierAdminChecks(ModelAdminChecks):
    def _check_field_spec_item(self, obj, field_name, label):
        if field_name in DOSSIER_M2M_FIELDS:
            return []
        return super()._check_field_spec_item(obj, field_name, label)


@register(Dossier)
class DossierAdmin(VersionAdmin, PublishedAdmin):
    checks_class = DossierAdminChecks
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

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # ``ModelAdmin`` builds no form field at all for a manually-``through``
        # M2M, which would drop these from the fieldsets above. Build the very
        # same raw-id field the base implementation produced when the through
        # models were auto-created — they are all listed in ``raw_id_fields``.
        if db_field.name in DOSSIER_M2M_FIELDS:
            kwargs.setdefault(
                'widget',
                ManyToManyRawIdWidget(db_field.remote_field, self.admin_site))
            return db_field.formfield(**kwargs)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

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

    def _conversion_context(self, request, dossier, title):
        return {
            **self.admin_site.each_context(request),
            'title': title,
            'object': dossier,
            'opts': self.opts,
            'rows': dossier.conversion_rows(),
        }

    def convert_to_static_view(self, request, object_id):
        """Snapshots each active kind's dynamic queryset into its manual
        selection, after a confirmation page detailing what will be frozen."""
        dossier = self._get_conversion_object(request, object_id)
        if dossier.is_fully_static:
            # Reached by URL although the button is hidden: nothing to do.
            self.message_user(
                request,
                _('« %s » est déjà un dossier statique.') % dossier,
                messages.INFO)
            return redirect('admin:dossiers_dossier_change', dossier.pk)
        if request.method == 'POST':
            dossier.convert_to_static(request.user)
            self.message_user(
                request,
                _('« %s » a été converti en dossier statique.') % dossier,
                messages.SUCCESS)
            return redirect('admin:dossiers_dossier_change', dossier.pk)
        return TemplateResponse(
            request, 'admin/dossiers/dossier/convert_to_static.html',
            self._conversion_context(
                request, dossier, _('Convertir en dossier statique')))

    def convert_to_dynamic_view(self, request, object_id):
        """Clears every kind's manual selection so the dossier goes back to
        being computed live from its dynamic criteria."""
        dossier = self._get_conversion_object(request, object_id)
        if request.method == 'POST':
            dossier.convert_to_dynamic(request.user)
            self.message_user(
                request,
                _('« %s » a été reconverti en dossier dynamique.') % dossier,
                messages.SUCCESS)
            return redirect('admin:dossiers_dossier_change', dossier.pk)
        return TemplateResponse(
            request, 'admin/dossiers/dossier/convert_to_dynamic.html',
            self._conversion_context(
                request, dossier, _('Reconvertir en dossier dynamique')))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        try:
            dossier = Dossier.objects.get(pk=object_id)
        except (Dossier.DoesNotExist, ValueError):
            dossier = None
        if dossier is not None and dossier.active_kinds:
            extra_context.update(
                show_convert_to_static=not dossier.is_fully_static,
                show_convert_to_dynamic=dossier.has_static_selection,
                convert_static_url=reverse(
                    'admin:dossiers_dossier_convert_static',
                    args=(dossier.pk,)),
                convert_dynamic_url=reverse(
                    'admin:dossiers_dossier_convert_dynamic',
                    args=(dossier.pk,)),
            )
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)
