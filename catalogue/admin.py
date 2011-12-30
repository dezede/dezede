from musicologie.catalogue.models import *
from django.contrib.admin import site
from reversion import VersionAdmin

class EtatAdmin(VersionAdmin):
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

class EngagementAdmin(VersionAdmin):
    filter_horizontal = ['individus']

class PersonnelAdmin(VersionAdmin):
    filter_horizontal = ['engagements']

class NaturedOeuvreAdmin(VersionAdmin):
    exclude = ['slug']

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

site.register(Document)
site.register(Illustration)
site.register(Etat, EtatAdmin)
site.register(NaturedeLieu, NaturedeLieuAdmin)
site.register(Lieu, LieuAdmin)
site.register(Saison)
site.register(Profession, ProfessionAdmin)
site.register(Individu, IndividuAdmin)
site.register(Devise)
site.register(Engagement, EngagementAdmin)
site.register(Personnel, PersonnelAdmin)
site.register(NaturedOeuvre, NaturedOeuvreAdmin)
site.register(Oeuvre, OeuvreAdmin)
site.register(Representation, RepresentationAdmin)
site.register(Evenement, EvenementAdmin)
site.register(TypedeSource, TypedeSourceAdmin)
site.register(Source, SourceAdmin)

