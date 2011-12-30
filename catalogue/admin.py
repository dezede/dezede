from musicologie.catalogue.models import *
from django.contrib import admin
from reversion import VersionAdmin

class StatutAdmin(VersionAdmin):
    exclude = ['slug']

class NaturedeLieuAdmin(VersionAdmin):
    exclude = ['slug']

class LieuAdmin(VersionAdmin):
    exclude = ['slug']
    filter_horizontal = ['illustrations', 'documents']

class ProfessionAdmin(VersionAdmin):
    exclude = ['slug']

class IndividuAdmin(VersionAdmin):
    exclude = ['slug']
    filter_horizontal = ['professions', 'parents', 'illustrations', 'documents']

class LivretAdmin(VersionAdmin):
    exclude = ['slug']
    filter_horizontal = ['auteurs', 'parents', 'documents', 'illustrations']

class OeuvreAdmin(VersionAdmin):
    exclude = ['slug']
    filter_horizontal = ['auteurs', 'parents', 'documents', 'illustrations']

class RepresentationAdmin(VersionAdmin):
    filter_horizontal = ['illustrations', 'documents']

class EvenementAdmin(VersionAdmin):
    filter_horizontal = ['documents', 'illustrations']

class TypedeSourceAdmin(VersionAdmin):
    exclude = ['slug']

class SourceAdmin(VersionAdmin):
    filter_horizontal = ['documents', 'illustrations']

admin.site.register(Document)
admin.site.register(Illustration)
admin.site.register(Statut, StatutAdmin)
admin.site.register(NaturedeLieu, NaturedeLieuAdmin)
admin.site.register(Lieu, LieuAdmin)
admin.site.register(Saison)
admin.site.register(Profession, ProfessionAdmin)
admin.site.register(Individu, IndividuAdmin)
admin.site.register(Livret, LivretAdmin)
admin.site.register(Oeuvre, OeuvreAdmin)
admin.site.register(Representation, RepresentationAdmin)
admin.site.register(Evenement, EvenementAdmin)
admin.site.register(TypedeSource, TypedeSourceAdmin)
admin.site.register(Source, SourceAdmin)

