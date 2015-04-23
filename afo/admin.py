# coding: utf-8

from __future__ import unicode_literals
from django.contrib.admin import site, ModelAdmin
from .models import *


class EvenementAFOAdmin(ModelAdmin):
    list_display = (
        '__str__', 'code_programme', 'exonerees', 'payantes', 'scolaires',
        'frequentation', 'jauge',
    )
    list_editable = (
        'code_programme', 'exonerees', 'payantes', 'scolaires',
        'frequentation', 'jauge',
    )
    raw_id_fields = ('evenement',)
    related_lookup_fields = {
        'fk': ('evenement',),
    }


class LieuAFOAdmin(ModelAdmin):
    list_display = ('__str__', 'code_postal', 'type_de_scene')
    list_editable = ('code_postal', 'type_de_scene')
    raw_id_fields = ('lieu',)
    related_lookup_fields = {
        'fk': ('lieu',),
    }


site.register(EvenementAFO, EvenementAFOAdmin)
site.register(LieuAFO, LieuAFOAdmin)
