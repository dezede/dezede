# coding: utf-8

from __future__ import unicode_literals
from django.contrib.admin import site
from catalogue.admin import CustomAdmin
from .forms import DossierDEvenementsForm
from .models import DossierDEvenements


class DossierDEvenementsAdmin(CustomAdmin):
    form = DossierDEvenementsForm
    list_display = ('__unicode__', 'circonstance', 'debut', 'fin',
                    'lieux_html', 'oeuvres_html', 'auteurs_html', 'get_count')
    readonly_fields = ('get_count', 'get_queryset')
    raw_id_fields = ('lieux', 'oeuvres', 'auteurs')
    autocomplete_lookup_fields = {
        'm2m': ('lieux', 'oeuvres', 'auteurs'),
    }


site.register(DossierDEvenements, DossierDEvenementsAdmin)
