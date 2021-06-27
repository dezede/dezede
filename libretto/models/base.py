import datetime
import re

from django.conf import settings
from django.contrib.admin.models import LogEntry
from django.core.exceptions import NON_FIELD_ERRORS, FieldError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db.models import (
    Model, CharField, BooleanField, ForeignKey, TextField,
    Manager, PROTECT, Q, SmallIntegerField, Count, DateField, TimeField,
    NOT_PROVIDED)
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import time
from django.utils.encoding import force_text
from django.utils.html import strip_tags
from django.utils.translation import ugettext, ugettext_lazy as _
from autoslug import AutoSlugField
from slugify import Slugify
from tinymce.models import HTMLField
from tree.fields import PathField
from tree.query import TreeQuerySetMixin

from typography.models import TypographicModel, TypographicManager, \
    TypographicQuerySet
from common.utils.html import capfirst, date_html, sanitize_html
from common.utils.text import str_list
from typography.utils import replace


__all__ = (
    'LOWER_MSG', 'PLURAL_MSG', 'DATE_MSG', 'calc_pluriel',
    'PublishedQuerySet', 'PublishedManager', 'PublishedModel',
    'AutoriteModel', 'SlugModel', 'UniqueSlugModel', 'CommonTreeQuerySet',
    'CommonTreeManager', 'Etat', 'TypeDeParente',
)


#
# Définitions globales du fichier
#

LOWER_MSG = _('En minuscules.')
PLURAL_MSG = _('À remplir si le pluriel n’est pas un simple '
               'ajout de « s ». Exemple : « animal » devient « animaux » '
               'et non « animals ».')
DATE_MSG = _('Exemple : « 14/7/1789 » pour le 14 juillet 1789.')
DATE_MSG_EXTENDED = _(
    'Exemple : « 14/7/1789 » pour le 14 juillet 1789. '
    'En cas de date approximative, '
    'saisir le premier jour du mois (« 1/10/1678 » pour octobre 1678) '
    'ou de l’année (« 1/1/1830 » pour 1830).')
DATE_APPROX_MESSAGE = _(
    'Ne remplir que si la date est approximative. '
    'Par exemple : « 1870 », « octobre 1812 », « été 1967 ».')
HEURE_MSG = _('Exemple : « 19:30 » pour 19h30.')
HEURE_APPROX_MSG = _('Ne remplir que si l’heure est approximative. '
                     'Par exemple : « matinée », « soirée ».')


def calc_pluriel(obj, attr_base='nom', attr_suffix='_pluriel'):
    """
    Renvoie le nom au pluriel d'obj, si possible.
    Sinon renvoie force_text(obj).
    """
    try:
        pluriel = getattr(obj, f'{attr_base}{attr_suffix}')
        if pluriel:
            return pluriel
        return f'{getattr(obj, attr_base)}s'
    except (AttributeError, TypeError):
        return force_text(obj)


ISNI_VALIDATORS = [
    MinLengthValidator(16),
    RegexValidator(r'^\d{15}[\dxX]$', _('Numéro d’ISNI invalide.'))]


#
# Modélisation abstraite
#


def get_related_fields(meta):
    return [
        f for f in meta.get_fields()
        if (f.one_to_many or f.one_to_one)
        and f.auto_created and not f.concrete
    ] + [f for f in meta.get_fields(include_hidden=True)
         if f.many_to_many and f.auto_created]


# TODO: Personnaliser order_by pour simuler automatiquement NULLS LAST
# en faisant comme https://coderwall.com/p/cjluxg
class CommonQuerySet(TypographicQuerySet):
    def _get_no_related_objects_filter_kwargs(self):
        meta = self.model._meta
        return {r.get_accessor_name(): None for r in get_related_fields(meta)}

    def with_related_objects(self):
        return self.exclude(**self._get_no_related_objects_filter_kwargs())

    def without_related_objects(self):
        return self.filter(**self._get_no_related_objects_filter_kwargs())


class CommonManager(TypographicManager):
    use_for_related_fields = True
    queryset_class = CommonQuerySet


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
        relations = get_related_fields(self._meta)
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

    def get_related_count(self):
        count = 0
        for field in get_related_fields(self._meta):
            count += (self.__class__._default_manager.filter(pk=self.pk)
                      .aggregate(n=Count(field.get_accessor_name()))['n'])
        return count

    @classmethod
    def class_name(cls):
        return force_text(cls.__name__)

    @classmethod
    def meta(cls):
        return cls._meta

    def related_label(self):
        return force_text(self)

    @staticmethod
    def autocomplete_term_adjust(term):
        return replace(term)


class PublishedQuerySet(CommonQuerySet):
    @staticmethod
    def _get_filters(request=None):
        filters = Q(etat__public=True)
        if request is None:
            return filters

        if request.user.is_superuser:
            return Q()

        if request.user.is_authenticated:
            filters |= Q(owner=request.user.pk)
        return filters

    def published(self, request=None):
        qs = self.filter(self._get_filters(request))

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

    def published(self, request=None):
        return self.get_queryset().published(request=request)


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

    def can_be_viewed(self, request=None):
        public = self.is_public
        if request is None or not request.user.is_authenticated:
            return public
        if request.user.is_superuser:
            return True
        return public or request.user.pk == self.owner_id


class AutoriteModel(PublishedModel):
    notes_publiques = HTMLField(blank=True, verbose_name=_('notes publiques'))
    notes_privees = HTMLField(blank=True, verbose_name=_('notes privées'))

    class Meta(object):
        abstract = True


slugify_unicode_class = Slugify(translate=None, to_lower=True, max_length=50)


def slugify_unicode(text):
    return slugify_unicode_class(force_text(text))


class SlugModel(Model):
    slug = AutoSlugField(populate_from='get_slug', always_update=True,
                         slugify=slugify_unicode)

    class Meta(object):
        abstract = True

    def get_slug(self):
        s = slugify_unicode(force_text(self))
        if not s:
            return force_text(self._meta.verbose_name)
        return s


class UniqueSlugModel(Model):
    slug = AutoSlugField(
        populate_from='get_slug', unique=True, always_update=True,
        slugify=slugify_unicode)

    class Meta(object):
        abstract = True

    def get_slug(self):
        s = slugify_unicode(force_text(self))
        if not s:
            return force_text(self._meta.verbose_name)
        return s


class CommonTreeQuerySet(TreeQuerySetMixin, CommonQuerySet):
    pass


class CommonTreeManager(CommonManager):
    queryset_class = CommonTreeQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db).order_by(
            [f.name for f in self.model._meta.fields
             if isinstance(f, PathField)][0])


class NumberCharField(CharField):
    NUMBER_RE = re.compile(r'\d+')

    def __init__(self, *args, zfill_size=6, **kwargs):
        super().__init__(*args, **kwargs)
        self.zfill_size = zfill_size

    def fill_zeros(self, match):
        return match.group(0).zfill(self.zfill_size)

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super().get_db_prep_value(value, connection, prepared=prepared)
        if value is None:
            return None
        return self.NUMBER_RE.sub(self.fill_zeros, value)

    def strip_zeros(self, match):
        return match.group(0).lstrip('0')

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.NUMBER_RE.sub(self.strip_zeros, value)


class AncrageSpatioTemporel(object):
    def __init__(self, not_null_fields=(),
                 has_date=True, has_heure=True, has_lieu=True, approx=True,
                 verbose_name=None):
        self.not_null_fields = not_null_fields
        self.has_date = has_date
        self.has_heure = has_heure
        self.has_lieu = has_lieu
        self.approx = approx
        self.verbose_name = verbose_name

        # Definitions expected by Django.
        self.remote_field = None
        self.rel = None
        self.is_relation = False
        self.column = None
        self.concrete = False
        self.auto_created = False
        self.one_to_many = False
        self.one_to_one = False
        self.many_to_many = False
        self.editable = True
        self.primary_key = False
        self.unique = False
        self.blank = True
        self.null = True
        self.default = NOT_PROVIDED
        self.serialize = False
        self.choices = []
        self.help_text = None
        self.db_index = False
        self.db_column = None
        self.db_tablespace = settings.DEFAULT_INDEX_TABLESPACE
        self.auto_created = False

    def get_col(self, *args, **kwargs):
        return list(self.fields.values())[0].get_col(*args, **kwargs)

    def create_fields(self):
        fields = []
        if self.has_date:
            is_null = 'date' not in self.not_null_fields
            date_msg = DATE_MSG_EXTENDED if self.approx else DATE_MSG
            fields.append(('date', DateField(
                _('date'), blank=is_null, null=is_null, db_index=True,
                help_text=date_msg)))
            if self.approx:
                is_null = 'date_approx' not in self.not_null_fields
                fields.append(('date_approx', CharField(
                    _('date (approximative)'), max_length=60, blank=is_null,
                    help_text=DATE_APPROX_MESSAGE)))
        if self.has_heure:
            is_null = 'heure' not in self.not_null_fields
            fields.append(('heure', TimeField(
                _('heure'), blank=is_null, null=is_null, db_index=True,
                help_text=HEURE_MSG)))
            if self.approx:
                is_null = 'heure_approx' not in self.not_null_fields
                fields.append(('heure_approx', CharField(
                    _('heure (approximative)'), max_length=30, blank=is_null,
                    help_text=HEURE_APPROX_MSG)))
        if self.has_lieu:
            is_null = 'lieu' not in self.not_null_fields
            fields.append(('lieu', ForeignKey(
                'Lieu', blank=is_null, null=is_null, verbose_name=_('lieu'),
                on_delete=PROTECT,
                related_name=f'{self.model._meta.model_name}_'
                             f'{self.name}_set')))
            if self.approx:
                is_null = 'lieu_approx' not in self.not_null_fields
                fields.append(('lieu_approx', CharField(
                    _('lieu (approximatif)'), max_length=50, blank=is_null,
                    help_text=_('Ne remplir que si le lieu (ou l’institution) '
                                'est approximatif(ve).'))))
        return fields

    def contribute_to_class(self, model, name):
        self.name = self.attname = name
        self.model = model
        if self.model._meta.abstract:
            return
        for parent in self.model._meta.parents:
            if (not parent._meta.abstract
                and hasattr(parent, name)
                    and isinstance(getattr(parent, name),
                                   AncrageSpatioTemporel)):
                return
        self.prefix = '' if name == 'ancrage' else f'{name}_'

        self.fields = self.create_fields()

        self.admin_order_field = f'{self.prefix}{self.fields[0][0]}'

        model._meta.add_field(self, private=True)
        setattr(model, name, self)

        for fieldname, field in self.fields:
            field.contribute_to_class(model, f'{self.prefix}{fieldname}')

        self.fields = dict(self.fields)

    def instance_bound(self):
        return hasattr(self, 'instance') and self.instance is not None

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            if key == 'instance':
                raise
            if self.instance_bound() and key in self.fields:
                return getattr(self.instance, f'{self.prefix}{key}')
            raise

    def __setattr__(self, key, value):
        if self.instance_bound() and key in self.fields:
            setattr(self.instance, f'{self.prefix}{key}', value)
        else:
            super(AncrageSpatioTemporel, self).__setattr__(key, value)

    def __get__(self, instance, owner):
        self.owner = owner
        self.instance = instance
        return self

    def __set__(self, instance, value):
        self.instance = instance
        super(AncrageSpatioTemporel, self).__set__(instance, value)

    def __bool__(self):
        return (self.instance_bound()
                and any(getattr(self, k) for k in self.fields))
    # Python 2 compatibility
    __nonzero__ = __bool__

    def __str__(self):
        return strip_tags(self.html(tags=False, short=True))

    def __repr__(self):
        return f'<AncrageSpatioTemporel: {self.name}>'

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
        if not self.has_lieu or self.lieu is None:
            return ''
        if self.approx and self.lieu_approx:
            return self.lieu_approx
        return self.lieu.html(tags, short)

    def isoformat(self):
        if not (self.has_date and self.date):
            return ''
        if self.has_heure and self.heure:
            return datetime.datetime.combine(self.date, self.heure).isoformat()
        return self.date.isoformat()

    def html(self, tags=True, short=False, caps=True):
        out = str_list((self.lieu_str(tags, short),
                        self.moment_str(tags, short)))
        if caps:
            return capfirst(out)
        return out

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


class TypeDeParente(CommonModel):
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

    class Meta(object):
        abstract = True

    def pluriel(self):
        return calc_pluriel(self)

    def relatif_pluriel(self):
        return calc_pluriel(self, attr_base='nom_relatif')

    def __str__(self):
        return f'{self.nom} ({self.nom_relatif})'


#
# Modèles communs
#


class Etat(CommonModel, UniqueSlugModel):
    nom = CharField(_('nom'), max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
                            help_text=PLURAL_MSG)
    message = HTMLField(
        _('message'), blank=True,
        help_text=_('Message à afficher dans la partie consultation.'))
    public = BooleanField(_('publié'), default=True, db_index=True)

    class Meta(object):
        verbose_name = _('état')
        verbose_name_plural = _('états')
        ordering = ('slug',)

    def __str__(self):
        return self.nom

    def pluriel(self):
        return calc_pluriel(self)


#
# Signals
#


@receiver(pre_save)
def handle_whitespaces(sender, **kwargs):
    # We skip LogEntry because the logged entry has already been saved
    # (and sanitized).
    if sender is LogEntry:
        return

    # We start by stripping all leading and trailing whitespaces.
    obj = kwargs['instance']
    for field_name in [f.attname for f in obj._meta.fields]:
        v = getattr(obj, field_name)
        if hasattr(v, 'strip'):
            setattr(obj, field_name, sanitize_html(v.strip()))
    # Then we call the specific whitespace handler of the model (if it exists).
    if hasattr(obj, 'handle_whitespaces'):
        obj.handle_whitespaces()
