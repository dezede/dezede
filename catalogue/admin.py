# coding: utf-8
from musicologie.catalogue.models import *
from django.contrib.admin import site, TabularInline, StackedInline
from reversion import VersionAdmin
from django.utils.translation import ugettext_lazy as _

TabularInline.extra = 0
StackedInline.extra = 0


class AncrageSpatioTemporelInline(TabularInline):
    model = AncrageSpatioTemporel
    classes = ('collapse closed',)


class AuteurInline(TabularInline):
    verbose_name = Auteur._meta.verbose_name
    verbose_name_plural = Auteur._meta.verbose_name_plural
    model = Auteur.individus.through
    classes = ('collapse closed',)


class ElementDeProgrammeInline(StackedInline):
    model = ElementDeProgramme
    classes = ('collapse closed',)


class EvenementInline(TabularInline):
    verbose_name = Evenement._meta.verbose_name
    verbose_name_plural = Evenement._meta.verbose_name_plural
    model = Evenement.programme.through
    classes = ('collapse closed',)


class DocumentAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'document',)
    list_editable = ('nom', 'document',)
    search_fields = ('nom',)


class IllustrationAdmin(VersionAdmin):
    list_display = ('__unicode__', 'legende', 'image',)
    list_editable = ('legende', 'image',)
    search_fields = ('legende',)


class EtatAdmin(VersionAdmin):
    exclude = ('slug',)


class NatureDeLieuAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel',)
    list_editable = ('nom', 'nom_pluriel',)
    exclude = ('slug',)


class LieuAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'parent', 'nature', 'link',)
    list_editable = ('nom', 'parent', 'nature',)
    search_fields = ('nom', 'parent__nom',)
    list_filter = ('nature__nom',)
    raw_id_fields = ('parent', 'illustrations', 'documents',)
    autocomplete_lookup_fields = {
        'fk': ['parent'],
        'm2m': ['illustrations', 'documents'],
    }
    filter_horizontal = ('illustrations', 'documents',)
    readonly_fields = ('__unicode__', 'html', 'link',)
    inlines = (AncrageSpatioTemporelInline,)
    fieldsets = (
        (_('Champs courants'), {
            'fields': ('nom', 'parent', 'nature', 'historique',),
        }),
        (_('Fichiers'), {
            'classes': ('collapse closed',),
            'fields': ('illustrations', 'documents',),
        }),
        (_(u'Champs avancés'), {
            'classes': ('collapse closed',),
            'fields': ('etat', 'notes',),
        }),
        (_(u'Champs générés (Méthodes)'), {
            'classes': ('collapse closed',),
            'fields': ('__unicode__', 'html', 'link',),
        }),
    )


class SaisonAdmin(VersionAdmin):
    list_display = ('__unicode__', 'lieu', 'debut', 'fin',)
    raw_id_fields = ('lieu',)
    autocomplete_lookup_fields = {
        'fk': ['lieu'],
    }


class ProfessionAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel', 'nom_feminin',
        'parente',)
    list_editable = ('nom', 'nom_pluriel', 'nom_feminin', 'parente',)
    raw_id_fields = ('parente',)
    autocomplete_lookup_fields = {
        'fk': ['parente']
    }
    exclude = ('slug',)


class AncrageSpatioTemporelAdmin(VersionAdmin):
    list_display = ('__unicode__', 'calc_date', 'calc_heure', 'calc_lieu',)
    search_fields = ('lieu__nom', 'lieu_approx', 'date_approx',
        'lieu__parent__nom', 'heure_approx',)
    raw_id_fields = ('lieu',)
    autocomplete_lookup_fields = {
        'fk': ['lieu'],
    }
    fieldsets = (
        (None, {
            'fields': (('date', 'date_approx',), ('heure', 'heure_approx',),
                       ('lieu', 'lieu_approx',))
        }),
    )


class PrenomAdmin(VersionAdmin):
    list_display = ('__unicode__', 'prenom', 'classement', 'favori',)
    list_editable = ('prenom', 'classement', 'favori',)


class TypeDeParenteDIndividusAdmin(VersionAdmin):
    list_display = ('nom', 'nom_pluriel', 'classement',)


class ParenteDIndividusAdmin(VersionAdmin):
    list_display = ('__unicode__',)
    raw_id_fields = ('individus_cibles',)
    autocomplete_lookup_fields = {
        'm2m': ['individus_cibles'],
    }


class IndividuAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'nom_naissance', 'calc_prenoms',
        'pseudonyme', 'titre', 'ancrage_naissance', 'ancrage_deces',
        'calc_professions', 'link',)
    list_editable = ('nom', 'titre',)
    search_fields = ('nom', 'pseudonyme', 'nom_naissance',)
    list_filter = ('titre',)
    raw_id_fields = ('prenoms', 'ancrage_naissance', 'ancrage_deces',
                     'professions', 'parentes', 'ancrage_approx',
                     'illustrations', 'documents',)
    autocomplete_lookup_fields = {
        'fk': ['ancrage_naissance', 'ancrage_deces', 'ancrage_approx'],
        'm2m': ['prenoms', 'professions', 'parentes', 'illustrations',
                'documents'],
    }
    readonly_fields = ('__unicode__', 'html', 'link',)
    inlines = (AuteurInline,)
    fieldsets = (
        (_('Champs courants'), {
            'fields': (('particule_nom', 'nom',), ('prenoms', 'pseudonyme',),
                       ('particule_nom_naissance', 'nom_naissance',),
                       ('titre', 'designation',), ('ancrage_naissance',
                        'ancrage_deces',), 'professions', 'parentes',),
        }),
        (_('Fichiers'), {
            'classes': ('collapse closed',),
            'fields': ('illustrations', 'documents',),
        }),
        (_(u'Champs avancés'), {
            'classes': ('collapse closed',),
            'fields': ('ancrage_approx', 'biographie', 'etat', 'notes',),
        }),
        (_(u'Champs générés (Méthodes)'), {
            'classes': ('collapse closed',),
            'fields': ('__unicode__', 'html', 'link',),
        }),
    )


class DeviseAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'symbole',)
    list_editable = ('nom', 'symbole',)


class EngagementAdmin(VersionAdmin):
    list_display = ('__unicode__', 'profession', 'salaire', 'devise',)
    raw_id_fields = ('profession', 'individus',)
    autocomplete_lookup_fields = {
        'fk': ['profession'],
        'm2m': ['individus'],
    }


class TypeDePersonnelAdmin(VersionAdmin):
    list_display = ('nom',)


class PersonnelAdmin(VersionAdmin):
    filter_horizontal = ('engagements',)


class GenreDOeuvreAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel',)
    list_editable = ('nom', 'nom_pluriel',)
    exclude = ('slug',)
    raw_id_fields = ('parents',)
    autocomplete_lookup_fields = {
        'm2m': ['parents'],
    }


class TypeDeCaracteristiqueDOeuvreAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel', 'classement',)
    list_editable = ('nom', 'nom_pluriel', 'classement',)


class CaracteristiqueDOeuvreAdmin(VersionAdmin):
    list_display = ('__unicode__', 'type', 'valeur', 'classement',)
    list_editable = ('type', 'valeur', 'classement',)


class PartieAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'parente', 'classement',)
    list_editable = ('nom', 'parente', 'classement',)
    raw_id_fields = ('professions',)
    autocomplete_lookup_fields = {
        'm2m': ['professions'],
    }


class PupitreAdmin(VersionAdmin):
    list_display = ('__unicode__', 'partie', 'quantite_min', 'quantite_max',)
    list_editable = ('partie', 'quantite_min', 'quantite_max',)
    raw_id_fields = ('partie',)
    autocomplete_lookup_fields = {
        'fk': ['partie'],
    }


class TypeDeParenteDOeuvresAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel', 'classement',)
    list_editable = ('nom', 'nom_pluriel', 'classement',)


class ParenteDOeuvresAdmin(VersionAdmin):
    list_display = ('__unicode__', 'type',)
    list_editable = ('type',)
    raw_id_fields = ('oeuvres_cibles',)
    autocomplete_lookup_fields = {
        'm2m': ['oeuvres_cibles'],
    }


class AuteurAdmin(VersionAdmin):
    list_display = ('__unicode__', 'profession',)
    list_editable = ('profession',)
    filter_horizontal = ('individus',)
    raw_id_fields = ('profession', 'individus',)
    autocomplete_lookup_fields = {
        'fk': ['profession'],
        'm2m': ['individus'],
    }

    def save_model(self, request, obj, form, change):
        obj.save()
        for individu in form.cleaned_data['individus']:
            individu.professions.add(obj.profession)


class OeuvreAdmin(VersionAdmin):
    list_display = ('__unicode__', 'titre', 'titre_secondaire', 'genre',
        'calc_caracteristiques', 'calc_auteurs', 'ancrage_composition',
        'link',)
    list_editable = ('genre',)
    search_fields = ('titre', 'titre_secondaire', 'genre__nom',)
    list_filter = ('genre__nom',)
    filter_horizontal = ('auteurs', 'parentes',)
    raw_id_fields = ('caracteristiques', 'ancrage_composition', 'pupitres',
        'documents', 'illustrations',)
    autocomplete_lookup_fields = {
        'fk': ['ancrage_composition'],
        'm2m': ['caracteristiques', 'pupitres', 'documents', 'illustrations'],
    }
    readonly_fields = ('__unicode__', 'html', 'link',)
    inlines = (ElementDeProgrammeInline,)
    fieldsets = (
        (_('Titre'), {
            'fields': (('prefixe_titre', 'titre',), 'coordination',
                        ('prefixe_titre_secondaire', 'titre_secondaire',),),
        }),
        (_('Autres champs courants'), {
            'fields': ('genre', 'caracteristiques', 'auteurs',
                        'ancrage_composition', 'pupitres', 'parentes',),
        }),
        (_('Fichiers'), {
            'classes': ('collapse closed',),
            'fields': ('documents', 'illustrations',),
        }),
        (_(u'Champs avancés'), {
            'classes': ('collapse closed', 'wide',),
            'fields': ('lilypond', 'description', 'etat', 'notes',),
        }),
        (_(u'Champs générés (Méthodes)'), {
            'classes': ('collapse closed',),
            'fields': ('__unicode__', 'html', 'link',),
        }),
    )


class AttributionDePupitreAdmin(VersionAdmin):
    list_display = ('__unicode__', 'pupitre',)
    list_editable = ('pupitre',)
    raw_id_fields = ('pupitre', 'individus',)
    autocomplete_lookup_fields = {
        'fk': ['pupitre'],
        'm2m': ['individus'],
    }


class CaracteristiqueDElementDeProgrammeAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel', 'classement',)
    list_editable = ('nom', 'nom_pluriel', 'classement',)


class ElementDeProgrammeAdmin(VersionAdmin):
    list_display = ('oeuvre', 'autre', 'classement', 'html',)
    list_editable = ('classement',)
    filter_horizontal = ('caracteristiques', 'distribution', 'personnels',
        'illustrations', 'documents',)
    raw_id_fields = ('oeuvre', 'caracteristiques', 'distribution',
        'personnels', 'documents', 'illustrations',)
    autocomplete_lookup_fields = {
        'fk': ['oeuvre'],
        'm2m': ['caracteristiques', 'distribution', 'personnels',
                'documents', 'illustrations'],
    }
    inlines = (EvenementInline,)


class EvenementAdmin(VersionAdmin):
    list_display = ('__unicode__', 'relache', 'circonstance', 'link',)
    list_editable = ('relache', 'circonstance',)
    search_fields = ('circonstance',)
    list_filter = ('relache',)
    raw_id_fields = ('programme', 'ancrage_debut', 'ancrage_fin', 'documents',
        'illustrations',)
    autocomplete_lookup_fields = {
        'fk': ['ancrage_debut', 'ancrage_fin'],
        'm2m': ['programme', 'documents', 'illustrations'],
    }
    readonly_fields = ('__unicode__', 'html', 'link',)
    fieldsets = (
        (_('Champs courants'), {
            'fields': ('ancrage_debut', 'ancrage_fin', 'relache',
                        'circonstance', 'programme',),
        }),
        (_('Fichiers'), {
            'classes': ('collapse closed',),
            'fields': ('documents', 'illustrations',),
        }),
        (_(u'Champs avancés'), {
            'classes': ('collapse closed',),
            'fields': ('etat', 'notes',),
        }),
        (_(u'Champs générés (Méthodes)'), {
            'classes': ('collapse closed',),
            'fields': ('__unicode__', 'html', 'link',),
        }),
    )


class TypeDeSourceAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel',)
    list_editable = ('nom', 'nom_pluriel',)
    exclude = ('slug',)


class SourceAdmin(VersionAdmin):
    list_display = ('__unicode__', 'nom', 'numero', 'date', 'page', 'type',
        'disp_contenu',)
    list_editable = ('type', 'date',)
    search_fields = ('nom', 'numero', 'type__nom',)
    list_filter = ('type__nom',)
    filter_horizontal = ('auteurs',)
    raw_id_fields = ('evenements', 'documents', 'illustrations',)
    autocomplete_lookup_fields = {
        'm2m': ['evenements', 'documents', 'illustrations'],
    }
    readonly_fields = ('__unicode__', 'html',)
    fieldsets = (
        (_('Champs courants'), {
            'fields': ('nom', 'numero', 'date', 'page', 'type', 'contenu',
                       'auteurs', 'evenements',),
        }),
        (_('Fichiers'), {
            'classes': ('collapse closed',),
            'fields': ('documents', 'illustrations',),
        }),
        (_(u'Champs avancés'), {
            'classes': ('collapse closed',),
            'fields': ('etat', 'notes',),
        }),
        (_(u'Champs générés (Méthodes)'), {
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
site.register(TypeDeParenteDIndividus, TypeDeParenteDIndividusAdmin)
site.register(ParenteDIndividus, ParenteDIndividusAdmin)
site.register(Individu, IndividuAdmin)
site.register(Devise, DeviseAdmin)
site.register(Engagement, EngagementAdmin)
site.register(TypeDePersonnel, TypeDePersonnelAdmin)
site.register(Personnel, PersonnelAdmin)
site.register(GenreDOeuvre, GenreDOeuvreAdmin)
site.register(TypeDeCaracteristiqueDOeuvre, TypeDeCaracteristiqueDOeuvreAdmin)
site.register(CaracteristiqueDOeuvre, CaracteristiqueDOeuvreAdmin)
site.register(Partie, PartieAdmin)
site.register(Pupitre, PupitreAdmin)
site.register(TypeDeParenteDOeuvres, TypeDeParenteDOeuvresAdmin)
site.register(ParenteDOeuvres, ParenteDOeuvresAdmin)
site.register(Auteur, AuteurAdmin)
site.register(Oeuvre, OeuvreAdmin)
site.register(AttributionDePupitre, AttributionDePupitreAdmin)
site.register(CaracteristiqueDElementDeProgramme,
        CaracteristiqueDElementDeProgrammeAdmin)
site.register(ElementDeProgramme, ElementDeProgrammeAdmin)
site.register(Evenement, EvenementAdmin)
site.register(TypeDeSource, TypeDeSourceAdmin)
site.register(Source, SourceAdmin)