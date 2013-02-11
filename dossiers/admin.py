# coding: utf-8

from __future__ import unicode_literals
from django.contrib.admin import site
from django.utils.translation import ugettext_lazy as _
from catalogue.admin import CustomAdmin
from .forms import DossierDEvenementsForm
from .models import DossierDEvenements


class DossierDEvenementsAdmin(CustomAdmin):
    form = DossierDEvenementsForm
    list_display = ('__unicode__', 'circonstance', 'debut', 'fin',
                    'lieux_html', 'oeuvres_html', 'auteurs_html', 'get_count')
    readonly_fields = ('get_count', 'get_queryset')
    raw_id_fields = ('lieux', 'oeuvres', 'auteurs', 'evenements')
    autocomplete_lookup_fields = {
        'm2m': ('lieux', 'oeuvres', 'auteurs'),
    }
    fieldsets = (
        (None, {
            'fields': ('titre', 'contenu'),
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
