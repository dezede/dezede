# coding: utf-8

from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.db.models import CharField, DateField, ManyToManyField, \
                             TextField, permalink
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from catalogue.models import Lieu, Oeuvre, Evenement, Individu
from catalogue.models.common import CommonModel
from catalogue.models.functions import str_list_w_last


class DossierDEvenements(MPTTModel, CommonModel):
    titre = CharField(_('titre'), max_length=100)
    contenu = TextField(_('contenu'))
    debut = DateField(_('début'), blank=True, null=True)
    fin = DateField(_('fin'), blank=True, null=True)
    lieux = ManyToManyField(Lieu, blank=True, null=True,
                            verbose_name=_('lieux'))
    oeuvres = ManyToManyField(Oeuvre, blank=True, null=True,
                              verbose_name=_('œuvres'))
    auteurs = ManyToManyField(Individu, blank=True, null=True,
                              verbose_name=_('auteurs'))
    circonstance = CharField(_('circonstance'), max_length=100, blank=True)
    evenements = ManyToManyField(Evenement, verbose_name=_('événements'),
                                 blank=True, null=True)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children')

    class Meta(object):
        verbose_name = ungettext_lazy('dossier d’événements',
                                      'dossiers d’événements', 0)
        verbose_name_plural = ungettext_lazy('dossier d’événements',
                                             'dossiers d’événements', 1)
        ordering = ('titre',)

    def __unicode__(self):
        return self.titre

    @permalink
    def get_absolute_url(self):
        return 'dossierdevenements_detail', (self.pk,)

    @permalink
    def get_data_absolute_url(self):
        return 'dossierdevenements_data_detail', (self.pk,)

    def get_queryset(self):
        if self.pk and self.evenements.exists():
            return self.evenements.all()
        kwargs = {}
        if self.debut:
            kwargs['ancrage_debut__date__gte'] = self.debut
        if self.fin:
            kwargs['ancrage_debut__date__lte'] = self.fin
        if self.pk:
            if self.lieux.exists():
                kwargs['ancrage_debut__lieu__in'] = self.lieux.all()
            if self.oeuvres.exists():
                kwargs['programme__oeuvre__in'] = self.oeuvres.all()
            if self.auteurs.exists():
                kwargs['programme__oeuvre__auteurs__individu__in'] \
                    = self.auteurs.all()
        if self.circonstance:
            kwargs['circonstance__icontains'] = self.circonstance
        if kwargs:
            return Evenement.objects.filter(**kwargs).distinct()
        return Evenement.objects.none()
    get_queryset.short_description = _('ensemble de données')

    def get_count(self):
        return self.get_queryset().count()
    get_count.short_description = _('quantité de données sélectionnées')

    def get_queryset_url(self):
        url = reverse('evenements')
        request_kwargs = []
        if self.lieux.exists():
            request_kwargs.append('lieu=|%s|' % '|'.join([str(l.pk)
                                  for l in self.lieux.all()]))
        if self.oeuvres.exists():
            request_kwargs.append('oeuvre=|%s|' % '|'.join([str(o.pk)
                                  for o in self.oeuvres.all()]))
        if request_kwargs:
            url += '?' + '&'.join(request_kwargs)
        return url

    def lieux_html(self):
        return str_list_w_last([l.html() for l in self.lieux.all()])
    lieux_html.short_description = _('lieux')
    lieux_html.allow_tags = True

    def oeuvres_html(self):
        return str_list_w_last([o.titre_html()
                                for o in self.oeuvres.all()])
    oeuvres_html.short_description = _('œuvres')
    oeuvres_html.allow_tags = True

    def auteurs_html(self):
        return str_list_w_last([a.html() for a in self.auteurs.all()])
    auteurs_html.short_description = _('auteurs')
    auteurs_html.allow_tags = True
