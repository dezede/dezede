# coding: utf-8

from __future__ import unicode_literals
import warnings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey, \
                                                GenericRelation
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import CharField, ForeignKey, ManyToManyField, \
    OneToOneField, BooleanField, PositiveSmallIntegerField, permalink, Q, \
    PositiveIntegerField, get_model, SmallIntegerField, PROTECT, Count
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.html import strip_tags
from django.utils.translation import ungettext_lazy
from cache_tools import model_method_cached, cached_ugettext as ugettext, \
    cached_ugettext_lazy as _
from .common import CommonModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, \
    calc_pluriel, CommonQuerySet, CommonManager, OrderedDefaultDict, \
    PublishedManager, PublishedQuerySet
from .functions import capfirst, str_list, str_list_w_last, href, hlp, \
    microdata


__all__ = (b'ElementDeDistribution', b'CaracteristiqueDElementDeProgramme',
           b'ElementDeProgramme', b'Evenement')


class ElementDeDistributionQuerySet(CommonQuerySet):
    def individus(self):
        return get_model('libretto', 'Individu').objects.filter(
            pk__in=self.values_list('individus', flat=True))

    def evenements(self):
        distributions_evenements = self.filter(
            content_type__app_label='libretto',
            content_type__model='evenement')
        pk_list = distributions_evenements.values_list('object_id', flat=True)
        return Evenement.objects.filter(Q(pk__in=pk_list)
                              | Q(programme__distribution__in=self)).distinct()

    def prefetch(self):
        return self.select_related(
            'pupitre', 'pupitre__partie',
            'profession').prefetch_related('individus')

    def html(self, tags=True):
        return ', '.join(e.html(tags=tags) for e in self)


class ElementDeDistributionManager(CommonManager):
    use_for_related_fields = True

    def get_query_set(self):
        return ElementDeDistributionQuerySet(self.model, using=self._db)

    def individus(self):
        return self.get_query_set().individus()

    def evenements(self):
        return self.get_query_set().evenements()

    def prefetch(self):
        return self.get_query_set().prefetch()

    def html(self, tags=True):
        return self.get_query_set().html(tags=tags)


@python_2_unicode_compatible
class ElementDeDistribution(CommonModel):
    individus = ManyToManyField('Individu', verbose_name=_('individus'),
                                related_name='elements_de_distribution')
    pupitre = ForeignKey(
        'Pupitre', verbose_name=_('pupitre'), null=True, blank=True,
        related_name='elements_de_distribution', on_delete=PROTECT)
    profession = ForeignKey(
        'Profession', verbose_name=_('profession'), null=True, blank=True,
        related_name='elements_de_distribution', on_delete=PROTECT)
    content_type = ForeignKey(ContentType, null=True, on_delete=PROTECT)
    object_id = PositiveIntegerField(null=True)
    content_object = GenericForeignKey()

    objects = ElementDeDistributionManager()

    class Meta(object):
        verbose_name = ungettext_lazy('élément de distribution',
                                      'éléments de distribution', 1)
        verbose_name_plural = ungettext_lazy('élément de distribution',
                                             'éléments de distribution', 2)
        ordering = ('pupitre',)
        app_label = 'libretto'

    def __str__(self):
        return self.html(tags=False)

    def html(self, tags=True):
        out = ''
        if self.pk:
            individus = self.individus.all()
            out += str_list_w_last(individu.html(tags=tags)
                                   for individu in individus)

        if self.pupitre:
            out += ' [' + self.pupitre.partie.link() + ']'
        elif self.profession:
            out += ' [' + self.profession.link() + ']'

        if not tags:
            return strip_tags(out)
        return out

    def related_label(self):
        return self.get_change_link()

    @permalink
    def get_change_url(self):
        return 'admin:libretto_elementdedistribution_change', (self.pk,)

    def get_change_link(self):
        return href(self.get_change_url(), smart_text(self), new_tab=True)

    def clean(self):
        if self.pupitre and self.profession:
            raise ValidationError(_('Vous ne pouvez remplir à la fois '
                                    '« Pupitre » et « Profession ».'))

    @staticmethod
    def autocomplete_search_fields():
        return (
            'pupitre__partie__nom__icontains',
            'individus__nom__icontains',
            'individus__pseudonyme__icontains',
        )


@python_2_unicode_compatible
class CaracteristiqueDElementDeProgramme(CommonModel):
    nom = CharField(_('nom'), max_length=100, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=110, blank=True,
                            help_text=PLURAL_MSG)
    classement = SmallIntegerField(default=1, db_index=True)

    def pluriel(self):
        return calc_pluriel(self)

    class Meta(object):
        verbose_name = ungettext_lazy(
            'caractéristique d’élément de programme',
            'caractéristiques d’élément de programme',
            1)
        verbose_name_plural = ungettext_lazy(
            'caractéristique d’élément de programme',
            'caractéristiques d’élément de programme',
            2)
        ordering = ('nom',)
        app_label = 'libretto'

    def __str__(self):
        return self.nom

    @staticmethod
    def autocomplete_search_fields():
        return (
            'nom__icontains',
            'nom_pluriel__icontains',
        )


@python_2_unicode_compatible
class ElementDeProgramme(AutoriteModel):
    evenement = ForeignKey('Evenement', related_name='programme',
                           db_index=True, verbose_name=_('événement'))
    oeuvre = ForeignKey('Oeuvre', related_name='elements_de_programme',
                        verbose_name=_('œuvre'), blank=True, null=True,
                        db_index=True, on_delete=PROTECT)
    autre = CharField(max_length=500, blank=True, db_index=True)
    caracteristiques = ManyToManyField(
        CaracteristiqueDElementDeProgramme,
        related_name='elements_de_programme', blank=True, null=True,
        verbose_name=_('caractéristiques'))
    NUMEROTATIONS = (
        ('O', _('Numéros')),  # O pour Ordered
        ('B', _('Numéros entre crochets (supposition)')),  # B pour Brackets
        ('U', _('Puce')),  # U pour Unordered
        ('E', _('Absente (entracte, etc)')),  # E pour Empty
    )
    numerotation = CharField(
        _('numérotation'), choices=NUMEROTATIONS, max_length=1, default='O')
    position = PositiveSmallIntegerField(_('Position'))
    # TODO: Quand les nested inlines seront possibles avec Django, remplacer
    # ceci par un GenericRelation.
    distribution = ManyToManyField(
        ElementDeDistribution, related_name='elements_de_programme',
        blank=True, null=True)
    personnels = ManyToManyField('Personnel', blank=True, null=True,
                                 related_name='elements_de_programme')

    class Meta(object):
        verbose_name = ungettext_lazy('élément de programme',
                                      'éléments de programme', 1)
        verbose_name_plural = ungettext_lazy('élément de programme',
                                             'éléments de programme', 2)
        ordering = ('position', 'oeuvre')
        app_label = 'libretto'

    def calc_caracteristiques(self):
        if self.pk is None:
            return ''
        return str_list(smart_text(c) for c in self.caracteristiques.all())
    calc_caracteristiques.allow_tags = True
    calc_caracteristiques.short_description = _('caractéristiques')

    @property
    @model_method_cached(24 * 60 * 60, b'programmes')
    def numero(self):
        numerotations_exclues = ('U', 'E',)
        if self.numerotation in numerotations_exclues:
            return ''
        return self.evenement.programme.exclude(Q(position__gt=self.position)
                           | Q(numerotation__in=numerotations_exclues)).count()

    @model_method_cached(24 * 60 * 60, b'programmes')
    def html(self, tags=True):
        has_pk = self.pk is not None

        distribution = self.distribution.prefetch()
        if has_pk and distribution:
            distribution = distribution.html(tags=tags)
            add_distribution = True
        else:
            distribution = ''
            add_distribution = False

        if self.oeuvre:
            out = self.oeuvre.html(tags)
        elif self.autre:
            out = self.autre
        elif distribution:
            out = distribution
            add_distribution = False
        else:
            warnings.warn('Il manque des champs dans <%(class)s pk=%(pk)s>' %
                          {'class': self.__class__.__name__, 'pk': self.pk})
            return ''

        caracteristiques = self.calc_caracteristiques()
        if caracteristiques:
            out += ' [' + caracteristiques + ']'

        if add_distribution:
            out += '. — ' + distribution

        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def __str__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return (
            'oeuvre__prefixe_titre__icontains', 'oeuvre__titre__icontains',
            'oeuvre__prefixe_titre_secondaire__icontains',
            'oeuvre__titre_secondaire__icontains',
            'oeuvre__genre__nom__icontains',
        )


class EvenementQuerySet(PublishedQuerySet):
    def yearly_counts(self):
        return get_model('libretto', 'AncrageSpatioTemporel').objects.filter(
            Q(evenements_debuts__in=self) | Q(evenements_fins__in=self)) \
            .extra({'year': connection.ops.date_trunc_sql('year', 'date')}) \
            .values('year').annotate(count=Count('evenements_debuts')) \
            .order_by('year')


class EvenementManager(PublishedManager):
    def get_query_set(self):
        return EvenementQuerySet(self.model, using=self._db)

    def yearly_counts(self):
        return self.get_query_set().yearly_counts()


@python_2_unicode_compatible
class Evenement(AutoriteModel):
    ancrage_debut = OneToOneField(
        'AncrageSpatioTemporel', related_name='evenements_debuts',
        db_index=True, on_delete=PROTECT)
    ancrage_fin = OneToOneField(
        'AncrageSpatioTemporel', related_name='evenements_fins', blank=True,
        null=True, db_index=True, on_delete=PROTECT)
    relache = BooleanField(verbose_name='relâche', db_index=True)
    circonstance = CharField(max_length=500, blank=True, db_index=True)
    distribution = GenericRelation(ElementDeDistribution)

    objects = EvenementManager()

    class Meta(object):
        verbose_name = ungettext_lazy('événement', 'événements', 1)
        verbose_name_plural = ungettext_lazy('événement', 'événements', 2)
        ordering = ('ancrage_debut',)
        app_label = 'libretto'
        permissions = (('can_change_status', _('Peut changer l’état')),)

    @permalink
    def get_absolute_url(self):
        return 'evenement_pk', (self.pk,)

    def permalien(self):
        return self.get_absolute_url()

    def link(self):
        return href(self.get_absolute_url(), smart_text(self))
    link.short_description = _('lien')
    link.allow_tags = True

    def sources_by_type(self):
        sources = OrderedDefaultDict()
        for source in self.sources.select_related('type'):
            sources[source.type].append(source)
        return sources.items()

    def get_meta_name(self, tags=False):
        if self.circonstance:
            out = self.circonstance
        else:
            distribution = self.distribution.prefetch()
            if distribution:
                out = distribution.html(tags=tags)
            else:
                programme = self.programme.all()
                if programme.exists():
                    element = programme[0]
                    out = element.oeuvre or element.autre
                else:
                    return ''
        return microdata(out, 'summary', tags=tags)

    def html(self, tags=True):
        relache = ''
        circonstance = ''
        if self.circonstance:
            circonstance = hlp(self.circonstance, ugettext('circonstance'),
                               tags)
        if self.relache:
            relache = microdata(ugettext('Relâche'), 'eventType', tags=tags)

        lieu = microdata(self.ancrage_debut.calc_lieu(tags), 'location',
                         tags=tags)

        return str_list((lieu, circonstance,
                         self.ancrage_debut.calc_heure(), relache))

    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def has_program(self):
        return self.relache or self.programme.exists()
    has_program.short_description = _('programme')
    has_program.boolean = True

    def has_source(self):
        return self.sources.exists()
    has_source.short_description = _('source')
    has_source.boolean = True
    has_source.admin_order_field = 'sources'

    def __str__(self):
        out = self.ancrage_debut.calc_date(False)
        out = capfirst(out)
        out += '\u00A0> ' + self.html(False)
        return strip_tags(out)

    @staticmethod
    def autocomplete_search_fields():
        return (
            'circonstance__icontains',
            'ancrage_debut__lieu__nom__icontains',
            'ancrage_debut__lieu__parent__nom__icontains',
            'ancrage_debut__date__icontains',
            'ancrage_debut__heure__icontains',
            'ancrage_debut__lieu_approx__icontains',
            'ancrage_debut__date_approx__icontains',
            'ancrage_debut__heure_approx__icontains',
        )
