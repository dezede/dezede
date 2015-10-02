# coding: utf-8

from __future__ import unicode_literals
from functools import partial

from django.contrib import messages
from django.contrib.admin import (site, TabularInline, StackedInline,
                                  ModelAdmin, HORIZONTAL)
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.contrib.admin import SimpleListFilter
from django.contrib.gis.admin import OSMGeoAdmin
from django.db.models import Q
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _
from grappelli.forms import GrappelliSortableHiddenMixin
from reversion import VersionAdmin
from super_inlines.admin import SuperInlineModelAdmin, SuperModelAdmin

from .models import *
from .forms import (
    OeuvreForm, SourceForm, IndividuForm, ElementDeProgrammeForm,
    ElementDeDistributionForm, EnsembleForm, SaisonForm, PartieForm)
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
        qs = super(CustomBaseModel, self).get_queryset(request)
        if not user.is_superuser and IS_POPUP_VAR not in request.REQUEST:
            qs = qs.filter(
                owner__in=user.get_descendants(include_self=True))
        return qs


# Common fieldsets


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
    fields = ('type', 'mere')
    classes = ('grp-collapse grp-closed',)


class PupitreInline(CustomTabularInline):
    model = Pupitre
    verbose_name = model._meta.verbose_name
    verbose_name_plural = _('effectif')
    raw_id_fields = ('partie',)
    autocomplete_lookup_fields = {
        'fk': ['partie'],
    }
    fields = ('partie', 'soliste', 'quantite_min', 'quantite_max',
              'facultatif')
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
    fields = ('type', 'parent')
    classes = ('grp-collapse grp-closed',)


class OeuvreLieesInline(StackedInline):
    model = Oeuvre
    classes = ('grp-collapse grp-closed',)


class AuteurInline(CustomTabularInline):
    model = Auteur
    raw_id_fields = ('individu', 'ensemble', 'profession')
    autocomplete_lookup_fields = {
        'fk': ['individu', 'ensemble', 'profession'],
    }
    fields = ('individu', 'ensemble', 'profession')

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(AuteurInline,
                        self).get_formset(request, obj=obj, **kwargs)
        if request.method == 'POST' or 'extrait_de' not in request.GET:
            return formset

        # Lorsqu’on saisit un extrait, il faut que les auteurs
        # soient déjà remplis, l’utilisateur n’aura qu’à les modifier dans les
        # cas où cela ne correspondrait pas à l’œuvre mère (par exemple
        # pour une ouverture d’opéra où le librettiste n’est pas auteur).

        extrait_de = Oeuvre.objects.get(pk=request.GET['extrait_de'])
        initial = list(
            extrait_de.auteurs.values('individu', 'ensemble', 'profession'))

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


class ElementDeDistributionInline(SuperInlineModelAdmin, CustomTabularInline):
    model = ElementDeDistribution
    form = ElementDeDistributionForm
    verbose_name_plural = _('distribution')
    raw_id_fields = ('individu', 'ensemble', 'partie', 'profession')
    autocomplete_lookup_fields = {
        'fk': ['individu', 'ensemble', 'partie', 'profession'],
    }
    fields = ('individu', 'ensemble', 'partie', 'profession')
    classes = ('grp-collapse grp-open',)

    def get_queryset(self, request):
        qs = super(ElementDeDistributionInline, self).get_queryset(request)
        return qs.select_related('individu', 'ensemble', 'partie', 'profession')


class ElementDeProgrammeInline(SuperInlineModelAdmin,
                               GrappelliSortableHiddenMixin,
                               CustomStackedInline):
    model = ElementDeProgramme
    form = ElementDeProgrammeForm
    verbose_name_plural = _('programme')
    fieldsets = (
        (None, {
            'fields': (('oeuvre', 'autre',), 'caracteristiques',
                       ('numerotation', 'part_d_auteur'),
                       'position'),
        }),
    )
    raw_id_fields = ('oeuvre', 'caracteristiques',)
    autocomplete_lookup_fields = {
        'fk': ('oeuvre',),
        'm2m': ('caracteristiques',),
    }
    classes = ('grp-collapse grp-open',)
    inlines = (ElementDeDistributionInline,)

    def get_queryset(self, request):
        qs = super(ElementDeProgrammeInline, self).get_queryset(request)
        return qs.select_related('oeuvre').prefetch_related(
            'caracteristiques', 'distribution',
            'distribution__individu', 'distribution__ensemble',
            'distribution__partie', 'distribution__profession')


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

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(CommonAdmin, self).get_fieldsets(request, obj=obj)
        return tuple(fieldsets) + self.added_fieldsets

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
        formset.save()

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
    search_fields = ('nom', 'nom_relatif',
                     'nom_pluriel', 'nom_relatif_pluriel')
    fieldsets = (
        (None, {'fields': (
            ('nom', 'nom_pluriel'), ('nom_relatif', 'nom_relatif_pluriel'),
            'classement',
        )
        }),
    )


class TypeDeParenteDOeuvresAdmin(VersionAdmin, TypeDeParenteCommonAdmin):
    pass


class TypeDeParenteDIndividusAdmin(VersionAdmin, TypeDeParenteCommonAdmin):
    pass


class EtatAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'public',
                    'has_related_objects')
    list_editable = ('nom', 'nom_pluriel', 'public')


class NatureDeLieuAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'referent',)
    list_editable = ('nom', 'nom_pluriel', 'referent',)
    list_filter = ('referent',)
    search_fields = ('nom', 'nom_pluriel')


class LieuAdmin(OSMGeoAdmin, AutoriteAdmin):
    list_display = ('__str__', 'nom', 'parent', 'nature', 'link',)
    list_editable = ('nom', 'parent', 'nature',)
    search_fields = ('nom', 'parent__nom',)
    list_filter = ('nature',)
    raw_id_fields = ('parent',)
    autocomplete_lookup_fields = {
        'fk': ['parent'],
    }
    readonly_fields = ('__str__', 'html', 'link',)
    fieldsets = (
        (None, {
            'fields': (('nom', 'parent'), ('nature', 'is_institution'),
                       'historique', 'geometry'),
        }),
    )
    layerswitcher = False
    default_lon = 300000
    default_lat = 5900000
    default_zoom = 5
    point_zoom = default_zoom
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1' \
                     '/OpenLayers.js'


class SaisonAdmin(VersionAdmin, CommonAdmin):
    form = SaisonForm
    list_display = ('__str__', 'lieu', 'ensemble', 'debut', 'fin',
                    'evenements_count')
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
        qs = super(IndividuAdmin, self).get_queryset(request)
        return qs.select_related(
            'naissance_lieu', 'deces_lieu', 'etat', 'owner'
        ).prefetch_related('professions')


class TypeDEnsembleAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'parent')
    list_editable = ('nom', 'nom_pluriel', 'parent')
    search_fields = ('nom', 'nom_pluriel',)
    raw_id_fields = ('parent',)
    autocomplete_lookup_fields = {
        'fk': ('parent',),
    }


class EnsembleAdmin(VersionAdmin, AutoriteAdmin):
    form = EnsembleForm
    list_display = ('__str__', 'type', 'membres_count')
    search_fields = ('nom', 'membres__individu__nom')
    inlines = (MembreInline,)
    raw_id_fields = ('siege', 'type')
    autocomplete_lookup_fields = {
        'fk': ('siege', 'type'),
    }
    fieldsets = (
        (None, {
            'fields': (('particule_nom', 'nom'), 'type', 'siege'),
        }),
        PERIODE_D_ACTIVITE_FIELDSET,
    )
    fieldsets_and_inlines_order = ('f', 'f', 'i')


class GenreDOeuvreAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'has_related_objects')
    list_editable = ('nom', 'nom_pluriel',)
    search_fields = ('nom', 'nom_pluriel',)
    raw_id_fields = ('parents',)
    autocomplete_lookup_fields = {
        'm2m': ('parents',),
    }


class TypeDeCaracteristiqueDeProgrammeAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'nom', 'nom_pluriel', 'classement',)
    list_editable = ('nom', 'nom_pluriel', 'classement',)
    search_fields = ('nom', 'nom_pluriel')


class CaracteristiqueDeProgrammeAdmin(VersionAdmin, CommonAdmin):
    list_display = ('__str__', 'type', 'valeur', 'classement',)
    list_editable = ('valeur', 'classement',)
    search_fields = ('type__nom', 'valeur')


class PartieAdmin(VersionAdmin, AutoriteAdmin):
    form = PartieForm
    list_display = ('__str__', 'nom', 'parent', 'classement',)
    list_editable = ('nom', 'parent', 'classement',)
    list_filter = ('type',)
    list_select_related = ('parent', 'etat', 'owner')
    search_fields = ('nom',)
    radio_fields = {'type': HORIZONTAL}
    raw_id_fields = ('oeuvre', 'professions', 'parent')
    autocomplete_lookup_fields = {
        'm2m': ('professions',),
        'fk': ('oeuvre', 'parent'),
    }
    fieldsets = (
        (None, {
            'fields': ('type', ('nom', 'nom_pluriel'),
                       'oeuvre', 'professions', 'parent', 'classement'),
        }),
    )


class OeuvreAdmin(VersionAdmin, AutoriteAdmin):
    form = OeuvreForm
    list_display = ('__str__', 'titre', 'titre_secondaire', 'genre',
                    'caracteristiques_html', 'auteurs_html',
                    'creation', 'link',)
    search_fields = Oeuvre.autocomplete_search_fields(add_icontains=False)
    list_filter = ('genre', 'tonalite', 'arrangement', 'type_extrait')
    list_select_related = ('genre', 'etat', 'owner')
    date_hierarchy = 'creation_date'
    raw_id_fields = ('genre', 'extrait_de', 'creation_lieu')
    autocomplete_lookup_fields = {
        'fk': ('genre', 'extrait_de', 'creation_lieu'),
    }
    readonly_fields = ('__str__', 'html', 'link',)
    inlines = (AuteurInline, PupitreInline, OeuvreMereInline)
    fieldsets = (
        (_('Titre significatif'), {
            'fields': (('prefixe_titre', 'titre',), 'coordination',
                       ('prefixe_titre_secondaire', 'titre_secondaire',),),
        }),
        (None, {
            'fields': (('genre', 'numero'), ('coupe', 'indeterminee')),
        }),
        (_('Données musicales'), {
            'fields': ('incipit', ('tempo', 'tonalite'),
                       ('sujet', 'arrangement')),
        }),
        (None, {
            'fields': (('surnom', 'nom_courant'),),
        }),
        (None, {
            'fields': (('opus', 'ict'),),
        }),
        (None, {
            'fields': ('extrait_de', ('type_extrait', 'numero_extrait')),
        }),
        (_('Création'), {
            'fields': (
                'creation_type',
                ('creation_date', 'creation_date_approx'),
                ('creation_heure', 'creation_heure_approx'),
                ('creation_lieu', 'creation_lieu_approx'))
        }),
    )
    fieldsets_and_inlines_order = ('i', 'f', 'f', 'i', 'f', 'f', 'f', 'f', 'f')

    def get_queryset(self, request):
        qs = super(OeuvreAdmin, self).get_queryset(request)
        return qs.select_related(
            'genre', 'extrait_de', 'creation_lieu',
            'etat', 'owner'
        ).prefetch_related(
            'auteurs__individu', 'auteurs__ensemble', 'auteurs__profession',
            'pupitres__partie'
        )


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


class EvenementAdmin(SuperModelAdmin, VersionAdmin, AutoriteAdmin):
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
        return qs.select_related(
            'debut_lieu', 'debut_lieu__nature',
            'debut_lieu__parent', 'debut_lieu__parent__nature',
            'etat', 'owner')


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
site.register(Saison, SaisonAdmin)
site.register(Profession, ProfessionAdmin)
site.register(TypeDeParenteDOeuvres, TypeDeParenteDOeuvresAdmin)
site.register(TypeDeParenteDIndividus, TypeDeParenteDIndividusAdmin)
site.register(Individu, IndividuAdmin)
site.register(TypeDEnsemble, TypeDEnsembleAdmin)
site.register(Ensemble, EnsembleAdmin)
site.register(GenreDOeuvre, GenreDOeuvreAdmin)
site.register(TypeDeCaracteristiqueDeProgramme,
              TypeDeCaracteristiqueDeProgrammeAdmin)
site.register(CaracteristiqueDeProgramme, CaracteristiqueDeProgrammeAdmin)
site.register(Partie, PartieAdmin)
site.register(Oeuvre, OeuvreAdmin)
site.register(Evenement, EvenementAdmin)
site.register(TypeDeSource, TypeDeSourceAdmin)
site.register(Source, SourceAdmin)
