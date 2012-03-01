# coding: utf-8
from musicologie.catalogue.models import *
from django.contrib.admin import site, TabularInline, StackedInline
from reversion import VersionAdmin

TabularInline.extra = 1
StackedInline.extra = 1

class AncrageSpatioTemporelInline(TabularInline):
    model = AncrageSpatioTemporel
    classes = ('collapse closed',)

class ElementDeProgrammeInline(StackedInline):
    model = ElementDeProgramme
    classes = ('collapse closed',)

class SourceInline(StackedInline):
    model = Source
    classes = ('collapse closed',)

class DocumentAdmin(VersionAdmin):
    list_display = ('nom', 'document',)
    search_fields = ('nom',)

class IllustrationAdmin(VersionAdmin):
    list_display = ('legende', 'image',)
    search_fields = ('legende',)

class EtatAdmin(VersionAdmin):
    exclude = ('slug',)

class NatureDeLieuAdmin(VersionAdmin):
    exclude = ('slug',)

class LieuAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'parent', 'nature',)
    search_fields = ('nom', 'parent__nom',)
    list_filter = ('nature__nom',)
    exclude = ('slug',)
    filter_horizontal = ('illustrations', 'documents',)
    inlines = (AncrageSpatioTemporelInline,)
    fieldsets = (
        ('Champs courants', {
            'fields': ('nom', 'parent', 'nature', 'historique',),
        }),
        ('Champs avancés', {
            'classes': ('collapse closed',),
            'fields': ('illustrations', 'documents', 'etat', 'notes',),
        }),
    )

class SaisonAdmin(VersionAdmin):
    list_display = ('__unicode__', 'lieu', 'debut', 'fin',)

class ProfessionAdmin(VersionAdmin):
    exclude = ('slug',)

class AncrageSpatioTemporelAdmin(VersionAdmin):
    list_display = ('__unicode__', 'calc_date', 'calc_heure', 'calc_lieu',)
    search_fields = ('lieu__nom', 'lieu_approx', 'date_approx',
        'lieu__parent__nom', 'heure_approx',)
    fieldsets = (
        ('Champs courants', {
            'fields': ('date', 'heure', 'lieu',),
        }),
        ('Champs avancés', {
            'classes': ('collapse open',),
            'fields': ('date_approx', 'heure_approx', 'lieu_approx',),
        }),
    )

class PrenomAdmin(VersionAdmin):
    list_display = ('__unicode__', 'prenom', 'classement', 'favori',)

class IndividuAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'nom_naissance', 'calc_prenoms',
        'pseudonyme', 'sexe', 'ancrage_naissance', 'ancrage_deces',
        'calc_professions', 'link',)
    search_fields = ('nom', 'pseudonyme', 'nom_naissance',)
    list_filter = ('sexe',)
    exclude = ('slug',)
    filter_horizontal = ('prenoms', 'professions', 'parentes', 'illustrations',
        'documents',)
    readonly_fields = ('__unicode__', 'html', 'link',)
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
        ('Champs générés (Méthodes)', {
            'classes': ('collapse closed',),
            'fields': ('__unicode__', 'html', 'link',),
        }),
    )

class EngagementAdmin(VersionAdmin):
    list_display = ('__unicode__', 'profession', 'salaire', 'devise',)
    filter_horizontal = ('individus',)

class PersonnelAdmin(VersionAdmin):
    filter_horizontal = ('engagements',)

class GenreDOeuvreAdmin(VersionAdmin):
    exclude = ('slug',)
    filter_horizontal = ('parents',)

class CaracteristiqueDOeuvreAdmin(VersionAdmin):
    list_display = ('__unicode__', 'type', 'valeur', 'classement')

class PartieAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'parente', 'classement')
    filter_horizontal = ('professions',)

class ParenteDOeuvresAdmin(VersionAdmin):
    filter_horizontal = ('oeuvres_cibles',)

class AuteurAdmin(VersionAdmin):
    filter_horizontal = ('individus',)
    def save_model(self, request, obj, form, change):
        obj.save()
        for individu in form.cleaned_data['individus']:
            individu.professions.add(obj.profession)

class OeuvreAdmin(VersionAdmin):
    list_display = ('__unicode__', 'titre', 'titre_secondaire', 'genre', 'calc_caracteristiques',
        'calc_auteurs', 'ancrage_composition', 'link',)
    search_fields = ('titre', 'titre_secondaire', 'genre__nom',)
    list_filter = ('genre__nom',)
    exclude = ('slug',)
    filter_horizontal = ['caracteristiques', 'pupitres', 'auteurs', 'parentes',
        'documents', 'illustrations']
    readonly_fields = ('__unicode__', 'html', 'link',)
    inlines = (ElementDeProgrammeInline,)
    fieldsets = (
        ('Titre', {
            'fields': ('prefixe_titre', 'titre', 'coordination',
                        'prefixe_titre_secondaire', 'titre_secondaire',),
        }),
        ('Autres champs courants', {
            'fields': ('genre', 'caracteristiques', 'auteurs',
                        'ancrage_composition', 'pupitres', 'parentes',),
        }),
        ('Champs avancés', {
            'classes': ('collapse closed',),
            'fields': ('lilypond', 'description', 'documents', 'illustrations',
                        'etat', 'notes',),
        }),
        ('Champs générés (Méthodes)', {
            'classes': ('collapse closed',),
            'fields': ('__unicode__', 'html', 'link',),
        }),
    )

class AttributionDePupitreAdmin(VersionAdmin):
    filter_horizontal = ('individus',)

class ElementDeProgrammeAdmin(VersionAdmin):
    list_display = ('oeuvre', 'autre', 'classement',)
    filter_horizontal = ('caracteristiques', 'distribution', 'personnels',
        'illustrations', 'documents',)

class EvenementAdmin(VersionAdmin):
    list_display = ('__unicode__', 'relache', 'circonstance', 'link',)
    search_fields = ('circonstance',)
    list_filter = ('relache',)
    filter_horizontal = ('programme', 'documents', 'illustrations',)
    readonly_fields = ('__unicode__', 'html', 'link',)
    fieldsets = (
        ('Champs courants', {
            'fields': ('ancrage_debut', 'ancrage_fin', 'relache',
                        'circonstance', 'programme',),
        }),
        ('Champs avancés', {
            'classes': ('collapse closed',),
            'fields': ('documents', 'illustrations', 'etat', 'notes',),
        }),
        ('Champs générés (Méthodes)', {
            'classes': ('collapse closed',),
            'fields': ('__unicode__', 'html', 'link',),
        }),
    )

class TypeDeSourceAdmin(VersionAdmin):
    exclude = ('slug',)
    inlines = (SourceInline,)

class SourceAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'numero', 'date', 'page', 'type', 'disp_contenu',)
    search_fields = ('nom', 'numero', 'type__nom',)
    list_filter = ('type__nom',)
    filter_horizontal = ('evenements', 'documents', 'illustrations',)
    readonly_fields = ('__unicode__', 'html',)
    fieldsets = (
        ('Champs courants', {
            'fields': ('nom', 'numero', 'date', 'page', 'type', 'contenu',
                        'evenements',),
        }),
        ('Champs avancés', {
            'classes': ('collapse closed',),
            'fields': ('documents', 'illustrations', 'etat', 'notes',),
        }),
        ('Champs générés (Méthodes)', {
            'classes': ('collapse closed',),
            'fields': ('__unicode__', 'html',),
        }),
    )

site.register(Document, DocumentAdmin)
site.register(Illustration, IllustrationAdmin)
site.register(Etat, EtatAdmin)
site.register(NatureDeLieu, NatureDeLieuAdmin)
site.register(Lieu, LieuAdmin)
site.register(Saison, SaisonAdmin)
site.register(Profession, ProfessionAdmin)
site.register(AncrageSpatioTemporel, AncrageSpatioTemporelAdmin)
site.register(Prenom, PrenomAdmin)
site.register(TypeDeParenteDIndividus)
site.register(ParenteDIndividus)
site.register(Individu, IndividuAdmin)
site.register(Devise)
site.register(Engagement, EngagementAdmin)
site.register(TypeDePersonnel)
site.register(Personnel, PersonnelAdmin)
site.register(GenreDOeuvre, GenreDOeuvreAdmin)
site.register(TypeDeCaracteristiqueDOeuvre)
site.register(CaracteristiqueDOeuvre, CaracteristiqueDOeuvreAdmin)
site.register(Partie, PartieAdmin)
site.register(Pupitre)
site.register(TypeDeParenteDOeuvres)
site.register(ParenteDOeuvres, ParenteDOeuvresAdmin)
site.register(Auteur, AuteurAdmin)
site.register(Oeuvre, OeuvreAdmin)
site.register(AttributionDePupitre, AttributionDePupitreAdmin)
site.register(CaracteristiqueDElementDeProgramme)
site.register(ElementDeProgramme, ElementDeProgrammeAdmin)
site.register(Evenement, EvenementAdmin)
site.register(TypeDeSource, TypeDeSourceAdmin)
site.register(Source, SourceAdmin)

