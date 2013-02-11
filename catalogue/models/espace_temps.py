# coding: utf-8

from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.db.models import CharField, ForeignKey, BooleanField, \
                             DateField, TimeField, permalink, Q
from django.template.defaultfilters import time, capfirst
from django.utils.html import strip_tags
from django.utils.translation import pgettext, ungettext_lazy, \
                                     ugettext,  ugettext_lazy as _
from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey
from tinymce.models import HTMLField
from .common import CustomModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, \
                    AutoriteManager, DATE_MSG, calc_pluriel, SlugModel, \
                    UniqueSlugModel
from .evenement import Evenement
from .functions import href, date_html, str_list, ex
from .individu import Individu
from .oeuvre import Oeuvre


__all__ = (b'NatureDeLieu', b'Lieu', b'Saison', b'AncrageSpatioTemporel')


class NatureDeLieu(CustomModel, SlugModel):
    nom = CharField(_('nom'), max_length=255, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=430, blank=True,
                            help_text=PLURAL_MSG)
    referent = BooleanField(_('référent'), default=False,
        help_text=_('L’affichage d’un lieu remonte jusqu’au lieu référent.') \
        + ' ' \
        + ex(unicode(_('ville, institution, salle')),
             pre=unicode(_('dans une architecture de pays, villes, théâtres, '
                           'etc, ')),
             post=unicode(_(' sera affiché car on remonte jusqu’à un lieu '
                            'référent, ici choisi comme étant ceux de nature '
                            '« ville »'))))

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
        return 'nom__icontains',


class LieuManager(TreeManager, AutoriteManager):
    pass


class Lieu(MPTTModel, AutoriteModel, UniqueSlugModel):
    nom = CharField(_('nom'), max_length=200)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='enfant', verbose_name=_('parent'))
    nature = ForeignKey(NatureDeLieu, related_name='lieux',
        verbose_name=_('nature'))
    historique = HTMLField(_('historique'), blank=True)
    objects = LieuManager()

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

    def evenements(self):  # TODO: gérer les fins d'événements.
        return Evenement.objects.filter(ancrage_debut__lieu=self)

    def individus_nes(self):
        return Individu.objects.filter(ancrage_naissance__lieu=self)

    def individus_decedes(self):
        return Individu.objects.filter(ancrage_deces__lieu=self)

    def oeuvres_creees(self):
        return Oeuvre.objects.filter(ancrage_creation__lieu=self)

    def html(self, tags=True, short=False):
        url = None if not tags else self.get_absolute_url()
        if short or self.parent is None or self.nature.referent:
            out = self.nom
        else:
            ancestors = self.get_ancestors(include_self=True)
            ancestors = ancestors.filter(Q(nature__referent=False)
                | Q(nature__referent=True,
                    enfant__nature__referent=False)).distinct()
            out = ', '.join(a.nom for a in ancestors)
        return href(url, out, tags)
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def clean(self):
        if self.parent == self:
            raise ValidationError(_('Le lieu a une parenté avec lui-même.'))

    class MPTTMeta:
        order_insertion_by = ['nom']

    class Meta:
        verbose_name = ungettext_lazy('lieu ou institution',
                                      'lieux ou institutions', 1)
        verbose_name_plural = ungettext_lazy('lieu', 'lieux', 2)
        ordering = ['nom']
        app_label = 'catalogue'
        unique_together = ('nom', 'parent',)

    def __unicode__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains',
                'parent__nom__icontains')


class Saison(CustomModel):
    lieu = ForeignKey('Lieu', related_name='saisons',
                      verbose_name=_('lieu ou institution'))
    debut = DateField(_('début'), help_text=DATE_MSG)
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
        return pgettext('saison : pattern d’affichage',
                        '%(lieu)s, %(debut)d–%(fin)d') % d


class AncrageSpatioTemporel(CustomModel):
    date = DateField(
        _('date (précise)'), blank=True, null=True, help_text=DATE_MSG)
    heure = TimeField(_('heure (précise)'), blank=True, null=True)
    lieu = ForeignKey('Lieu', related_name='ancrages', blank=True, null=True,
        verbose_name=_('lieu ou institution (précis)'))
    date_approx = CharField(_('date (approximative)'), max_length=200,
        blank=True, help_text=_('Ne remplir que si la date est imprécise.'))
    heure_approx = CharField(_('heure (approximative)'), max_length=200,
        blank=True, help_text=_('Ne remplir que si l’heure est imprécise.'))
    lieu_approx = CharField(
        _('lieu ou institution (approximatif)'), max_length=200, blank=True,
        help_text=_('Ne remplir que si le lieu (ou institution) est '
                    'imprécis(e).'))

    def year(self):
        if self.date:
            return self.date.year

    def month(self):
        if self.date:
            return self.date.month

    def day(self):
        if self.date:
            return self.date.day

    def calc_date(self, tags=True, short=False):
        if self.date:
            return date_html(self.date, tags, short)
        return self.date_approx
    calc_date.short_description = _('date')
    calc_date.admin_order_field = 'date'

    def calc_heure(self):
        if self.heure:
            return time(self.heure, ugettext('H\hi'))
        return self.heure_approx
    calc_heure.short_description = _('heure')
    calc_heure.admin_order_field = 'heure'

    def calc_moment(self, tags=True, short=False):
        l = []
        date = self.calc_date(tags, short)
        heure = self.calc_heure()
        pat_date = ugettext('%(date)s') if self.date \
              else ugettext('%(date)s')
        pat_heure = ugettext('à %(heure)s') if self.heure \
               else ugettext('%(heure)s')
        l.append(pat_date % {'date': date})
        l.append(pat_heure % {'heure': heure})
        return str_list(l, ' ')

    def calc_lieu(self, tags=True, short=False):
        if self.lieu:
            return self.lieu.html(tags, short)
        return self.lieu_approx
    calc_lieu.short_description = _('lieu ou institution')
    calc_lieu.admin_order_field = 'lieu'
    calc_lieu.allow_tags = True

    def html(self, tags=True, short=False):
        out = str_list((self.calc_lieu(tags, short),
                        self.calc_moment(tags, short)))
        return capfirst(out)

    def short_html(self, tags=True):
        return self.html(tags, short=True)

    def related_label(self):
        return self.get_change_link()

    @permalink
    def get_change_url(self):
        return 'admin:catalogue_ancragespatiotemporel_change', (self.pk,)

    def get_change_link(self):
        return href(self.get_change_url(), unicode(self))

    def clean(self):
        if not (self.date or self.date_approx or self.lieu
                                              or self.lieu_approx):
            raise ValidationError(_('Il faut au moins une date ou un lieu '
                                    '(ils peuvent n’être qu’approximatifs)'))

    class Meta:
        verbose_name = ungettext_lazy('ancrage spatio-temporel',
                                      'ancrages spatio-temporels', 1)
        verbose_name_plural = ungettext_lazy('ancrage spatio-temporel',
                                             'ancrages spatio-temporels', 2)
        ordering = ['date', 'heure', 'lieu__parent', 'lieu', 'date_approx',
                    'heure_approx', 'lieu_approx']
        app_label = 'catalogue'

    def __unicode__(self):
        return strip_tags(self.html(tags=False, short=True))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        cmp_fields = ('lieu', 'lieu_approx', 'date', 'date_approx',
                      'heure', 'heure_approx')
        for field in cmp_fields:
            if getattr(self, field) != getattr(other, field):
                return False
        return True

    @staticmethod
    def autocomplete_search_fields():
        return (
            'lieu__nom__icontains', 'lieu__parent__nom__icontains',
            'date__icontains', 'heure__icontains',
            'lieu_approx__icontains', 'date_approx__icontains',
            'heure_approx__icontains',
        )
