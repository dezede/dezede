# coding: utf-8

from __future__ import unicode_literals
from django.contrib.admin import site
from cache_tools import cached_ugettext_lazy as _
from libretto.admin import PublishedAdmin
from .forms import DossierDEvenementsForm
from .models import DossierDEvenements


class DossierDEvenementsAdmin(PublishedAdmin):
    form = DossierDEvenementsForm
    list_display = ('__str__', 'circonstance', 'debut', 'fin',
                    'lieux_html', 'oeuvres_html', 'auteurs_html', 'get_count')
    readonly_fields = ('get_count', 'get_queryset')
    raw_id_fields = ('lieux', 'oeuvres', 'auteurs', 'evenements')
    autocomplete_lookup_fields = {
        'm2m': ('lieux', 'oeuvres', 'auteurs'),
    }
    fieldsets = (
        (None, {
            'fields': ('titre', 'parent', 'contenu'),
        }),
        (_('Sélection dynamique'), {
            'fields': ('debut', 'fin', 'lieux', 'oeuvres', 'auteurs',
                       'circonstance'),
        }),
        (_('Sélection manuelle'), {
            'fields': ('evenements', 'statique', 'get_count', 'get_queryset'),
        })
    )


site.register(DossierDEvenements, DossierDEvenementsAdmin)
