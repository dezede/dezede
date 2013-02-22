# coding: utf-8

from __future__ import unicode_literals
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey, \
                                                GenericRelation
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import CharField, ForeignKey, ManyToManyField, \
                             FloatField, OneToOneField, BooleanField, \
                             PositiveSmallIntegerField, permalink, Q, \
                             PositiveIntegerField, get_model
from django.dispatch import receiver
from django.template.defaultfilters import capfirst
from django.utils.html import strip_tags
from django.utils.translation import ungettext_lazy, ugettext, \
                                     ugettext_lazy as _
from reversion.models import post_revision_commit
from .common import CommonModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, \
    calc_pluriel, CommonQuerySet, CommonManager

from .functions import str_list, str_list_w_last, href, hlp
from .source import TypeDeSource


__all__ = (b'ElementDeDistribution', b'CaracteristiqueDElementDeProgramme',
           b'ElementDeProgramme', b'Evenement')


class ElementDeDistributionQuerySet(CommonQuerySet):
    def individus(self):
        return get_model('catalogue', 'Individu').objects.filter(
            pk__in=self.values_list('individus', flat=True))

    def evenements(self):
        distributions_evenements = self.filter(
            content_type__app_label='catalogue',
            content_type__model='evenement')
        pk_list = distributions_evenements.values_list('object_id', flat=True)
        return Evenement.objects.filter(Q(pk__in=pk_list)
                              | Q(programme__distribution__in=self)).distinct()

    def html(self, tags=True):
        return ', '.join(e.html(tags=tags) for e in self.iterator())


class ElementDeDistributionManager(CommonManager):
    use_for_related_fields = True

    def get_query_set(self):
        return ElementDeDistributionQuerySet(self.model, using=self._db)

    def individus(self):
        return self.all().individus()

    def evenements(self):
        return self.all().evenements()

    def html(self, tags=True):
        return self.all().html(tags=tags)


class ElementDeDistribution(CommonModel):
    individus = ManyToManyField('Individu', verbose_name=_('individus'),
                                related_name='elements_de_distribution')
    pupitre = ForeignKey(
        'Pupitre', verbose_name=_('pupitre'), null=True, blank=True,
        related_name='elements_de_distribution')
    profession = ForeignKey(
        'Profession', verbose_name=_('profession'), null=True, blank=True,
        related_name='elements_de_distribution')
    content_type = ForeignKey(ContentType, null=True)
    object_id = PositiveIntegerField(null=True)
    content_object = GenericForeignKey()

    objects = ElementDeDistributionManager()

    class Meta(object):
        verbose_name = ungettext_lazy('élément de distribution',
                                      'éléments de distribution', 1)
        verbose_name_plural = ungettext_lazy('élément de distribution',
                                             'éléments de distribution', 2)
        ordering = ('pupitre',)
        app_label = 'catalogue'

    def __unicode__(self):
        return self.html(tags=False)

    def html(self, tags=True):
        individus = self.individus.iterator()
        out = str_list_w_last(individu.html(tags=tags)
                              for individu in individus)
        partie_ou_profession = ''
        if self.pupitre:
            partie_ou_profession = self.pupitre.partie.link()
        elif self.profession:
            partie_ou_profession = self.profession.link()
        out += ' [' + partie_ou_profession + ']'
        if not tags:
            out = strip_tags(out)
        return out

    def clean(self):
        if not (bool(self.pupitre) ^ bool(self.profession)):
            raise ValidationError(_('Vous devez remplir un pupitre ou '
                                    'une profession, mais pas les deux.'))

    @staticmethod
    def autocomplete_search_fields():
        return (
            'pupitre__partie__nom__icontains',
            'individus__nom__icontains',
            'individus__pseudonyme__icontains',
        )


class CaracteristiqueDElementDeProgramme(CommonModel):
    nom = CharField(_('nom'), max_length=100, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=110, blank=True,
                            help_text=PLURAL_MSG)
    classement = FloatField(default=1.0, db_index=True)

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
        app_label = 'catalogue'

    def __unicode__(self):
        return self.nom

    @staticmethod
    def autocomplete_search_fields():
        return (
            'nom__icontains',
            'nom_pluriel__icontains',
        )


class ElementDeProgramme(AutoriteModel):
    evenement = ForeignKey('Evenement', related_name='programme',
                           db_index=True, verbose_name=_('événement'))
    oeuvre = ForeignKey('Oeuvre', related_name='elements_de_programme',
                        verbose_name=_('œuvre'), blank=True, null=True,
                        db_index=True)
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

    def calc_caracteristiques(self):
        if self.pk is None:
            return ''
        cs = self.caracteristiques.iterator()
        return str_list(unicode(c) for c in cs)
    calc_caracteristiques.allow_tags = True
    calc_caracteristiques.short_description = _('caractéristiques')

    @property
    def numero(self):
        numerotations_exclues = ('U', 'E',)
        if self.numerotation in numerotations_exclues:
            return ''
        return self.evenement.programme.exclude(Q(position__gt=self.position)
                           | Q(numerotation__in=numerotations_exclues)).count()

    def html(self, tags=True):
        out = ''
        oeuvre = self.oeuvre
        if oeuvre:
            out += oeuvre.html(tags)
        else:
            out += self.autre
        if self.pk:
            if self.caracteristiques.exists():
                out += ' [' + self.calc_caracteristiques() + ']'
            if self.distribution.exists():
                out += '. — ' + self.distribution.html(tags=tags)
        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def clean(self):
        if not (self.oeuvre or self.autre):
            raise ValidationError(_('Vous devez remplir au moins « Œuvre » ou '
                                    '« Autre ».'))

    class Meta(object):
        verbose_name = ungettext_lazy('élément de programme',
                                      'éléments de programme', 1)
        verbose_name_plural = ungettext_lazy('élément de programme',
                                             'éléments de programme', 2)
        ordering = ('position', 'oeuvre')
        app_label = 'catalogue'

    def __unicode__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return (
            'oeuvre__prefixe_titre__icontains', 'oeuvre__titre__icontains',
            'oeuvre__prefixe_titre_secondaire__icontains',
            'oeuvre__titre_secondaire__icontains',
            'oeuvre__genre__nom__icontains',
        )


class Evenement(AutoriteModel):
    ancrage_debut = OneToOneField(
        'AncrageSpatioTemporel', related_name='evenements_debuts',
        db_index=True)
    ancrage_fin = OneToOneField(
        'AncrageSpatioTemporel', related_name='evenements_fins', blank=True,
        null=True, db_index=True)
    relache = BooleanField(verbose_name='relâche', db_index=True)
    circonstance = CharField(max_length=500, blank=True, db_index=True)
    distribution = GenericRelation(ElementDeDistribution)

    @permalink
    def get_absolute_url(self):
        return 'evenement_pk', (self.pk,)

    def permalien(self):
        return self.get_absolute_url()

    def link(self):
        return href(self.get_absolute_url(), unicode(self))
    link.short_description = _('lien')
    link.allow_tags = True

    def sources_dict(self):
        types = TypeDeSource.objects.filter(
            sources__evenements=self).distinct()
        d = {}
        for type in types:
            sources = self.sources.filter(type=type)
            d[type] = sources
        return d

    def html(self, tags=True):
        relache, circonstance = '', ''
        if self.circonstance:
            circonstance = hlp(self.circonstance, ugettext('circonstance'),
                               tags)
        if self.relache:
            relache = ugettext('Relâche')
        l = (self.ancrage_debut.calc_lieu(tags), circonstance,
             self.ancrage_debut.calc_heure(), relache)
        out = str_list(l)
        return out
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

    class Meta(object):
        verbose_name = ungettext_lazy('événement', 'événements', 1)
        verbose_name_plural = ungettext_lazy('événement', 'événements', 2)
        ordering = ('ancrage_debut',)
        app_label = 'catalogue'

    def __unicode__(self):
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


@receiver(post_revision_commit)
def clear_all_cache(sender, **kwargs):
    """On vide le cache pour les templates d'événements."""
    cache.clear()
