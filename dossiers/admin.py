# coding: utf-8

from __future__ import unicode_literals
from django.contrib.admin import site
from django.db.models import TextField
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin
from tinymce.widgets import TinyMCE
from libretto.admin import PublishedAdmin
from .forms import DossierDEvenementsForm
from .models import DossierDEvenements, CategorieDeDossiers


class CategorieDeDossierAdmin(VersionAdmin, PublishedAdmin):
    list_display = ('__str__', 'position')
    list_editable = ('position',)
    fieldsets = (
        (None, {
            'fields': ('nom', 'position')
        }),
    )


class DossierDEvenementsAdmin(VersionAdmin, PublishedAdmin):
    form = DossierDEvenementsForm
    list_display = ('__str__',)
    search_fields = ('titre', 'titre_court',)
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ('get_count', 'get_queryset')
    raw_id_fields = ('editeurs_scientifiques', 'lieux', 'oeuvres', 'auteurs',
                     'ensembles', 'sources', 'evenements', 'saisons')
    autocomplete_lookup_fields = {
        'm2m': ('editeurs_scientifiques', 'lieux', 'oeuvres', 'auteurs',
                'ensembles'),
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
                'publications', 'developpements',),
            'classes': ('grp-collapse grp-open',),
        }),
        (_('Article'), {
            'fields': (
                'presentation', 'contexte', 'sources_et_protocole',
                'bibliographie'
            ),
            'classes': ('grp-collapse grp-open',),
        }),
        (_('Sélection dynamique'), {
            'fields': ('saisons', ('debut', 'fin'), 'lieux', 'oeuvres',
                       'auteurs', 'ensembles', 'sources', 'circonstance'),
        }),
        (_('Sélection manuelle'), {
            'fields': ('evenements', 'statique', 'get_count', 'get_queryset'),
        })
    )
    formfield_overrides = {
        TextField: {'widget': TinyMCE},
    }


site.register(CategorieDeDossiers, CategorieDeDossierAdmin)
site.register(DossierDEvenements, DossierDEvenementsAdmin)
