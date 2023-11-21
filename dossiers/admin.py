from django.contrib.admin import register
from django.db.models import TextField
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin
from tinymce.widgets import TinyMCE
from libretto.admin import PublishedAdmin
from .forms import DossierDEvenementsForm, DossierForm, DossierDOeuvresForm
from .models import DossierDEvenements, CategorieDeDossiers, DossierDOeuvres


@register(CategorieDeDossiers)
class CategorieDeDossierAdmin(VersionAdmin, PublishedAdmin):
    list_display = ('__str__', 'position')
    list_editable = ('position',)
    fieldsets = (
        (None, {
            'fields': ('nom', 'position')
        }),
    )


class DossierAdmin(VersionAdmin, PublishedAdmin):
    form = DossierForm
    list_display = ('__str__',)
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ('get_count',)
    raw_id_fields = ('editeurs_scientifiques',)
    autocomplete_lookup_fields = {
        'm2m': ('editeurs_scientifiques',),
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
                'publications', 'developpements', 'logo'),
            'classes': ('grp-collapse grp-open',),
        }),
        (_('Article'), {
            'fields': (
                'presentation', 'contexte', 'sources_et_protocole',
                'bibliographie'
            ),
            'classes': ('grp-collapse grp-open',),
        }),
    )
    formfield_overrides = {
        **PublishedAdmin.formfield_overrides,
        TextField: {'widget': TinyMCE},
    }


@register(DossierDEvenements)
class DossierDEvenementsAdmin(DossierAdmin):
    form = DossierDEvenementsForm
    raw_id_fields = DossierAdmin.raw_id_fields + (
        'lieux', 'oeuvres', 'individus', 'ensembles', 'sources', 'evenements',
        'saisons',
    )
    autocomplete_lookup_fields = {
        **DossierAdmin.autocomplete_lookup_fields,
        'm2m': ('editeurs_scientifiques', 'lieux', 'oeuvres', 'individus',
                'ensembles'),
    }
    fieldsets = (
        *DossierAdmin.fieldsets,
        (_('Sélection dynamique'), {
            'fields': ('saisons', ('debut', 'fin'), 'lieux', 'oeuvres',
                       'individus', 'ensembles', 'sources', 'circonstance'),
        }),
        (_('Sélection manuelle'), {
            'fields': ('evenements', 'statique', 'get_count',),
        })
    )


@register(DossierDOeuvres)
class DossierDOeuvresAdmin(DossierAdmin):
    form = DossierDOeuvresForm
    raw_id_fields = DossierAdmin.raw_id_fields + (
        'lieux', 'genres', 'individus', 'ensembles', 'sources', 'oeuvres',
    )
    autocomplete_lookup_fields = {
        **DossierAdmin.autocomplete_lookup_fields,
        'm2m': (
            'editeurs_scientifiques', 'lieux', 'individus', 'ensembles', 'genres',
        ),
    }
    fieldsets = (
        *DossierAdmin.fieldsets,
        (_('Sélection dynamique'), {
            'fields': (
                ('debut', 'fin'), 'lieux', 'genres', 'individus', 'ensembles',
                'sources',
            ),
        }),
        (_('Sélection manuelle'), {
            'fields': ('oeuvres', 'statique', 'get_count',),
        })
    )
