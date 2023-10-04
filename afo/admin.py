from django.contrib.admin import register
from reversion.admin import VersionAdmin
from libretto.admin import CommonAdmin, EvenementAdmin, LieuAdmin
from .models import *


@register(EvenementAFO)
class EvenementAFOAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'code_programme', 'frequentation')
    raw_id_fields = ('evenement',)
    related_lookup_fields = {
        'fk': ('evenement',),
    }
    search_fields = [
        f'evenement__{search_field}'
        for search_field in EvenementAdmin.search_fields
    ]

    def get_queryset(self, request):
        qs = super(EvenementAFOAdmin, self).get_queryset(request)
        return qs.select_related('evenement', 'owner')


@register(LieuAFO)
class LieuAFOAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'code_postal', 'type_de_scene', 'type_de_salle')
    list_editable = ('code_postal', 'type_de_scene', 'type_de_salle')
    raw_id_fields = ('lieu',)
    related_lookup_fields = {
        'fk': ('lieu',),
    }
    search_fields = [
        f'lieu__{search_field}'
        for search_field in LieuAdmin.search_fields
    ]

    def get_queryset(self, request):
        qs = super(LieuAFOAdmin, self).get_queryset(request)
        return qs.select_related('lieu', 'owner')
