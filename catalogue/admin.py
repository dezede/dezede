# coding: utf-8
from musicologie.catalogue.models import *
from django.contrib.admin import site, TabularInline, StackedInline
from reversion import VersionAdmin

class AncrageSpatioTemporelInline(TabularInline):
    model = AncrageSpatioTemporel
    classes = ('collapse closed',)

class ElementDeProgrammeInline(StackedInline):
    model = ElementDeProgramme
    classes = ('collapse closed',)

class SourceInline(StackedInline):
    model = Source
    classes = ('collapse closed',)

class EtatAdmin(VersionAdmin):
    exclude = ['slug']

class NatureDeLieuAdmin(VersionAdmin):
    exclude = ['slug']

class LieuAdmin(VersionAdmin):
    exclude = ['slug']
    filter_horizontal = ['illustrations', 'documents']
    inlines = [AncrageSpatioTemporelInline,]
    fieldsets = (
        ('Champs courants', {
            'fields': ('nom', 'parent', 'nature', 'historique',),
        }),
        ('Champs avancés', {
            'classes': ('collapse closed',),
            'fields': ('illustrations', 'documents', 'etat', 'notes',),
        }),
    )

class ProfessionAdmin(VersionAdmin):
    exclude = ['slug']

class AncrageSpatioTemporelAdmin(VersionAdmin):
    list_display = ('__unicode__', 'date', 'heure', 'lieu', 'date_approx',
        'heure_approx', 'lieu_approx', 'calc_date', 'calc_heure', 'calc_lieu',)
    search_fields = ['lieu__nom', 'lieu__parent__nom',]
    fieldsets = (
        ('Champs courants', {
            'fields': ('date', 'heure', 'lieu',),
        }),
        ('Champs avancés', {
            'classes': ('collapse closed',),
            'fields': ('date_approx', 'heure_approx', 'lieu_approx',),
        }),
    )

class IndividuAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'nom_naissance', 'calc_prenoms',
        'pseudonyme', 'sexe', 'ancrage_naissance', 'ancrage_deces',
        'calc_professions')
    exclude = ['slug']
    filter_horizontal = ['prenoms', 'professions', 'parentes', 'illustrations',
        'documents']
    fieldsets = (
        ('Champs courants', {
            'fields': ('nom', 'nom_naissance', 'prenoms', 'pseudonyme',
                        'designation', 'sexe', 'ancrage_naissance',
                        'ancrage_deces', 'professions', 'parentes',),
        }),
        ('Champs avancés', {
            'classes': ('collapse closed',),
            'fields': ('ancrage_approx', 'biographie', 'illustrations',
            'documents', 'etat', 'notes',),
        }),
    )

class EngagementAdmin(VersionAdmin):
    filter_horizontal = ['individus']

class PersonnelAdmin(VersionAdmin):
    filter_horizontal = ['engagements']

class GenreDOeuvreAdmin(VersionAdmin):
    exclude = ['slug']

class OeuvreAdmin(VersionAdmin):
    list_display = ('titre', 'soustitre', 'genre', 'calc_caracteristiques',
        'calc_auteurs', 'ancrage_composition',)
    exclude = ['slug']
    filter_horizontal = ['caracteristiques', 'pupitres', 'auteurs', 'parentes',
        'documents', 'illustrations']
    inlines = [ElementDeProgrammeInline,]
    fieldsets = (
        ('Titre', {
            'fields': ('prefixe_titre', 'titre', 'liaison',
                        'prefixe_soustitre', 'soustitre',),
        }),
        ('Autres champs courants', {
            'fields': ('genre', 'caracteristiques', 'auteurs',
                        'ancrage_composition', 'pupitres', 'parentes',),
        }),
        ('Champs avancés', {
            'classes': ('collapse closed',),
            'fields': ('lilypond', 'description', 'referenced', 'documents',
                        'illustrations', 'etat', 'notes',),
        }),
    )

class AttributionDeRoleAdmin(VersionAdmin):
    filter_horizontal = ['individus']

class ElementDeProgrammeAdmin(VersionAdmin):
    filter_horizontal = ['caracteristiques', 'distribution', 'illustrations',
        'documents']

class EvenementAdmin(VersionAdmin):
    filter_horizontal = ['programme', 'documents', 'illustrations']
    fieldsets = (
        ('Champs courants', {
            'fields': ('ancrage_debut', 'ancrage_fin', 'relache',
                        'circonstance', 'programme',),
        }),
        ('Champs avancés', {
            'classes': ('collapse closed',),
            'fields': ('documents', 'illustrations', 'etat', 'notes',),
        }),
    )

class TypeDeSourceAdmin(VersionAdmin):
    exclude = ['slug']
    inlines = [SourceInline,]

class SourceAdmin(VersionAdmin):
    filter_horizontal = ['evenements', 'documents', 'illustrations']
    fieldsets = (
        ('Champs courants', {
            'fields': ('nom', 'numero', 'date', 'page', 'type', 'contenu',
                        'evenements',),
        }),
        ('Champs avancés', {
            'classes': ('collapse closed',),
            'fields': ('documents', 'illustrations', 'etat', 'notes',),
        }),
    )

site.register(Document)
site.register(Illustration)
site.register(Etat, EtatAdmin)
site.register(NatureDeLieu, NatureDeLieuAdmin)
site.register(Lieu, LieuAdmin)
site.register(Saison)
site.register(Profession, ProfessionAdmin)
site.register(AncrageSpatioTemporel, AncrageSpatioTemporelAdmin)
site.register(Prenom)
site.register(TypeDeParenteDIndividus)
site.register(ParenteDIndividus)
site.register(Individu, IndividuAdmin)
site.register(Devise)
site.register(Engagement, EngagementAdmin)
site.register(TypeDePersonnel)
site.register(Personnel, PersonnelAdmin)
site.register(GenreDOeuvre, GenreDOeuvreAdmin)
site.register(TypeDeCaracteristiqueDOeuvre)
site.register(CaracteristiqueDOeuvre)
site.register(Role)
site.register(Pupitre)
site.register(TypeDeParenteDOeuvres)
site.register(ParenteDOeuvres)
site.register(Oeuvre, OeuvreAdmin)
site.register(AttributionDeRole, AttributionDeRoleAdmin)
site.register(CaracteristiqueDElementDeProgramme)
site.register(ElementDeProgramme, ElementDeProgrammeAdmin)
site.register(Evenement, EvenementAdmin)
site.register(TypeDeSource, TypeDeSourceAdmin)
site.register(Source, SourceAdmin)

