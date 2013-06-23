# coding: utf-8

from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.db.models import CharField, BooleanField, ForeignKey, \
    ManyToManyField, OneToOneField, permalink, Q, SmallIntegerField, PROTECT
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.html import strip_tags
from django.utils.translation import pgettext_lazy, ungettext_lazy
from tinymce.models import HTMLField
from cache_tools import model_method_cached, cached_ugettext as ugettext, \
    cached_ugettext_lazy as _
from ..utils import abbreviate
from .common import CommonModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, \
    calc_pluriel, UniqueSlugModel
from .evenement import Evenement
from .functions import str_list, str_list_w_last, href, sc


__all__ = (b'Prenom', b'TypeDeParenteDIndividus', b'ParenteDIndividus',
           b'Individu')


@python_2_unicode_compatible
class Prenom(CommonModel):
    prenom = CharField(_('prénom'), max_length=100, db_index=True)
    classement = SmallIntegerField(_('classement'), default=1, db_index=True)
    favori = BooleanField(_('favori'), default=True, db_index=True)

    class Meta(object):
        verbose_name = ungettext_lazy('prénom', 'prénoms', 1)
        verbose_name_plural = ungettext_lazy('prénom', 'prénoms', 2)
        ordering = ('classement', 'prenom')
        app_label = 'libretto'

    def has_individu(self):
        return self.individus.exists()
    has_individu.short_description = _('individu(s) lié(s)')
    has_individu.boolean = True

    def __str__(self):
        return self.prenom

    @staticmethod
    def autocomplete_search_fields():
        return 'prenom__icontains',


@python_2_unicode_compatible
class TypeDeParenteDIndividus(CommonModel):
    nom = CharField(_('nom'), max_length=50, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=55, blank=True,
                            help_text=PLURAL_MSG)
    nom_relatif = CharField(_('nom relatif'), max_length=50, db_index=True,
                            help_text=LOWER_MSG)
    nom_relatif_pluriel = CharField(_('nom relatif (au pluriel)'),
                                    max_length=55, help_text=PLURAL_MSG,
                                    blank=True)
    classement = SmallIntegerField(_('classement'), default=1, db_index=True)

    class Meta(object):
        verbose_name = ungettext_lazy('type de parenté d’individus',
                                      'types de parenté d’individus', 1)
        verbose_name_plural = ungettext_lazy(
            'type de parenté d’individus',
            'types de parenté d’individus',
            2)
        ordering = ('classement',)
        app_label = 'libretto'

    def pluriel(self):
        return calc_pluriel(self)

    def relatif_pluriel(self):
        return calc_pluriel(self, 'nom_relatif')

    def __str__(self):
        return self.nom


@python_2_unicode_compatible
class ParenteDIndividus(CommonModel):
    type = ForeignKey('TypeDeParenteDIndividus', related_name='parentes',
                      verbose_name=_('type'), db_index=True, on_delete=PROTECT)
    parent = ForeignKey('Individu', related_name='enfances',
                        verbose_name=_('individu parent'), db_index=True,
                        on_delete=PROTECT)
    enfant = ForeignKey('Individu', related_name='parentes',
                        verbose_name=_('individu enfant'), db_index=True,
                        on_delete=PROTECT)

    class Meta(object):
        verbose_name = ungettext_lazy('parenté d’individus',
                                      'parentés d’individus', 1)
        verbose_name_plural = ungettext_lazy('parenté d’individus',
                                             'parentés d’individus', 2)
        ordering = ('type', 'parent', 'enfant')
        app_label = 'libretto'

    def clean(self):
        try:
            parent, enfant = self.parent, self.enfant
        except Individu.DoesNotExist:
            return
        if parent and enfant and parent == enfant:
            raise ValidationError(_('Un individu ne peut avoir une '
                                    'parenté avec lui-même.'))

    def __str__(self):
        return ugettext('%(parent)s, %(type)s de %(enfant)s') % {
            'parent': self.parent, 'type': self.type.nom,
            'enfant': self.enfant}

    def pluriel(self):
        return calc_pluriel(self)

    def relatif_pluriel(self):
        return calc_pluriel(self, attr_base='nom_relatif')


@python_2_unicode_compatible
class Individu(AutoriteModel, UniqueSlugModel):
    particule_nom = CharField(
        _('particule du nom d’usage'), max_length=10, blank=True,
        db_index=True)
    # TODO: rendre le champ nom 'blank'
    nom = CharField(_('nom d’usage'), max_length=200, db_index=True)
    particule_nom_naissance = CharField(
        _('particule du nom de naissance'), max_length=10, blank=True,
        db_index=True)
    nom_naissance = CharField(
        _('nom de naissance'), max_length=200, blank=True, db_index=True,
        help_text=_('Ne remplir que s’il est différent du nom d’usage.'))
    prenoms = ManyToManyField('Prenom', related_name='individus', blank=True,
                              null=True, db_index=True,
                              verbose_name=_('prénoms'))
    pseudonyme = CharField(_('pseudonyme'), max_length=200, blank=True,
                           db_index=True)
    DESIGNATIONS = (
        ('S', _('Standard (nom, prénoms et pseudonyme)')),
        ('P', _('Pseudonyme (uniquement)')),
        ('L', _('Nom d’usage (uniquement)')),  # L pour Last name
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
    titre = CharField(pgettext_lazy('individu', 'titre'), max_length=1,
                      choices=TITRES, blank=True, db_index=True)
    ancrage_naissance = OneToOneField(
        'AncrageSpatioTemporel', blank=True, null=True,
        related_name='individus_nes', verbose_name=_('ancrage de naissance'),
        db_index=True, on_delete=PROTECT)
    ancrage_deces = OneToOneField(
        'AncrageSpatioTemporel', blank=True, null=True,
        related_name='individus_decedes', verbose_name=_('ancrage du décès'),
        db_index=True, on_delete=PROTECT)
    ancrage_approx = OneToOneField(
        'AncrageSpatioTemporel', blank=True, null=True,
        related_name='individus', verbose_name=_('ancrage approximatif'),
        help_text=_('Ne remplir que si on ne connaît aucune date précise.'),
        db_index=True, on_delete=PROTECT)
    professions = ManyToManyField(
        'Profession', related_name='individus', blank=True, null=True,
        verbose_name=_('professions'), db_index=True)
    enfants = ManyToManyField(
        'self', through='ParenteDIndividus', related_name='parents',
        symmetrical=False, db_index=True)
    biographie = HTMLField(_('biographie'), blank=True)

    class Meta(object):
        verbose_name = ungettext_lazy('individu', 'individus', 1)
        verbose_name_plural = ungettext_lazy('individu', 'individus', 2)
        ordering = ('nom',)
        app_label = 'libretto'
        permissions = (('can_change_status', _('Peut changer l’état')),)

    def get_slug(self):
        return self.nom or smart_text(self)

    @permalink
    def get_absolute_url(self):
        return b'individu_detail', (self.slug,)

    @permalink
    def permalien(self):
        return b'individu_permanent_detail', (self.pk,)

    def link(self):
        return self.html()
    link.short_description = _('lien')
    link.allow_tags = True

    def oeuvres(self):
        oeuvres = self.auteurs.oeuvres()
        return oeuvres.exclude(contenu_dans__in=oeuvres)

    def oeuvres_with_descendants(self):
        return self.auteurs.oeuvres()

    def publications(self):
        return self.auteurs.sources()

    def apparitions(self):
        # FIXME: Pas sûr que la condition soit logique.
        return Evenement.objects.filter(
            Q(distribution__individus=self)
            | Q(programme__distribution__individus=self)).distinct()

    def calc_prenoms_methode(self, fav):
        if not self.pk:
            return ''
        prenoms = self.prenoms.order_by('classement', 'prenom')
        if fav:
            prenoms = (p for p in prenoms if p.favori)
        return ' '.join(smart_text(p) for p in prenoms)

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
            return smart_text(self.ancrage_naissance)
        return ''

    def naissance_html(self, tags=True):
        if self.ancrage_naissance:
            return self.ancrage_naissance.short_html(tags)
        return ''

    def deces(self):
        if self.ancrage_deces:
            return smart_text(self.ancrage_deces)
        return ''

    def deces_html(self, tags=True):
        if self.ancrage_deces:
            return self.ancrage_deces.short_html(tags)
        return ''

    def ancrage(self):
        if self.ancrage_approx:
            return smart_text(self.ancrage_approx)
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

    @model_method_cached(24 * 60 * 60, b'individus')
    def html(self, tags=True, lon=False, prenoms_fav=True,
             show_prenoms=True, designation=None, abbr=True):
        def add_particule(nom, lon, naissance=False):
            particule = self.get_particule(naissance)
            if lon:
                nom = particule + nom
            return nom

        if designation is None:
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
                    s = str_list((abbreviate(prenoms, tags=tags,
                                             enabled=abbr),
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
        main = main_style(main_choices[designation])
        out = standard(main) if designation in ('S', 'B',) else main
        url = None if not tags else self.get_absolute_url()
        out = href(url, out, tags)
        return out
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def nom_seul(self, tags=False, abbr=False):
        return self.html(tags=tags, lon=False, show_prenoms=False,
                         abbr=abbr)

    def nom_complet(self, tags=True, prenoms_fav=False, designation='S',
                    abbr=False):
        return self.html(tags=tags, lon=True, prenoms_fav=prenoms_fav,
                         designation=designation, abbr=abbr)

    def related_label(self):
        return self.html(tags=False, abbr=False)

    def clean(self):
        try:
            naissance = getattr(self.ancrage_naissance, 'date')
            deces = getattr(self.ancrage_deces, 'date')
        except AttributeError:
            pass
        else:
            if naissance and deces and deces < naissance:
                raise ValidationError(_('Le décès ne peut précéder '
                                        'la naissance.'))

    def __str__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return (
            'nom__icontains',
            'nom_naissance__icontains',
            'pseudonyme__icontains',
            'prenoms__prenom__icontains',
        )
