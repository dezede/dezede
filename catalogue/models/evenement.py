# coding: utf-8

from __future__ import unicode_literals
from .functions import str_list, str_list_w_last, href, hlp
from django.db.models import CharField, ForeignKey, ManyToManyField, \
                             FloatField, OneToOneField, BooleanField, \
                             PositiveSmallIntegerField, permalink, get_model
from django.utils.html import strip_tags
from django.utils.translation import ungettext_lazy, ugettext, \
                                     ugettext_lazy as _
from django.template.defaultfilters import capfirst
from .common import CustomModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, \
                    calc_pluriel
from django.core.cache import cache
from reversion.models import post_revision_commit
from django.dispatch import receiver


class ElementDeDistribution(CustomModel):
    pupitre = ForeignKey('Pupitre', related_name='elements_de_distribution')
    individus = ManyToManyField('Individu',
                                related_name='elements_de_distribution')

    class Meta:
        verbose_name = ungettext_lazy('élément de distribution',
                                      'éléments de distribution', 1)
        verbose_name_plural = ungettext_lazy('élément de distribution',
                                             'éléments de distribution', 2)
        ordering = ['pupitre']
        app_label = 'catalogue'

    def __unicode__(self):
        out = unicode(self.pupitre.partie) + ' : '
        ins = self.individus.iterator()
        out += str_list_w_last(unicode(i) for i in ins)
        return out

    @staticmethod
    def autocomplete_search_fields():
        return (
            'pupitre__partie__nom__icontains',
            'individus__nom__icontains',
            'individus__pseudonyme__icontains',
            )


class CaracteristiqueDElementDeProgramme(CustomModel):
    nom = CharField(max_length=100, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(max_length=110, blank=True,
        verbose_name=_('nom (au pluriel)'), help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)

    def pluriel(self):
        return calc_pluriel(self)

    class Meta:
        verbose_name = ungettext_lazy(
                'caractéristique d’élément de programme',
                'caractéristiques d’élément de programme',
                1)
        verbose_name_plural = ungettext_lazy(
                'caractéristique d’élément de programme',
                'caractéristiques d’élément de programme',
                2)
        ordering = ['nom']
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
                            verbose_name=_('événement'))
    oeuvre = ForeignKey('Oeuvre', related_name='elements_de_programme',
        verbose_name=_('œuvre'), blank=True, null=True)
    autre = CharField(max_length=500, blank=True)
    caracteristiques = ManyToManyField(CaracteristiqueDElementDeProgramme,
        related_name='elements_de_programme', blank=True, null=True,
        verbose_name=_('caractéristiques'))
    position = PositiveSmallIntegerField(_('Position'))
    distribution = ManyToManyField(ElementDeDistribution,
        related_name='elements_de_programme', blank=True, null=True)
    personnels = ManyToManyField('Personnel',
        related_name='elements_de_programme', blank=True, null=True)

    def calc_caracteristiques(self):
        if self.pk is None:
            return ''
        cs = self.caracteristiques.iterator()
        return str_list(unicode(c) for c in cs)
    calc_caracteristiques.allow_tags = True
    calc_caracteristiques.short_description = _('caractéristiques')

    def calc_distribution(self, tags=True):
        if self.pk is None:
            return ''
        out = []
        out__append = out.append
        distribution = self.distribution
        if distribution.exists():
            out__append('. — ')
            maxi = distribution.count() - 1
        for i, element in enumerate(distribution.iterator()):
            individus = element.individus.iterator()
            out__append(str_list(individu.html(tags)
                for individu in individus))
            out__append(' [' + element.pupitre.partie.link() + ']')
            if i < maxi:
                out__append(', ')
        return ''.join(out)

    def html(self, tags=True):
        out = []
        out__append = out.append
        oeuvre = self.oeuvre
        if oeuvre:
            out__append(oeuvre.html(tags))
        else:
            out__append(self.autre)
        cs = self.calc_caracteristiques()
        if cs:
            out__append(' [' + cs + ']')
        out__append(self.calc_distribution(tags))
        return ''.join(out)
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    class Meta:
        verbose_name = ungettext_lazy('élément de programme',
                'éléments de programme', 1)
        verbose_name_plural = ungettext_lazy('élément de programme',
                'éléments de programme', 2)
        ordering = ['position', 'oeuvre']
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
    ancrage_debut = OneToOneField('AncrageSpatioTemporel',
        related_name='evenements_debuts')
    ancrage_fin = OneToOneField('AncrageSpatioTemporel',
        related_name='evenements_fins', blank=True, null=True)
    relache = BooleanField(verbose_name='relâche')
    circonstance = CharField(max_length=500, blank=True)

    @permalink
    def get_absolute_url(self):
        return 'evenement_pk', [self.pk]

    def permalien(self):
        return self.get_absolute_url()

    def link(self):
        return href(self.get_absolute_url(), unicode(self))
    link.short_description = _('lien')
    link.allow_tags = True

    def sources_dict(self):
        types = get_model('catalogue',
                          'TypeDeSource').objects \
                                         .filter(sources__evenements=self)
        types = types.distinct()
        d = {}
        for type in types:
            sources = self.sources.filter(type=type)
            if sources:
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

    class Meta:
        verbose_name = ungettext_lazy('événement', 'événements', 1)
        verbose_name_plural = ungettext_lazy('événement', 'événements', 2)
        ordering = ['ancrage_debut']
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
    "On vide le cache pour les templates d'événements."
    cache.clear()
