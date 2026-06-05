from django.contrib.admin import register
from reversion.admin import VersionAdmin
from libretto.admin import CommonAdmin
from libretto.models.espace_temps import Lieu
from libretto.models.evenement import Evenement
from .models import *


@register(EvenementAFO)
class EvenementAFOAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'code_programme', 'frequentation')
    raw_id_fields = ('evenement',)
    related_lookup_fields = {
        'fk': ('evenement',),
    }

    def get_queryset(self, request):
        qs = super(EvenementAFOAdmin, self).get_queryset(request)
        return qs.select_related(
            'evenement__debut_lieu__nature',
            'evenement__debut_lieu__parent__nature',
            'owner',
        )

    def get_search_results(self, request, queryset, search_term):
        searched_queryset, may_have_duplicates = super().get_search_results(
            request,
            Evenement.objects.filter(pk__in=queryset.values('evenement_id')),
            search_term,
        )
        return queryset.filter(evenement_id__in=searched_queryset), may_have_duplicates


@register(LieuAFO)
class LieuAFOAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'code_postal', 'type_de_scene', 'type_de_salle')
    list_editable = ('code_postal', 'type_de_scene', 'type_de_salle')
    raw_id_fields = ('lieu',)
    related_lookup_fields = {
        'fk': ('lieu',),
    }

    def get_queryset(self, request):
        qs = super(LieuAFOAdmin, self).get_queryset(request)
        return qs.select_related(
            'lieu__parent__nature', 'lieu__nature', 'owner',
        )

    def get_search_results(self, request, queryset, search_term):
        searched_queryset, may_have_duplicates = super().get_search_results(
            request,
            Lieu.objects.filter(pk__in=queryset.values('lieu_id')),
            search_term,
        )
        return queryset.filter(evenement_id__in=searched_queryset), may_have_duplicates
