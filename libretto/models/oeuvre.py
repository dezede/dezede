from collections import OrderedDict
import re

from django.apps import apps
from django.core.exceptions import ValidationError
from django.contrib.humanize.templatetags.humanize import apnumber
from django.core.validators import RegexValidator
from django.db.models import (
    CharField, ManyToManyField, ForeignKey, IntegerField,
    BooleanField, SmallIntegerField, PROTECT, Count,
    PositiveSmallIntegerField, CASCADE)
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.html import strip_tags, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _
from tree.fields import PathField
from tree.models import TreeModelMixin

from .base import (
    CommonModel, AutoriteModel, LOWER_MSG, PLURAL_MSG, calc_pluriel, SlugModel,
    UniqueSlugModel, CommonQuerySet, CommonManager, PublishedManager,
    PublishedQuerySet, CommonTreeManager, CommonTreeQuerySet, TypeDeParente,
    AncrageSpatioTemporel, NumberCharField,
)
from common.utils.html import capfirst, hlp, href, cite, em
from common.utils.text import str_list, str_list_w_last, to_roman, BiGrouper
from .individu import Individu
from .personnel import Profession
from .source import Source


__all__ = (
    'GenreDOeuvre', 'Partie', 'Pupitre',
    'TypeDeParenteDOeuvres', 'ParenteDOeuvres', 'Auteur', 'Oeuvre'
)


class GenreDOeuvre(CommonModel, SlugModel):
    nom = CharField(_('nom'), max_length=255, help_text=LOWER_MSG, unique=True,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=430, blank=True,
        help_text=PLURAL_MSG)
    referent = BooleanField(
        _('référent'), default=False, db_index=True,
        help_text=_(
            'L’affichage d’une œuvre remonte jusqu’à l’œuvre référente '
            'la contenant. Exemple : le rendu d’une scène sera du type '
            '« Le jeune Henri, acte 2, scène 3 » car on remonte jusqu’à '
            'l’œuvre référente, ici choisie comme étant celle de nature '
            '« opéra »'))
    parents = ManyToManyField('GenreDOeuvre', related_name='enfants',
                              blank=True, verbose_name=_('parents'))

    class Meta(object):
        verbose_name = _('genre d’œuvre')
        verbose_name_plural = _('genres d’œuvre')
        ordering = ('nom',)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        relations = ('oeuvres',)
        if all_relations:
            relations += ('enfants',)
        return relations

    def __str__(self):
        return strip_tags(self.nom)

    @staticmethod
    def autocomplete_search_fields():
        return 'nom__unaccent__icontains', 'nom_pluriel__unaccent__icontains'


class Partie(AutoriteModel, UniqueSlugModel):
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
    INSTRUMENT = 1
    ROLE = 2
    TYPES = (
        (INSTRUMENT, _('instrument')),
        (ROLE, _('rôle')),
    )
    type = PositiveSmallIntegerField(_('type'), choices=TYPES, db_index=True)
    # TODO: Ajouter automatiquement le rôle à l’effectif.
    oeuvre = ForeignKey(
        'Oeuvre', verbose_name=_('œuvre'), blank=True, null=True,
        related_name='parties',
        help_text=_('Ne remplir que pour les rôles.'), on_delete=CASCADE)
    # TODO: Changer le verbose_name en un genre de "types de voix"
    # pour les rôles, mais en plus générique (ou un help_text).
    professions = ManyToManyField(
        'Profession', related_name='parties', verbose_name=_('professions'),
        blank=True)
    parent = ForeignKey('self', related_name='enfants', blank=True, null=True,
                        verbose_name=_('rôle ou instrument parent'),
                        on_delete=CASCADE)
    classement = SmallIntegerField(_('classement'), default=1, db_index=True)
    premier_interprete = ForeignKey(
        'Individu', related_name='parties_creees', on_delete=PROTECT,
        null=True, blank=True, verbose_name=_('premier(ère) interprète'),
    )

    class Meta(object):
        unique_together = ('nom', 'parent', 'oeuvre')
        verbose_name = _('rôle ou instrument')
        verbose_name_plural = _('rôles et instruments')
        ordering = ('type', 'classement', 'nom',)
        permissions = (('can_change_status', _('Peut changer l’état')),)

    def clean(self):
        if self.premier_interprete and (
            self.type == self.INSTRUMENT
            or self.type == self.ROLE and not self.oeuvre
        ):
            raise ValidationError({
                'premier_interprete': _(
                    'Le premier interprète ne peut être rempli que pour '
                    'un rôle d’une œuvre donnée.'
                ),
            })

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('pupitres',)

    def interpretes(self):
        return self.elements_de_distribution.individus()

    def interpretes_html(self):
        return str_list([i.html() for i in self.interpretes()])
    interpretes_html.short_description = _('interprètes')

    def evenements(self):
        return self.elements_de_distribution.evenements()

    def repertoire(self):
        return self.pupitres.oeuvres()

    def get_children(self):
        return self.enfants.all()

    def is_leaf_node(self):
        return not self.enfants.exists()

    def pluriel(self):
        return calc_pluriel(self)

    def get_absolute_url(self):
        return reverse('partie_detail', args=(self.slug,))

    def permalien(self):
        return reverse('partie_permanent_detail', args=(self.pk,))

    def link(self):
        return self.html()

    def html(self, pluriel=False, oeuvre=True, tags=True):
        url = '' if not tags else self.get_absolute_url()
        if pluriel:
            out = self.pluriel()
        else:
            out = self.nom
        if oeuvre and self.oeuvre:
            out = f'{out} ({self.oeuvre})'
        return href(url, out, tags=tags)

    def __str__(self):
        return self.html(tags=False)

    def short_html(self, pluriel=False, tags=True):
        return self.html(pluriel=pluriel, oeuvre=False, tags=tags)

    @staticmethod
    def autocomplete_search_fields():
        return (
            'nom__unaccent__icontains', 'nom_pluriel__unaccent__icontains',
            'professions__nom__unaccent__icontains',
            'professions__nom_pluriel__unaccent__icontains',
            'oeuvre__prefixe_titre__unaccent__icontains',
            'oeuvre__titre__unaccent__icontains',
            'oeuvre__coordination__unaccent__icontains',
            'oeuvre__prefixe_titre_secondaire__unaccent__icontains',
            'oeuvre__titre_secondaire__unaccent__icontains',
        )


class PupitreQuerySet(CommonQuerySet):
    def oeuvres(self):
        return Oeuvre.objects.filter(
            pk__in=self.values('oeuvre').distinct()
        ).order_by(*Oeuvre._meta.ordering)


class PupitreManager(CommonManager):
    queryset_class = PupitreQuerySet

    def oeuvres(self):
        return self.get_queryset().oeuvres()


class Pupitre(CommonModel):
    oeuvre = ForeignKey('Oeuvre', related_name='pupitres',
                        verbose_name=_('œuvre'), on_delete=CASCADE)
    partie = ForeignKey(
        'Partie', related_name='pupitres',
        verbose_name=_('rôle ou instrument'), on_delete=PROTECT)
    soliste = BooleanField(_('soliste'), default=False, db_index=True)
    quantite_min = IntegerField(_('quantité minimale'), default=1)
    quantite_max = IntegerField(_('quantité maximale'), default=1)
    facultatif = BooleanField(_('ad libitum'), default=False,)

    objects = PupitreManager()

    class Meta(object):
        verbose_name = _('pupitre')
        verbose_name_plural = _('pupitres')
        ordering = ('-soliste', 'partie')

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('oeuvre',)

    def __str__(self):
        n_min = self.quantite_min
        n_max = self.quantite_max
        partie = self.partie.html(pluriel=n_max > 1, oeuvre=False, tags=False)
        if n_min != n_max:
            out = ugettext('%s à %s %s') % (
                apnumber(n_min), apnumber(n_max), partie)
        elif n_min > 1:
            out = f'{apnumber(n_min)} {partie}'
        else:
            out = partie
        if self.facultatif:
            out = format_html('{} <em>ad libitum</em>', out)
        return out

    def get_absolute_url(self):
        return self.partie.get_absolute_url()

    def html(self, tags=True):
        return href(self.get_absolute_url(), force_text(self), tags=tags)

    def related_label(self):
        out = force_text(self)
        if self.partie.oeuvre is not None:
            out += f' ({self.partie.oeuvre})'
        return out

    @staticmethod
    def autocomplete_search_fields():
        return ('partie__nom__unaccent__icontains',
                'partie__nom_pluriel__unaccent__icontains',
                'partie__professions__nom__unaccent__icontains',
                'partie__professions__nom_pluriel__unaccent__icontains',)


class TypeDeParenteDOeuvres(TypeDeParente):
    class Meta(object):
        unique_together = ('nom', 'nom_relatif')
        verbose_name = _('type de parenté d’œuvres')
        verbose_name_plural = _('types de parentés d’œuvres')
        ordering = ('classement',)
        # app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('parentes',)
        return ()


class ParenteDOeuvresManager(CommonManager):
    def meres_en_ordre(self):
        return self.order_by(
            'type', 'mere__creation_date', 'mere__creation_heure',
            'mere__creation_lieu', 'mere__creation_date_approx',
            'mere__creation_heure_approx', 'mere__creation_lieu_approx')

    def filles_en_ordre(self):
        return self.order_by(
            'type', 'fille__creation_date', 'fille__creation_heure',
            'fille__creation_lieu', 'fille__creation_date_approx',
            'fille__creation_heure_approx', 'fille__creation_lieu_approx')


class ParenteDOeuvres(CommonModel):
    type = ForeignKey('TypeDeParenteDOeuvres', related_name='parentes',
                      verbose_name=_('type'), on_delete=PROTECT)
    mere = ForeignKey(
        'Oeuvre', related_name='parentes_filles', verbose_name=_('œuvre mère'),
        on_delete=CASCADE)
    fille = ForeignKey(
        'Oeuvre', related_name='parentes_meres', verbose_name=_('œuvre fille'),
        on_delete=CASCADE)

    objects = ParenteDOeuvresManager()

    class Meta(object):
        verbose_name = _('parenté d’œuvres')
        verbose_name_plural = _('parentés d’œuvres')
        ordering = ('type',)
        unique_together = ('type', 'mere', 'fille',)

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        if all_relations:
            return ('mere', 'fille',)
        return ()

    def __str__(self):
        return f'{self.fille} {self.type.nom} {self.mere}'

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


class AuteurBiGrouper(BiGrouper):
    def __init__(self, iterator, tags=False):
        self.tags = tags
        super().__init__(iterator)

    def get_key(self, obj):
        return obj.profession

    def get_value(self, obj):
        return obj.individu if obj.ensemble is None else obj.ensemble

    def get_verbose_key(self, key, values):
        Individu = apps.get_model('libretto.Individu')
        return key.short_html(
            tags=self.tags, pluriel=len(values) > 1,
            feminin=all(isinstance(v, Individu) and v.is_feminin()
                        for v in values))

    def get_verbose_value(self, value, keys):
        if value is None:
            return ''
        return value.html(tags=self.tags)


class AuteurQuerySet(CommonQuerySet):
    def __get_related(self, model):
        qs = model._default_manager.filter(auteurs__in=self)
        return qs.distinct().order_by(*model._meta.ordering)

    def individus(self):
        return self.__get_related(Individu)

    def professions(self):
        return self.__get_related(Profession)

    def oeuvres(self):
        return self.__get_related(Oeuvre)

    def sources(self):
        return self.__get_related(Source)

    def html(self, tags=True):
        return force_text(AuteurBiGrouper(self, tags=tags))


class AuteurManager(CommonManager):
    queryset_class = AuteurQuerySet

    def individus(self):
        return self.get_queryset().individus()

    def professions(self):
        return self.get_queryset().professions()

    def oeuvres(self):
        return self.get_queryset().oeuvres()

    def sources(self):
        return self.get_queryset().sources()

    def html(self, tags=True):
        return self.get_queryset().html(tags)


class Auteur(CommonModel):
    # Une contrainte de base de données existe dans les migrations
    # pour éviter que les deux soient remplis.
    oeuvre = ForeignKey(
        'Oeuvre', null=True, blank=True,
        related_name='auteurs', verbose_name=_('œuvre'), on_delete=CASCADE)
    source = ForeignKey(
        'Source', null=True, blank=True,
        related_name='auteurs', verbose_name=_('source'), on_delete=CASCADE)
    # Une contrainte de base de données existe dans les migrations
    # pour éviter que les deux soient remplis.
    individu = ForeignKey(
        'Individu', related_name='auteurs', null=True, blank=True,
        verbose_name=_('individu'), on_delete=PROTECT)
    ensemble = ForeignKey(
        'Ensemble', related_name='auteurs', null=True, blank=True,
        verbose_name=_('ensemble'), on_delete=PROTECT)
    profession = ForeignKey(
        'Profession', related_name='auteurs', null=True, blank=True,
        verbose_name=_('profession'), on_delete=PROTECT)

    objects = AuteurManager()

    class Meta(object):
        verbose_name = _('auteur')
        verbose_name_plural = _('auteurs')
        ordering = ('profession', 'ensemble', 'individu')

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return (
            'oeuvre', 'source',
        )

    def html(self, tags=True):
        return mark_safe(force_text(AuteurBiGrouper((self,), tags=tags)))
    html.short_description = _('rendu HTML')

    def clean(self):
        if self.oeuvre is not None and self.profession is None:
            raise ValidationError({
                'profession': ugettext('This field is required.')
            })
        if self.individu_id is not None and self.ensemble_id is not None:
            msg = ugettext('« Individu » et « Ensemble » '
                           'ne peuvent être saisis sur la même ligne.')
            raise ValidationError({'individu': msg, 'ensemble': msg})
        if self.individu is not None and self.profession is not None:
            try:
                self.individu.professions.add(self.profession)
            except (Individu.DoesNotExist,
                    Profession.DoesNotExist):
                pass

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.individu == other.individu \
            and self.profession == other.profession

    def __str__(self):
        return self.html(tags=False)

    def get_absolute_url(self):
        return reverse('individu_detail', args=(self.individu_id,))


class OeuvreQuerySet(CommonTreeQuerySet, PublishedQuerySet):
    def html(self, *args, **kwargs):
        return str_list_w_last([o.html(*args, **kwargs) for o in self])

    def prefetch_all(self):
        return self.select_related('genre').prefetch_related(
            'pupitres__partie')


class OeuvreManager(CommonTreeManager, PublishedManager):
    queryset_class = OeuvreQuerySet

    def html(self, *args, **kwargs):
        return self.get_queryset().html(*args, **kwargs)

    def prefetch_all(self):
        return self.get_queryset().prefetch_all()


NOTES = OrderedDict((
    ('c', 'do'),
    ('d', 'ré'),
    ('e', 'mi'),
    ('f', 'fa'),
    ('g', 'sol'),
    ('a', 'la'),
    ('b', 'si'),
    ('u', 'ut'),  # C’est un do, mais on le déprécie.
))
ALTERATIONS = OrderedDict((
    ('-', 'bémol'),
    ('0', ''),
    ('+', 'dièse'),
))
GAMMES = OrderedDict((
    ('C', 'majeur'),
    ('A', 'mineur'),
    ('0', ''),
    # ('c', 'mode de do'),
    # ('d', 'mode de ré'),
    # ('e', 'mode de mi'),
    # ('f', 'mode de fa'),
    # ('g', 'mode de sol'),
    # ('a', 'mode de la'),
    # ('b', 'mode de si'),
))
# FIXME: This list of computed values is here for makemessages to detect them.
#        Remove whenever a system is created to handle computed values.
TONALITE_I18N_CHOICES = (
    _('do bémol majeur'),
    _('do majeur'),
    _('do dièse majeur'),
    _('ré bémol majeur'),
    _('ré majeur'),
    _('ré dièse majeur'),
    _('mi bémol majeur'),
    _('mi majeur'),
    _('mi dièse majeur'),
    _('fa bémol majeur'),
    _('fa majeur'),
    _('fa dièse majeur'),
    _('sol bémol majeur'),
    _('sol majeur'),
    _('sol dièse majeur'),
    _('la bémol majeur'),
    _('la majeur'),
    _('la dièse majeur'),
    _('si bémol majeur'),
    _('si majeur'),
    _('si dièse majeur'),
    _('ut bémol majeur'),
    _('ut majeur'),
    _('ut dièse majeur'),
    _('do bémol mineur'),
    _('do mineur'),
    _('do dièse mineur'),
    _('ré bémol mineur'),
    _('ré mineur'),
    _('ré dièse mineur'),
    _('mi bémol mineur'),
    _('mi mineur'),
    _('mi dièse mineur'),
    _('fa bémol mineur'),
    _('fa mineur'),
    _('fa dièse mineur'),
    _('sol bémol mineur'),
    _('sol mineur'),
    _('sol dièse mineur'),
    _('la bémol mineur'),
    _('la mineur'),
    _('la dièse mineur'),
    _('si bémol mineur'),
    _('si mineur'),
    _('si dièse mineur'),
    _('ut bémol mineur'),
    _('ut mineur'),
    _('ut dièse mineur'),
    _('do bémol'),
    _('do'),
    _('do dièse'),
    _('ré bémol'),
    _('ré'),
    _('ré dièse'),
    _('mi bémol'),
    _('mi'),
    _('mi dièse'),
    _('fa bémol'),
    _('fa'),
    _('fa dièse'),
    _('sol bémol'),
    _('sol'),
    _('sol dièse'),
    _('la bémol'),
    _('la'),
    _('la dièse'),
    _('si bémol'),
    _('si'),
    _('si dièse'),
    _('ut bémol'),
    _('ut'),
    _('ut dièse'),
)


class Oeuvre(TreeModelMixin, AutoriteModel, UniqueSlugModel):
    prefixe_titre = CharField(_('article'), max_length=20, blank=True)
    titre = CharField(_('titre'), max_length=200, blank=True, db_index=True)
    coordination = CharField(_('coordination'), max_length=20, blank=True,
                             db_index=True)
    prefixe_titre_secondaire = CharField(
        _('article'), max_length=20, blank=True)
    titre_secondaire = CharField(_('titre secondaire'), max_length=200,
                                 blank=True, db_index=True)
    genre = ForeignKey(
        'GenreDOeuvre', related_name='oeuvres', blank=True, null=True,
        verbose_name=_('genre'), on_delete=PROTECT)
    numero = NumberCharField(
        _('numéro'), max_length=10, blank=True, db_index=True,
        validators=[RegexValidator(
            r'^[\d\w\-]+$', _('Vous ne pouvez saisir que des chiffres, '
                              'lettres non accentuées et tiret, '
                              'le tout sans espace.'))],
        help_text=_(
            'Exemple : « 5 » pour symphonie n° 5, « 7a » pour valse n° 7 a, '
            'ou encore « 3-7 » pour sonates n° 3 à 7. '
            '<strong>Ne pas confondre avec le sous-numéro d’opus.</strong>'))
    coupe = CharField(
        _('coupe'), max_length=100, blank=True, db_index=True,
        validators=[RegexValidator(
            r'^\D+$', _('Vous devez saisir les quantités '
                        'en toutes lettres.'))],
        help_text=_('Exemple : « trois actes » pour un opéra en trois actes.'))
    indeterminee = BooleanField(
        _('indéterminée'), default=False,
        help_text=_(
            'Cocher si l’œuvre n’est pas identifiable, par exemple '
            'un quatuor de Haydn, sans savoir lequel. '
            '<strong>Ne pas utiliser pour un extrait indéterminé</strong>, '
            'sélectionner plutôt dans le programme l’œuvre dont il est tiré '
            'et joindre une caractéristique le décrivant '
            '(« un air », « un mouvement », etc.).'))
    incipit = CharField(
        _('incipit'), max_length=100, blank=True, db_index=True,
        help_text=_('Exemple : « Belle nuit, ô nuit d’amour » pour le n° 13 '
                    'de l’acte III des <em>Contes d’Hoffmann</em> '
                    'd’Offenbach.'))
    tempo = CharField(
        _('tempo'), max_length=50, blank=True, db_index=True,
        help_text=_('Exemple : « Largo », « Presto ma non troppo », etc. '
                    'Ne pas saisir d’indication métronomique.'))
    NOTES = NOTES
    ALTERATIONS = ALTERATIONS
    GAMMES = GAMMES
    TONALITES = [
        (f'{gamme_k}{note_k}{alter_k}',
         _(str_list((note_v, alter_v, gamme_v), ' ')))
        for gamme_k, gamme_v in GAMMES.items()
        for note_k, note_v in NOTES.items()
        for alter_k, alter_v in ALTERATIONS.items()
    ]
    tonalite = CharField(_('tonalité'), max_length=3, choices=TONALITES,
                         blank=True, db_index=True)
    sujet = CharField(
        _('sujet'), max_length=80, blank=True,
        help_text=_(
            'Exemple : « un thème de Beethoven » pour une variation sur un '
            'thème de Beethoven, « des motifs de '
            '&lt;em&gt;Lucia di Lammermoor&lt;/em&gt; » pour une fantaisie '
            'sur des motifs de <em>Lucia di Lammermoor</em> '
            '(&lt;em&gt; et &lt;/em&gt; sont les balises HTML '
            'pour mettre en emphase).'))
    TRANSCRIPTION = 1
    ORCHESTRATION = 2
    ARRANGEMENTS = (
        (TRANSCRIPTION, _('transcription')),
        (ORCHESTRATION, _('orchestration'))
    )
    arrangement = PositiveSmallIntegerField(
        _('arrangement'), choices=ARRANGEMENTS, blank=True, null=True,
        db_index=True)
    surnom = CharField(
        _('surnom'), max_length=50, blank=True, db_index=True,
        help_text=_('Exemple : « Jupiter » pour la symphonie n° 41 '
                    'de Mozart.'))
    nom_courant = CharField(
        _('nom courant'), max_length=70, blank=True, db_index=True,
        help_text=_('Exemple : « barcarolle » pour le n° 13 de l’acte III des '
                    '<em>Contes d’Hoffmann</em> d’Offenbach.'))
    opus = CharField(
        _('opus'), max_length=6, blank=True, db_index=True,
        validators=[RegexValidator(
            r'^[\d\w\-/]+$', _('Vous ne pouvez saisir que des chiffres, '
                               'lettres non accentuées, tiret '
                               'et barre oblique, le tout sans espace.'))],
        help_text=_('Exemple : « 12 » pour op. 12, « 27/3 » pour op. 27 n° 3, '
                    '« 8b » pour op. 8 b, ou encore « 12-15 » '
                    'pour op. 12 à 15.'))
    ict = CharField(
        _('ICT'), max_length=25, blank=True, db_index=True,
        help_text=_('Indice de Catalogue Thématique. Exemple : « RV 42 », '
                    '« K. 299d » ou encore « Hob. XVI:24 ».'))
    CREATION_TYPES = (
        (1, _('genèse (composition, écriture, etc.)')),
        (2, _('première mondiale')),
        (3, _('première édition')),
    )
    creation_type = PositiveSmallIntegerField(
        _('type de création'), choices=CREATION_TYPES, null=True, blank=True)
    creation = AncrageSpatioTemporel(verbose_name=_('création'))
    ORDERING = ('type_extrait', 'numero_extrait', 'titre',
                'genre', 'numero', 'coupe',
                'incipit', 'tempo', 'tonalite', 'sujet', 'arrangement',
                'surnom', 'nom_courant',
                'opus', 'ict')
    extrait_de = ForeignKey(
        'self', null=True, blank=True, related_name='enfants',
        verbose_name=_('extrait de'), on_delete=CASCADE)
    path = PathField(
        order_by=ORDERING, parent_field_name='extrait_de', db_index=True,
    )
    ACTE = 1
    TABLEAU = 2
    SCENE = 3
    MORCEAU = 4
    PARTIE = 5
    LIVRE = 6
    ALBUM = 7
    VOLUME = 8
    CAHIER = 9
    ORDRE = 10
    MOUVEMENT = 11
    PIECE = 12
    SERIE = 13
    TYPES_EXTRAIT_ROMAINS = (ACTE, LIVRE, ORDRE)
    TYPES_EXTRAIT_CACHES = (MORCEAU, MOUVEMENT, PIECE)
    TYPES_EXTRAIT = (
        (ACTE,      _('acte')),
        (TABLEAU,   _('tableau')),
        (SCENE,     _('scène')),
        (MORCEAU,   _('morceau chanté')),
        (PARTIE,    _('partie')),
        (LIVRE,     _('livre')),
        (ALBUM,     _('album')),
        (VOLUME,    _('volume')),
        (CAHIER,    _('cahier')),
        (ORDRE,     _('ordre')),
        (MOUVEMENT, _('mouvement')),
        (PIECE,     _('pièce de recueil')),
        (SERIE,     _('série')),
    )
    type_extrait = PositiveSmallIntegerField(
        _('type d’extrait'), choices=TYPES_EXTRAIT, blank=True, null=True,
        db_index=True)
    NUMERO_EXTRAIT_PATTERN = r'^([1-9]\d*)([^\d\.\-]*)$'
    NUMERO_EXTRAIT_RE = re.compile(NUMERO_EXTRAIT_PATTERN)
    numero_extrait = NumberCharField(
        _('numéro d’extrait'), max_length=10, blank=True, db_index=True,
        help_text=_(
            'Le numéro de l’extrait au sein de l’œuvre, par exemple « 3 » '
            'pour le 3<sup>e</sup> mouvement d’un concerto, « 4 » pour '
            'l’acte IV d’un opéra, ou encore « 12b ».'),
        validators=[RegexValidator(
            NUMERO_EXTRAIT_PATTERN,
            _('Vous devez saisir un nombre en chiffres arabes '
              'éventellement suivi de lettres.'))])
    filles = ManyToManyField(
        'self', through='ParenteDOeuvres', related_name='meres',
        symmetrical=False, blank=True, verbose_name=_('filles'))

    objects = OeuvreManager()

    class Meta:
        verbose_name = _('œuvre')
        verbose_name_plural = _('œuvres')
        ordering = ['path']
        permissions = (('can_change_status', _('Peut changer l’état')),)
        indexes = [
            *PathField.get_indexes('oeuvre', 'path'),
        ]

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        relations = ('enfants', 'elements_de_programme',)
        if all_relations:
            relations += ('dossiers', 'filles',)
        return relations

    def get_absolute_url(self):
        return reverse('oeuvre_detail', args=[self.slug])

    def permalien(self):
        return reverse('oeuvre_permanent_detail', args=[self.pk])

    def link(self):
        return self.html(tags=True, auteurs=False, titre=True, descr=True,
                         ancestors=True)
    link.short_description = _('lien')

    def get_extrait(self, show_type=True):
        if not self.type_extrait or not self.numero_extrait:
            return ''
        match = self.NUMERO_EXTRAIT_RE.match(
            self.numero_extrait)
        if match is None:
            return ''
        digits, suffix = match.groups()
        if self.type_extrait in self.TYPES_EXTRAIT_ROMAINS:
            digits = to_roman(int(digits))
        out = f'{digits}{suffix}'
        if self.type_extrait == self.MORCEAU:
            out = ugettext('№ ') + out
        elif self.type_extrait in (self.MOUVEMENT, self.PIECE):
            out += '.'
        elif show_type:
            return f'{self.get_type_extrait_display()} {out}'
        return out

    def caracteristiques_iterator(self, tags=False):
        if self.numero:
            yield ugettext('n° %s') % self.numero
        if self.coupe:
            yield hlp(ugettext('en %s') % self.coupe, ugettext('coupe'), tags)
        if self.incipit:
            yield hlp(ugettext('« %s »') % self.incipit,
                      ugettext('incipit'), tags)
        # On ajoute uniquement le tempo s’il n’y a pas besoin de lui dans le
        # titre non significatif, c’est-à-dire s’il y a déjà un genre.
        if self.tempo and self.genre_id is not None:
            yield hlp(self.tempo, ugettext('Tempo'), tags)
        if self.tonalite:
            gamme, note, alteration = self.tonalite
            gamme = GAMMES.get(gamme, '')
            note = self.NOTES[note]
            alteration = self.ALTERATIONS[alteration]
            tonalite = ugettext('en %s') % str_list(
                (em(note, tags), alteration, gamme), ' ')
            yield tonalite
        if self.sujet:
            yield hlp(ugettext('sur %s') % self.sujet, ugettext('sujet'), tags)
        if self.arrangement is not None:
            yield f'({self.get_arrangement_display()})'
        if self.surnom:
            yield hlp(f'({self.surnom})', ugettext('surnom'), tags)
        if self.nom_courant:
            yield hlp(self.nom_courant, ugettext('nom courant'), tags)
        if self.opus:
            yield hlp(ugettext('op. %s') % self.opus, ugettext('opus'), tags)
        if self.ict:
            yield hlp(self.ict,
                      ugettext('Indice de Catalogue Thématique'), tags)

    def caracteristiques_html(self, tags=True):
        return mark_safe(
            ' '.join(list(self.caracteristiques_iterator(tags=tags))),
        )
    caracteristiques_html.short_description = _('caractéristiques')

    def get_pupitres_str(self, prefix=True, tags=False, solistes=False):
        if not self.pk:
            return ''
        pupitres = self.pupitres.all()
        if solistes:
            pupitres = [p for p in pupitres if p.soliste]

        if not pupitres:
            return ''
        if not prefix:
            return str_list_w_last([p.html(tags=tags) for p in pupitres])

        pupitres_roles = str_list_w_last([
            p.html(tags=tags) for p in pupitres
            if p.partie.type == Partie.ROLE])
        pupitres_instruments = str_list_w_last([
            p.html(tags=tags) for p in pupitres
            if p.partie.type == Partie.INSTRUMENT])

        if pupitres_roles:
            out = ugettext('de ') + pupitres_roles
            if pupitres_instruments:
                out += ugettext(' avec ') + pupitres_instruments
            return out
        return ugettext('pour ') + pupitres_instruments

    def pupitres_html(self, prefix=False, tags=True, solistes=False):
        return self.get_pupitres_str(prefix=prefix, tags=tags,
                                     solistes=solistes)

    def auteurs_html(self, tags=True):
        return self.auteurs.html(tags)
    auteurs_html.short_description = _('auteur(s)')
    auteurs_html.admin_order_field = 'auteurs__individu__nom'

    def parentes_in_order(self, relation):
        return getattr(self, relation).order_by(
            'creation_date', 'creation_heure', 'creation_lieu',
            'creation_date_approx', 'creation_heure_approx',
            'creation_lieu_approx')

    def meres_in_order(self):
        return self.parentes_in_order('meres')

    def filles_in_order(self):
        return self.parentes_in_order('filles')

    @property
    def evenements(self):
        # We use a subquery, otherwise yearly_counts counts the number of
        # program elements instead of events.
        return apps.get_model('libretto', 'Evenement').objects.filter(
            pk__in=apps.get_model('libretto', 'Evenement').objects.filter(
                programme__oeuvre__in=self.get_descendants(include_self=True))
        )

    def oeuvres_associees(self):
        # TODO: Limiter à ce que l’utilisateur peut voir.
        return (
            Oeuvre.objects.exclude(
                pk__in=self.get_descendants(include_self=True))
            .filter(elements_de_programme__evenement__programme__oeuvre=self)
            .annotate(n=Count('elements_de_programme__evenement'))
            .order_by('-n', *self._meta.ordering)).distinct()

    def _link_with_number(self):
        return ugettext('œuvre jouée %s fois avec : %s') % (
            self.n, self.link())

    def get_referent_ancestors_html(self, tags=False, links=False):
        if not self.pk or self.extrait_de is None or \
                (self.genre and self.genre.referent):
            return ''
        return self.extrait_de.titre_html(
            tags=tags, links=links, ancestors_links=links,
            show_type_extrait=False)

    def has_titre_significatif(self):
        return bool(self.titre)

    def get_titre_significatif(self):
        return (f'{self.prefixe_titre}{self.titre}'
                f'{self.coordination}'
                f'{self.prefixe_titre_secondaire}{self.titre_secondaire}')

    def has_titre_non_significatif(self):
        return self.tempo or self.genre_id is not None

    def get_titre_non_significatif(self, tags=True, caps=False):
        if not self.has_titre_non_significatif():
            return ''
        if self.genre is None:
            assert self.tempo != ''
            l = [capfirst(self.tempo) if caps else self.tempo]
        else:
            l = [capfirst(self.genre.nom) if caps else self.genre.nom]
        if not self.has_titre_significatif():
            l.append(self.get_pupitres_str(tags=False, solistes=True))
        l.append(next(self.caracteristiques_iterator(tags=tags), None))

        return str_list(l, infix=' ')

    def get_description(self, tags=True):
        l = []
        if self.has_titre_significatif():
            l.append(self.get_titre_non_significatif(tags=tags))
        caracteristiques = list(self.caracteristiques_iterator(tags=tags))
        if self.has_titre_non_significatif():
            # La première caractéristique est utilisée dans le titre non
            # significatif.
            caracteristiques = caracteristiques[1:]
        l.extend(caracteristiques)
        return str_list(l, infix=' ')

    def html(self, tags=True, auteurs=True, titre=True, descr=True,
             ancestors=True, ancestors_links=False, links=True,
             show_type_extrait=True):
        l = []
        if auteurs:
            l.append(self.auteurs_html(tags=tags))
        if titre:
            if ancestors:
                l.append(self.get_referent_ancestors_html(
                    tags=tags, links=ancestors_links))
            if self.has_titre_significatif():
                titre_complet = cite(self.get_titre_significatif(), tags=tags)
            else:
                titre_complet = self.get_titre_non_significatif(
                    tags=tags,
                    caps=(self.type_extrait is None
                          or self.type_extrait in self.TYPES_EXTRAIT_CACHES))
            extrait = capfirst(self.get_extrait(show_type=show_type_extrait))
            if extrait:
                if titre_complet:
                    titre_complet = f'{extrait} {titre_complet}'
                elif self.type_extrait not in self.TYPES_EXTRAIT_CACHES:
                    titre_complet = extrait
            url = None if not tags else self.get_absolute_url()
            l.append(href(url, titre_complet, tags & links))
        if descr:
            l.append(self.get_description(tags=tags))
        return mark_safe(str_list(l))
    html.short_description = _('rendu HTML')

    def short_html(self, tags=True, links=False):
        return self.html(tags=tags, auteurs=False, titre=True, descr=False,
                         ancestors=False, links=links)

    def titre_html(self, tags=True, links=True, ancestors_links=True,
                   show_type_extrait=True):
        return self.html(tags, auteurs=False, titre=True, descr=False,
                         ancestors=True, ancestors_links=ancestors_links,
                         links=links, show_type_extrait=show_type_extrait)
    titre_html.short_description = _('titre')

    def titre_descr(self, tags=False):
        return self.html(tags=tags, auteurs=False, titre=True, descr=True,
                         ancestors=True)

    def titre_descr_html(self):
        return self.titre_descr(tags=True)

    def description_html(self, tags=True):
        return self.html(tags, auteurs=False, titre=False, descr=True)

    def handle_whitespaces(self):
        match = re.match(r'^,\s*(.+)$', self.coordination)
        v = self.coordination if match is None else match.group(1)
        if v:
            self.coordination = f', {v}'
        for attr in ('prefixe_titre', 'prefixe_titre_secondaire',
                     'coordination'):
            v = getattr(self, attr)
            if v and v[-1] not in (' ', "'", '’'):
                setattr(self, attr, f'{v} ')

    def related_label(self):
        txt = force_text(self)
        auteurs = self.auteurs.html(tags=False)
        if auteurs:
            txt += f' ({auteurs})'
        return txt

    def __str__(self):
        return strip_tags(self.titre_html(False))  # strip_tags car on autorise
                         # les rédacteurs à mettre des tags dans les CharFields

    _str = __str__
    _str.short_description = _('œuvre')

    @staticmethod
    def autocomplete_search_fields(add_icontains=True):
        lookups = (
            'auteurs__individu__nom', 'auteurs__individu__prenoms',
            'auteurs__individu__pseudonyme', 'auteurs__ensemble__nom',
            'prefixe_titre', 'titre',
            'prefixe_titre_secondaire', 'titre_secondaire',
            'genre__nom', 'numero', 'coupe',
            'tempo', 'sujet',
            'surnom', 'nom_courant', 'incipit',
            'opus', 'ict',
            'pupitres__partie__nom')
        lookups = [f'{lookup}__unaccent' for lookup in lookups]
        if add_icontains:
            return [f'{lookup}__icontains' for lookup in lookups]
        return lookups
