# coding: utf-8

from .functions import href, date_html, str_list
from django.db.models import CharField, ForeignKey, ManyToManyField, \
                             DateField, TimeField, permalink, get_model
from tinymce.models import HTMLField
from django.utils.html import strip_tags
from django.utils.translation import pgettext, ungettext_lazy, \
                                     ugettext,  ugettext_lazy as _
from django.template.defaultfilters import time, capfirst
from autoslug import AutoSlugField
from .common import CustomModel, LOWER_MSG, PLURAL_MSG, DATE_MSG, calc_pluriel


class NatureDeLieu(CustomModel):
    nom = CharField(_('nom'), max_length=255, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=430, blank=True,
                            help_text=PLURAL_MSG)
    slug = AutoSlugField(populate_from='nom')

    class Meta:
        verbose_name = ungettext_lazy('nature de lieu', 'natures de lieu', 1)
        verbose_name_plural = ungettext_lazy('nature de lieu',
                                             'natures de lieu', 2)
        ordering = ['slug']
        app_label = 'catalogue'

    def pluriel(self):
        return calc_pluriel(self)

    def __unicode__(self):
        return self.nom

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains',)


class Lieu(CustomModel):
    nom = CharField(_('nom'), max_length=200)
    parent = ForeignKey('Lieu', related_name='enfants', null=True, blank=True,
        verbose_name=_('parent'))
    nature = ForeignKey(NatureDeLieu, related_name='lieux',
        verbose_name=_('nature'))
    historique = HTMLField(_('historique'), blank=True)
    illustrations = ManyToManyField('Illustration', related_name='lieux',
        blank=True, null=True, verbose_name=_('illustrations'))
    documents = ManyToManyField('Document', related_name='lieux', blank=True,
        null=True, verbose_name=_('documents'))
    etat = ForeignKey('Etat', related_name='lieux', null=True, blank=True,
        verbose_name=_('état'))
    notes = HTMLField(_('notes'), blank=True)
    slug = AutoSlugField(populate_from='nom')

    @permalink
    def get_absolute_url(self):
        return ('lieu', [self.slug])

    @permalink
    def permalien(self):
        return ('lieu_pk', [self.pk])

    def link(self):
        return self.html()
    link.short_description = _('lien')
    link.allow_tags = True

    def short_link(self):
        return self.html(short=True)

    def evenements(self):  # TODO: gérer les fins d'événements.
        return get_model('Evenement').objects.filter(ancrage_debut__lieu=self)

    def individus_nes(self):
        return get_model('Individu').objects \
                                    .filter(ancrage_naissance__lieu=self)

    def individus_decedes(self):
        return get_model('Individu').objects.filter(ancrage_deces__lieu=self)

    def oeuvres_composees(self):
        return get_model('Oeuvre').objects \
                                  .filter(ancrage_composition__lieu=self)

    def html(self, tags=True, short=False):
        pat = ugettext('%(lieu)s')
        url = None if not tags else self.get_absolute_url()
        d = {'lieu': self.nom}
        parent = self.parent
        if parent and not short:
            d['lieu_parent'] = parent.nom
            pat = ugettext('%(lieu_parent)s, %(lieu)s')
        out = pat % d
        return href(url, out, tags)
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    class Meta:
        verbose_name = ungettext_lazy('lieu', 'lieux', 1)
        verbose_name_plural = ungettext_lazy('lieu', 'lieux', 2)
        ordering = ['nom']
        app_label = 'catalogue'

    def __unicode__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains',)


class Saison(CustomModel):
    lieu = ForeignKey('Lieu', related_name='saisons', verbose_name=_('lieu'))
    debut = DateField(_(u'début'), help_text=DATE_MSG)
    fin = DateField(_('fin'))

    class Meta:
        verbose_name = ungettext_lazy('saison', 'saisons', 1)
        verbose_name_plural = ungettext_lazy('saison', 'saisons', 2)
        ordering = ['lieu', 'debut']
        app_label = 'catalogue'

    def __unicode__(self):
        d = {
                'lieu': unicode(self.lieu),
                'debut': self.debut.year,
                'fin': self.fin.year
            }
        return pgettext("saison : pattern d'affichage",
                        u'%(lieu)s, %(debut)d–%(fin)d') % d


class AncrageSpatioTemporel(CustomModel):
    date = DateField(_(u'date (précise)'), blank=True, null=True,
        help_text=DATE_MSG)
    heure = TimeField(_(u'heure (précise)'), blank=True, null=True)
    lieu = ForeignKey('Lieu', related_name='ancrages', blank=True, null=True,
        verbose_name=_(u'lieu (précis)'))
    date_approx = CharField(_('date (approximative)'), max_length=200,
        blank=True, help_text=_(u'Ne remplir que si la date est imprécise.'))
    heure_approx = CharField(_('heure (approximative)'), max_length=200,
        blank=True, help_text=_(u'Ne remplir que si l’heure est imprécise.'))
    lieu_approx = CharField(_('lieu (approximatif)'), max_length=200,
        blank=True, help_text=_(u'Ne remplir que si le lieu est imprécis.'))

    def year(self):
        if self.date:
            return self.date.year
        return None

    def month(self):
        if self.date:
            return self.date.month
        return None

    def day(self):
        if self.date:
            return self.date.day
        return None

    def calc_date(self, tags=True):
        if self.date:
            return date_html(self.date, tags)
        return self.date_approx
    calc_date.short_description = _('date')
    calc_date.admin_order_field = 'date'

    def calc_heure(self):
        if self.heure:
            return time(self.heure, ugettext('H\hi'))
        return self.heure_approx
    calc_heure.short_description = _('heure')
    calc_heure.admin_order_field = 'heure'

    def calc_moment(self, tags=True):
        l = []
        date = self.calc_date(tags)
        heure = self.calc_heure()
        pat_date = ugettext('le %(date)s') if self.date \
              else ugettext('%(date)s')
        pat_heure = ugettext(u'à %(heure)s') if self.heure \
               else ugettext('%(heure)s')
        l.append(pat_date % {'date': date})
        l.append(pat_heure % {'heure': heure})
        return str_list(l, ' ')

    def calc_lieu(self, tags=True):
        if self.lieu:
            return self.lieu.html(tags)
        return self.lieu_approx
    calc_lieu.short_description = _('lieu')
    calc_lieu.admin_order_field = 'lieu'
    calc_lieu.allow_tags = True

    def html(self, tags=True):
        out = str_list((self.calc_lieu(tags), self.calc_moment(tags)))
        return capfirst(out)

    class Meta:
        verbose_name = ungettext_lazy('ancrage spatio-temporel',
                                      'ancrages spatio-temporels', 1)
        verbose_name_plural = ungettext_lazy('ancrage spatio-temporel',
                                             'ancrages spatio-temporels', 2)
        ordering = ['date', 'heure', 'lieu', 'date_approx',
                    'heure_approx', 'lieu_approx']
        app_label = 'catalogue'

    def __unicode__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return ('lieu__nom__icontains', 'lieu__parent__nom__icontains',
                'date__icontains', 'heure__icontains',
                'lieu_approx__icontains', 'date_approx__icontains',
                'heure_approx__icontains',)
