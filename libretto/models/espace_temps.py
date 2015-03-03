# coding: utf-8

from __future__ import unicode_literals
from django.contrib.gis.db.models import GeometryField, GeoManager
from django.contrib.gis.db.models.query import GeoQuerySet
from django.core.exceptions import ValidationError
from django.db.models import (CharField, ForeignKey, BooleanField, DateField,
                              permalink, Q, PROTECT)
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.html import strip_tags
from django.utils.translation import (
    ungettext_lazy, pgettext, ugettext_lazy as _)
from polymorphic_tree.managers import PolymorphicMPTTQuerySet, \
    PolymorphicMPTTModelManager
from polymorphic_tree.models import PolymorphicMPTTModel, \
    PolymorphicTreeForeignKey
from tinymce.models import HTMLField
from cache_tools import model_method_cached
from .common import CommonModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, \
                    PublishedManager, DATE_MSG, calc_pluriel, SlugModel, \
                    UniqueSlugModel, PublishedQuerySet, CommonTreeQuerySet, \
    CommonTreeManager
from .evenement import Evenement
from .functions import href
from .individu import Individu
from .oeuvre import Oeuvre


__all__ = (
    b'NatureDeLieu', b'Lieu', b'LieuDivers', b'Institution', b'Saison',
)


@python_2_unicode_compatible
class NatureDeLieu(CommonModel, SlugModel):
    nom = CharField(_('nom'), max_length=255, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=430, blank=True,
                            help_text=PLURAL_MSG)
    referent = BooleanField(
        _('référent'), default=False, db_index=True,
        help_text=_(
            'L’affichage d’un lieu remonte jusqu’au lieu référent. '
            'Exemple : dans une architecture de pays, villes, théâtres, etc, '
            '« ville, institution, salle » sera affiché car on remonte '
            'jusqu’à un lieu référent, ici choisi comme étant ceux de nature '
            '« ville »'))

    class Meta(object):
        verbose_name = ungettext_lazy('nature de lieu', 'natures de lieu', 1)
        verbose_name_plural = ungettext_lazy('nature de lieu',
                                             'natures de lieu', 2)
        ordering = ('slug',)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('lieux',)
        return ()

    def pluriel(self):
        return calc_pluriel(self)

    def __str__(self):
        return self.nom

    @staticmethod
    def autocomplete_search_fields():
        return 'nom__icontains',


class LieuQuerySet(PolymorphicMPTTQuerySet, PublishedQuerySet,
                   CommonTreeQuerySet, GeoQuerySet):
    pass


class LieuManager(CommonTreeManager, PolymorphicMPTTModelManager,
                  PublishedManager, GeoManager):
    queryset_class = LieuQuerySet


@python_2_unicode_compatible
class Lieu(PolymorphicMPTTModel, AutoriteModel, UniqueSlugModel):
    nom = CharField(_('nom'), max_length=200, db_index=True)
    parent = PolymorphicTreeForeignKey(
        'self', null=True, blank=True, db_index=True, related_name='enfants',
        verbose_name=_('parent'))
    nature = ForeignKey(NatureDeLieu, related_name='lieux', db_index=True,
                        verbose_name=_('nature'), on_delete=PROTECT)
    # TODO: Parentés d'institution avec périodes d'activité pour l'histoire des
    # institutions.
    historique = HTMLField(_('historique'), blank=True)
    geometry = GeometryField(
        _('point, tracé ou polygone'), blank=True, null=True, db_index=True)
    code_postal = CharField(_('code postal'), max_length=10, blank=True)

    # TODO: Déplacer ce champ dans un champ HStore, JSON ou JSONb en arrivant
    #       à Django 1.8 ou 1.9.  En effet, ceci n’a rien à faire
    #       dans la modélisation.
    TYPES_DE_SCENES = (
        ('N', 'nationale'),
        ('C', 'conventionnée'),
    )
    type_de_scene = CharField(_('type de scène'), max_length=1, blank=True,
                              choices=TYPES_DE_SCENES)

    objects = LieuManager()

    class MPTTMeta(object):
        order_insertion_by = ('nom',)

    class Meta(object):
        verbose_name = ungettext_lazy('lieu ou institution',
                                      'lieux et institutions', 1)
        verbose_name_plural = ungettext_lazy('lieu ou institution',
                                             'lieux et institutions', 2)
        ordering = ('nom',)
        app_label = 'libretto'
        unique_together = ('nom', 'parent',)
        index_together = (('tree_id', 'level', 'lft', 'rght'),)
        permissions = (('can_change_status', _('Peut changer l’état')),)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        relations = (
            'get_real_instance', 'enfants', 'saisons',
            'evenement_debut_set', 'evenement_fin_set',
        )
        if all_relations:
            relations += (
                'individu_naissance_set', 'individu_deces_set',
                'oeuvre_creation_set', 'dossiers',
            )
        return relations

    @permalink
    def get_absolute_url(self):
        return b'lieu_detail', [self.slug]

    @permalink
    def permalien(self):
        return b'lieu_permanent_detail', [self.pk]

    def link(self):
        return self.html()
    link.short_description = _('lien')
    link.allow_tags = True

    def get_slug(self):
        return self.nom

    def short_link(self):
        return self.html(short=True)

    def evenements(self):
        qs = self.get_descendants(include_self=True)
        return Evenement.objects.filter(
            Q(debut_lieu__in=qs) | Q(fin_lieu__in=qs))

    def individus_nes(self):
        return Individu.objects.filter(
            naissance_lieu__in=self.get_descendants(include_self=True)
        ).order_by(*Individu._meta.ordering)

    def individus_decedes(self):
        return Individu.objects.filter(
            deces_lieu__in=self.get_descendants(include_self=True)
        ).order_by(*Individu._meta.ordering)

    def oeuvres_creees(self):
        return Oeuvre.objects.filter(
            creation_lieu__in=self.get_descendants(include_self=True)
        ).order_by(*Oeuvre._meta.ordering)

    def ancestors_until_referent(self):
        ancestors = self.get_ancestors(include_self=True)
        values = ancestors.values_list('nom', 'nature__referent')
        l = []
        for nom, ref in values[::-1]:
            l.append(nom)
            if ref:
                break
        return l[::-1]

    @model_method_cached()
    def html(self, tags=True, short=False):
        if short or self.parent_id is None or self.nature.referent:
            out = self.nom
        else:
            out = ', '.join(self.ancestors_until_referent())

        url = None if not tags else self.get_absolute_url()
        return href(url, out, tags)
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def clean(self):
        if self.parent == self:
            raise ValidationError(_('Le lieu a une parenté avec lui-même.'))

    def __str__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains',
                'parent__nom__icontains')


class LieuDivers(Lieu):
    class Meta(object):
        verbose_name = ungettext_lazy('lieu', 'lieux', 1)
        verbose_name_plural = ungettext_lazy('lieu', 'lieux', 2)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('lieu_ptr',)


class Institution(Lieu):
    class Meta(object):
        verbose_name = ungettext_lazy('institution', 'institutions', 1)
        verbose_name_plural = ungettext_lazy('institution', 'institutions', 2)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('lieu_ptr',)


@python_2_unicode_compatible
class Saison(CommonModel):
    ensemble = ForeignKey('Ensemble', related_name='saisons',
                          verbose_name=_('ensemble'), blank=True, null=True)
    lieu = ForeignKey('Lieu', related_name='saisons', blank=True, null=True,
                      verbose_name=_('lieu ou institution'))
    debut = DateField(_('début'), help_text=DATE_MSG)
    fin = DateField(_('fin'))

    class Meta(object):
        verbose_name = ungettext_lazy('saison', 'saisons', 1)
        verbose_name_plural = ungettext_lazy('saison', 'saisons', 2)
        ordering = ('lieu', 'debut')
        app_label = 'libretto'

    def __str__(self):
        d = {
            'fk': smart_text(self.ensemble or self.lieu),
            'debut': self.debut.year,
            'fin': self.fin.year
        }
        return pgettext('saison : pattern d’affichage',
                        '%(fk)s, %(debut)d–%(fin)d') % d
