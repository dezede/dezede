# coding: utf-8

from __future__ import unicode_literals
from collections import defaultdict
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import apnumber
from django.db.models import CharField, ManyToManyField, \
                             PositiveIntegerField, FloatField, ForeignKey, \
                             OneToOneField, IntegerField, TextField, \
                             BooleanField, permalink, get_model
from django.template.defaultfilters import capfirst
from django.utils.html import strip_tags
from django.utils.translation import ungettext_lazy, ugettext, \
                                     ugettext_lazy as _
from django.utils.safestring import mark_safe
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from tinymce.models import HTMLField
from .common import CustomModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, \
                    calc_pluriel, SlugModel, UniqueSlugModel, CustomManager, \
                    CustomQuerySet
from .functions import ex, hlp, str_list, str_list_w_last, href, cite
from .individu import Individu
from .personnel import Profession
from .source import Source


__all__ = (b'GenreDOeuvre', b'TypeDeCaracteristiqueDOeuvre',
           b'CaracteristiqueDOeuvre', b'Partie', b'Pupitre',
           b'TypeDeParenteDOeuvres', b'ParenteDOeuvres', b'Auteur', b'Oeuvre')


class GenreDOeuvre(CustomModel, SlugModel):
    nom = CharField(_('nom'), max_length=255, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=430, blank=True,
        help_text=PLURAL_MSG)
    referent = BooleanField(_('référent'), default=False, db_index=True,
        help_text=_('L’affichage d’une œuvre remonte jusqu’à l’œuvre '
                    'référente la contenant.') \
            + ' ' \
            + ex(unicode(_('Le jeune Henri, acte 2, scène 3')),
                 pre=unicode(_('le rendu d’une scène sera du type ')),
                 post=unicode(_(' car on remonte jusqu’à l’œuvre référente, '
                                'ici choisie comme étant celle de nature '
                                '« opéra »'))))
    parents = ManyToManyField('GenreDOeuvre', related_name='enfants',
        blank=True, null=True)

    class Meta(object):
        verbose_name = ungettext_lazy('genre d’œuvre', 'genres d’œuvre', 1)
        verbose_name_plural = ungettext_lazy('genre d’œuvre',
                                             'genres d’œuvre', 2)
        ordering = ('slug',)
        app_label = 'catalogue'

    def html(self, tags=True, caps=False, pluriel=False):
        nom = self.pluriel() if pluriel else self.nom
        if caps:
            nom = capfirst(nom)
        return hlp(nom, ugettext('genre'), tags)

    def pluriel(self):
        return calc_pluriel(self)

    def __unicode__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return 'nom__icontains', 'nom_pluriel__icontains',


class TypeDeCaracteristiqueDOeuvre(CustomModel):
    nom = CharField(_('nom'), max_length=200, help_text=ex(_('tonalité')),
                    unique=True, db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
        help_text=PLURAL_MSG)
    classement = FloatField(default=1.0)

    class Meta(object):
        verbose_name = ungettext_lazy('type de caractéristique d’œuvre',
                                      'types de caracteristique d’œuvre', 1)
        verbose_name_plural = ungettext_lazy(
            'type de caractéristique d’œuvre',
            'types de caracteristique d’œuvre',
            2)
        ordering = ('classement',)
        app_label = 'catalogue'

    def pluriel(self):
        return calc_pluriel(self)

    def __unicode__(self):
        return self.nom


class CaracteristiqueDOeuvre(CustomModel):
    type = ForeignKey('TypeDeCaracteristiqueDOeuvre',
        related_name='caracteristiques_d_oeuvre', db_index=True,
        verbose_name=_('type'))
    # TODO: Changer valeur en nom ?
    valeur = CharField(_('valeur'), max_length=400,
                       help_text=ex(_('en trois actes')))
    classement = FloatField(_('classement'), default=1.0, db_index=True,
        help_text=_('Par exemple, on peut choisir de classer'
                    'les découpages par nombre d’actes.'))

    class Meta(object):
        verbose_name = ungettext_lazy('caractéristique d’œuvre',
                                      'caractéristiques d’œuvre', 1)
        verbose_name_plural = ungettext_lazy('caractéristique d’œuvre',
                                             'caractéristiques d’œuvre', 2)
        ordering = ('type', 'classement', 'valeur')
        app_label = 'catalogue'

    def html(self, tags=True):
        return hlp(self.valeur, self.type, tags)
    html.allow_tags = True

    def __unicode__(self):
        return unicode(self.type) + ' : ' + strip_tags(self.valeur)

    @staticmethod
    def autocomplete_search_fields():
        return 'type__nom__icontains', 'valeur__icontains',


class Partie(MPTTModel, CustomModel, SlugModel):
    """
    Partie de l’œuvre, c’est-à-dire typiquement un rôle ou un instrument pour
    une œuvre musicale.
    Pour plus de compréhensibilité, on affiche « rôle ou instrument » au lieu
    de « partie ».
    """
    nom = CharField(_('nom'), max_length=200, db_index=True,
        help_text=_('Le nom d’une partie de la partition, '
                    'instrumentale ou vocale.'))
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
        help_text=PLURAL_MSG)
    professions = ManyToManyField('Profession', related_name='parties',
        verbose_name=_('professions'), db_index=True,
        help_text=_('La ou les profession(s) capable(s) '
                    'de jouer ce rôle ou cet instrument.'))
    parent = TreeForeignKey('Partie', related_name='enfant',
                            blank=True, null=True, db_index=True,
                            verbose_name=_('rôle ou instrument parent'))
    classement = FloatField(_('classement'), default=1.0, db_index=True)

    objects = TreeManager()

    class Meta(object):
        verbose_name = ungettext_lazy('rôle ou instrument',
                                      'rôles et instruments', 1)
        verbose_name_plural = ungettext_lazy('rôle ou instrument',
                                             'rôles et instruments', 2)
        ordering = ('classement', 'nom',)
        app_label = 'catalogue'

    class MPTTMeta(object):
        order_insertion_by = ['classement', 'nom']

    def interpretes(self):
        return self.pupitres.elements_de_distribution().individus()

    def interpretes_html(self):
        return str_list(i.html() for i in self.interpretes())

    def evenements(self):
        return self.pupitres.elements_de_distribution().evenements()

    def pluriel(self):
        return calc_pluriel(self)

    @permalink
    def get_absolute_url(self):
        return b'partie_detail', (self.slug,)

    @permalink
    def permalien(self):
        return b'partie_permanent_detail', (self.pk,)

    def link(self):
        return href(self.get_absolute_url(), self.html())

    def html(self):
        return self.nom

    def __unicode__(self):
        return self.html()

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'nom_pluriel__icontains',
                'professions__nom__icontains',
                'professions__nom_pluriel__icontains',)


class PupitreQuerySet(CustomQuerySet):
    def elements_de_distribution(self):
        return get_model('catalogue', 'ElementDeDistribution').objects.filter(
                                                              pupitre__in=self)


class PupitreManager(CustomManager):
    use_for_related_fields = True

    def get_query_set(self):
        return PupitreQuerySet(self.model, using=self._db)

    def elements_de_distribution(self):
        return self.all().elements_de_distribution()


class Pupitre(CustomModel):
    partie = ForeignKey('Partie', related_name='pupitres',
                        verbose_name=_('partie'), db_index=True)
    quantite_min = IntegerField(_('quantité minimale'), default=1,
                                db_index=True)
    quantite_max = IntegerField(_('quantité maximale'), default=1,
                                db_index=True)

    objects = PupitreManager()

    class Meta(object):
        verbose_name = ungettext_lazy('pupitre', 'pupitres', 1)
        verbose_name_plural = ungettext_lazy('pupitre', 'pupitres', 2)
        ordering = ('partie',)
        app_label = 'catalogue'

    def __unicode__(self):
        out = ''
        partie = self.partie
        mi = self.quantite_min
        ma = self.quantite_max
        if ma > 1:
            partie = partie.pluriel()
        else:
            partie = unicode(partie)
        mi_str = apnumber(mi)
        ma_str = apnumber(ma)
        if mi != ma:
            d = {'min': mi_str, 'max': ma_str}
            out += ugettext('%(min)s à %(max)s ') % d
        elif mi > 1:
            out += mi_str + ' '
        out += partie
        return out

    def get_absolute_url(self):
        return self.partie.get_absolute_url()

    def html(self, tags=True):
        return href(self.get_absolute_url(), unicode(self), tags=tags)

    @staticmethod
    def autocomplete_search_fields():
        return ('partie__nom__icontains', 'partie__nom_pluriel__icontains',
                'partie__professions__nom__icontains',
                'partie__professions__nom_pluriel__icontains',)


class TypeDeParenteDOeuvres(CustomModel):
    nom = CharField(_('nom'), max_length=100, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_relatif = CharField(_('nom relatif'), max_length=100,
                            help_text=LOWER_MSG, unique=True, db_index=True)
    nom_relatif_pluriel = CharField(_('nom relatif (au pluriel)'),
        max_length=130, blank=True, help_text=PLURAL_MSG)
    classement = FloatField(_('classement'), default=1.0, db_index=True)

    class Meta(object):
        verbose_name = ungettext_lazy('type de parenté d’œuvres',
                                      'types de parentés d’œuvres', 1)
        verbose_name_plural = ungettext_lazy('type de parenté d’œuvres',
                                             'types de parentés d’œuvres', 2)
        ordering = ('classement',)
        app_label = 'catalogue'

    def relatif_pluriel(self):
        return calc_pluriel(self, attr_base='nom_relatif')

    def __unicode__(self):
        return '< %s | %s >' % (self.nom, self.nom_relatif)


class ParenteDOeuvresManager(CustomManager):
    def meres_en_ordre(self):
        return self.all().order_by('mere__ancrage_creation')

    def filles_en_ordre(self):
        return self.all().order_by('fille__ancrage_creation')


class ParenteDOeuvres(CustomModel):
    type = ForeignKey('TypeDeParenteDOeuvres', related_name='parentes',
                      verbose_name=_('type'), db_index=True)
    mere = ForeignKey('Oeuvre', related_name='parentes_filles',
                      verbose_name=_('œuvre mère'), db_index=True)
    fille = ForeignKey('Oeuvre', related_name='parentes_meres',
                       verbose_name=_('œuvre fille'), db_index=True)
    objects = ParenteDOeuvresManager()

    class Meta(object):
        verbose_name = ungettext_lazy('parenté d’œuvres',
                                      'parentés d’œuvres', 1)
        verbose_name_plural = ungettext_lazy('parenté d’œuvres',
                                             'parentés d’œuvres', 2)
        ordering = ('type',)
        app_label = 'catalogue'
        unique_together = ('type', 'mere', 'fille',)

    def __unicode__(self):
        return '%s %s %s' % (self.fille, self.type.nom, self.mere)

    def clean(self):
        try:
            type, mere, fille = self.type, self.mere, self.fille
            if mere == fille:
                raise ValidationError(_('Les deux champs de parenté ne '
                                        'peuvent pas être identiques'))
            if ParenteDOeuvres.objects.filter(mere=fille,
                                              fille=mere).exists():
                raise ValidationError(_('Une relation entre ces deux objets '
                                        'existe déjà dans le sens inverse'))
        except (Oeuvre.DoesNotExist, TypeDeParenteDOeuvres.DoesNotExist):
            pass


class AuteurQuerySet(CustomQuerySet):
    def __get_related(self, Model):
        qs = Model._default_manager.filter(auteurs__in=self)
        return qs.distinct().order_by(*Model._meta.ordering)

    def individus(self):
        return self.__get_related(Individu)

    def professions(self):
        return self.__get_related(Profession)

    def oeuvres(self):
        return self.__get_related(Oeuvre)

    def sources(self):
        return self.__get_related(Source)

    def html(self, tags=True):
        auteurs = self
        d = defaultdict(list)
        for auteur in auteurs:
            d[auteur.profession].append(auteur.individu)
        return mark_safe(str_list(
            '%s [%s]' % (str_list_w_last(i.html(tags=tags) for i in ins),
                         p.short_html(tags=tags))
                for p, ins in d.items()))


class AuteurManager(CustomManager):
    def get_query_set(self):
        return AuteurQuerySet(self.model, using=self._db)

    def individus(self):
        return self.get_query_set().individus()

    def professions(self):
        return self.get_query_set().professions()

    def oeuvres(self):
        return self.get_query_set().oeuvres()

    def sources(self):
        return self.get_query_set().sources()

    def html(self, tags=True):
        return self.get_query_set().html(tags)


class Auteur(CustomModel):
    content_type = ForeignKey(ContentType, db_index=True)
    object_id = PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()
    individu = ForeignKey('Individu', related_name='auteurs',
                          verbose_name=_('individu'), db_index=True)
    profession = ForeignKey('Profession', related_name='auteurs',
                            verbose_name=_('profession'), db_index=True)
    objects = AuteurManager()

    def html(self, tags=True):
        return '%s [%s]' % (self.individu.html(tags=tags),
                            self.profession.short_html(tags=tags))
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def clean(self):
        try:
            self.individu.professions.add(self.profession)
        except (Individu.DoesNotExist,
                Profession.DoesNotExist):
            pass

    class Meta(object):
        verbose_name = ungettext_lazy('auteur', 'auteurs', 1)
        verbose_name_plural = ungettext_lazy('auteur', 'auteurs', 2)
        ordering = ('profession', 'individu__nom')
        app_label = 'catalogue'

    def __unicode__(self):
        return self.html(tags=False)


class Oeuvre(MPTTModel, AutoriteModel, UniqueSlugModel):
    prefixe_titre = CharField(_('préfixe du titre'), max_length=20, blank=True,
                              db_index=True)
    titre = CharField(_('titre'), max_length=200, blank=True, db_index=True)
    coordination = CharField(_('coordination'), max_length=20, blank=True,
                             db_index=True)
    prefixe_titre_secondaire = CharField(_('préfixe du titre secondaire'),
         max_length=20, blank=True, db_index=True)
    titre_secondaire = CharField(_('titre secondaire'), max_length=200,
                                 blank=True, db_index=True)
    genre = ForeignKey('GenreDOeuvre', related_name='oeuvres', blank=True,
        null=True, verbose_name=_('genre'), db_index=True)
    caracteristiques = ManyToManyField('CaracteristiqueDOeuvre', blank=True,
        null=True, verbose_name=_('caractéristiques'), db_index=True)
    auteurs = GenericRelation('Auteur')
    ancrage_creation = OneToOneField('AncrageSpatioTemporel',
        related_name='oeuvres_creees', blank=True, null=True, db_index=True,
        verbose_name=_('ancrage spatio-temporel de création'))
    pupitres = ManyToManyField('Pupitre', related_name='oeuvres', blank=True,
        null=True, verbose_name=_('effectif'), db_index=True)
    contenu_dans = TreeForeignKey('self', null=True, blank=True, db_index=True,
                                  related_name='enfants',
                                  verbose_name=_('contenu dans'))
    filles = ManyToManyField('self', through='ParenteDOeuvres', db_index=True,
                             related_name='meres', symmetrical=False)
    lilypond = TextField(blank=True, verbose_name='LilyPond')
    description = HTMLField(blank=True)
    evenements = ManyToManyField('Evenement', through='ElementDeProgramme',
                                 related_name='oeuvres', db_index=True)

    objects = TreeManager()

    @permalink
    def get_absolute_url(self):
        return b'oeuvre_detail', [self.slug]

    @permalink
    def permalien(self):
        return b'oeuvre_permanent_detail', [self.pk]

    def link(self):
        return self.html(tags=True, auteurs=False, titre=True, descr=True,
                         ancestors=True)
    link.short_description = _('lien')
    link.allow_tags = True

    def individus_auteurs(self):
        return self.auteurs.individus()

    def calc_caracteristiques(self, limite=0, tags=True):
        if not self.pk:
            return ''
        cs = self.caracteristiques.all()

        def clist(cs):
            return str_list(c.html(tags) for c in cs)
        out2 = clist(cs[limite:])
        if limite:
            out1 = clist(cs[:limite])
            return out1, out2
        return out2
    calc_caracteristiques.allow_tags = True
    calc_caracteristiques.short_description = _('caractéristiques')
    calc_caracteristiques.admin_order_field = 'caracteristiques__valeur'

    def calc_pupitres(self, prefix=True, tags=False):
        if not self.pk or not self.pupitres.exists():
            return ''
        out = ugettext('pour ') if prefix else ''
        out += str_list_w_last(
                        p.html(tags=tags) for p in self.pupitres.iterator())
        return out

    def pupitres_html(self, prefix=False, tags=True):
        return self.calc_pupitres(prefix=prefix, tags=tags)

    def auteurs_html(self, tags=True):
        return self.auteurs.html(tags)
    auteurs_html.short_description = _('auteurs')
    auteurs_html.allow_tags = True
    auteurs_html.admin_order_field = 'auteurs__individu__nom'

    def parentes_in_order(self, relation):
        return getattr(self, relation).order_by('ancrage_creation')

    def meres_in_order(self):
        return self.parentes_in_order('meres')

    def filles_in_order(self):
        return self.parentes_in_order('filles')

    def calc_referent_ancestors(self, links=False):
        if not self.pk or self.contenu_dans is None or (self.genre
                                                     and  self.genre.referent):
            return ''
        return self.contenu_dans.titre_html(links=links)

    def titre_complet(self):
        l = (self.prefixe_titre, self.titre, self.coordination,
             self.prefixe_titre_secondaire, self.titre_secondaire)
        return str_list(l, infix='')

    def html(self, tags=True, auteurs=True, titre=True,
             descr=True, genre_caps=False, ancestors=True,
             ancestors_links=False, links=True):
        # FIXME: Nettoyer cette horreur
        out = ''
        auts = self.auteurs_html(tags)
        pars = self.calc_referent_ancestors(links=ancestors_links)
        titre_complet = self.titre_complet()
        genre = self.genre
        caracteristiques = self.calc_caracteristiques(tags=tags)
        url = None if not tags else self.get_absolute_url()
        if auteurs and auts:
            out += auts + ', '
        if titre:
            if ancestors and pars:
                out += pars + ', '
            if titre_complet:
                out += href(url, cite(titre_complet, tags=tags), tags & links)
                if descr and genre:
                    out += ', '
        if genre:
            genre = genre.html(tags, caps=genre_caps)
            pupitres = self.calc_pupitres()
            if not titre_complet:
                cs = None
                titre_complet = self.genre.html(tags, caps=True)
                if pupitres:
                    titre_complet += ' ' + pupitres
                elif caracteristiques:
                    cs = self.calc_caracteristiques(1, tags)
                    titre_complet += ' ' + cs[0]
                    caracteristiques = cs[1]
                if titre:
                    out += href(url, titre_complet, tags=tags & links)
                    if descr and cs and cs[1]:
                        out += ','
            elif descr:
                out += genre
        if descr and caracteristiques:
            if out:
                # TODO: BUG : le validateur HTML supprime l'espace qu'on ajoute
                #       ci-dessous si on ne le met pas en syntaxe HTML
                if tags:
                    out += '&#32;'
                else:
                    out += ' '
            out += caracteristiques
        return mark_safe(out)
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def short_html(self, tags=True, links=False):
        return self.html(tags=tags, auteurs=False, titre=True, descr=False,
                         ancestors=False, links=links)


    def titre_html(self, tags=True, links=True):
        return self.html(tags, auteurs=False, titre=True, descr=False,
                         ancestors=True, ancestors_links=True, links=links)

    def titre_descr_html(self, tags=True):
        return self.html(tags, auteurs=False, titre=True, descr=True,
                         ancestors=True)

    def description_html(self, tags=True):
        return self.html(tags, auteurs=False, titre=False, descr=True,
                         genre_caps=True)

    def clean(self):
        if not self.titre and not self.genre:
            raise ValidationError(_('Un titre ou un genre doit au moins '
                                    'être précisé.'))

    class Meta(object):
        verbose_name = ungettext_lazy('œuvre', 'œuvres', 1)
        verbose_name_plural = ungettext_lazy('œuvre', 'œuvres', 2)
        ordering = ('titre', 'genre', 'slug')
        app_label = 'catalogue'

    class MPTTMeta(object):
        parent_attr = 'contenu_dans'

    def __unicode__(self):
        return strip_tags(self.titre_html(False))  # strip_tags car on autorise
                         # les rédacteurs à mettre des tags dans les CharFields

    @staticmethod
    def autocomplete_search_fields():
        return ('prefixe_titre__icontains', 'titre__icontains',
                'prefixe_titre_secondaire__icontains',
                'titre_secondaire__icontains', 'genre__nom__icontains',
                'auteurs__individu__nom__icontains',
                'caracteristiques__valeur__icontains')
