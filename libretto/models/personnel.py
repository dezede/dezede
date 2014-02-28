# coding: utf-8

from __future__ import unicode_literals
import warnings
from django.db.models import CharField, ForeignKey, ManyToManyField, \
     FloatField, permalink, SmallIntegerField, PROTECT, DateField, \
    PositiveSmallIntegerField, Model, Q
from django.template.defaultfilters import date
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext_lazy
from mptt.models import MPTTModel, TreeForeignKey
from cache_tools import cached_ugettext_lazy as _, cached_ugettext as ugettext
from ..utils import abbreviate
from .common import CommonModel, LOWER_MSG, PLURAL_MSG, calc_pluriel,\
    UniqueSlugModel, PublishedManager, AutoriteModel, CommonTreeManager, \
    PublishedQuerySet, CommonTreeQuerySet, Caracteristique, \
    TypeDeCaracteristique
from .evenement import Evenement
from .functions import capfirst, ex, href, date_html, sc


__all__ = (
    b'Profession', b'Devise', b'TypeDeCaracteristiqueDEnsemble',
    b'CaracteristiqueDEnsemble', b'Membre', b'Ensemble', b'Engagement',
    b'TypeDePersonnel', b'Personnel')


class ProfessionQuerySet(CommonTreeQuerySet, PublishedQuerySet):
    pass


class ProfessionManager(CommonTreeManager, PublishedManager):
    queryset_class = ProfessionQuerySet


# TODO: Songer à l’arrivée du polymorphisme "Emploi".
@python_2_unicode_compatible
class Profession(MPTTModel, AutoriteModel, UniqueSlugModel):
    nom = CharField(_('nom'), max_length=200, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
                            help_text=PLURAL_MSG)
    nom_feminin = CharField(
        _('nom (au féminin)'), max_length=230, blank=True,
        help_text=_('Ne préciser que s’il est différent du nom.'))
    parent = TreeForeignKey('Profession', blank=True, null=True, db_index=True,
                            related_name='enfants', verbose_name=_('parent'))
    classement = SmallIntegerField(default=1, db_index=True)

    objects = ProfessionManager()

    class Meta(object):
        verbose_name = ungettext_lazy('profession', 'professions', 1)
        verbose_name_plural = ungettext_lazy('profession', 'professions', 2)
        ordering = ('classement', 'nom')
        app_label = 'libretto'
        permissions = (('can_change_status', _('Peut changer l’état')),)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        relations = ('auteurs', 'elements_de_distribution',)
        if all_relations:
            relations += ('enfants', 'individus', 'parties', 'engagements',)
        return relations

    @permalink
    def get_absolute_url(self):
        return b'profession_detail', (self.slug,)

    @permalink
    def permalien(self):
        return b'profession_permanent_detail', (self.pk,)

    def pretty_link(self):
        return self.html(caps=True)

    def link(self):
        return self.html()

    def short_link(self):
        return self.short_html()

    def pluriel(self):
        return calc_pluriel(self)

    def feminin(self):
        f = self.nom_feminin
        return f or self.nom

    def html(self, tags=True, short=False, caps=False, feminin=False,
             pluriel=False):
        if pluriel:
            nom = self.pluriel()
            if feminin:
                warnings.warn("Pas de feminin pluriel pour l'instant")
        elif feminin:
            nom = self.feminin()
        else:
            nom = self.nom
        if caps:
            nom = capfirst(nom)
        if short:
            nom = abbreviate(nom, min_vowels=1, min_len=4, tags=tags)
        url = '' if not tags else self.get_absolute_url()
        out = href(url, nom, tags)
        return out

    def short_html(self, tags=True, pluriel=False):
        return self.html(tags, short=True, pluriel=pluriel)

    def __hash__(self):
        return hash(self.nom)

    def __str__(self):
        return capfirst(self.html(tags=False))

    @staticmethod
    def autocomplete_search_fields():
        return 'nom__icontains', 'nom_pluriel__icontains',


class TypeDeCaracteristiqueDEnsemble(TypeDeCaracteristique):
    class Meta(object):
        verbose_name = ungettext_lazy(
            'type de caractéristique d’ensemble',
            'types de caractéristique d’ensemble', 1)
        verbose_name_plural = ungettext_lazy(
            'type de caractéristique d’ensemble',
            'types de caractéristique d’ensemble', 2)
        ordering = ('classement',)
        app_label = 'libretto'


class CaracteristiqueDEnsemble(Caracteristique):
    class Meta(object):
        verbose_name = ungettext_lazy(
            'caractéristique d’ensemble',
            'caractéristiques d’ensemble', 1)
        verbose_name_plural = ungettext_lazy(
            'caractéristique d’ensemble',
            'caractéristiques d’ensemble', 2)
        ordering = ('type', 'classement', 'valeur')
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('caracteristique_ptr', 'ensembles',)


class PeriodeDActivite(Model):
    YEAR = 0
    MONTH = 1
    DAY = 2
    PRECISIONS = (
        (YEAR, _('Année')),
        (MONTH, _('Mois')),
        (DAY, _('Jour')),
    )
    debut = DateField(_('début'), blank=True, null=True)
    debut_precision = PositiveSmallIntegerField(
        _('précision du début'), choices=PRECISIONS, default=0)
    fin = DateField(_('fin'), blank=True, null=True)
    fin_precision = PositiveSmallIntegerField(
        _('précision de la fin'), choices=PRECISIONS, default=0)

    class Meta(object):
        abstract = True

    def _smart_date(self, attr, attr_precision, tags=True):
        d = getattr(self, attr)
        if d is None:
            return
        precision = getattr(self, attr_precision)
        if precision == self.YEAR:
            return smart_text(d.year)
        if precision == self.MONTH:
            return date(d, 'F Y')
        if precision == self.DAY:
            return date_html(d, tags=tags)

    def smart_debut(self, tags=True):
        return self._smart_date('debut', 'debut_precision', tags=tags)

    def smart_fin(self, tags=True):
        return self._smart_date('fin', 'fin_precision', tags=tags)

    def smart_period(self, tags=True):
        debut = self.smart_debut(tags=tags)
        fin = self.smart_fin(tags=tags)
        # TODO: Rendre ceci plus simple en conservant les possibilités
        # d’internationalisation.
        if fin is None:
            if debut is None:
                return ''
            if self.debut_precision == self.DAY:
                t = ugettext('depuis le %(debut)s')
            else:
                t = ugettext('depuis %(debut)s')
        else:
            if debut is None:
                if self.fin_precision == self.DAY:
                    t = ugettext('jusqu’au %(fin)s')
                else:
                    t = ugettext('jusqu’à %(fin)s')
            else:
                if self.debut_precision == self.DAY:
                    if self.fin_precision == self.DAY:
                        t = ugettext('du %(debut)s au %(fin)s')
                    else:
                        t = ugettext('du %(debut)s à %(fin)s')
                else:
                    if self.fin_precision == self.DAY:
                        t = ugettext('de %(debut)s au %(fin)s')
                    else:
                        t = ugettext('de %(debut)s à %(fin)s')
        return t % {'debut': debut, 'fin': fin}
    smart_period.short_description = _('Période d’activité')


@python_2_unicode_compatible
class Membre(CommonModel, PeriodeDActivite):
    ensemble = ForeignKey('Ensemble', related_name='membres',
                          verbose_name=_('ensemble'))
    # TODO: Ajouter nombre pour les membres d'orchestre pouvant être saisi
    # au lieu d'un individu.
    individu = ForeignKey('Individu', related_name='membres',
                          verbose_name=_('individu'))
    instrument = ForeignKey(
        'Instrument', blank=True, null=True, related_name='membres',
        verbose_name=_('instrument'))
    classement = SmallIntegerField(default=1)

    class Meta(object):
        verbose_name = _('membre')
        verbose_name_plural = _('membres')
        ordering = ('instrument', 'classement')
        app_label = 'libretto'

    def html(self, tags=True):
        l = [self.individu.html(tags=tags)]
        if self.instrument:
            l.append('[%s]' % self.instrument.html(tags=tags))
        if self.debut or self.fin:
            l.append('(%s)' % self.smart_period(tags=tags))
        return mark_safe(' '.join(l))

    def __str__(self):
        return self.html(tags=False)

    def link(self):
        return self.html()


@python_2_unicode_compatible
class Ensemble(AutoriteModel, PeriodeDActivite, UniqueSlugModel):
    particule_nom = CharField(
        _('particule du nom'), max_length=5, blank=True, db_index=True)
    nom = CharField(_('nom'), max_length=75, db_index=True)
    # TODO: Ajouter une typologie (orchestre, chœur, groupe de rock)
    # facultative.
    caracteristiques = ManyToManyField(
        CaracteristiqueDEnsemble, blank=True, null=True,
        related_name='ensembles', verbose_name=_('caractéristiques'))
    # TODO: Permettre deux villes sièges.
    siege = ForeignKey('Lieu', null=True, blank=True,
                       related_name='ensembles', verbose_name=_('siège'))
    # TODO: Ajouter historique d'ensemble.

    individus = ManyToManyField('Individu', through=Membre,
                                related_name='ensembles')

    class Meta(object):
        app_label = 'libretto'

    def __str__(self):
        return self.html(tags=False)

    def html(self, tags=True):
        if tags:
            return href(self.get_absolute_url(),
                        sc(self.nom, tags=tags), tags=tags)
        return self.nom

    def link(self):
        return self.html()

    @permalink
    def get_absolute_url(self):
        return b'ensemble_detail', (self.slug,)

    @permalink
    def permalien(self):
        return b'ensemble_permanent_detail', (self.pk,)

    def calc_caracteristiques(self, tags=True, caps=False):
        return self.caracteristiques.html(tags=tags, caps=caps)
    calc_caracteristiques.short_description = _('caractéristiques')
    calc_caracteristiques.allow_tags = True
    calc_caracteristiques.admin_order_field = 'caracteristiques'

    def membres_count(self):
        return self.membres.count()
    membres_count.short_description = _('nombre de membres')

    def apparitions(self):
        # FIXME: Pas sûr que la condition soit logique.
        return Evenement.objects.filter(
            Q(distribution__ensembles=self)
            | Q(programme__distribution__ensembles=self)).distinct()

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('elements_de_distribution',)

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'siege__nom__icontains')


# TODO: Peut-être supprimer ce modèle.
@python_2_unicode_compatible
class Devise(CommonModel):
    """
    Modélisation naïve d’une unité monétaire.
    """
    nom = CharField(max_length=200, blank=True, help_text=ex(_('euro')),
        unique=True, db_index=True)
    symbole = CharField(max_length=10, help_text=ex(_('€')), unique=True,
                        db_index=True)

    class Meta(object):
        verbose_name = ungettext_lazy('devise', 'devises', 1)
        verbose_name_plural = ungettext_lazy('devise', 'devises', 2)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('engagements',)
        return ()

    def __str__(self):
        if self.nom:
            return self.nom
        return self.symbole


# TODO: Peut-être supprimer ce modèle.
@python_2_unicode_compatible
class Engagement(CommonModel):
    individus = ManyToManyField('Individu', related_name='engagements',
                                db_index=True)
    profession = ForeignKey('Profession', related_name='engagements',
                            db_index=True, on_delete=PROTECT)
    salaire = FloatField(blank=True, null=True, db_index=True)
    devise = ForeignKey('Devise', blank=True, null=True, db_index=True,
                        related_name='engagements', on_delete=PROTECT)

    class Meta(object):
        verbose_name = ungettext_lazy('engagement', 'engagements', 1)
        verbose_name_plural = ungettext_lazy('engagement', 'engagements', 2)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('personnels',)
        return ()

    def __str__(self):
        return self.profession.nom


# TODO: Peut-être supprimer ce modèle.
@python_2_unicode_compatible
class TypeDePersonnel(CommonModel):
    nom = CharField(max_length=100, unique=True, db_index=True)

    class Meta(object):
        verbose_name = ungettext_lazy('type de personnel',
                                      'types de personnel', 1)
        verbose_name_plural = ungettext_lazy('type de personnel',
                                             'types de personnel', 2)
        ordering = ('nom',)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('personnels',)
        return ()

    def __str__(self):
        return self.nom


# TODO: Peut-être supprimer ce modèle.
@python_2_unicode_compatible
class Personnel(CommonModel):
    type = ForeignKey('TypeDePersonnel', related_name='personnels',
                      db_index=True, on_delete=PROTECT)
    saison = ForeignKey('Saison', related_name='personnels', db_index=True,
                        on_delete=PROTECT)
    engagements = ManyToManyField('Engagement', related_name='personnels',
                                  db_index=True)

    class Meta(object):
        verbose_name = ungettext_lazy('personnel', 'personnels', 1)
        verbose_name_plural = ungettext_lazy('personnel', 'personnels', 2)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('elements_de_programme',)
        return ()

    def __str__(self):
        return smart_text(self.type) + smart_text(self.saison)
