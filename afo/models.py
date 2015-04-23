# coding: utf-8

from __future__ import unicode_literals
from django.db.models import (
    Model, OneToOneField, CharField, PositiveIntegerField
)
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.translation import ugettext_lazy as _
from libretto.models import Evenement, Lieu

__all__ = ('EvenementAFO', 'LieuAFO')


@python_2_unicode_compatible
class EvenementAFO(Model):
    evenement = OneToOneField(Evenement, related_name='afo',
                              verbose_name=_('événement'))
    code_programme = CharField(_('code du programme'), max_length=55,
                               blank=True)
    exonerees = PositiveIntegerField(_('entrées exonérées'), null=True,
                                     blank=True)
    payantes = PositiveIntegerField(_('entrées payantes'), null=True,
                                    blank=True)
    scolaires = PositiveIntegerField(_('entrées scolaires'), null=True,
                                     blank=True)
    frequentation = PositiveIntegerField(_('fréquentation totale'), null=True,
                                         blank=True)
    jauge = PositiveIntegerField(_('jauge'), null=True, blank=True)

    class Meta(object):
        verbose_name = _('événement AFO')
        verbose_name_plural = _('événements AFO')

    def __str__(self):
        return force_text(self.evenement)


@python_2_unicode_compatible
class LieuAFO(Model):
    lieu = OneToOneField(Lieu, related_name='afo',
                         verbose_name=_('lieu ou institution'))
    code_postal = CharField(_('code postal'), max_length=10, blank=True)
    TYPES_DE_SCENES = (
        ('N', 'nationale'),
        ('C', 'conventionnée'),
    )
    type_de_scene = CharField(_('type de scène'), max_length=1, blank=True,
                              choices=TYPES_DE_SCENES)

    class Meta(object):
        verbose_name = _('lieu ou institution AFO')
        verbose_name_plural = _('lieux et institutions AFO')

    def __str__(self):
        return force_text(self.lieu)
