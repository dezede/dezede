from musicologie.catalogue.models import *
from django.contrib.admin import site
from reversion import VersionAdmin

class EtatAdmin(VersionAdmin):
    exclude = ['slug']

class NatureDeLieuAdmin(VersionAdmin):
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

class GenreDOeuvreAdmin(VersionAdmin):
    exclude = ['slug']

class OeuvreAdmin(VersionAdmin):
    exclude = ['slug']
    filter_horizontal = ['caracteristiques', 'pupitres', 'auteurs', 'parents', 'documents', 'illustrations']

class ElementDeProgrammeAdmin(VersionAdmin):
    filter_horizontal = ['distribution', 'illustrations', 'documents']

class EvenementAdmin(VersionAdmin):
    filter_horizontal = ['programme', 'documents', 'illustrations']

class TypeDeSourceAdmin(VersionAdmin):
    exclude = ['slug']

class SourceAdmin(VersionAdmin):
    filter_horizontal = ['evenements', 'documents', 'illustrations']

site.register(Document)
site.register(Illustration)
site.register(Etat, EtatAdmin)
site.register(NatureDeLieu, NatureDeLieuAdmin)
site.register(Lieu, LieuAdmin)
site.register(Saison)
site.register(Profession, ProfessionAdmin)
site.register(Individu, IndividuAdmin)
site.register(Devise)
site.register(Engagement, EngagementAdmin)
site.register(Personnel, PersonnelAdmin)
site.register(GenreDOeuvre, GenreDOeuvreAdmin)
site.register(TypeDeCaracteristiqueDOeuvre)
site.register(CaracteristiqueDOeuvre)
site.register(Role)
site.register(Pupitre)
site.register(Oeuvre, OeuvreAdmin)
site.register(AttributionDeRole)
site.register(ElementDeProgramme, ElementDeProgrammeAdmin)
site.register(Evenement, EvenementAdmin)
site.register(TypeDeSource, TypeDeSourceAdmin)
site.register(Source, SourceAdmin)

