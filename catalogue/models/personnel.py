# coding: utf-8

from .common import CustomModel, LOWER_MSG, PLURAL_MSG, autoslugify, \
                    calc_pluriel
from .functions import ex
from django.db.models import CharField, SlugField, ForeignKey, \
                             ManyToManyField, FloatField
from . import *
from django.utils.translation import ungettext_lazy, ugettext_lazy as _


class Profession(CustomModel):
    nom = CharField(_('nom'), max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
        help_text=PLURAL_MSG)
    nom_feminin = CharField(_(u'nom (au féminin)'), max_length=230, blank=True,
        help_text=_(u'Ne préciser que s’il est différent du nom.'))
    parente = ForeignKey('Profession', blank=True, null=True,
        related_name='enfant', verbose_name=_('parente'))
    slug = SlugField(blank=True)

    class Meta:
        verbose_name = ungettext_lazy('profession', 'professions', 1)
        verbose_name_plural = ungettext_lazy('profession', 'professions', 2)
        ordering = ['slug']
        app_label = 'catalogue'

    def save(self, *args, **kwargs):
        self.slug = autoslugify(self, unicode(self))
        super(Profession, self).save(*args, **kwargs)

    def pluriel(self):
        return calc_pluriel(self)

    def feminin(self):
        f = self.nom_feminin
        return f if f else self.nom

    def gendered(self, titre='M'):
        return self.nom if titre == 'M' else self.feminin()

    def __unicode__(self):
        return self.nom

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'nom_pluriel__icontains',)


class Devise(CustomModel):
    u'''
    Modélisation naïve d’une unité monétaire.
    '''
    nom = CharField(max_length=200, blank=True, help_text=ex(_('euro')),
        unique=True)
    symbole = CharField(max_length=10, help_text=ex(_(u'€')), unique=True)

    class Meta:
        verbose_name = ungettext_lazy('devise', 'devises', 1)
        verbose_name_plural = ungettext_lazy('devise', 'devises', 2)
        app_label = 'catalogue'

    def __unicode__(self):
        if self.nom:
            return self.nom
        return self.symbole


class Engagement(CustomModel):
    individus = ManyToManyField('Individu', related_name='engagements')
    profession = ForeignKey(Profession, related_name='engagements')
    salaire = FloatField(blank=True)
    devise = ForeignKey(Devise, blank=True, null=True,
        related_name='engagements')

    class Meta:
        verbose_name = ungettext_lazy('engagement', 'engagements', 1)
        verbose_name_plural = ungettext_lazy('engagement', 'engagements', 2)
        app_label = 'catalogue'

    def __unicode__(self):
        return self.profession.nom


class TypeDePersonnel(CustomModel):
    nom = CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = ungettext_lazy('type de personnel',
                                      'types de personnel', 1)
        verbose_name_plural = ungettext_lazy('type de personnel',
                                             'types de personnel', 2)
        ordering = ['nom']
        app_label = 'catalogue'

    def __unicode__(self):
        return self.nom


class Personnel(CustomModel):
    type = ForeignKey(TypeDePersonnel, related_name='personnels')
    saison = ForeignKey('Saison', related_name='personnels')
    engagements = ManyToManyField(Engagement, related_name='personnels')

    class Meta:
        verbose_name = ungettext_lazy('personnel', 'personnels', 1)
        verbose_name_plural = ungettext_lazy('personnel', 'personnels', 2)
        app_label = 'catalogue'

    def __unicode__(self):
        return unicode(self.type) + unicode(self.saison)
