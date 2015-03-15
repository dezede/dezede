# coding: utf-8

from __future__ import unicode_literals
import copy
from functools import partial

from django.contrib import messages
from django.contrib.admin import (site, TabularInline, StackedInline,
                                  ModelAdmin)
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.contrib.admin import SimpleListFilter
from django.contrib.gis.admin import OSMGeoAdmin
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _
from grappelli.forms import GrappelliSortableHiddenMixin
from polymorphic.admin import (
    PolymorphicChildModelAdmin, PolymorphicParentModelAdmin,
    PolymorphicChildModelFilter)
from reversion import VersionAdmin
import reversion

from .models import *
from .forms import (
    OeuvreForm, SourceForm, IndividuForm, ElementDeProgrammeForm,
    ElementDeDistributionForm, EnsembleForm, SaisonForm)
from .jobs import events_to_pdf as events_to_pdf_job
from common.utils.export import launch_export
from typography.utils import replace


__all__ = ()


#
# Common
#


class CustomBaseModel(BaseModelAdmin):
    # FIXME: Utiliser un AuthenticationBackend personnalisé.

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

    def get_queryset(self, request):
        user = request.user
        qs = super(CustomBaseModel, self).queryset(request)
        if not user.is_superuser and IS_POPUP_VAR not in request.REQUEST:
            qs = qs.filter(
                owner__in=user.get_descendants(include_self=True))
        return qs


# Common fieldsets


ADVANCED_FIELDSET_LABEL = _('Champs avancés')
PERIODE_D_ACTIVITE_FIELDSET = (_('Période d’activité'), {
    'fields': (('debut', 'debut_precision'), ('fin', 'fin_precision'))
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


class OeuvreLieesInline(StackedInline):
    model = Oeuvre
    classes = ('grp-collapse grp-closed',)


class AuteurInline(CustomTabularInline):
    model = Auteur
    raw_id_fields = ('profession', 'individu',)
    autocomplete_lookup_fields = {
        'fk': ['profession', 'individu'],
    }
    fields = ('individu', 'profession')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(AuteurInline,
                        self).get_formset(request, obj=obj, **kwargs)
        if request.method == 'POST' or 'contenu_dans' not in request.GET:
            return formset

        # Lorsqu’on saisit un extrait, il faut que les auteurs
        # soient déjà remplis, l’utilisateur n’aura qu’à les modifier dans les
        # cas où cela ne correspondrait pas à l’œuvre mère (par exemple
        # pour une ouverture d’opéra où le librettiste n’est pas auteur).

        contenu_dans = Oeuvre.objects.get(pk=request.GET['contenu_dans'])
        initial = list(contenu_dans.auteurs.values('individu', 'profession'))

        class TmpFormset(formset):
            extra = len(initial)

            def __init__(self, *args, **kwargs):
                kwargs['initial'] = initial
                super(TmpFormset, self).__init__(*args, **kwargs)

        return TmpFormset


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


class ElementDeDistributionInline(CustomStackedInline):
    """
    Utilisé uniquement pour les distributions de tête d'événement.
    La restriction est que l’on n’utilise pas de champ 'pupitre'.
    """
    model = ElementDeDistribution
    form = ElementDeDistributionForm
    verbose_name_plural = _('distribution')
    raw_id_fields = ('individu', 'ensemble', 'profession')
    autocomplete_lookup_fields = {
        'fk': ['individu', 'ensemble', 'profession'],
    }
    fieldsets = (
        (None, {
            'description': _('Distribution commune à l’ensemble de '
                             'l’événement. Une distribution plus précise peut '
                             'être saisie avec le programme.'),
            'fields': ('individu', 'ensemble', 'profession',),
        }),
    )
    classes = ('grp-collapse grp-open',)


class ElementDeProgrammeInline(GrappelliSortableHiddenMixin,
                               CustomStackedInline):
    model = ElementDeProgramme
    form = ElementDeProgrammeForm
    verbose_name_plural = _('programme')
    fieldsets = (
        (None, {
            'fields': (('oeuvre', 'autre',), 'caracteristiques',
                       'distribution', ('numerotation', 'part_d_auteur'),
                       'position'),
        }),
    )
    raw_id_fields = ('oeuvre', 'caracteristiques', 'distribution',)
    related_lookup_fields = {
        'm2m': ('distribution',),
    }
    autocomplete_lookup_fields = {
        'fk': ('oeuvre',),
        'm2m': ('caracteristiques',),
    }
    classes = ('grp-collapse grp-open',)


class FichierInline(GrappelliSortableHiddenMixin, CustomTabularInline):
    model = Fichier
    classes = ('grp-collapse grp-closed',)
    fields = ('fichier', 'folio', 'page', 'position')


class SourceEvenementInline(TabularInline):
    model = SourceEvenement
    verbose_name = _('événement lié')
    verbose_name_plural = _('événements liés')
    classes = ('grp-collapse grp-closed',)
    extra = 0
    raw_id_fields = ('evenement',)
    related_lookup_fields = {
        'fk': ('evenement',),
    }


class SourceOeuvreInline(TabularInline):
    model = SourceOeuvre
    verbose_name = _('œuvre liée')
    verbose_name_plural = _('œuvres liées')
    classes = ('grp-collapse grp-closed',)
    extra = 0
    raw_id_fields = ('oeuvre',)
    autocomplete_lookup_fields = {
        'fk': ('oeuvre',),
    }


class SourceIndividuInline(TabularInline):
    model = SourceIndividu
    verbose_name = _('individu lié')
    verbose_name_plural = _('individus liés')
    classes = ('grp-collapse grp-closed',)
    extra = 0
    raw_id_fields = ('individu',)
    autocomplete_lookup_fields = {
        'fk': ('individu',),
    }


class SourceEnsembleInline(TabularInline):
    model = SourceEnsemble
    verbose_name = _('ensemble lié')
    verbose_name_plural = _('ensembles liés')
    classes = ('grp-collapse grp-closed',)
    extra = 0
    raw_id_fields = ('ensemble',)
    autocomplete_lookup_fields = {
        'fk': ('ensemble',),
    }


class SourceLieuInline(TabularInline):
    model = SourceLieu
    verbose_name = _('lieu lié')
    verbose_name_plural = _('lieux liés')
    classes = ('grp-collapse grp-closed',)
    extra = 0
    raw_id_fields = ('lieu',)
    autocomplete_lookup_fields = {
        'fk': ('lieu',),
    }


class SourcePartieInline(TabularInline):
    model = SourcePartie
    verbose_name = _('rôle ou instrument lié')
    verbose_name_plural = _('rôles ou instruments liés')
    classes = ('grp-collapse grp-closed',)
    extra = 0
    raw_id_fields = ('partie',)
    autocomplete_lookup_fields = {
        'fk': ('partie',),
    }


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
                (_('Notes'), {
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
            if getattr(instance, 'owner', None) is None:
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

    def get_search_results(self, request, queryset, search_term):
        search_term = replace(search_term)
        return super(CommonAdmin, self).get_search_results(request, queryset,
                                                           search_term)


class PublishedAdmin(CommonAdmin):
    additional_fields = ('etat', 'owner')
    admin_fields = ('etat',)
    additional_list_display = ('etat', 'owner')
    additional_list_editable = ('etat',)
    additional_list_filters = ('etat', 'owner', HasRelatedObjectsListFilter,)


class AutoriteAdmin(PublishedAdmin):
    additional_fields = ('etat', 'notes_publiques', 'notes_privees', 'owner')


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


class EtatAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'public',
                    'has_related_objects')
    list_editable = ('nom', 'nom_pluriel', 'public')


class NatureDeLieuAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'referent',)
    list_editable = ('nom', 'nom_pluriel', 'referent',)
    list_filter = ('referent',)
    search_fields = ('nom', 'nom_pluriel')


class LieuCommonAdmin(OSMGeoAdmin, AutoriteAdmin):
    list_display = ('__str__', 'nom', 'parent', 'nature', 'link',)
    list_editable = ('nom', 'parent', 'nature',)
    search_fields = ('nom', 'parent__nom',)
    list_filter = (PolymorphicChildModelFilter, 'nature',)
    raw_id_fields = ('parent',)
    autocomplete_lookup_fields = {
        'fk': ['parent'],
    }
    readonly_fields = ('__str__', 'html', 'link',)
    fieldsets = (
        (None, {
            'fields': ('nom', 'parent', 'nature', 'historique', 'geometry'),
        }),
        (_('Données politiques'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('type_de_scene',),
        }),
    )
    layerswitcher = False
    default_lon = 300000
    default_lat = 5900000
    default_zoom = 5
    point_zoom = default_zoom
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.11' \
                     '/OpenLayers.js'


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
    form = SaisonForm
    list_display = ('__str__', 'lieu', 'ensemble', 'debut', 'fin',)
    date_hierarchy = 'debut'
    raw_id_fields = ('lieu', 'ensemble')
    autocomplete_lookup_fields = {
        'fk': ['lieu', 'ensemble'],
    }


class ProfessionAdmin(VersionAdmin, AutoriteAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'nom_feminin',
                    'parent', 'classement')
    list_editable = ('nom', 'nom_pluriel', 'nom_feminin', 'parent',
                     'classement')
    search_fields = ('nom', 'nom_pluriel', 'nom_feminin')
    raw_id_fields = ('parent',)
    autocomplete_lookup_fields = {
        'fk': ('parent',),
    }
    fieldsets = (
        (None, {
            'fields': ('nom', 'nom_pluriel', 'nom_feminin', 'parent',
                       'classement'),
        }),
    )


class IndividuAdmin(VersionAdmin, AutoriteAdmin):
    list_per_page = 20
    list_display = ('__str__', 'nom', 'prenoms',
                    'pseudonyme', 'titre', 'naissance',
                    'deces', 'calc_professions', 'link',)
    list_editable = ('nom', 'titre',)
    search_fields = ('nom', 'pseudonyme', 'nom_naissance',
                     'prenoms',)
    list_filter = ('titre',)
    form = IndividuForm
    raw_id_fields = ('naissance_lieu', 'deces_lieu', 'professions')
    autocomplete_lookup_fields = {
        'fk': ('naissance_lieu', 'deces_lieu'),
        'm2m': ('professions', 'parentes'),
    }
    readonly_fields = ('__str__', 'html', 'link',)
    inlines = (IndividuParentInline,)
    fieldsets = (
        (None, {
            'fields': (('titre', 'prenoms'), ('particule_nom', 'nom'),
                       'professions',),
        }),
        (_('Naissance'), {
            'fields': (
                ('naissance_date', 'naissance_date_approx'),
                ('naissance_lieu', 'naissance_lieu_approx'))
        }),
        (_('Décès'), {
            'fields': (
                ('deces_date', 'deces_date_approx'),
                ('deces_lieu', 'deces_lieu_approx'))
        }),
        (_('Informations complémentaires'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('pseudonyme',
                       'prenoms_complets',
                       ('particule_nom_naissance', 'nom_naissance'),
                       'designation', 'biographie', 'isni'),
        }),
    )
    fieldsets_and_inlines_order = ('f', 'f', 'f', 'f', 'i', 'i')

    def get_queryset(self, request):
        qs = super(IndividuAdmin, self).queryset(request)
        return qs.select_related(
            'naissance_lieu', 'deces_lieu', 'etat', 'owner'
        ).prefetch_related('professions')


class EnsembleAdmin(VersionAdmin, AutoriteAdmin):
    form = EnsembleForm
    list_display = ('__str__', 'calc_caracteristiques', 'membres_count')
    search_fields = ('nom', 'membres__individu__nom')
    inlines = (MembreInline,)
    raw_id_fields = ('caracteristiques', 'siege')
    autocomplete_lookup_fields = {
        'fk': ('siege',),
        'm2m': ('caracteristiques',),
    }
    fieldsets = (
        (None, {
            'fields': (('particule_nom', 'nom'), 'caracteristiques', 'siege'),
        }),
        PERIODE_D_ACTIVITE_FIELDSET,
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
    raw_id_fields = ('professions', 'parent')
    autocomplete_lookup_fields = {
        'm2m': ('professions',),
        'fk': ('parent',),
    }
    fieldsets = (
        (None, {
            'fields': ('nom', 'nom_pluriel', 'professions', 'parent',
                       'classement'),
        }),
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

    # N'affiche que les pupitres différents pour éviter de flooder les
    # admins de doublons (qui sont pourtant nécessaires).
    def get_queryset(self, request):
        qs = super(PupitreAdmin, self).queryset(request)
        return (qs.order_by('quantite_min', 'quantite_max')
                  .distinct('partie__classement', 'partie__nom',
                            'quantite_min', 'quantite_max'))


class OeuvreAdmin(VersionAdmin, AutoriteAdmin):
    form = OeuvreForm
    list_display = ('__str__', 'titre', 'titre_secondaire', 'genre',
                    'caracteristiques_html', 'auteurs_html',
                    'creation', 'link',)
    list_editable = ('genre',)
    search_fields = ('titre', 'titre_secondaire', 'genre__nom',
                     'auteurs__individu__nom')
    list_filter = ('genre',)
    list_select_related = ('genre', 'etat', 'owner')
    date_hierarchy = 'creation_date'
    raw_id_fields = ('genre', 'caracteristiques', 'contenu_dans',
                     'creation_lieu', 'pupitres')
    autocomplete_lookup_fields = {
        'fk': ('genre', 'contenu_dans', 'creation_lieu'),
        'm2m': ('caracteristiques', 'pupitres'),
    }
    readonly_fields = ('__str__', 'html', 'link',)
    inlines = (AuteurInline, OeuvreMereInline)
    fieldsets = (
        (_('Titre significatif'), {
            'fields': (('prefixe_titre', 'titre',), 'coordination',
                       ('prefixe_titre_secondaire', 'titre_secondaire',),),
        }),
        (None, {
            'fields': (('genre', 'coupe'),
                       ('numero', 'opus',),
                       ('tempo', 'tonalite'),
                       'ict',
                       ('surnom', 'nom_courant'),
                       'incipit', 'sujet'),
        }),
        (None, {
            'fields': ('caracteristiques',),
        }),
        (_('Création'), {
            'fields': (
                ('creation_date', 'creation_date_approx'),
                ('creation_heure', 'creation_heure_approx'),
                ('creation_lieu', 'creation_lieu_approx'))
        }),
        (None, {
            'fields': ('pupitres',),
        }),
        (None, {
            'fields': ('contenu_dans', ('type_extrait', 'numero_extrait')),
        }),
        (ADVANCED_FIELDSET_LABEL, {
            'classes': ('grp-collapse grp-closed', 'wide',),
            'fields': ('lilypond', 'description',),
        }),
    )
    fieldsets_and_inlines_order = ('i', 'f', 'f', 'f', 'f', 'f', 'f', 'i', 'i')

    def get_queryset(self, request):
        qs = super(OeuvreAdmin, self).get_queryset(request)
        return qs.prefetch_related(
            'auteurs__individu', 'auteurs__profession', 'pupitres__partie',
            'caracteristiques__type')


class ElementDeDistributionAdmin(VersionAdmin, CommonAdmin):
    form = ElementDeDistributionForm
    list_display = ('__str__', 'pupitre', 'profession',)
    list_editable = ('pupitre', 'profession',)
    search_fields = ('individu__nom', 'individu__prenoms', 'ensemble__nom',
                     'pupitre__partie__nom', 'profession__nom')
    fields = ('individu', 'ensemble', 'pupitre', 'profession')
    raw_id_fields = ('individu', 'ensemble', 'pupitre', 'profession')
    autocomplete_lookup_fields = {
        'fk': ['individu', 'ensemble', 'pupitre', 'profession'],
    }


MAX_EXPORTED_EVENTS = 200


def events_to_pdf(modeladmin, request, queryset):
    # Ensures the user is not trying to see something he should not.
    queryset = queryset.published(request)

    n = queryset.count()
    if n > MAX_EXPORTED_EVENTS:
        modeladmin.message_user(
            request,
            'Trop d’événements sélectionnés pour l’export ; '
            'seuls les %s premiers seront exportés' % MAX_EXPORTED_EVENTS,
            messages.WARNING)
        queryset = queryset[:MAX_EXPORTED_EVENTS]
        n = MAX_EXPORTED_EVENTS
    launch_export(
        events_to_pdf_job, request,
        list(queryset.values_list('pk', flat=True)), 'PDF', 'de %s événements' % n)
events_to_pdf.short_description = _('Exporter en PDF')


class EvenementAdmin(VersionAdmin, AutoriteAdmin):
    list_display = ('__str__', 'relache', 'circonstance',
                    'has_source', 'has_program', 'link',)
    list_editable = ('relache', 'circonstance',)
    search_fields = ('circonstance', 'debut_lieu__nom')
    list_filter = ('relache', EventHasSourceListFilter,
                   EventHasProgramListFilter)
    list_select_related = ('debut_lieu', 'debut_lieu__nature',
                           'fin_lieu', 'fin_lieu__nature',
                           'etat', 'owner')
    date_hierarchy = 'debut_date'
    raw_id_fields = ('debut_lieu', 'fin_lieu', 'caracteristiques')
    autocomplete_lookup_fields = {
        'fk': ('debut_lieu', 'fin_lieu'),
        'm2m': ('caracteristiques',),
    }
    readonly_fields = ('__str__', 'html', 'link')
    inlines = (ElementDeDistributionInline, ElementDeProgrammeInline)
    actions = [events_to_pdf]
    fieldsets = (
        (_('Début'), {
            'fields': (
                ('debut_date', 'debut_date_approx'),
                ('debut_heure', 'debut_heure_approx'),
                ('debut_lieu', 'debut_lieu_approx'))
        }),
        (_('Fin'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': (
                ('fin_date', 'fin_date_approx'),
                ('fin_heure', 'fin_heure_approx'),
                ('fin_lieu', 'fin_lieu_approx'))
        }),
        (None, {
            'fields': (('circonstance', 'programme_incomplet', 'relache',),
                       'caracteristiques',),
        }),
        (_('Données économiques'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': (('recette_generale', 'recette_par_billets'),),
        }),
    )
    fieldsets_and_inlines_order = ('f', 'f', 'f', 'i', 'i')

    def get_queryset(self, request):
        qs = super(EvenementAdmin, self).get_queryset(request)
        qs = qs.extra(select={
            '_has_program':
            'EXISTS (SELECT 1 FROM %s WHERE evenement_id = %s.id)'
            % (ElementDeProgramme._meta.db_table, Evenement._meta.db_table),
            '_has_source':
            'EXISTS (SELECT 1 FROM %s WHERE evenement_id = %s.id)'
            % (Source.evenements.field.m2m_db_table(),
               Evenement._meta.db_table)})
        return qs


class TypeDeSourceAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel',)
    list_editable = ('nom', 'nom_pluriel',)
    search_fields = ('nom', 'nom_pluriel')


class SourceAdmin(VersionAdmin, AutoriteAdmin):
    form = SourceForm
    list_display = ('__str__', 'date', 'type', 'has_events', 'has_program', 'link')
    list_editable = ('type', 'date',)
    list_select_related = ('type', 'etat', 'owner')
    date_hierarchy = 'date'
    search_fields = (
        'type__nom', 'titre', 'date', 'date_approx', 'numero',
        'lieu_conservation', 'cote')
    list_filter = ('type', 'titre', SourceHasEventsListFilter,
                   SourceHasProgramListFilter)
    raw_id_fields = ('evenements',)
    related_lookup_fields = {
        'm2m': ['evenements'],
    }
    readonly_fields = ('__str__', 'html',)
    inlines = (
        FichierInline, AuteurInline, SourceEvenementInline, SourceOeuvreInline,
        SourceIndividuInline, SourceEnsembleInline, SourceLieuInline,
        SourcePartieInline,
    )
    fieldsets = (
        (None, {
            'fields': ('type', 'titre', 'legende',),
        }),
        (None, {
            'fields': (
                ('date', 'date_approx'),
                ('numero', 'page', 'folio',),
                ('lieu_conservation', 'cote',),
                'url',
            )
        }),
        (_('Transcription'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('transcription',),
        }),
    )
    fieldsets_and_inlines_order = ('f', 'f', 'f', 'i', 'i',
                                   'i', 'i', 'i', 'i', 'i', 'i')

    def get_queryset(self, request):
        qs = super(SourceAdmin, self).get_queryset(request)
        qs = qs.extra(
            select={
                '_has_events':
                'EXISTS ('
                '    SELECT 1 FROM %(evenement)s '
                '    INNER JOIN %(m2m)s ON %(evenement)s.id '
                '                          = %(m2m)s.evenement_id '
                '    WHERE %(m2m)s.source_id = %(source)s.id)' % {
                    'evenement': Evenement._meta.db_table,
                    'm2m': Source.evenements.field.m2m_db_table(),
                    'source': Source._meta.db_table,
                },
                '_has_program':
                'EXISTS ('
                '    SELECT 1 FROM %(evenement)s '
                '    INNER JOIN %(m2m)s ON %(evenement)s.id '
                '                          = %(m2m)s.evenement_id '
                '    WHERE (%(m2m)s.source_id = %(source)s.id '
                '           AND (%(evenement)s.relache = true '
                '                OR EXISTS (SELECT 1 FROM %(programme)s '
                '                           WHERE %(programme)s.evenement_id '
                '                                 = %(evenement)s.id))))' % {
                    'evenement': Evenement._meta.db_table,
                    'm2m': Source.evenements.field.m2m_db_table(),
                    'source': Source._meta.db_table,
                    'programme': ElementDeProgramme._meta.db_table,
                }
            }
        )
        return qs


site.register(Etat, EtatAdmin)
site.register(NatureDeLieu, NatureDeLieuAdmin)
site.register(Lieu, LieuAdmin)
site.register(LieuDivers, LieuDiversAdmin)
site.register(Institution, InstitutionAdmin)
site.register(Saison, SaisonAdmin)
site.register(Profession, ProfessionAdmin)
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
