# coding: utf-8

from __future__ import unicode_literals
from collections import OrderedDict
import datetime
from django.conf import settings
from django.contrib.contenttypes.generic import GenericRelation
from django.core.exceptions import NON_FIELD_ERRORS, FieldError
from django.db.models import (
    Model, CharField, BooleanField, ManyToManyField, ForeignKey, TextField,
    Manager, PROTECT, Q, SmallIntegerField, Count, DateField, TimeField,
    get_model)
from django.db.models.query import EmptyQuerySet
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import time
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ungettext_lazy, ugettext
from autoslug import AutoSlugField
from filebrowser.fields import FileBrowseField
from mptt.managers import TreeManager
from polymorphic import PolymorphicModel, PolymorphicManager, \
    PolymorphicQuerySet
from tinymce.models import HTMLField
from cache_tools import cached_ugettext_lazy as _
from typography.models import TypographicModel, TypographicManager, \
    TypographicQuerySet
from .functions import href, ex, hlp, capfirst, str_list, date_html


__all__ = (
    b'LOWER_MSG', b'PLURAL_MSG', b'DATE_MSG', b'calc_pluriel',
    b'PublishedQuerySet', b'PublishedManager', b'PublishedModel',
    b'AutoriteModel', b'SlugModel', b'UniqueSlugModel', b'CommonTreeQuerySet',
    b'CommonTreeManager', b'Document', b'Illustration', b'Etat',
    b'OrderedDefaultDict', b'TypeDeParente', b'TypeDeCaracteristique',
)


class OrderedDefaultDict(OrderedDict):
    def __missing__(self, k):
        self[k] = l = []
        return l


#
# Définitions globales du fichier
#

LOWER_MSG = _('En minuscules.')
PLURAL_MSG = _('À remplir si le pluriel n’est pas un simple '
               'ajout de « s ». Exemple : « animal » devient « animaux » '
               'et non « animals ».')
DATE_MSG = _('Exemple : « 6/6/1944 » pour le 6 juin 1944.')


def calc_pluriel(obj, attr_base='nom', attr_suffix='_pluriel'):
    """
    Renvoie le nom au pluriel d'obj, si possible.
    Sinon renvoie smart_text(obj).
    """
    try:
        pluriel = getattr(obj, attr_base + attr_suffix)
        if pluriel:
            return pluriel
        return getattr(obj, attr_base) + 's'
    except (AttributeError, TypeError):
        return smart_text(obj)


#
# Modélisation abstraite
#


class CommonEmptyQuerySet(EmptyQuerySet):
    def with_related_objects(self):
        return self

    def without_related_objects(self):
        return self


# TODO: Personnaliser order_by pour simuler automatiquement NULLS LAST
# en faisant comme https://coderwall.com/p/cjluxg
class CommonQuerySet(TypographicQuerySet):
    def _get_no_related_objects_filter_kwargs(self):
        meta = self.model._meta
        return {r.get_accessor_name(): None for r in
                meta.get_all_related_objects()
                + meta.get_all_related_many_to_many_objects()}

    def with_related_objects(self):
        return self.exclude(**self._get_no_related_objects_filter_kwargs())

    def without_related_objects(self):
        return self.filter(**self._get_no_related_objects_filter_kwargs())


class CommonManager(TypographicManager):
    use_for_related_fields = True
    queryset_class = CommonQuerySet
    empty_queryset_class = CommonEmptyQuerySet

    def get_empty_query_set(self):
        return self.empty_queryset_class(self.model, using=self._db)


class CommonModel(TypographicModel):
    """
    Modèle commun à l’application, ajoutant diverses possibilités.
    """
    owner = ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        verbose_name=_('propriétaire'), on_delete=PROTECT,
        related_name='%(class)s')
    objects = CommonManager()

    class Meta(object):
        abstract = True  # = prototype de modèle, et non un vrai modèle.

    def _perform_unique_checks(self, unique_checks):
        # Taken from the overridden method.
        errors = {}

        for model_class, unique_check in unique_checks:

            lookup_kwargs = {}
            for field_name in unique_check:
                f = self._meta.get_field(field_name)
                lookup_value = getattr(self, f.attname)
                if lookup_value is None:
                    continue
                if f.primary_key and not self._state.adding:
                    continue
                if isinstance(f, (CharField, TextField)):
                    field_name += '__iexact'
                lookup_kwargs[str(field_name)] = lookup_value

            if len(unique_check) != len(lookup_kwargs.keys()):
                continue

            qs = model_class._default_manager.filter(**lookup_kwargs)

            if not self._state.adding and self.pk is not None:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                if len(unique_check) == 1:
                    key = unique_check[0]
                else:
                    key = NON_FIELD_ERRORS
                errors.setdefault(key, []).append(
                    self.unique_error_message(model_class, unique_check))

        return errors

    def _has_related_objects__fallback(self):
        relations = self._meta.get_all_related_objects() \
            + self._meta.get_all_related_many_to_many_objects()
        for r in relations:
            try:
                v = getattr(self, r.get_accessor_name())
            except r.model.DoesNotExist:
                continue
            if isinstance(v, Manager):
                v = v.exists()
            if v:
                return True
        return False

    def has_related_objects(self):
        self_qs = self.__class__.objects.filter(pk=self.pk)
        try:
            return self_qs.with_related_objects().exists()
        except FieldError:
            return self._has_related_objects__fallback()
    has_related_objects.boolean = True
    has_related_objects.short_description = _('a des objets liés')

    def get_related_counts(self):
        attrs = [f.get_accessor_name()
                 for f in self._meta.get_all_related_objects()
                        + self._meta.get_all_related_many_to_many_objects()]
        return self.__class__._default_manager.filter(pk=self.pk) \
            .aggregate(**{attr: Count(attr) for attr in attrs})

    def get_related_count(self):
        return sum(self.get_related_counts().values())

    @classmethod
    def class_name(cls):
        return smart_text(cls.__name__)

    @classmethod
    def meta(cls):
        return cls._meta

    def related_label(self):
        return smart_text(self)


class PublishedEmptyQuerySet(CommonEmptyQuerySet):
    def published(self, request=None):
        return self


class PublishedQuerySet(CommonQuerySet):
    @staticmethod
    def _get_filters(request=None):
        if request is None or not request.user.is_authenticated:
            return (), {'etat__public': True}
        elif not request.user.is_superuser:
            return (Q(etat__public=True) | Q(owner=request.user.pk),), {}
        return (), {}

    def published(self, request=None):
        filter_args, filter_kwargs = self._get_filters(request)

        qs = self.filter(*filter_args, **filter_kwargs)

        # Automatically orders by the correct ordering.
        ordering = []
        if self.ordered:
            query = self.query
            if query.order_by:
                ordering = query.order_by
            elif query.default_ordering:
                ordering = self.model._meta.ordering

        return qs.order_by(*ordering)


class PublishedManager(CommonManager):
    queryset_class = PublishedQuerySet
    empty_queryset_class = PublishedEmptyQuerySet

    def published(self, request=None):
        return self.get_query_set().published(request=request)


def _get_default_etat():
    return Etat.objects.get_or_create(nom='nouveau', defaults={
        'nom_pluriel': 'nouveaux',
        'message': '<p>Cette donnée a été créée récemment et nécessite '
                   'plusieurs relectures.  À lire avec précaution.</p>',
        'public': True,
    })[0]


class PublishedModel(CommonModel):
    etat = ForeignKey('libretto.Etat', default=_get_default_etat,
                      verbose_name=_('état'), on_delete=PROTECT)

    objects = PublishedManager()

    class Meta(object):
        abstract = True

    @property
    def is_public(self):
        return self.etat.public


class AutoriteModel(PublishedModel):
    documents = ManyToManyField(
        'Document', blank=True, null=True, related_name='%(class)s_set')
    illustrations = ManyToManyField(
        'Illustration', blank=True, null=True, related_name='%(class)s_set')
    notes = HTMLField(blank=True)

    class Meta(object):
        abstract = True


class SlugModel(Model):
    slug = AutoSlugField(populate_from='get_slug', always_update=True)

    class Meta(object):
        abstract = True

    def get_slug(self):
        return smart_text(self)


class UniqueSlugModel(Model):
    slug = AutoSlugField(
        populate_from='get_slug', unique=True, always_update=True)

    class Meta(object):
        abstract = True

    def get_slug(self):
        return smart_text(self)


class CommonTreeQuerySet(CommonQuerySet):
    def get_descendants(self, include_self=False):
        manager = self.model._default_manager
        tree_id_attr = manager.tree_id_attr
        left_attr = manager.left_attr
        right_attr = manager.right_attr
        filters = Q()

        for tree_id, left, right in self.values_list(
                tree_id_attr, left_attr, right_attr):
            if not include_self:
                left += 1
                right -= 1
            filters |= Q(**{tree_id_attr: tree_id,
                            left_attr + '__gte': left,
                            left_attr + '__lte': right})

        qs = self.model._tree_manager.filter(filters)
        if getattr(self, 'polymorphic_disabled', False):
            qs = qs.non_polymorphic()
        return qs


class CommonTreeManager(CommonManager, TreeManager):
    queryset_class = CommonTreeQuerySet

    def get_query_set(self):
        return self.queryset_class(self.model, using=self._db).order_by(
            self.tree_id_attr, self.left_attr)

    def get_descendants(self, *args, **kwargs):
        return self.get_query_set().get_descendants(*args, **kwargs)


@python_2_unicode_compatible
class AncrageSpatioTemporel(object):
    def __init__(self, not_null_fields=(),
                 has_date=True, has_heure=True, has_lieu=True, approx=True,
                 short_description=None):
        self.not_null_fields = not_null_fields
        self.has_date = has_date
        self.has_heure = has_heure
        self.has_lieu = has_lieu
        self.approx = approx
        if short_description is not None:
            self.short_description = short_description

    def create_fields(self):
        fields = []
        if self.has_date:
            is_null = 'date' not in self.not_null_fields
            fields.append(('date', DateField(
                _('date'), blank=is_null, null=is_null, db_index=True,
                help_text=DATE_MSG)))
            if self.approx:
                is_null = 'date_approx' not in self.not_null_fields
                fields.append(('date_approx', CharField(
                    _('date (approximative)'), max_length=200, blank=is_null,
                    db_index=True,
                    help_text=_('Ne remplir que si la date est imprécise.'))))
        if self.has_heure:
            is_null = 'heure' not in self.not_null_fields
            fields.append(('heure', TimeField(
                _('heure'), blank=is_null, null=is_null, db_index=True)))
            if self.approx:
                is_null = 'heure_approx' not in self.not_null_fields
                fields.append(('heure_approx', CharField(
                    _('heure (approximative)'), max_length=200, blank=is_null,
                    db_index=True,
                    help_text=_('Ne remplir que si l’heure est imprécise.'))))
        if self.has_lieu:
            is_null = 'lieu' not in self.not_null_fields
            fields.append(('lieu', ForeignKey(
                'Lieu', blank=is_null, null=is_null, verbose_name=_('lieu'),
                related_name='%s_%s_set' % (self.model._meta.module_name,
                                            self.name))))
            if self.approx:
                is_null = 'lieu_approx' not in self.not_null_fields
                fields.append(('lieu_approx', CharField(
                    _('lieu (approximatif)'), max_length=200,
                    blank=is_null, db_index=is_null,
                    help_text=_('Ne remplir que si le lieu (ou institution) '
                                'est imprécis(e).'))))
        return fields

    def contribute_to_class(self, model, name):
        self.name = name
        self.model = model
        self.prefix = name + '_'

        self.fields = self.create_fields()

        self.admin_order_field = self.prefix + self.fields[0][0]

        model._meta.add_virtual_field(self)
        setattr(model, name, self)

        for fieldname, field in self.fields:
            field.contribute_to_class(model, self.prefix+fieldname)

        self.fields = dict(self.fields)

    def instance_bound(self):
        return hasattr(self, 'instance') and self.instance is not None

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            if self.instance_bound() and key in self.fields:
                return getattr(self.instance, self.prefix+key)
            raise

    def __setattr__(self, key, value):
        if self.instance_bound() and key in self.fields:
            setattr(self.instance, self.prefix + key, value)
        else:
            super(AncrageSpatioTemporel, self).__setattr__(key, value)

    def __get__(self, instance, owner):
        self.owner = owner
        self.instance = instance
        return self

    def __set__(self, instance, value):
        self.instance = instance
        super(AncrageSpatioTemporel, self).__set__(instance, value)

    def __nonzero__(self):
        return (self.instance_bound()
                and any(getattr(self, k) for k in self.fields))

    def __str__(self):
        return strip_tags(self.html(tags=False, short=True))

    def __repr__(self):
        return '<AncrageSpatioTemporel: %s>' % self.name

    def date_str(self, tags=True, short=False):
        if not self.has_date:
            return ''
        if self.approx and self.date_approx:
            return self.date_approx
        return date_html(self.date, tags, short)

    def heure_str(self):
        if not self.has_heure:
            return ''
        if self.approx and self.heure_approx:
            return self.heure_approx
        return time(self.heure, ugettext('H\hi'))

    def moment_str(self, tags=True, short=False):
        l = []
        date = self.date_str(tags, short)
        heure = self.heure_str()
        pat_date = (ugettext('%(date)s') if self.has_date and self.date
                    else ugettext('%(date)s'))
        pat_heure = (ugettext('à %(heure)s') if self.has_heure and self.heure
                     else ugettext('%(heure)s'))
        l.append(pat_date % {'date': date})
        l.append(pat_heure % {'heure': heure})
        return str_list(l, ' ')

    def lieu_str(self, tags=True, short=False):
        try:
            if self.has_lieu and self.lieu:
                return self.lieu.html(tags, short)
        except get_model('libretto', 'Lieu').DoesNotExist:
            pass
        if self.has_lieu and self.approx:
            return self.lieu_approx
        return ''

    def isoformat(self):
        if not (self.has_date and self.date):
            return ''
        if self.has_heure and self.heure:
            return datetime.datetime.combine(self.date, self.heure).isoformat()
        return self.date.isoformat()

    def html(self, tags=True, short=False):
        out = str_list((self.lieu_str(tags, short),
                        self.moment_str(tags, short)))
        return capfirst(out)

    def short_html(self, tags=True):
        return self.html(tags, short=True)

    def get_preciseness(self):
        score = 0
        for k in ('date', 'date_approx', 'lieu', 'lieu_approx'):
            if getattr(self, k):
                score += 1 if '_approx' in k else 2
        return score

    def is_more_precise_than(self, other):
        if other.__class__ is not self.__class__:
            return False

        if self.get_preciseness() > other.get_preciseness():
            return True
        return False


#
# Modèles génériques polymorphes.
#


class TypeDeCaracteristiqueQuerySet(PolymorphicQuerySet, CommonQuerySet):
    pass


class TypeDeCaracteristiqueManager(PolymorphicManager, CommonManager):
    queryset_class = TypeDeCaracteristiqueQuerySet


@python_2_unicode_compatible
class TypeDeCaracteristique(PolymorphicModel, CommonModel):
    nom = CharField(_('nom'), max_length=200, help_text=ex(_('tonalité')),
                    unique=True, db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
                            help_text=PLURAL_MSG)
    classement = SmallIntegerField(default=1)

    objects = TypeDeCaracteristiqueManager()

    class Meta(object):
        verbose_name = ungettext_lazy('type de caractéristique',
                                      'types de caracteristique', 1)
        verbose_name_plural = ungettext_lazy(
            'type de caractéristique',
            'types de caracteristique',
            2)
        ordering = ('classement',)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('get_real_instance', 'caracteristiques',)

    def pluriel(self):
        return calc_pluriel(self)

    def __str__(self):
        return self.nom

    @staticmethod
    def autocomplete_search_fields():
        return 'nom__icontains', 'nom_pluriel__icontains',


class CaracteristiqueQuerySet(PolymorphicQuerySet, CommonQuerySet):
    def html_list(self, tags=True):
        return [hlp(valeur, type, tags)
                for type, valeur in self.values_list('type__nom', 'valeur')]

    def html(self, tags=True, caps=False):
        l = []
        first = True
        for type, valeur in self.values_list('type__nom', 'valeur'):
            if first and caps:
                valeur = capfirst(valeur)
                first = False
            valeur = mark_safe(valeur)
            if type:
                l.append(hlp(valeur, type, tags=tags))
            else:
                l.append(valeur)
        return str_list(l)


class CaracteristiqueManager(PolymorphicManager, CommonManager):
    queryset_class = CaracteristiqueQuerySet

    def html_list(self, tags=True):
        return self.get_query_set().html_list(tags=tags)

    def html(self, tags=True, caps=True):
        return self.get_query_set().html(tags=tags, caps=caps)


@python_2_unicode_compatible
class Caracteristique(PolymorphicModel, CommonModel):
    type = ForeignKey(
        'TypeDeCaracteristique', null=True, blank=True, db_index=True,
        on_delete=PROTECT, related_name='caracteristiques',
        verbose_name=_('type'))
    valeur = CharField(_('valeur'), max_length=400,
                       help_text=ex(_('en trois actes')))
    classement = SmallIntegerField(
        _('classement'), default=1, db_index=True,
        help_text=_('Par exemple, on peut choisir de classer '
                    'les découpages par nombre d’actes.'))

    objects = CaracteristiqueManager()

    class Meta(object):
        # FIXME: Retirer les doublons et activer ce qui suit.
        # unique_together = ('type', 'valeur')
        verbose_name = ungettext_lazy('caractéristique',
                                      'caractéristiques', 1)
        verbose_name_plural = ungettext_lazy('caractéristique',
                                             'caractéristiques', 2)
        ordering = ('type', 'classement', 'valeur')
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('get_real_instance',)

    def html(self, tags=True, caps=False):
        value = self.valeur
        if caps:
            value = capfirst(self.valeur)
        value = mark_safe(value)
        if self.type:
            return hlp(value, self.type, tags=tags)
        return value
    html.allow_tags = True

    def __str__(self):
        if self.type:
            return smart_text(self.type) + ' : ' + strip_tags(self.valeur)
        return strip_tags(self.valeur)

    @staticmethod
    def autocomplete_search_fields():
        return 'type__nom__icontains', 'valeur__icontains',


class TypeDeParenteQuerySet(PolymorphicQuerySet, CommonQuerySet):
    pass


class TypeDeParenteManager(PolymorphicManager, CommonManager):
    queryset_class = TypeDeParenteQuerySet


@python_2_unicode_compatible
class TypeDeParente(PolymorphicModel, CommonModel):
    nom = CharField(_('nom'), max_length=100, help_text=LOWER_MSG,
                    db_index=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=55, blank=True,
                            help_text=PLURAL_MSG)
    nom_relatif = CharField(_('nom relatif'), max_length=100,
                            help_text=LOWER_MSG, db_index=True)
    nom_relatif_pluriel = CharField(
        _('nom relatif (au pluriel)'), max_length=130, blank=True,
        help_text=PLURAL_MSG)
    classement = SmallIntegerField(_('classement'), default=1, db_index=True)

    objects = TypeDeParenteManager()

    class Meta(object):
        unique_together = ('nom', 'nom_relatif')
        verbose_name = ungettext_lazy('type de parenté',
                                      'types de parentés', 1)
        verbose_name_plural = ungettext_lazy('type de parenté',
                                             'types de parentés', 2)
        ordering = ('classement',)
        app_label = 'libretto'

    @staticmethod
    def invalidated_relations_when_saved(all_relations=False):
        return ('get_real_instance',)

    def pluriel(self):
        return calc_pluriel(self)

    def relatif_pluriel(self):
        return calc_pluriel(self, attr_base='nom_relatif')

    def __str__(self):
        return '< %s | %s >' % (self.nom, self.nom_relatif)


#
# Modèles communs
#


@python_2_unicode_compatible
class Document(CommonModel):
    nom = CharField(_('nom'), max_length=300, blank=True)
    document = FileBrowseField(
        _('document'), max_length=400, directory='documents/',
        format='document')
    description = HTMLField(_('description'), blank=True)
    auteurs = GenericRelation('Auteur')

    class Meta(object):
        verbose_name = ungettext_lazy('document', 'documents', 1)
        verbose_name_plural = ungettext_lazy('document', 'documents', 2)
        ordering = ('document',)
        app_label = 'libretto'

    def __str__(self):
        if self.nom:
            return self.nom
        return smart_text(self.document)

    def link(self):
        return href(self.document.url, smart_text(self))

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'document__icontains',
                'description__icontains', 'auteurs__individu__nom',)


@python_2_unicode_compatible
class Illustration(CommonModel):
    legende = CharField(_('légende'), max_length=300, blank=True)
    image = FileBrowseField(
        _('image'), max_length=400, directory='images/', format='image')
    commentaire = HTMLField(_('commentaire'), blank=True)
    auteurs = GenericRelation('Auteur')

    class Meta(object):
        verbose_name = ungettext_lazy('illustration', 'illustrations', 1)
        verbose_name_plural = ungettext_lazy('illustration',
                                             'illustrations', 2)
        ordering = ('image',)
        app_label = 'libretto'

    def __str__(self):
        if self.legende:
            return self.legende
        return smart_text(self.image)

    def link(self):
        return href(self.image.url, smart_text(self))

    @staticmethod
    def autocomplete_search_fields():
        return ('legende__icontains', 'image__icontains',
                'commentaire__icontains',)


@python_2_unicode_compatible
class Etat(CommonModel, UniqueSlugModel):
    nom = CharField(_('nom'), max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
                            help_text=PLURAL_MSG)
    message = HTMLField(
        _('message'), blank=True,
        help_text=_('Message à afficher dans la partie consultation.'))
    public = BooleanField(_('publié'), default=True, db_index=True)

    class Meta(object):
        verbose_name = ungettext_lazy('état', 'états', 1)
        verbose_name_plural = ungettext_lazy('état', 'états', 2)
        ordering = ('slug',)
        app_label = 'libretto'

    def __str__(self):
        return self.nom

    def pluriel(self):
        return calc_pluriel(self)


#
# Signals
#


@receiver(pre_save)
def handle_whitespaces(sender, **kwargs):
    # We start by stripping all leading and trailing whitespaces.
    obj = kwargs['instance']
    for field_name in [f.attname for f in obj._meta.fields]:
        v = getattr(obj, field_name)
        if hasattr(v, 'strip'):
            setattr(obj, field_name, v.strip())
    # Then we call the specific whitespace handler of the model (if it exists).
    if hasattr(obj, 'handle_whitespaces'):
        obj.handle_whitespaces()
