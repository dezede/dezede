from django.contrib.gis.db.models import GeometryField
from django.core.exceptions import ValidationError
from django.db.models import (
    CharField, ForeignKey, BooleanField, DateField, Q, PROTECT, CASCADE,
)
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from tinymce.models import HTMLField
from tree.fields import PathField
from tree.models import TreeModelMixin

from .base import (
    CommonModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, PublishedManager,
    DATE_MSG, calc_pluriel, SlugModel, UniqueSlugModel, PublishedQuerySet,
    CommonTreeQuerySet, CommonTreeManager, CommonQuerySet, CommonManager,
    slugify_unicode)
from common.utils.html import href
from .evenement import Evenement
from .individu import Individu
from .oeuvre import Oeuvre


__all__ = (
    'NatureDeLieu', 'Lieu', 'Saison',
)


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

    search_fields = ['nom', 'nom_pluriel']

    class Meta(CommonModel.Meta):
        verbose_name = _('nature de lieu')
        verbose_name_plural = _('natures de lieu')
        ordering = ('slug',)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('lieux',)
        return ()

    def pluriel(self):
        return calc_pluriel(self)

    def __str__(self):
        return self.nom


class LieuQuerySet(PublishedQuerySet,
                   CommonTreeQuerySet):
    pass


class LieuManager(CommonTreeManager, PublishedManager):
    queryset_class = LieuQuerySet


class Lieu(TreeModelMixin, AutoriteModel, UniqueSlugModel):
    nom = CharField(_('nom'), max_length=200, db_index=True)
    parent = ForeignKey(
        'self', null=True, blank=True, related_name='enfants',
        verbose_name=_('parent'), on_delete=CASCADE)
    path = PathField(order_by=('nom',), db_index=True)
    nature = ForeignKey(NatureDeLieu, related_name='lieux',
                        verbose_name=_('nature'), on_delete=PROTECT)
    is_institution = BooleanField(_('institution'), default=False)
    # TODO: Parentés d'institution avec périodes d'activité pour l'histoire des
    # institutions.
    historique = HTMLField(_('historique'), blank=True)
    geometry = GeometryField(
        _('géo-positionnement'), blank=True, null=True, db_index=True)

    objects = LieuManager()

    search_fields = ['nom']

    class Meta(AutoriteModel.Meta):
        verbose_name = _('lieu ou institution')
        verbose_name_plural = _('lieux et institutions')
        ordering = ['path']
        unique_together = ('nom', 'parent',)
        permissions = (('can_change_status', _('Peut changer l’état')),)
        indexes = [
            *PathField.get_indexes('lieu', 'path'),
            *AutoriteModel.Meta.indexes,
        ]

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        relations = (
            'enfants', 'evenement_debut_set', 'evenement_fin_set',
        )
        if all_relations:
            relations += (
                'individu_naissance_set', 'individu_deces_set',
                'oeuvre_creation_set', 'dossiers',
            )
        return relations

    def get_absolute_url(self):
        return reverse('lieu_detail', args=[self.slug])

    def permalien(self):
        return reverse('lieu_permanent_detail', args=[self.pk])

    def link(self):
        return self.html()
    link.short_description = _('lien')

    def get_slug(self):
        parent = super(Lieu, self).get_slug()
        return slugify_unicode(self.nom) or parent

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
        l = []
        parent = self
        while parent is not None:
            l.append(parent.nom)
            if parent.nature.referent:
                break
            parent = parent.parent
        return l[::-1]

    def html(self, tags=True, short=False):
        if short or self.parent_id is None or self.nature.referent:
            out = self.nom
        else:
            out = ', '.join(self.ancestors_until_referent())

        url = None if not tags else self.get_absolute_url()
        return href(url, out, tags)
    html.short_description = _('rendu HTML')

    def clean(self):
        if self.parent == self:
            raise ValidationError(_('Le lieu a une parenté avec lui-même.'))

    def __str__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return [
            'search_vector__autocomplete',
            'parent__search_vector__autocomplete',
        ]


class SaisonQuerySet(CommonQuerySet):
    def between_years(self, year0, year1):
        return self.filter(
            debut__range=(f'{year0}-1-1', f'{year1}-12-31'),
            fin__range=(f'{year0}-1-1', f'{year1}-12-31'))

    def evenements(self):
        # FIXME: Implémenter ceci de manière plus performante.
        evenements = Evenement.objects.none()
        for saison in self.defer('owner'):
            evenements |= saison.non_distinct_evenements()
        evenement_ids = set(evenements.values_list('pk', flat=True))
        return Evenement.objects.filter(id__in=evenement_ids).distinct()


class SaisonManager(CommonManager):
    queryset_class = SaisonQuerySet

    def between_years(self, year0, year1):
        return self.get_queryset().between_years(year0, year1)

    def evenements(self):
        return self.get_queryset().evenements()


class Saison(CommonModel):
    ensemble = ForeignKey('Ensemble', related_name='saisons',
                          verbose_name=_('ensemble'), blank=True, null=True,
                          on_delete=CASCADE)
    lieu = ForeignKey('Lieu', related_name='saisons', blank=True, null=True,
                      verbose_name=_('lieu ou institution'), on_delete=CASCADE)
    debut = DateField(_('début'), help_text=DATE_MSG)
    fin = DateField(_('fin'))

    objects = SaisonManager()

    class Meta(object):
        verbose_name = _('saison')
        verbose_name_plural = _('saisons')
        ordering = ('lieu', 'debut')

    def get_periode(self):
        if self.debut.year != self.fin.year:
            return f'{self.debut.year}–{self.fin.year}'
        return f'{self.debut.year}'

    def __str__(self):
        return f'{self.ensemble or self.lieu}, {self.get_periode()}'

    def get_absolute_url(self):
        q = (f'?par_saison=True&'
             f'dates_0={self.debut.year}&dates_1={self.fin.year}')
        if self.lieu_id is not None:
            q += f'&lieu=|{self.lieu_id}|'
        elif self.ensemble_id is not None:
            q += f'&ensemble=|{self.ensemble_id}|'
        return reverse('evenements') + q

    def non_distinct_evenements(self):
        # TODO: Gérer les lieux de fin.
        evenements = Evenement.objects.filter(
            debut_date__range=(self.debut, self.fin))
        if self.lieu_id is not None:
            return evenements.filter(debut_lieu=self.lieu_id)
        return evenements.filter(
            Q(distribution__ensemble=self.ensemble_id)
            | Q(programme__distribution__ensemble=self.ensemble_id))

    def evenements(self):
        return self.non_distinct_evenements().distinct()

    def evenements_count(self):
        return self.evenements().count()
    evenements_count.short_description = _('Nombre d’événements')
