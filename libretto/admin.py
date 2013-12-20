# coding: utf-8

from __future__ import unicode_literals
import copy
from functools import partial
from django.contrib.admin import (site, TabularInline, StackedInline,
                                  ModelAdmin)
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.generic import GenericStackedInline
from django.db.models import Q
from django.forms.models import modelformset_factory
from polymorphic.admin import (
    PolymorphicChildModelAdmin, PolymorphicParentModelAdmin,
    PolymorphicChildModelFilter)
from reversion import VersionAdmin
import reversion
from cache_tools import cached_ugettext_lazy as _
from .models import *
from .forms import (
    OeuvreForm, SourceForm, IndividuForm, ElementDeProgrammeForm,
    ElementDeDistributionForm, EnsembleForm)


__all__ = ()


#
# Common
#


class CustomBaseModel(BaseModelAdmin):
    def check_user_ownership(self, request, obj, has_class_permission):
        if not has_class_permission:
            return False
        user = request.user
        if obj is not None and not user.is_superuser \
                and obj.owner not in user.get_descendants(include_self=True):
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
        qs = super(CustomBaseModel, self).queryset(request)
        if not user.is_superuser and IS_POPUP_VAR not in request.REQUEST:
            qs = qs.filter(
                owner__in=user.get_descendants(include_self=True))
        return qs


# Common fieldsets


COMMON_FIELDSET_LABEL = _('Champs courants')
ADVANCED_FIELDSET_LABEL = _('Champs courants')
PERIODE_D_ACTIVITE_FIELDSET = (_('Période d’activité'), {
    'fields': (('debut', 'debut_precision'), ('fin', 'fin_precision'))
})
FILES_FIELDSET = (_('Fichiers'), {
    'classes': ('grp-collapse grp-closed',),
    'fields': ('illustrations', 'documents',),
})


#
# Filters
#


class HasRelatedObjectsListFilter(SimpleListFilter):
    title = _('possède des objets liés')
    parameter_name = 'has_related_objects'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Oui')),
            ('0', _('Non')),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.with_related_objects()
        if self.value() == '0':
            return queryset.without_related_objects()


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
                return query(filter if filter is not None
                             else exclude).distinct()
            if self.value() == '0':
                query = getattr(queryset, 'filter' if exclude is not None
                                else 'exclude')
                return query(exclude if exclude is not None
                             else filter).distinct()

    return HasEventsListFilter


EventHasSourceListFilter = build_boolean_list_filter(_('source'), 'has_source',
                                                     exclude=Q(sources=None))

EventHasProgramListFilter = build_boolean_list_filter(
    _('programme'), 'has_program',
    Q(programme__isnull=False) | Q(relache=True))

SourceHasEventsListFilter = build_boolean_list_filter(
    _('événements'), 'has_events', exclude=Q(evenements=None))

SourceHasProgramListFilter = build_boolean_list_filter(
    _('programme'), 'has_program',
    Q(evenements__programme__isnull=False) | Q(evenements__relache=True))


#
# Inlines
#


class CustomTabularInline(TabularInline, CustomBaseModel):
    extra = 0
    exclude = ('owner',)


class CustomStackedInline(StackedInline, CustomBaseModel):
    extra = 0
    exclude = ('owner',)


class AncrageSpatioTemporelInline(CustomTabularInline):
    model = AncrageSpatioTemporel
    classes = ('grp-collapse grp-closed',)


class OeuvreMereInline(CustomTabularInline):
    model = ParenteDOeuvres
    verbose_name = model._meta.get_field('mere').verbose_name
    verbose_name_plural = _('œuvres mères')
    fk_name = 'fille'
    raw_id_fields = ('mere',)
    autocomplete_lookup_fields = {
        'fk': ('mere',),
    }
    fields = ('mere', 'type',)
    classes = ('grp-collapse grp-closed',)


class OeuvreFilleInline(CustomTabularInline):
    model = ParenteDOeuvres
    verbose_name = model._meta.get_field('fille').verbose_name
    verbose_name_plural = _('œuvres filles')
    fk_name = 'mere'
    raw_id_fields = ('fille',)
    autocomplete_lookup_fields = {
        'fk': ('fille',),
    }
    fields = ('type', 'fille')
    classes = ('grp-collapse grp-closed',)


class IndividuParentInline(CustomTabularInline):
    model = ParenteDIndividus
    verbose_name = model._meta.get_field('parent').verbose_name
    verbose_name_plural = _('individus parents')
    fk_name = 'enfant'
    raw_id_fields = ('parent',)
    autocomplete_lookup_fields = {
        'fk': ('parent',),
    }
    fields = ('parent', 'type',)
    classes = ('grp-collapse grp-closed',)


class IndividuEnfantInline(CustomTabularInline):
    model = ParenteDIndividus
    verbose_name = model._meta.get_field('enfant').verbose_name
    verbose_name_plural = _('individus enfants')
    fk_name = 'parent'
    raw_id_fields = ('enfant',)
    autocomplete_lookup_fields = {
        'fk': ('enfant',),
    }
    fields = ('type', 'enfant')
    classes = ('grp-collapse grp-closed',)


class OeuvreLieesInline(StackedInline):
    model = Oeuvre
    classes = ('grp-collapse grp-closed',)


class AuteurInline(CustomTabularInline, GenericStackedInline):
    model = Auteur
    raw_id_fields = ('profession', 'individu',)
    autocomplete_lookup_fields = {
        'fk': ['profession', 'individu'],
    }


class MembreInline(CustomStackedInline):
    model = Membre
    raw_id_fields = ('individu', 'instrument')
    autocomplete_lookup_fields = {
        'fk': ['individu', 'instrument'],
    }
    fieldsets = (
        (None, {'fields': ('individu', 'instrument', 'classement')}),
        PERIODE_D_ACTIVITE_FIELDSET,
    )


class ElementDeDistributionInline(CustomStackedInline, GenericStackedInline):
    """
    Utilisé uniquement pour les distributions de tête d'événement.
    La restriction est que l'on utilise pas de champ 'pupitre'.
    """
    model = ElementDeDistribution
    form = ElementDeDistributionForm
    verbose_name_plural = _('distribution')
    raw_id_fields = ('individus', 'ensembles', 'profession')
    autocomplete_lookup_fields = {
        'fk': ['profession'],
        'm2m': ['individus', 'ensembles'],
    }
    fieldsets = (
        (None, {
            'description': _('Distribution commune à l’ensemble de '
                             'l’événement. Une distribution plus précise peut '
                             'être saisie avec le programme.'),
            'fields': ('individus', 'ensembles', 'profession',),
        }),
    )
    classes = ('grp-collapse grp-open',)


class ElementDeProgrammeInline(CustomStackedInline):
    model = ElementDeProgramme
    form = ElementDeProgrammeForm
    verbose_name_plural = _('programme')
    fieldsets = (
        (COMMON_FIELDSET_LABEL, {
            'fields': (('oeuvre', 'autre',), 'caracteristiques',
                       'distribution', 'numerotation',),
        }),
        FILES_FIELDSET,
        (ADVANCED_FIELDSET_LABEL, {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('position',),
        }),
    )
    sortable_field_name = 'position'
    raw_id_fields = ('oeuvre', 'caracteristiques', 'distribution',
                     'illustrations', 'documents')
    related_lookup_fields = {
        'm2m': ('distribution',),
    }
    autocomplete_lookup_fields = {
        'fk': ('oeuvre',),
        'm2m': ('caracteristiques', 'illustrations', 'documents'),
    }
    classes = ('grp-collapse grp-open',)


class SourceInline(TabularInline):
    model = Source.evenements.through
    verbose_name = Source._meta.verbose_name
    verbose_name_plural = Source._meta.verbose_name_plural
    readonly_fields = ('source',)
    max_num = 0
    exclude = ()
    classes = ('grp-collapse grp-closed',)


#
# ModelAdmins
#


class CommonAdmin(CustomBaseModel, ModelAdmin):
    list_per_page = 20
    additional_fields = ('owner',)
    additional_readonly_fields = ('owner',)
    admin_fields = ()
    additional_list_display = ('owner',)
    additional_list_editable = ()
    additional_list_filters = ('owner', HasRelatedObjectsListFilter,)
    fieldsets_and_inlines_order = ()

    def __init__(self, *args, **kwargs):
        self.readonly_fields += self.additional_readonly_fields
        self.list_display += self.additional_list_display
        self.list_filter += self.additional_list_filters
        self.added_fieldsets = ()
        super(CommonAdmin, self).__init__(*args, **kwargs)

    @property
    def declared_fieldsets(self):
        declared_fieldsets = self._declared_fieldsets()
        if declared_fieldsets is None:
            return
        return tuple(declared_fieldsets) + self.added_fieldsets

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(CommonAdmin, self).get_fieldsets(request, obj=obj)
        if self.declared_fieldsets is None:
            return tuple(fieldsets) + self.added_fieldsets
        return fieldsets

    def _get_added_fields(self, request, additional_fields_attname,
                          excluded=()):
        if not request.user.is_superuser:
            excluded += self.admin_fields

        added_fields = []
        for added_field in getattr(self, additional_fields_attname, ()):
            if added_field not in excluded:
                added_fields.append(added_field)

        return tuple(added_fields)

    # TODO: Ajouter cette méthode aux inlines.
    def pre_get_form(self, request, obj=None, **kwargs):
        if not self.fields and not self.fieldsets:
            # Cas où le formulaire est fait automatiquement et inclut donc
            # les champs qu'on voudrait ajouter ci-dessous.
            return

        added_fields = self._get_added_fields(
            request, 'additional_fields', excluded=self.exclude or ())
        if added_fields:
            self.added_fieldsets = (
                (_('Champs d’administration'), {
                    'classes': ('grp-collapse grp-closed',),
                    'fields': added_fields,
                }),
            )

    def get_form(self, request, obj=None, **kwargs):
        self.pre_get_form(request, obj=obj, **kwargs)
        return super(CommonAdmin, self).get_form(request, obj=obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.owner is None:
            obj.owner = request.user
        super(CommonAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if getattr(instance, 'owner') is None:
                instance.owner = request.user
            instance.save()
        formset.save_m2m()

    def get_list_editable(self, request, **kwargs):
        added_editable_fields = self._get_added_fields(
            request, 'additional_list_editable')
        return tuple(self.list_editable) + added_editable_fields

    def get_changelist_formset(self, request, **kwargs):
        """
        Modified version of the overriden method.
        """
        defaults = {
            'formfield_callback': partial(
                self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)

        list_editable = self.get_list_editable(request, **kwargs)
        return modelformset_factory(
            self.model, self.get_changelist_form(request), extra=0,
            fields=list_editable, **defaults)

    def get_changelist(self, request, **kwargs):
        ChangeList = super(CommonAdmin, self).get_changelist(request, **kwargs)
        list_editable = self.get_list_editable(request, **kwargs)

        class NewChangeList(ChangeList):
            def __init__(self, *args, **kwargs):
                super(NewChangeList, self).__init__(*args, **kwargs)
                if not self.is_popup:
                    self.list_editable = list_editable

        return NewChangeList


class PublishedAdmin(CommonAdmin):
    additional_fields = ('etat', 'owner')
    admin_fields = ('etat',)
    additional_list_display = ('etat', 'owner')
    additional_list_editable = ('etat',)
    additional_list_filters = ('etat', 'owner', HasRelatedObjectsListFilter,)


class AutoriteAdmin(PublishedAdmin):
    additional_fields = ('etat', 'notes', 'owner')


class TypeDeParenteCommonAdmin(CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'nom_relatif',
                    'nom_relatif_pluriel', 'classement',)
    list_editable = ('nom', 'nom_pluriel', 'nom_relatif',
                     'nom_relatif_pluriel', 'classement',)
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ('nom', 'nom_relatif',
                     'nom_pluriel', 'nom_relatif_pluriel')
    fieldsets = (
        (None, {'fields': (
            ('nom', 'nom_pluriel'), ('nom_relatif', 'nom_relatif_pluriel'),
            'classement',
        )
        }),
    )


class TypeDeParenteAdmin(VersionAdmin, TypeDeParenteCommonAdmin,
                         PolymorphicParentModelAdmin):
    base_model = TypeDeParente
    child_models = (TypeDeParenteDOeuvres, TypeDeParenteDIndividus)


class TypeDeParenteChildAdmin(TypeDeParenteCommonAdmin,
                              PolymorphicChildModelAdmin):
    base_model = TypeDeParente


class TypeDeParenteDOeuvresAdmin(VersionAdmin, TypeDeParenteChildAdmin):
    pass


class TypeDeParenteDIndividusAdmin(VersionAdmin, TypeDeParenteChildAdmin):
    pass


reversion.register(TypeDeParenteDOeuvres, follow=('typedeparente_ptr',))
reversion.register(TypeDeParenteDIndividus, follow=('typedeparente_ptr',))


class DocumentAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'document', 'has_related_objects',)
    list_editable = ('nom', 'document',)
    search_fields = ('nom',)
    inlines = (AuteurInline,)


class IllustrationAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'legende', 'image', 'has_related_objects')
    list_editable = ('legende', 'image',)
    search_fields = ('legende',)
    inlines = (AuteurInline,)


class EtatAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'public',
                    'has_related_objects')
    list_editable = ('nom', 'nom_pluriel', 'public')


class NatureDeLieuAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'referent',)
    list_editable = ('nom', 'nom_pluriel', 'referent',)
    list_filter = ('referent',)
    search_fields = ('nom', 'nom_pluriel')


class LieuCommonAdmin(AutoriteAdmin):
    list_display = ('__str__', 'nom', 'parent', 'nature', 'link',)
    list_editable = ('nom', 'parent', 'nature',)
    search_fields = ('nom', 'parent__nom',)
    list_filter = (PolymorphicChildModelFilter, 'nature',)
    raw_id_fields = ('parent', 'illustrations', 'documents',)
    autocomplete_lookup_fields = {
        'fk': ['parent'],
        'm2m': ['illustrations', 'documents'],
    }
    filter_horizontal = ('illustrations', 'documents',)
    readonly_fields = ('__str__', 'html', 'link',)
#    inlines = (AncrageSpatioTemporelInline,)
    fieldsets = (
        (COMMON_FIELDSET_LABEL, {
            'fields': ('nom', 'parent', 'nature', 'historique',),
        }),
        FILES_FIELDSET,
#        (_('Champs générés (Méthodes)'), {
#            'classes': ('grp-collapse grp-closed',),
#            'fields': ('__str__', 'html', 'link',),
#        }),
    )


class LieuAdmin(VersionAdmin, LieuCommonAdmin, PolymorphicParentModelAdmin):
    base_model = Lieu
    child_models = (LieuDivers, Institution)


class LieuChildAdmin(LieuCommonAdmin, PolymorphicChildModelAdmin):
    base_model = Lieu


class LieuDiversAdmin(VersionAdmin, LieuChildAdmin):
    pass


class InstitutionAdmin(VersionAdmin, LieuChildAdmin):
    pass


reversion.register(LieuDivers, follow=('lieu_ptr',))
reversion.register(Institution, follow=('lieu_ptr',))


class SaisonAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'lieu', 'debut', 'fin',)
    date_hierarchy = 'debut'
    raw_id_fields = ('lieu',)
    autocomplete_lookup_fields = {
        'fk': ['lieu'],
    }


class ProfessionAdmin(VersionAdmin, AutoriteAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'nom_feminin',
                    'parent', 'classement')
    list_editable = ('nom', 'nom_pluriel', 'nom_feminin', 'parent',
                     'classement')
    search_fields = ('nom', 'nom_pluriel', 'nom_feminin')
    raw_id_fields = ('parent', 'illustrations', 'documents')
    autocomplete_lookup_fields = {
        'fk': ('parent',),
        'm2m': ('illustrations', 'documents'),
    }
    fieldsets = (
        (COMMON_FIELDSET_LABEL, {
            'fields': ('nom', 'nom_pluriel', 'nom_feminin', 'parent',
                       'classement'),
        }),
        FILES_FIELDSET,
#        (_('Champs générés (Méthodes)'), {
#            'classes': ('grp-collapse grp-closed',),
#            'fields': ('__str__', 'html', 'link',),
#        }),
    )


class AncrageSpatioTemporelAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'calc_date', 'calc_heure', 'calc_lieu',)
    date_hierarchy = 'date'
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


class PrenomAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'prenom', 'classement', 'favori',
                    'has_individu')
    search_fields = ('prenom',)
    list_editable = ('prenom', 'classement', 'favori',)


class IndividuAdmin(VersionAdmin, AutoriteAdmin):
    list_per_page = 20
    list_display = ('__str__', 'nom', 'calc_prenoms',
                    'pseudonyme', 'titre', 'ancrage_naissance',
                    'ancrage_deces', 'calc_professions', 'link',)
    list_editable = ('nom', 'titre',)
    search_fields = ('nom', 'pseudonyme', 'nom_naissance',
                     'prenoms__prenom',)
    list_filter = ('titre',)
    form = IndividuForm
    raw_id_fields = ('prenoms', 'ancrage_naissance', 'ancrage_deces',
                     'professions', 'ancrage_approx',
                     'illustrations', 'documents',)
    related_lookup_fields = {
        'fk': ('ancrage_naissance', 'ancrage_deces', 'ancrage_approx'),
    }
    autocomplete_lookup_fields = {
        'm2m': ('prenoms', 'professions', 'parentes', 'illustrations',
                'documents'),
    }
    readonly_fields = ('__str__', 'html', 'link',)
    inlines = (IndividuParentInline, IndividuEnfantInline)
    fieldsets = (
        (COMMON_FIELDSET_LABEL, {
            'fields': (('particule_nom', 'nom',), ('prenoms', 'pseudonyme',),
                       ('particule_nom_naissance', 'nom_naissance',),
                       ('titre', 'designation',),
                       ('ancrage_naissance', 'ancrage_deces',),
                       'professions',),
        }),
        FILES_FIELDSET,
        (ADVANCED_FIELDSET_LABEL, {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('ancrage_approx', 'biographie',),
        }),
#        (_('Champs générés (Méthodes)'), {
#            'classes': ('grp-collapse grp-closed',),
#            'fields': ('__str__', 'html', 'link',),
#        }),
    )
    fieldsets_and_inlines_order = ('f', 'i', 'i')


class EnsembleAdmin(VersionAdmin, AutoriteAdmin):
    form = EnsembleForm
    list_display = ('__str__', 'calc_caracteristiques', 'membres_count')
    search_fields = ('nom', 'membres__individu__nom')
    inlines = (MembreInline,)
    raw_id_fields = ('caracteristiques', 'siege', 'documents', 'illustrations')
    autocomplete_lookup_fields = {
        'fk': ('siege',),
        'm2m': ('caracteristiques', 'documents', 'illustrations'),
    }
    fieldsets = (
        (COMMON_FIELDSET_LABEL, {
            'fields': (('particule_nom', 'nom'), 'caracteristiques', 'siege'),
        }),
        PERIODE_D_ACTIVITE_FIELDSET,
        FILES_FIELDSET,
    )
    fieldsets_and_inlines_order = ('f', 'f', 'i')


class DeviseAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'symbole',)
    list_editable = ('nom', 'symbole',)


class EngagementAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'profession', 'salaire', 'devise',)
    raw_id_fields = ('profession', 'individus',)
    autocomplete_lookup_fields = {
        'fk': ['profession'],
        'm2m': ['individus'],
    }


class TypeDePersonnelAdmin(VersionAdmin, CommonAdmin):
    list_display = ('nom',)


class PersonnelAdmin(VersionAdmin, CommonAdmin):
    filter_horizontal = ('engagements',)


class GenreDOeuvreAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'has_related_objects')
    list_editable = ('nom', 'nom_pluriel',)
    search_fields = ('nom', 'nom_pluriel',)
    raw_id_fields = ('parents',)
    autocomplete_lookup_fields = {
        'm2m': ('parents',),
    }


class TypeDeCaracteristiqueCommonAdmin(CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'classement',)
    list_editable = ('nom', 'nom_pluriel', 'classement',)
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ('nom', 'nom_pluriel')


class TypeDeCaracteristiqueAdmin(
        VersionAdmin, TypeDeCaracteristiqueCommonAdmin,
        PolymorphicParentModelAdmin):
    base_model = TypeDeCaracteristique
    child_models = (TypeDeCaracteristiqueDOeuvre,
                    TypeDeCaracteristiqueDEnsemble,
                    TypeDeCaracteristiqueDeProgramme)


class TypeDeCaracteristiqueChildAdmin(TypeDeCaracteristiqueCommonAdmin,
                                      PolymorphicChildModelAdmin):
    base_model = TypeDeCaracteristique


class TypeDeCaracteristiqueDOeuvreAdmin(
        VersionAdmin, TypeDeCaracteristiqueChildAdmin):
    pass


class TypeDeCaracteristiqueDEnsembleAdmin(
        VersionAdmin, TypeDeCaracteristiqueChildAdmin):
    pass


class TypeDeCaracteristiqueDeProgrammeAdmin(
        VersionAdmin, TypeDeCaracteristiqueChildAdmin):
    pass


reversion.register(TypeDeCaracteristiqueDOeuvre,
                   follow=('typedecaracteristique_ptr',))
reversion.register(TypeDeCaracteristiqueDEnsemble,
                   follow=('typedecaracteristique_ptr',))
reversion.register(TypeDeCaracteristiqueDeProgramme,
                   follow=('typedecaracteristique_ptr',))


class CaracteristiqueCommonAdmin(CommonAdmin):
    list_display = ('__str__', 'type', 'valeur', 'classement',)
    list_editable = ('valeur', 'classement',)
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ('type__nom', 'valeur')


class CaracteristiqueAdmin(VersionAdmin, CaracteristiqueCommonAdmin,
                           PolymorphicParentModelAdmin):
    base_model = Caracteristique
    child_models = (
        CaracteristiqueDOeuvre,
        CaracteristiqueDEnsemble,
        CaracteristiqueDeProgramme,
    )


class CaracteristiqueChildAdmin(CaracteristiqueCommonAdmin,
                                PolymorphicChildModelAdmin):
    base_model = Caracteristique
    type_to = {
        CaracteristiqueDOeuvre: TypeDeCaracteristiqueDOeuvre,
        CaracteristiqueDEnsemble: TypeDeCaracteristiqueDEnsemble,
        CaracteristiqueDeProgramme: TypeDeCaracteristiqueDeProgramme,
    }

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'type' and db_field.rel is not None \
                and db_field.rel.to == TypeDeCaracteristique:
            db_field = copy.copy(db_field)
            db_field.rel = copy.copy(db_field.rel)
            db_field.rel.to = self.type_to[self.model]
        return super(CaracteristiqueChildAdmin, self) \
            .formfield_for_dbfield(db_field, **kwargs)


class CaracteristiqueDOeuvreAdmin(VersionAdmin, CaracteristiqueChildAdmin):
    pass


class CaracteristiqueDEnsembleAdmin(VersionAdmin, CaracteristiqueChildAdmin):
    pass


class CaracteristiqueDeProgrammeAdmin(VersionAdmin, CaracteristiqueChildAdmin):
    pass


reversion.register(CaracteristiqueDOeuvre,
                   follow=('caracteristique_ptr',))
reversion.register(CaracteristiqueDeProgramme,
                   follow=('caracteristique_ptr',))


class PartieCommonAdmin(AutoriteAdmin):
    list_display = ('__str__', 'nom', 'parent', 'classement',)
    list_editable = ('nom', 'parent', 'classement',)
    search_fields = ('nom',)
    list_filter = (PolymorphicChildModelFilter,)
    raw_id_fields = ('professions', 'parent', 'documents', 'illustrations')
    autocomplete_lookup_fields = {
        'm2m': ('professions', 'documents', 'illustrations'),
        'fk': ('parent',),
    }
    fieldsets = (
        (COMMON_FIELDSET_LABEL, {
            'fields': ('nom', 'nom_pluriel', 'professions', 'parent',
                       'classement'),
        }),
        FILES_FIELDSET,
#        (_('Champs générés (Méthodes)'), {
#            'classes': ('grp-collapse grp-closed',),
#            'fields': ('__str__', 'html', 'link',),
#        }),
    )


class PartieAdmin(VersionAdmin, PartieCommonAdmin,
                  PolymorphicParentModelAdmin):
    base_model = Partie
    child_models = (Role, Instrument)


class PartieChildAdmin(PartieCommonAdmin, PolymorphicChildModelAdmin):
    base_model = Partie


class RoleAdmin(VersionAdmin, PartieChildAdmin):
    pass
RoleAdmin.fieldsets = copy.deepcopy(RoleAdmin.fieldsets)
RoleAdmin.fieldsets[0][1]['fields'] = (
    'nom', 'nom_pluriel', 'oeuvre', 'professions', 'parent',
    'classement',
)
RoleAdmin.raw_id_fields += ('oeuvre',)
RoleAdmin.autocomplete_lookup_fields['fk'] += ('oeuvre',)


class InstrumentAdmin(VersionAdmin, PartieChildAdmin):
    pass


reversion.register(Role, follow=('partie_ptr',))
reversion.register(Instrument, follow=('partie_ptr',))


class PupitreAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'partie', 'quantite_min', 'quantite_max',)
    list_editable = ('partie', 'quantite_min', 'quantite_max',)
    search_fields = ('partie__nom', 'quantite_min', 'quantite_max')
    raw_id_fields = ('partie',)
    autocomplete_lookup_fields = {
        'fk': ['partie'],
    }


class OeuvreAdmin(VersionAdmin, AutoriteAdmin):
    form = OeuvreForm
    list_display = ('__str__', 'titre', 'titre_secondaire', 'genre',
                    'caracteristiques_html', 'auteurs_html',
                    'ancrage_creation', 'link',)
    list_editable = ('genre',)
    search_fields = ('titre', 'titre_secondaire', 'genre__nom',
                     'auteurs__individu__nom')
    list_filter = ('genre',)
    raw_id_fields = ('genre', 'caracteristiques', 'contenu_dans',
                     'ancrage_creation', 'pupitres', 'documents',
                     'illustrations',)
    related_lookup_fields = {
        'fk': ('ancrage_creation',)
    }
    autocomplete_lookup_fields = {
        'fk': ('genre', 'contenu_dans'),
        'm2m': ('caracteristiques', 'pupitres',
                'documents', 'illustrations'),
    }
    readonly_fields = ('__str__', 'html', 'link',)
    inlines = (AuteurInline, OeuvreMereInline, OeuvreFilleInline)
#    inlines = (ElementDeProgrammeInline,)
    fieldsets = (
        (_('Titre'), {
            'fields': (('prefixe_titre', 'titre',), 'coordination',
                       ('prefixe_titre_secondaire', 'titre_secondaire',),),
        }),
        (_('Autres champs courants'), {
            'fields': ('genre', 'caracteristiques',
                       'ancrage_creation', 'pupitres', 'contenu_dans',),
        }),
        FILES_FIELDSET,
        (ADVANCED_FIELDSET_LABEL, {
            'classes': ('grp-collapse grp-closed', 'wide',),
            'fields': ('lilypond', 'description',),
        }),
#        (_('Champs générés (Méthodes)'), {
#            'classes': ('grp-collapse grp-closed',),
#            'fields': ('__str__', 'html', 'link',),
#        }),
    )
    fieldsets_and_inlines_order = ('f', 'i', 'f', 'i', 'i')


class ElementDeDistributionAdmin(VersionAdmin, CommonAdmin):
    form = ElementDeDistributionForm
    list_display = ('__str__', 'pupitre', 'profession',)
    list_editable = ('pupitre', 'profession',)
    search_fields = ('individus__nom', 'individus__prenoms__prenom',
                     'pupitre__partie__nom', 'profession__nom')
    fields = ('individus', 'ensembles', 'pupitre', 'profession',)
    raw_id_fields = ('individus', 'ensembles', 'pupitre', 'profession',)
    autocomplete_lookup_fields = {
        'fk': ['pupitre', 'profession'],
        'm2m': ['individus', 'ensembles'],
    }


class EvenementAdmin(VersionAdmin, AutoriteAdmin):
    list_display = ('__str__', 'relache', 'circonstance',
                    'has_source', 'has_program', 'link',)
    list_editable = ('relache', 'circonstance',)
    search_fields = ('circonstance', 'ancrage_debut__lieu__nom')
    list_filter = ('relache', EventHasSourceListFilter,
                   EventHasProgramListFilter)
    raw_id_fields = ('ancrage_debut', 'ancrage_fin', 'caracteristiques',
                     'documents', 'illustrations',)
    related_lookup_fields = {
        'fk': ('ancrage_debut', 'ancrage_fin'),
    }
    autocomplete_lookup_fields = {
        'm2m': ('caracteristiques', 'documents', 'illustrations'),
    }
    readonly_fields = ('__str__', 'html', 'link')
    inlines = (ElementDeDistributionInline, ElementDeProgrammeInline,
               SourceInline)
    fieldsets = (
        (COMMON_FIELDSET_LABEL, {
            'description': _(
                'Commencez par <strong>saisir ces quelques champs</strong> '
                'avant d’ajouter des <em>éléments de programme</em> '
                'plus bas.'),
            'fields': (('ancrage_debut', 'ancrage_fin',),
                       ('circonstance', 'relache',), 'caracteristiques',),
        }),
        FILES_FIELDSET,
#        (_('Champs générés (Méthodes)'), {
#            'classes': ('grp-collapse grp-closed',),
#            'fields': ('__str__', 'html', 'link',),
#        }),
    )
    fieldsets_and_inlines_order = ('f', 'i', 'i')


class TypeDeSourceAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel',)
    list_editable = ('nom', 'nom_pluriel',)
    search_fields = ('nom', 'nom_pluriel')


class SourceAdmin(VersionAdmin, AutoriteAdmin):
    form = SourceForm
    list_display = ('nom', 'date', 'type', 'has_events', 'has_program', 'link')
    list_editable = ('type', 'date',)
    date_hierarchy = 'date'
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
    readonly_fields = ('__str__', 'html',)
    inlines = (AuteurInline,)
    fieldsets = (
        (COMMON_FIELDSET_LABEL, {
            'fields': ('nom', ('numero', 'page',), ('date', 'type',),
                       'contenu', 'evenements',),
        }),
        FILES_FIELDSET,
        #        (_('Champs générés (Méthodes)'), {
        #            'classes': ('grp-collapse grp-closed',),
        #            'fields': ('__str__', 'html',),
        #        }),
    )
    fieldsets_and_inlines_order = ('f', 'i')


site.register(Document, DocumentAdmin)
site.register(Illustration, IllustrationAdmin)
site.register(Etat, EtatAdmin)
site.register(NatureDeLieu, NatureDeLieuAdmin)
site.register(Lieu, LieuAdmin)
site.register(LieuDivers, LieuDiversAdmin)
site.register(Institution, InstitutionAdmin)
site.register(Saison, SaisonAdmin)
site.register(Profession, ProfessionAdmin)
site.register(AncrageSpatioTemporel, AncrageSpatioTemporelAdmin)
site.register(Prenom, PrenomAdmin)
site.register(TypeDeParente, TypeDeParenteAdmin)
site.register(TypeDeParenteDOeuvres, TypeDeParenteDOeuvresAdmin)
site.register(TypeDeParenteDIndividus, TypeDeParenteDIndividusAdmin)
site.register(Individu, IndividuAdmin)
site.register(Ensemble, EnsembleAdmin)
# site.register(Devise, DeviseAdmin)
# site.register(Engagement, EngagementAdmin)
# site.register(TypeDePersonnel, TypeDePersonnelAdmin)
# site.register(Personnel, PersonnelAdmin)
site.register(GenreDOeuvre, GenreDOeuvreAdmin)
site.register(TypeDeCaracteristique, TypeDeCaracteristiqueAdmin)
site.register(TypeDeCaracteristiqueDOeuvre, TypeDeCaracteristiqueDOeuvreAdmin)
site.register(TypeDeCaracteristiqueDEnsemble,
              TypeDeCaracteristiqueDEnsembleAdmin)
site.register(TypeDeCaracteristiqueDeProgramme,
              TypeDeCaracteristiqueDeProgrammeAdmin)
site.register(Caracteristique, CaracteristiqueAdmin)
site.register(CaracteristiqueDOeuvre, CaracteristiqueDOeuvreAdmin)
site.register(CaracteristiqueDEnsemble, CaracteristiqueDEnsembleAdmin)
site.register(CaracteristiqueDeProgramme, CaracteristiqueDeProgrammeAdmin)
site.register(Partie, PartieAdmin)
site.register(Role, RoleAdmin)
site.register(Instrument, InstrumentAdmin)
site.register(Pupitre, PupitreAdmin)
site.register(Oeuvre, OeuvreAdmin)
site.register(ElementDeDistribution, ElementDeDistributionAdmin)
site.register(Evenement, EvenementAdmin)
site.register(TypeDeSource, TypeDeSourceAdmin)
site.register(Source, SourceAdmin)
