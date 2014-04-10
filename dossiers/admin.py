# coding: utf-8

from __future__ import unicode_literals
from django.conf import settings
from django.contrib.admin import site
from django.db.models import TextField
from reversion import VersionAdmin
from tinymce.widgets import TinyMCE
from cache_tools import cached_ugettext_lazy as _
from libretto.admin import PublishedAdmin
from .forms import DossierDEvenementsForm
from .models import DossierDEvenements


class DossierDEvenementsAdmin(VersionAdmin, PublishedAdmin):
    form = DossierDEvenementsForm
    list_display = ('__str__', 'circonstance', 'debut', 'fin',
                    'lieux_html', 'oeuvres_html', 'auteurs_html',
                    'ensembles_html', 'get_count')
    search_fields = ('titre', 'titre_court',)
    readonly_fields = ('get_count', 'get_queryset')
    raw_id_fields = ('editeurs_scientifiques', 'lieux', 'oeuvres', 'auteurs',
                     'ensembles', 'evenements')
    autocomplete_lookup_fields = {
        'm2m': ('editeurs_scientifiques', 'lieux', 'oeuvres', 'auteurs',
                'ensembles'),
    }
    fieldsets = (
        (None, {
            'fields': ('titre', 'titre_court', ('parent', 'position'))
        }),
        (_('Métadonnées'), {
            'fields': (
                ('editeurs_scientifiques', 'date_publication'),
                'publications', 'developpements',),
            'classes': ('grp-collapse grp-open',),
        }),
        (_('Article'), {
            'fields': ('presentation', 'contexte', 'sources', 'bibliographie'),
            'classes': ('grp-collapse grp-open',),
        }),
        (_('Sélection dynamique'), {
            'fields': (('debut', 'fin'), 'lieux', 'oeuvres', 'auteurs',
                       'ensembles', 'circonstance'),
        }),
        (_('Sélection manuelle'), {
            'fields': ('evenements', 'statique', 'get_count', 'get_queryset'),
        })
    )
    formfield_overrides = {
        TextField: {'widget': TinyMCE},
    }


site.register(DossierDEvenements, DossierDEvenementsAdmin)
