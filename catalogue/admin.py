# coding: utf-8

from .models import *
from .forms import OeuvreForm, SourceForm
from django.contrib.admin import site, TabularInline, StackedInline
from django.contrib.admin.options import BaseModelAdmin
from reversion import VersionAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.contrib.contenttypes.generic import GenericStackedInline


#
# Common
#


class CustomBaseModel(BaseModelAdmin):
    exclude = ('owner',)

    def check_user_ownership(self, request, obj, has_class_permission):
        if not has_class_permission:
            return False
        user = request.user
        if obj is not None and not user.is_superuser and user != obj.owner:
            return False
        return True

    def has_change_permission(self, request, obj=None):
        has_class_permission = super(CustomBaseModel,
                                     self).has_change_permission(request, obj)
        return self.check_user_ownership(request, obj, has_class_permission)

    def has_delete_permission(self, request, obj=None):
        # FIXME: À cause d'un bug dans
        # django.contrib.admin.actions.delete_selected, cette action autorise
        # un utilisateur restreint à supprimer des objets pour lesquels il n'a
        # pas le droit.
        has_class_permission = super(CustomBaseModel,
                                     self).has_delete_permission(request, obj)
        return self.check_user_ownership(request, obj, has_class_permission)

    def queryset(self, request):
        user = request.user
        objects = self.model.objects.all()
        if not user.is_superuser:
            objects = objects.filter(owner=user)
        return objects


#
# Filters
#


def build_boolean_list_filter(class_title, class_parameter_name, filter=None,
                              exclude=None):
    class HasEventsListFilter(SimpleListFilter):
        title = class_title
        parameter_name = class_parameter_name

        def lookups(self, request, model_admin):
            return (
                ('1', _('Oui')),
                ('0', _('Non')),
            )

        def queryset(self, request, queryset):
            if self.value() == '1':
                query = getattr(queryset, 'filter' if filter is not None
                                     else 'exclude')
                return query(filter if filter is not None else exclude).distinct()
            if self.value() == '0':
                query = getattr(queryset, 'filter' if exclude is not None
                                     else 'exclude')
                return query(exclude if exclude is not None else filter).distinct()

    return HasEventsListFilter


EventHasSourceListFilter = build_boolean_list_filter(_('source'), 'has_source',
                                                     exclude=Q(sources=None))


EventHasProgramListFilter = build_boolean_list_filter(_('programme'),
                   'has_program', Q(programme__isnull=False) | Q(relache=True))


SourceHasEventsListFilter = build_boolean_list_filter(
                   _(u'événements'), 'has_events', exclude=Q(evenements=None))


SourceHasProgramListFilter = build_boolean_list_filter(
    _('programme'), 'has_program', Q(evenements__programme__isnull=False)
                                   | Q(evenements__relache=True))


#
# Inlines
#


class CustomTabularInline(TabularInline, CustomBaseModel):
    extra = 0


class CustomStackedInline(StackedInline, CustomBaseModel):
    extra = 0


class AncrageSpatioTemporelInline(CustomTabularInline):
    model = AncrageSpatioTemporel
    classes = ('grp-collapse grp-closed',)


class OeuvreMereInline(CustomTabularInline):
    verbose_name = ParenteDOeuvres._meta.get_field_by_name('mere')[0].verbose_name
    verbose_name_plural = _(u'œuvres mères')
    model = ParenteDOeuvres
    fk_name = 'fille'
    raw_id_fields = ('mere',)
    autocomplete_lookup_fields = {
        'fk': ['mere'],
    }
    fields = ('mere', 'type',)
    classes = ('grp-collapse grp-closed',)


class OeuvreFilleInline(CustomTabularInline):
    verbose_name = ParenteDOeuvres._meta.get_field_by_name('fille')[0].verbose_name
    verbose_name_plural = _(u'œuvres filles')
    model = ParenteDOeuvres
    fk_name = 'mere'
    raw_id_fields = ('fille',)
    autocomplete_lookup_fields = {
        'fk': ['fille'],
    }
    fields = ('type', 'fille')
    classes = ('grp-collapse grp-closed',)


class OeuvreLieesInline(StackedInline):
    verbose_name = Oeuvre._meta.verbose_name
    verbose_name_plural = Oeuvre._meta.verbose_name_plural
    model = Oeuvre
    classes = ('grp-collapse grp-closed',)


class AuteurInline(CustomTabularInline, GenericStackedInline):
    verbose_name = Auteur._meta.verbose_name
    verbose_name_plural = Auteur._meta.verbose_name_plural
    model = Auteur
    raw_id_fields = ('profession', 'individu',)
    autocomplete_lookup_fields = {
        'fk': ['profession', 'individu'],
    }
    classes = ('grp-collapse grp-closed',)


class ElementDeProgrammeInline(CustomStackedInline):
    fieldsets = (
        (_('Champs courants'), {
            'fields': (('oeuvre', 'autre',), 'caracteristiques',
                       'distribution',),
        }),
        (_('Fichiers'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('illustrations', 'documents',),
        }),
        (_(u'Champs avancés'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('personnels', 'etat', 'position',),
        }),
    )
    model = ElementDeProgramme
    sortable_field_name = 'position'
    raw_id_fields = ('oeuvre', 'caracteristiques', 'distribution',
                     'personnels', 'illustrations', 'documents')
    autocomplete_lookup_fields = {
        'fk': ['oeuvre'],
        'm2m': ['caracteristiques', 'distribution',
                'personnels', 'illustrations', 'documents'],
        }
    classes = ('grp-collapse grp-open',)


#
# ModelAdmins
#


class CustomAdmin(VersionAdmin, CustomBaseModel):
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'owner') is None:
            obj.owner = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if getattr(instance, 'owner') is None:
                instance.owner = request.user
            instance.save()
        formset.save_m2m()


class DocumentAdmin(CustomAdmin):
    list_display = ('__unicode__', 'nom', 'document',)
    list_editable = ('nom', 'document',)
    search_fields = ('nom',)


class IllustrationAdmin(CustomAdmin):
    list_display = ('__unicode__', 'legende', 'image',)
    list_editable = ('legende', 'image',)
    search_fields = ('legende',)


class EtatAdmin(CustomAdmin):
    pass


class NatureDeLieuAdmin(CustomAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel', 'referent',)
    list_editable = ('nom', 'nom_pluriel', 'referent',)


class LieuAdmin(CustomAdmin):
    list_display = ('__unicode__', 'nom', 'parent', 'nature', 'etat', 'link',)
    list_editable = ('nom', 'parent', 'nature', 'etat',)
    search_fields = ('nom', 'parent__nom',)
    list_filter = ('nature__nom',)
    raw_id_fields = ('parent', 'illustrations', 'documents',)
    autocomplete_lookup_fields = {
        'fk': ['parent'],
        'm2m': ['illustrations', 'documents'],
    }
    filter_horizontal = ('illustrations', 'documents',)
    readonly_fields = ('__unicode__', 'html', 'link',)
#    inlines = (AncrageSpatioTemporelInline,)
    fieldsets = (
        (_('Champs courants'), {
            'fields': ('nom', 'parent', 'nature', 'historique',),
        }),
        (_('Fichiers'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('illustrations', 'documents',),
        }),
        (_(u'Champs avancés'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('etat', 'notes',),
        }),
#        (_(u'Champs générés (Méthodes)'), {
#            'classes': ('grp-collapse grp-closed',),
#            'fields': ('__unicode__', 'html', 'link',),
#        }),
    )


class SaisonAdmin(CustomAdmin):
    list_display = ('__unicode__', 'lieu', 'debut', 'fin',)
    raw_id_fields = ('lieu',)
    autocomplete_lookup_fields = {
        'fk': ['lieu'],
    }


class ProfessionAdmin(CustomAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel', 'nom_feminin',
        'parente',)
    list_editable = ('nom', 'nom_pluriel', 'nom_feminin', 'parente',)
    raw_id_fields = ('parente',)
    autocomplete_lookup_fields = {
        'fk': ['parente']
    }


class AncrageSpatioTemporelAdmin(CustomAdmin):
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


class PrenomAdmin(CustomAdmin):
    list_display = ('__unicode__', 'prenom', 'classement', 'favori',
                    'has_individu')
    list_editable = ('prenom', 'classement', 'favori',)


class TypeDeParenteDIndividusAdmin(CustomAdmin):
    list_display = ('nom', 'nom_pluriel', 'classement',)


class ParenteDIndividusAdmin(CustomAdmin):
    list_display = ('__unicode__',)
    raw_id_fields = ('individus_cibles',)
    autocomplete_lookup_fields = {
        'm2m': ['individus_cibles'],
    }


class IndividuAdmin(CustomAdmin):
    list_per_page = 20
    list_display = ('__unicode__', 'nom', 'calc_prenoms',
        'pseudonyme', 'titre', 'ancrage_naissance', 'ancrage_deces',
        'calc_professions', 'etat', 'link',)
    list_editable = ('nom', 'titre', 'etat')
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
#    inlines = (AuteurInline,)
    fieldsets = (
        (_('Champs courants'), {
            'fields': (('particule_nom', 'nom',), ('prenoms', 'pseudonyme',),
                       ('particule_nom_naissance', 'nom_naissance',),
                       ('titre', 'designation',), ('ancrage_naissance',
                        'ancrage_deces',), 'professions', 'parentes',),
        }),
        (_('Fichiers'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('illustrations', 'documents',),
        }),
        (_(u'Champs avancés'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('ancrage_approx', 'biographie', 'etat', 'notes',),
        }),
#        (_(u'Champs générés (Méthodes)'), {
#            'classes': ('grp-collapse grp-closed',),
#            'fields': ('__unicode__', 'html', 'link',),
#        }),
    )


class DeviseAdmin(CustomAdmin):
    list_display = ('__unicode__', 'nom', 'symbole',)
    list_editable = ('nom', 'symbole',)


class EngagementAdmin(CustomAdmin):
    list_display = ('__unicode__', 'profession', 'salaire', 'devise',)
    raw_id_fields = ('profession', 'individus',)
    autocomplete_lookup_fields = {
        'fk': ['profession'],
        'm2m': ['individus'],
    }


class TypeDePersonnelAdmin(CustomAdmin):
    list_display = ('nom',)


class PersonnelAdmin(CustomAdmin):
    filter_horizontal = ('engagements',)


class GenreDOeuvreAdmin(CustomAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel',)
    list_editable = ('nom', 'nom_pluriel',)
    raw_id_fields = ('parents',)
    autocomplete_lookup_fields = {
        'm2m': ['parents'],
    }


class TypeDeCaracteristiqueDOeuvreAdmin(CustomAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel', 'classement',)
    list_editable = ('nom', 'nom_pluriel', 'classement',)


class CaracteristiqueDOeuvreAdmin(CustomAdmin):
    list_display = ('__unicode__', 'type', 'valeur', 'classement',)
    list_editable = ('type', 'valeur', 'classement',)


class PartieAdmin(CustomAdmin):
    list_display = ('__unicode__', 'nom', 'parente', 'classement',)
    list_editable = ('nom', 'parente', 'classement',)
    raw_id_fields = ('professions', 'parente',)
    autocomplete_lookup_fields = {
        'm2m': ['professions'],
        'fk': ['parente'],
    }


class PupitreAdmin(CustomAdmin):
    list_display = ('__unicode__', 'partie', 'quantite_min', 'quantite_max',)
    list_editable = ('partie', 'quantite_min', 'quantite_max',)
    search_fields = ('partie__nom', 'quantite_min', 'quantite_max')
    raw_id_fields = ('partie',)
    autocomplete_lookup_fields = {
        'fk': ['partie'],
    }


class TypeDeParenteDOeuvresAdmin(CustomAdmin):
    list_display = ('__unicode__', 'nom', 'nom_relatif', 'nom_relatif_pluriel',
                    'classement',)
    list_editable = ('nom', 'nom_relatif', 'nom_relatif_pluriel',
                     'classement',)


class ParenteDOeuvresAdmin(CustomAdmin):
    fields = ('mere', 'type', 'fille',)
    list_display = ('__unicode__', 'mere', 'type', 'fille',)
    list_editable = ('mere', 'type', 'fille',)
    raw_id_fields = ('fille', 'mere',)
    autocomplete_lookup_fields = {
        'fk': ['fille', 'mere'],
    }


class OeuvreAdmin(CustomAdmin):
    form = OeuvreForm
    list_display = ('__unicode__', 'titre', 'titre_secondaire', 'genre',
        'calc_caracteristiques', 'auteurs_html', 'ancrage_creation',
        'etat', 'link',)
    list_editable = ('genre', 'etat')
    search_fields = ('titre', 'titre_secondaire', 'genre__nom',)
    list_filter = ('genre__nom',)
    raw_id_fields = ('genre', 'caracteristiques',
                 'ancrage_creation', 'pupitres', 'documents', 'illustrations',)
    autocomplete_lookup_fields = {
        'fk': ['genre', 'ancrage_creation'],
        'm2m': ['caracteristiques', 'pupitres',
                'documents', 'illustrations'],
    }
    readonly_fields = ('__unicode__', 'html', 'link',)
    inlines = (OeuvreMereInline, OeuvreFilleInline, AuteurInline,)
#    inlines = (ElementDeProgrammeInline,)
    fieldsets = (
        (_('Titre'), {
            'fields': (('prefixe_titre', 'titre',), 'coordination',
                        ('prefixe_titre_secondaire', 'titre_secondaire',),),
        }),
        (_('Autres champs courants'), {
            'fields': ('genre', 'caracteristiques',
                        'ancrage_creation', 'pupitres',),
        }),
        (_('Fichiers'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('documents', 'illustrations',),
        }),
        (_(u'Champs avancés'), {
            'classes': ('grp-collapse grp-closed', 'wide',),
            'fields': ('lilypond', 'description', 'etat', 'notes',),
        }),
#        (_(u'Champs générés (Méthodes)'), {
#            'classes': ('grp-collapse grp-closed',),
#            'fields': ('__unicode__', 'html', 'link',),
#        }),
    )


class AttributionDePupitreAdmin(CustomAdmin):
    list_display = ('__unicode__', 'pupitre',)
    list_editable = ('pupitre',)
    raw_id_fields = ('pupitre', 'individus',)
    autocomplete_lookup_fields = {
        'fk': ['pupitre'],
        'm2m': ['individus'],
    }


class CaracteristiqueDElementDeProgrammeAdmin(CustomAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel', 'classement',)
    list_editable = ('nom', 'nom_pluriel', 'classement',)


class ElementDeProgrammeAdmin(CustomAdmin):
    list_display = ('oeuvre', 'autre', 'position', 'html', 'etat')
    list_editable = ('position', 'etat')
    search_fields = ('oeuvre__titre', 'oeuvre__titre_secondaire',
                     'autre')
    filter_horizontal = ('caracteristiques', 'distribution', 'personnels',
        'illustrations', 'documents',)
    raw_id_fields = ('oeuvre', 'caracteristiques', 'distribution',
        'personnels', 'documents', 'illustrations',)
    autocomplete_lookup_fields = {
        'fk': ['oeuvre'],
        'm2m': ['caracteristiques', 'distribution', 'personnels',
                'documents', 'illustrations'],
    }


class EvenementAdmin(CustomAdmin):
    list_display = ('__unicode__', 'relache', 'circonstance',
                    'has_source', 'has_program', 'etat', 'link',)
    list_editable = ('relache', 'circonstance', 'etat')
    search_fields = ('circonstance', 'ancrage_debut__lieu__nom')
    list_filter = ('relache', EventHasSourceListFilter,
                   EventHasProgramListFilter)
    raw_id_fields = ('ancrage_debut', 'ancrage_fin', 'documents',
        'illustrations',)
    autocomplete_lookup_fields = {
        'fk': ['ancrage_debut', 'ancrage_fin'],
        'm2m': ['documents', 'illustrations'],
    }
    readonly_fields = ('__unicode__', 'html', 'link',)
    inlines = (ElementDeProgrammeInline,)
    fieldsets = (
        (_('Champs courants'), {
            'description': _(
                u'Commencez par <strong>saisir ces quelques champs</strong> '
                u'avant d’ajouter des <em>éléments de programme</em> '
                u'plus bas.'),
            'fields': (('ancrage_debut', 'ancrage_fin',),
                       ('circonstance', 'relache',),),
        }),
        (_('Fichiers'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('documents', 'illustrations',),
        }),
        (_(u'Champs avancés'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('etat', 'notes',),
        }),
#        (_(u'Champs générés (Méthodes)'), {
#            'classes': ('grp-collapse grp-closed',),
#            'fields': ('__unicode__', 'html', 'link',),
#        }),
    )


class TypeDeSourceAdmin(CustomAdmin):
    list_display = ('__unicode__', 'nom', 'nom_pluriel',)
    list_editable = ('nom', 'nom_pluriel',)


class SourceAdmin(CustomAdmin):
    form = SourceForm
    list_display = ('nom', 'date', 'type', 'has_events', 'has_program',
                    'owner', 'etat', 'link')
    list_editable = ('type', 'date', 'etat')
    search_fields = ('nom', 'date', 'type__nom', 'numero', 'contenu',
                     'owner__username', 'owner__first_name',
                     'owner__last_name')
    list_filter = ('type', 'nom', SourceHasEventsListFilter,
                   SourceHasProgramListFilter)
    raw_id_fields = ('evenements', 'documents', 'illustrations',)
    related_lookup_fields = {
        'm2m': ['evenements'],
    }
    autocomplete_lookup_fields = {
        'm2m': ['documents', 'illustrations'],
    }
    readonly_fields = ('__unicode__', 'html',)
    inlines = (AuteurInline,)
    fieldsets = (
        (_('Champs courants'), {
            'fields': ('nom', ('numero', 'page',), ('date', 'type',),
                       'contenu', 'evenements',),
        }),
        (_('Fichiers'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('documents', 'illustrations',),
        }),
        (_(u'Champs avancés'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('etat', 'notes',),
        }),
#        (_(u'Champs générés (Méthodes)'), {
#            'classes': ('grp-collapse grp-closed',),
#            'fields': ('__unicode__', 'html',),
#        }),
    )

    class Media:
        js = [
            '/static/tinymce_setup/tinymce_setup.js',
            '/static/tiny_mce/tiny_mce.js',
        ]

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
site.register(Oeuvre, OeuvreAdmin)
site.register(AttributionDePupitre, AttributionDePupitreAdmin)
site.register(CaracteristiqueDElementDeProgramme,
        CaracteristiqueDElementDeProgrammeAdmin)
site.register(ElementDeProgramme, ElementDeProgrammeAdmin)
site.register(Evenement, EvenementAdmin)
site.register(TypeDeSource, TypeDeSourceAdmin)
site.register(Source, SourceAdmin)
