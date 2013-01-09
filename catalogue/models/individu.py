# coding: utf-8

from __future__ import unicode_literals
from .functions import str_list, str_list_w_last, href, sc
from django.db.models import CharField, FloatField, BooleanField, ForeignKey, \
                             ManyToManyField, OneToOneField, permalink, \
                             get_model
from tinymce.models import HTMLField
from ..templatetags.extras import abbreviate
from django.utils.html import strip_tags
from django.utils.translation import pgettext, ungettext_lazy, \
                                     ugettext,  ugettext_lazy as _
from .common import CustomModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, \
                    calc_pluriel, UniqueSlugModel
from django.core.exceptions import ValidationError


class Prenom(CustomModel):
    prenom = CharField(_('prénom'), max_length=100)
    classement = FloatField(_('classement'), default=1.0)
    favori = BooleanField(_('favori'), default=True)

    class Meta:
        verbose_name = ungettext_lazy('prénom', 'prénoms', 1)
        verbose_name_plural = ungettext_lazy('prénom', 'prénoms', 2)
        ordering = ['prenom', 'classement']
        app_label = 'catalogue'

    def has_individu(self):
        return self.individus.exists()
    has_individu.short_description = _('individu(s) lié(s)')
    has_individu.boolean = True

    def __unicode__(self):
        return self.prenom

    @staticmethod
    def autocomplete_search_fields():
        return 'prenom__icontains',


class TypeDeParenteDIndividus(CustomModel):
    nom = CharField(_('nom'), max_length=50, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=55, blank=True,
        help_text=PLURAL_MSG)
    classement = FloatField(_('classement'), default=1.0)

    class Meta:
        verbose_name = ungettext_lazy('type de parenté d’individus',
                                      'types de parenté d’individus', 1)
        verbose_name_plural = ungettext_lazy(
                'type de parenté d’individus',
                'types de parenté d’individus',
                2)
        ordering = ['classement']
        app_label = 'catalogue'

    def pluriel(self):
        return calc_pluriel(self)

    def __unicode__(self):
        return self.nom


class ParenteDIndividus(CustomModel):
    type = ForeignKey('TypeDeParenteDIndividus', related_name='parentes',
        verbose_name=_('type'))
    individus_cibles = ManyToManyField('Individu',
        related_name='enfances_cibles', verbose_name=_('individus cibles'))

    class Meta:
        verbose_name = ungettext_lazy('parenté d’individus',
                                      'parentés d’individus', 1)
        verbose_name_plural = ungettext_lazy('parenté d’individus',
                                             'parentés d’individus', 2)
        ordering = ['type']
        app_label = 'catalogue'

    def __unicode__(self):
        out = self.type.nom
        if self.individus_cibles.count() > 1:
            out = self.type.pluriel()
        out += ' :'
        cs = self.individus_cibles.iterator()
        out += str_list((unicode(c) for c in cs), ' ; ')
        return out


class Individu(AutoriteModel, UniqueSlugModel):
    particule_nom = CharField(_('particule du nom d’usage'), max_length=10,
        blank=True)
    # TODO: rendre le champ nom 'blank'
    nom = CharField(_('nom d’usage'), max_length=200)
    particule_nom_naissance = CharField(_('particule du nom de naissance'),
        max_length=10, blank=True)
    nom_naissance = CharField(_('nom de naissance'), max_length=200,
        blank=True,
        help_text=_('Ne remplir que s’il est différent du nom d’usage.'))
    prenoms = ManyToManyField('Prenom', related_name='individus', blank=True,
        null=True, verbose_name=_('prénoms'))
    pseudonyme = CharField(_('pseudonyme'), max_length=200, blank=True)
    DESIGNATIONS = (
        ('S', _('Standard (nom, prénoms et pseudonyme)')),
        ('P', _('Pseudonyme (uniquement)')),
        ('L', _('Nom de famille (uniquement)')),  # L pour Last name
        ('B', _('Nom de naissance (standard)')),  # B pour Birth name
        ('F', _('Prénom(s) favori(s) (uniquement)')),  # F pour First name
    )
    designation = CharField(_('désignation'), max_length=1,
        choices=DESIGNATIONS, default='S')
    TITRES = (
        ('M', _('M.')),
        ('J', _('Mlle')),  # J pour Jouvencelle
        ('F', _('Mme')),
    )
    titre = CharField(pgettext('individu', 'titre'), max_length=1,
        choices=TITRES, blank=True)
    ancrage_naissance = OneToOneField('AncrageSpatioTemporel', blank=True,
        null=True, related_name='individus_nes',
        verbose_name=_('ancrage de naissance'))
    ancrage_deces = OneToOneField('AncrageSpatioTemporel', blank=True,
        null=True, related_name='individus_decedes',
        verbose_name=_('ancrage du décès'))
    ancrage_approx = OneToOneField('AncrageSpatioTemporel',
        blank=True, null=True,
        related_name='individus', verbose_name=_('ancrage approximatif'),
        help_text=_('Ne remplir que si on ne connaît aucune date précise.'))
    professions = ManyToManyField('Profession', related_name='individus',
        blank=True, null=True, verbose_name=_('professions'))
    parentes = ManyToManyField('ParenteDIndividus',
        related_name='individus_orig', blank=True, null=True,
        verbose_name=_('parentés'))
    biographie = HTMLField(_('biographie'), blank=True)

    def get_slug(self):
        return self.nom or unicode(self)

    @permalink
    def get_absolute_url(self):
        return 'individu', [self.slug],

    @permalink
    def permalien(self):
        return 'individu_pk', [self.pk]

    def link(self):
        return self.html()
    link.short_description = _('lien')
    link.allow_tags = True

    def oeuvres(self):
        return self.auteurs.oeuvres()

    def publications(self):
        return self.auteurs.sources()

    def apparitions(self):
        # FIXME: Pas sûr que la condition soit logique.
        return get_model('catalogue', 'Evenement').objects.filter(
                            programme__distribution__individus=self).distinct()

    def parents(self):
        # FIXME: À simplifier
        pk_list = self.parentes.values_list('individus_cibles', flat=True) \
                                             .order_by('individus_cibles__nom')
        if pk_list:
            return Individu.objects.in_bulk(tuple(pk_list)).values()

    def enfants(self):
        # FIXME: À simplifier
        pk_list = self.enfances_cibles.values_list('individus_orig',
                                     flat=True).order_by('individus_orig__nom')
        if pk_list:
            return Individu.objects.in_bulk(tuple(pk_list)).values()

    def calc_prenoms_methode(self, fav):
        if not self.pk:
            return ''
        prenoms = self.prenoms.order_by('classement', 'prenom')
        if fav:
            prenoms = (p for p in prenoms if p.favori)
        return ' '.join(unicode(p) for p in prenoms)

    def calc_prenoms(self):
        return self.calc_prenoms_methode(False)
    calc_prenoms.short_description = _('prénoms')
    calc_prenoms.admin_order_field = 'prenoms__prenom'

    def calc_fav_prenoms(self):
        return self.calc_prenoms_methode(True)

    def calc_titre(self, tags=False):
        if tags:
            titres = {
                'M': ugettext('M.'),
                'J': ugettext('M<sup>lle</sup>'),
                'F': ugettext('M<sup>me</sup>'),
            }
        else:
            titres = {
                'M': ugettext('Monsieur'),
                'J': ugettext('Mademoiselle'),
                'F': ugettext('Madame'),
            }
        if self.titre:
            return titres[self.titre]
        return ''

    def get_particule(self, naissance=False, lon=True):
        particule = self.particule_nom_naissance if naissance \
               else self.particule_nom
        if lon and particule != '' and particule[-1] not in ("'", '’'):
            particule += ' '
        return particule

    def naissance(self):
        if self.ancrage_naissance:
            return unicode(self.ancrage_naissance)
        return ''

    def naissance_html(self, tags=True):
        if self.ancrage_naissance:
            return self.ancrage_naissance.short_html(tags)
        return ''

    def deces(self):
        if self.ancrage_deces:
            return unicode(self.ancrage_deces)
        return ''

    def deces_html(self, tags=True):
        if self.ancrage_deces:
            return self.ancrage_deces.short_html(tags)
        return ''

    def ancrage(self):
        if self.ancrage_approx:
            return unicode(self.ancrage_approx)
        return ''

    def calc_professions(self, tags=True):
        if not self.pk:
            return ''
        ps = self.professions.iterator()
        titre = self.titre
        return str_list_w_last(p.gendered(titre, tags, caps=i == 0)
                                                     for i, p in enumerate(ps))
    calc_professions.short_description = _('professions')
    calc_professions.admin_order_field = 'professions__nom'
    calc_professions.allow_tags = True

    def html(self, tags=True, lon=False, prenoms_fav=True,
             force_standard=False, show_prenoms=True):
        def add_particule(nom, lon, naissance=False):
            particule = self.get_particule(naissance)
            if lon:
                nom = particule + nom
            return nom

        designation = self.designation
        titre = self.calc_titre(tags)
        prenoms = self.calc_prenoms_methode(prenoms_fav)
        nom = self.nom
        nom = add_particule(nom, lon)
        pseudonyme = self.pseudonyme
        nom_naissance = self.nom_naissance
        nom_naissance = add_particule(nom_naissance, lon, naissance=True)
        particule = self.get_particule(naissance=(designation == 'B'), lon=lon)

        def main_style(s):
            return sc(s, tags)

        def standard(main):
            l = []
            if nom and not prenoms:
                l.append(titre)
            l.append(main)
            if show_prenoms and (prenoms or particule and not lon):
                if lon:
                    l.insert(max(len(l) - 1, 0), prenoms)
                else:
                    s = str_list((abbreviate(prenoms, tags=tags),
                                  sc(particule, tags)),
                                 ' ')
                    l.append('(%s)' % s)
            out = str_list(l, ' ')
            if pseudonyme:
                alias = ugettext('dite') if self.titre in ('J', 'F',) \
                   else ugettext('dit')
                out += ugettext(', %(alias)s %(pseudonyme)s') % \
                    {'alias': alias,
                     'pseudonyme': pseudonyme}
            return out

        main_choices = {
          'S': nom,
          'F': prenoms,
          'L': nom,
          'P': pseudonyme,
          'B': nom_naissance,
        }
        main = main_style(main_choices['S' if force_standard else designation])
        out = standard(main) if designation in ('S', 'B',) or force_standard \
              else main
        url = None if not tags else self.get_absolute_url()
        out = href(url, out, tags)
        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def nom_seul(self, tags=False):
        return self.html(tags, False, show_prenoms=False)

    def nom_complet(self, tags=True, prenoms_fav=False, force_standard=True):
        return self.html(tags, True, prenoms_fav, force_standard)

    def clean(self):
        if self.pk:
            for p in self.parentes.all():
                if self in p.individus_cibles.all():
                    raise ValidationError(_('L’individu a une parenté avec '
                                            'lui-même.'))
        try:
            naissance = getattr(self.ancrage_naissance, 'date')
            deces = getattr(self.ancrage_deces, 'date')
        except AttributeError:
            pass
        else:
            if naissance and deces and deces < naissance:
                raise ValidationError(_('Le décès ne peut précéder '
                                        'la naissance.'))

    class Meta:
        verbose_name = ungettext_lazy('individu', 'individus', 1)
        verbose_name_plural = ungettext_lazy('individu', 'individus', 2)
        ordering = ['nom']
        app_label = 'catalogue'

    def __unicode__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return (
            'nom__icontains',
            'nom_naissance__icontains',
            'pseudonyme__icontains',
            'prenoms__prenom__icontains',
        )
