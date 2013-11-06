# coding: utf-8

from __future__ import unicode_literals
import re
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import apnumber
from django.db.models import CharField, ManyToManyField, \
    PositiveIntegerField, ForeignKey, OneToOneField, IntegerField, TextField, \
    BooleanField, permalink, get_model, SmallIntegerField, PROTECT
from django.utils.encoding import python_2_unicode_compatible, smart_text, \
    force_text
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext_lazy
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from polymorphic_tree.managers import PolymorphicMPTTModelManager, \
    PolymorphicMPTTQuerySet
from polymorphic_tree.models import PolymorphicMPTTModel, \
    PolymorphicTreeForeignKey
from tinymce.models import HTMLField
from cache_tools import model_method_cached, cached_ugettext as ugettext, \
    cached_ugettext_lazy as _
from .common import (
    CommonModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, calc_pluriel, SlugModel,
    UniqueSlugModel, CommonQuerySet, CommonManager, PublishedManager,
    OrderedDefaultDict, PublishedQuerySet, CommonTreeManager,
    CommonTreeQuerySet, TypeDeParente, TypeDeCaracteristique, Caracteristique)
from .functions import capfirst, ex, hlp, str_list, str_list_w_last, href, cite
from .individu import Individu
from .personnel import Profession
from .source import Source


__all__ = (
    b'GenreDOeuvre', b'TypeDeCaracteristiqueDOeuvre',b'CaracteristiqueDOeuvre',
    b'Partie', b'Role', b'Instrument', b'Pupitre', b'TypeDeParenteDOeuvres',
    b'ParenteDOeuvres', b'Auteur', b'Oeuvre'
)


@python_2_unicode_compatible
class GenreDOeuvre(CommonModel, SlugModel):
    nom = CharField(_('nom'), max_length=255, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=430, blank=True,
        help_text=PLURAL_MSG)
    referent = BooleanField(_('référent'), default=False, db_index=True,
        help_text=_('L’affichage d’une œuvre remonte jusqu’à l’œuvre '
                    'référente la contenant.') \
            + ' ' \
            + ex(force_text(_('Le jeune Henri, acte 2, scène 3')),
                 pre=force_text(_('le rendu d’une scène sera du type ')),
                 post=force_text(_(' car on remonte jusqu’à l’œuvre référente, '
                                'ici choisie comme étant celle de nature '
                                '« opéra »'))))
    parents = ManyToManyField('GenreDOeuvre', related_name='enfants',
        blank=True, null=True)

    class Meta(object):
        verbose_name = ungettext_lazy('genre d’œuvre', 'genres d’œuvre', 1)
        verbose_name_plural = ungettext_lazy('genre d’œuvre',
                                             'genres d’œuvre', 2)
        ordering = ('slug',)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        relations = ('oeuvres',)
        if all_relations:
            relations += ('enfants',)
        return relations

    def html(self, tags=True, caps=False, pluriel=False):
        nom = self.pluriel() if pluriel else self.nom
        if caps:
            nom = capfirst(nom)
        return hlp(nom, ugettext('genre'), tags)

    def pluriel(self):
        return calc_pluriel(self)

    def __str__(self):
        return strip_tags(self.html(False))

    @staticmethod
    def autocomplete_search_fields():
        return 'nom__icontains', 'nom_pluriel__icontains'


class TypeDeCaracteristiqueDOeuvre(TypeDeCaracteristique):
    class Meta(object):
        verbose_name = ungettext_lazy('type de caractéristique d’œuvre',
                                      'types de caracteristique d’œuvre', 1)
        verbose_name_plural = ungettext_lazy(
            'type de caractéristique d’œuvre',
            'types de caracteristique d’œuvre',
            2)
        ordering = ('classement',)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('typedecaracteristique_ptr',)


class CaracteristiqueDOeuvre(Caracteristique):
    class Meta(object):
        verbose_name = ungettext_lazy('caractéristique d’œuvre',
                                      'caractéristiques d’œuvre', 1)
        verbose_name_plural = ungettext_lazy('caractéristique d’œuvre',
                                             'caractéristiques d’œuvre', 2)
        ordering = ('type', 'classement', 'valeur')
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('caracteristique_ptr', 'oeuvres',)


class PartieQuerySet(PolymorphicMPTTQuerySet, PublishedQuerySet,
                     CommonTreeQuerySet):
    pass


class PartieManager(CommonTreeManager, PolymorphicMPTTModelManager,
                    PublishedManager):
    queryset_class = PartieQuerySet


@python_2_unicode_compatible
class Partie(PolymorphicMPTTModel, AutoriteModel, UniqueSlugModel):
    """
    Partie de l’œuvre, c’est-à-dire typiquement un rôle ou un instrument pour
    une œuvre musicale.
    Pour plus de compréhensibilité, on affiche « rôle ou instrument » au lieu
    de « partie ».
    """

    # FIXME: retirer cette contrainte et la recréer virtuellement pour les
    # instruments.
    nom = CharField(_('nom'), max_length=200, db_index=True, unique=True,
        help_text=_('Le nom d’une partie de la partition, '
                    'instrumentale ou vocale.'))
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
        help_text=PLURAL_MSG)
    # TODO: Changer le verbose_name en un genre de "types de voix"
    # pour les rôles, mais en plus générique (ou un help_text).
    professions = ManyToManyField('Profession', related_name='parties',
        verbose_name=_('professions'), db_index=True, blank=True, null=True,
        help_text=_('La ou les profession(s) capable(s) '
                    'de jouer ce rôle ou cet instrument.'))
    parent = PolymorphicTreeForeignKey(
        'self', related_name='enfant', blank=True, null=True, db_index=True,
        verbose_name=_('rôle ou instrument parent')
    )
    classement = SmallIntegerField(_('classement'), default=1, db_index=True)

    objects = PartieManager()

    class Meta(object):
        verbose_name = ungettext_lazy('rôle ou instrument',
                                      'rôles et instruments', 1)
        verbose_name_plural = ungettext_lazy('rôle ou instrument',
                                             'rôles et instruments', 2)
        ordering = ('classement', 'nom',)
        app_label = 'libretto'
        permissions = (('can_change_status', _('Peut changer l’état')),)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('get_real_instance', 'pupitres',)

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
        return self.html()

    def html(self, pluriel=False, tags=True):
        url = '' if not tags else self.get_absolute_url()
        if pluriel:
            out = self.pluriel()
        else:
            out = self.nom
        return href(url, out, tags=tags)

    def __str__(self):
        return self.html(tags=False)

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'nom_pluriel__icontains',
                'professions__nom__icontains',
                'professions__nom_pluriel__icontains',)


class Role(Partie):
    # TODO: créer un unique_together virtuel entre nom et œuvre.
    oeuvre = ForeignKey('Oeuvre', verbose_name=_('œuvre'), blank=True,
                        null=True, related_name='roles')

    class Meta(object):
        verbose_name = ungettext_lazy('rôle', 'rôles', 1)
        verbose_name_plural = ungettext_lazy('rôle', 'rôles', 2)
        app_label = 'libretto'

    def related_label(self):
        txt = super(Role, self).related_label()
        oeuvre = smart_text(self.oeuvre)
        if oeuvre:
            txt += ' (' + oeuvre + ')'
        return txt

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('partie_ptr',)


class Instrument(Partie):
    class Meta(object):
        verbose_name = ungettext_lazy('instrument', 'instruments', 1)
        verbose_name_plural = ungettext_lazy('instrument', 'instruments', 2)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('partie_ptr',)


class PupitreQuerySet(CommonQuerySet):
    def elements_de_distribution(self):
        return get_model(
            'libretto',
            'ElementDeDistribution').objects.filter(pupitre__in=self)


class PupitreManager(CommonManager):
    queryset_class = PupitreQuerySet

    def elements_de_distribution(self):
        return self.all().elements_de_distribution()


# TODO: une fois les quantités déplacées en inline, ce modèle ne doit plus être
# registered dans l'admin.
@python_2_unicode_compatible
class Pupitre(CommonModel):
    partie = ForeignKey(
        'Partie', related_name='pupitres', verbose_name=_('partie'),
        db_index=True, on_delete=PROTECT)
    quantite_min = IntegerField(_('quantité minimale'), default=1,
                                db_index=True)
    quantite_max = IntegerField(_('quantité maximale'), default=1,
                                db_index=True)

    objects = PupitreManager()

    class Meta(object):
        verbose_name = ungettext_lazy('pupitre', 'pupitres', 1)
        verbose_name_plural = ungettext_lazy('pupitre', 'pupitres', 2)
        ordering = ('partie',)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('oeuvres', 'elements_de_distribution')

    def __str__(self):
        out = ''
        partie = self.partie
        mi = self.quantite_min
        ma = self.quantite_max
        if ma > 1:
            partie = partie.pluriel()
        else:
            partie = smart_text(partie)
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
        return href(self.get_absolute_url(), smart_text(self), tags=tags)

    @staticmethod
    def autocomplete_search_fields():
        return ('partie__nom__icontains', 'partie__nom_pluriel__icontains',
                'partie__professions__nom__icontains',
                'partie__professions__nom_pluriel__icontains',)


class TypeDeParenteDOeuvres(TypeDeParente):
    class Meta(object):
        verbose_name = ungettext_lazy('type de parenté d’œuvres',
                                      'types de parentés d’œuvres', 1)
        verbose_name_plural = ungettext_lazy('type de parenté d’œuvres',
                                             'types de parentés d’œuvres', 2)
        ordering = ('classement',)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        relations = ('typedeparente_ptr',)
        if all_relations:
            relations += ('parentes',)
        return relations


class ParenteDOeuvresManager(CommonManager):
    def meres_en_ordre(self):
        return self.all().order_by('mere__ancrage_creation')

    def filles_en_ordre(self):
        return self.all().order_by('fille__ancrage_creation')


@python_2_unicode_compatible
class ParenteDOeuvres(CommonModel):
    type = ForeignKey('TypeDeParenteDOeuvres', related_name='parentes',
                      verbose_name=_('type'), db_index=True, on_delete=PROTECT)
    mere = ForeignKey(
        'Oeuvre', related_name='parentes_filles', verbose_name=_('œuvre mère'),
        db_index=True)
    fille = ForeignKey(
        'Oeuvre', related_name='parentes_meres', verbose_name=_('œuvre fille'),
        db_index=True)

    objects = ParenteDOeuvresManager()

    class Meta(object):
        verbose_name = ungettext_lazy('parenté d’œuvres',
                                      'parentés d’œuvres', 1)
        verbose_name_plural = ungettext_lazy('parenté d’œuvres',
                                             'parentés d’œuvres', 2)
        ordering = ('type',)
        app_label = 'libretto'
        unique_together = ('type', 'mere', 'fille',)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('mere', 'fille',)
        return ()

    def __str__(self):
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


class AuteurQuerySet(CommonQuerySet):
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
        auteurs = self.select_related('individu', 'profession')
        d = OrderedDefaultDict()
        for auteur in auteurs:
            d[auteur.profession].append(auteur.individu)
        return mark_safe(str_list(
            '%s [%s]' % (str_list_w_last(i.html(tags=tags) for i in ins),
                         p.short_html(tags=tags, pluriel=len(ins) > 1))
                for p, ins in d.items()))


class AuteurManager(CommonManager):
    queryset_class = AuteurQuerySet

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


@python_2_unicode_compatible
class Auteur(CommonModel):
    content_type = ForeignKey(ContentType, db_index=True, on_delete=PROTECT)
    object_id = PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()
    individu = ForeignKey('Individu', related_name='auteurs',
                          verbose_name=_('individu'), db_index=True,
                          on_delete=PROTECT)
    profession = ForeignKey('Profession', related_name='auteurs',
                            verbose_name=_('profession'), db_index=True,
                            on_delete=PROTECT)

    objects = AuteurManager()

    class Meta(object):
        verbose_name = ungettext_lazy('auteur', 'auteurs', 1)
        verbose_name_plural = ungettext_lazy('auteur', 'auteurs', 2)
        ordering = ('profession', 'individu__nom')
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return (
            'content_object',
        )

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

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.individu == other.individu \
            and self.profession == other.profession

    def __str__(self):
        return self.html(tags=False)


class OeuvreQuerySet(CommonTreeQuerySet, PublishedQuerySet):
    def html(self, *args, **kwargs):
        return str_list_w_last([o.html(*args, **kwargs) for o in self])


class OeuvreManager(CommonTreeManager, PublishedManager):
    queryset_class = OeuvreQuerySet

    def html(self, *args, **kwargs):
        return self.get_query_set().html(*args, **kwargs)


@python_2_unicode_compatible
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
        null=True, verbose_name=_('genre'), db_index=True, on_delete=PROTECT)
    caracteristiques = ManyToManyField('CaracteristiqueDOeuvre', blank=True,
        null=True, verbose_name=_('caractéristiques'), related_name='oeuvres',
        db_index=True)
    auteurs = GenericRelation('Auteur')
    ancrage_creation = OneToOneField('AncrageSpatioTemporel',
        related_name='oeuvres_creees', blank=True, null=True, db_index=True,
        verbose_name=_('ancrage spatio-temporel de création'),
        on_delete=PROTECT)
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

    objects = OeuvreManager()

    class Meta(object):
        verbose_name = ungettext_lazy('œuvre', 'œuvres', 1)
        verbose_name_plural = ungettext_lazy('œuvre', 'œuvres', 2)
        ordering = ('titre', 'genre', 'slug')
        app_label = 'libretto'
        permissions = (('can_change_status', _('Peut changer l’état')),)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        relations = ('enfants', 'elements_de_programme',)
        if all_relations:
            relations += ('dossiers', 'filles',)
        return relations

    class MPTTMeta(object):
        parent_attr = 'contenu_dans'

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

    def caracteristiques_html(self, tags=True):
        if not self.pk:
            return ''
        return str_list(self.caracteristiques.html_list(tags=tags))
    caracteristiques_html.allow_tags = True
    caracteristiques_html.short_description = _('caractéristiques')
    caracteristiques_html.admin_order_field = 'caracteristiques__valeur'

    def calc_pupitres(self, prefix=True, tags=False):
        if not self.pk:
            return ''
        pupitres = self.pupitres.select_related('partie')
        if not pupitres:
            return ''
        out = ugettext('pour ') if prefix else ''
        out += str_list_w_last(p.html(tags=tags) for p in pupitres)
        return out

    def pupitres_html(self, prefix=False, tags=True):
        return self.calc_pupitres(prefix=prefix, tags=tags)

    def auteurs_html(self, tags=True):
        return self.auteurs.order_by(*Auteur._meta.ordering).html(tags)
    auteurs_html.short_description = _('auteurs')
    auteurs_html.allow_tags = True
    auteurs_html.admin_order_field = 'auteurs__individu__nom'

    def parentes_in_order(self, relation):
        return getattr(self, relation).order_by('ancrage_creation')

    def meres_in_order(self):
        return self.parentes_in_order('meres')

    def filles_in_order(self):
        return self.parentes_in_order('filles')

    def calc_referent_ancestors(self, tags=False, links=False):
        if not self.pk or self.contenu_dans is None or (self.genre
                                                     and  self.genre.referent):
            return ''
        return self.contenu_dans.titre_html(tags=tags, links=links)

    def titre_complet(self):
        l = (self.prefixe_titre, self.titre, self.coordination,
             self.prefixe_titre_secondaire, self.titre_secondaire)
        return str_list(l, infix='')

    @model_method_cached()
    def html(self, tags=True, auteurs=True, titre=True,
             descr=True, genre_caps=False, ancestors=True,
             ancestors_links=False, links=True):
        # FIXME: Nettoyer cette horreur
        out = ''
        titre_complet = self.titre_complet()
        genre = self.genre
        caracteristiques = [] if not self.pk \
            else self.caracteristiques.html_list(tags=tags)
        url = None if not tags else self.get_absolute_url()
        if auteurs:
            auts = self.auteurs_html(tags)
            if auts:
                out += auts + ', '
        if titre:
            if ancestors:
                pars = self.calc_referent_ancestors(
                    tags=tags, links=ancestors_links)
                if pars:
                    out += pars + ', '
            if titre_complet:
                out += href(url, cite(titre_complet, tags=tags), tags & links)
                if descr and genre:
                    out += ', '
        if genre:
            genre = genre.html(tags, caps=genre_caps)
            if not titre_complet:
                titre_complet = self.genre.html(tags, caps=True)
                pupitres = self.calc_pupitres()
                if pupitres:
                    titre_complet += ' ' + pupitres
                if caracteristiques:
                    titre_complet += ' ' + caracteristiques.pop(0)
                if titre:
                    out += href(url, titre_complet, tags=tags & links)
                    if descr and caracteristiques:
                        out += ','
            elif descr:
                out += genre
        if descr and caracteristiques:
            if out:
                # TODO: BUG : le validateur HTML supprime l'espace qu'on ajoute
                #       ci-dessous si on ne le met pas en syntaxe HTML
                out += '&#32;' if tags else ' '
            out += str_list(caracteristiques)
        return mark_safe(out)
    html.short_description = _('rendu HTML')
    html.allow_tags = True

    def short_html(self, tags=True, links=False):
        return self.html(tags=tags, auteurs=False, titre=True, descr=False,
                         ancestors=False, links=links)

    def titre_html(self, tags=True, links=True):
        return self.html(tags, auteurs=False, titre=True, descr=False,
                         ancestors=True, ancestors_links=True, links=links)

    def titre_descr(self, tags=False):
        return self.html(tags=tags, auteurs=False, titre=True, descr=True,
                         ancestors=True)

    def titre_descr_html(self):
        return self.titre_descr(tags=True)

    def description_html(self, tags=True):
        return self.html(tags, auteurs=False, titre=False, descr=True,
                         genre_caps=True)

    def clean(self):
        if not self.titre and not self.genre:
            raise ValidationError(_('Un titre ou un genre doit au moins '
                                    'être précisé.'))
        # Ensures title look like "Le Tartuffe, ou l’Imposteur.".
        self.prefixe_titre = capfirst(self.prefixe_titre)
        self.titre = capfirst(self.titre)
        self.prefixe_titre_secondaire = self.prefixe_titre_secondaire.lower()
        self.titre_secondaire = capfirst(self.titre_secondaire)

    def handle_whitespaces(self):
        match = re.match(r'^,\s*(.+)$', self.coordination)
        v = self.coordination if match is None else match.group(1)
        if v:
            self.coordination = ', %s' % v
        for attr in ('prefixe_titre', 'prefixe_titre_secondaire',
                     'coordination'):
            v = getattr(self, attr)
            if v and v[-1] not in (' ', "'", '’'):
                setattr(self, attr, v + ' ')

    def related_label(self):
        txt = smart_text(self)
        auteurs = self.auteurs.html(tags=False)
        if auteurs:
            txt += ' (' + auteurs + ')'
        return txt

    def __str__(self):
        return strip_tags(self.titre_html(False))  # strip_tags car on autorise
                         # les rédacteurs à mettre des tags dans les CharFields

    @staticmethod
    def autocomplete_search_fields():
        return ('prefixe_titre__icontains', 'titre__icontains',
                'prefixe_titre_secondaire__icontains',
                'titre_secondaire__icontains', 'genre__nom__icontains',
                'auteurs__individu__nom__icontains',
                'caracteristiques__valeur__icontains',
                'pupitres__partie__nom__icontains')
