# coding: utf-8

from __future__ import unicode_literals
from collections import OrderedDict, defaultdict
import datetime
import json
import os
from subprocess import check_output, CalledProcessError, PIPE
from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, FieldError, ValidationError
from django.db.models import (
    Model, CharField, BooleanField, ForeignKey, TextField,
    Manager, PROTECT, Q, SmallIntegerField, Count, DateField, TimeField,
    get_model, FileField, PositiveSmallIntegerField, OneToOneField, SET_NULL)
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import time
from django.utils.encoding import python_2_unicode_compatible, force_text
from django.utils.html import strip_tags
from django.utils.translation import (
    ungettext_lazy, ugettext, ugettext_lazy as _)
from autoslug import AutoSlugField
from mptt.managers import TreeManager
from mptt.querysets import TreeQuerySet
from slugify import Slugify
from tinymce.models import HTMLField
from cache_tools import invalidate_object
from typography.models import TypographicModel, TypographicManager, \
    TypographicQuerySet
from common.utils.html import href, capfirst, date_html, sanitize_html
from common.utils.text import str_list
from typography.utils import replace


__all__ = (
    b'LOWER_MSG', b'PLURAL_MSG', b'DATE_MSG', b'calc_pluriel',
    b'PublishedQuerySet', b'PublishedManager', b'PublishedModel',
    b'AutoriteModel', b'SlugModel', b'UniqueSlugModel', b'CommonTreeQuerySet',
    b'CommonTreeManager', b'Etat', b'OrderedDefaultDict',
    b'TypeDeParente',
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
DATE_MSG_EXTENDED = _('Exemple : « 6/6/1944 » pour le 6 juin 1944. '
                      'En cas de date approximative, saisir ici le début de '
                      'l’intervalle, par exemple « 1/1/1678 » pour 1678.')


def calc_pluriel(obj, attr_base='nom', attr_suffix='_pluriel'):
    """
    Renvoie le nom au pluriel d'obj, si possible.
    Sinon renvoie force_text(obj).
    """
    try:
        pluriel = getattr(obj, attr_base + attr_suffix)
        if pluriel:
            return pluriel
        return getattr(obj, attr_base) + 's'
    except (AttributeError, TypeError):
        return force_text(obj)


#
# Modélisation abstraite
#


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

        if request.user.is_authenticated():
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
    })[0].pk


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
        if request is None or not request.user.is_authenticated():
            return public
        if request.user.is_superuser:
            return True
        return public or request.user.pk == self.owner_id


class AutoriteModel(PublishedModel):
    notes_publiques = HTMLField(blank=True, verbose_name='notes publiques')
    notes_privees = HTMLField(blank=True, verbose_name='notes privées')

    class Meta(object):
        abstract = True


slugify_unicode = Slugify(translate=None)
slugify_unicode.to_lower = True
slugify_unicode.max_length = 50


class SlugModel(Model):
    slug = AutoSlugField(populate_from='get_slug', always_update=True,
                         slugify=slugify_unicode)

    class Meta(object):
        abstract = True

    def get_slug(self):
        invalidate_object(self)
        return force_text(self)


class UniqueSlugModel(Model):
    slug = AutoSlugField(
        populate_from='get_slug', unique=True, always_update=True,
        slugify=slugify_unicode)

    class Meta(object):
        abstract = True

    def get_slug(self):
        invalidate_object(self)
        return force_text(self)


class CommonTreeQuerySet(CommonQuerySet, TreeQuerySet):
    pass


class CommonTreeManager(CommonManager, TreeManager):
    queryset_class = CommonTreeQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db).order_by(
            self.tree_id_attr, self.left_attr)

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
            date_msg = DATE_MSG_EXTENDED if self.approx else DATE_MSG
            fields.append(('date', DateField(
                _('date'), blank=is_null, null=is_null, db_index=True,
                help_text=date_msg)))
            if self.approx:
                is_null = 'date_approx' not in self.not_null_fields
                fields.append(('date_approx', CharField(
                    _('date (approximative)'), max_length=60, blank=is_null,
                    help_text=_('Ne remplir que si la date est imprécise.'))))
        if self.has_heure:
            is_null = 'heure' not in self.not_null_fields
            fields.append(('heure', TimeField(
                _('heure'), blank=is_null, null=is_null, db_index=True)))
            if self.approx:
                is_null = 'heure_approx' not in self.not_null_fields
                fields.append(('heure_approx', CharField(
                    _('heure (approximative)'), max_length=30, blank=is_null,
                    help_text=_('Ne remplir que si l’heure est imprécise.'))))
        if self.has_lieu:
            is_null = 'lieu' not in self.not_null_fields
            fields.append(('lieu', ForeignKey(
                'Lieu', blank=is_null, null=is_null, verbose_name=_('lieu'),
                on_delete=PROTECT,
                related_name='%s_%s_set' % (self.model._meta.model_name,
                                            self.name))))
            if self.approx:
                is_null = 'lieu_approx' not in self.not_null_fields
                fields.append(('lieu_approx', CharField(
                    _('lieu (approximatif)'), max_length=50, blank=is_null,
                    help_text=_('Ne remplir que si le lieu (ou institution) '
                                'est imprécis(e).'))))
        return fields

    def contribute_to_class(self, model, name):
        self.name = name
        self.model = model
        if self.model._meta.abstract:
            return
        for parent in self.model._meta.parents:
            if (not parent._meta.abstract
                and hasattr(parent, name)
                    and isinstance(getattr(parent, name),
                                   AncrageSpatioTemporel)):
                return
        self.prefix = '' if name == 'ancrage' else name + '_'

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


@python_2_unicode_compatible
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
        return '%s (%s)' % (self.nom, self.nom_relatif)


#
# Modèles communs
#


class FichierQuerySet(CommonQuerySet):
    def others(self):
        return self.filter(type=self.model.OTHER)

    def images(self):
        return self.filter(type=self.model.IMAGE)

    def audios(self):
        return self.filter(type=self.model.AUDIO)

    def videos(self):
        return self.filter(type=self.model.VIDEO)

    def group_by_type(self):
        groups = defaultdict(list)
        groups.update(audios=OrderedDefaultDict(),
                      videos=OrderedDefaultDict())
        for fichier in self:
            if fichier.is_image():
                groups['images'].append(fichier)
            elif fichier.is_audio():
                groups['audios'][fichier.get_stem()].append(fichier)
            elif fichier.is_video():
                groups['videos'][fichier.get_stem()].append(fichier)
            else:
                groups['others'].append(fichier)
        groups.update(audios=groups['audios'].values(),
                      videos=groups['videos'].values())
        return groups

    def published(self, request=None):
        if request is None or not request.user.is_authenticated():
            return self.filter(extract=None)
        return self.filter(Q(extract__isnull=False) | Q(extract_from=None))


class FichierManager(CommonManager):
    queryset_class = FichierQuerySet

    def others(self):
        return self.get_queryset().others()

    def images(self):
        return self.get_queryset().images()

    def audios(self):
        return self.get_queryset().audios()

    def videos(self):
        return self.get_queryset().videos()

    def group_by_type(self):
        return self.get_queryset().group_by_type()


@python_2_unicode_compatible
class Fichier(CommonModel):
    source = ForeignKey('Source', related_name='fichiers')
    fichier = FileField(upload_to='files/')
    folio = CharField(max_length=10, blank=True)
    page = CharField(max_length=10, blank=True)

    # Internal fields
    OTHER = 0
    IMAGE = 1
    AUDIO = 2
    VIDEO = 3
    TYPES = (
        (OTHER, 'autre'),
        (IMAGE, 'image'),
        (AUDIO, 'audio'),
        (VIDEO, 'vidéo'),
    )
    type = PositiveSmallIntegerField(choices=TYPES, null=True, blank=True,
                                     db_index=True)
    format = CharField(max_length=10, blank=True)
    width = PositiveSmallIntegerField(_('largeur'), null=True, blank=True)
    height = PositiveSmallIntegerField(_('hauteur'), null=True, blank=True)
    duration = PositiveSmallIntegerField(_('durée (en secondes)'),
                                         null=True, blank=True)
    EXTRACT_INFIX = '.extrait'
    extract = OneToOneField(
        'self', related_name='extract_from', null=True, blank=True,
        verbose_name=_('extrait'), on_delete=SET_NULL)
    position = PositiveSmallIntegerField(_('position'))

    objects = FichierManager()

    class Meta(object):
        verbose_name = ungettext_lazy('fichier', 'fichiers', 1)
        verbose_name_plural = ungettext_lazy('fichier', 'fichiers', 2)
        ordering = ('position',)
        app_label = 'libretto'

    def __str__(self):
        return force_text(self.fichier)

    def link(self):
        return href(self.fichier.url, force_text(self))

    def is_image(self):
        return self.type == self.IMAGE

    def is_audio(self):
        return self.type == self.AUDIO

    def is_video(self):
        return self.type == self.VIDEO

    def get_filename(self):
        return os.path.basename(self.fichier.url)

    def get_stem(self):
        return os.path.splitext(self.get_filename())[0]

    FORMAT_BINDINGS = {
        'matroska,webm': 'webm',
        'mov,mp4,m4a,3gp,3g2,mj2': 'mp4',
    }
    HTML5_AV_FORMATS = {
        'mp3': (('mp3',),),
        'webm': (('vorbis',), ('vp8', 'vorbis'), ('vp9', 'opus')),
        'ogg': (('vorbis',), ('opus',),
                ('theora', 'vorbis'),),
        'mp4': (('aac',), ('h264', 'mp3'), ('h264', 'aac')),
    }

    def _get_normalized_filename(self, filename):
        return self._meta.get_field('fichier').get_filename(filename)

    def get_fichier_complet(self):
        l = self.fichier.name.split(self.EXTRACT_INFIX, 1)
        if len(l) == 2:
            fichier_complet_filename = self._get_normalized_filename(''.join(l))
            qs = self.source.fichiers.exclude(
                pk=self.pk).filter(
                fichier__regex=r'^(?:.+/)?%s$' % fichier_complet_filename)
            if len(qs) < 1:
                raise ValidationError(_('Il n’y a pas d’enregistrement entier '
                                        'pour cet extrait.'))
            elif len(qs) == 1:
                try:
                    list(qs)[0].extract_from
                except Fichier.DoesNotExist:
                    pass
                else:
                    raise ValidationError(
                        _('L’enregistrement dont ce fichier est extrait est '
                          'déjà un extrait.'))
            return list(qs)[0]

    def clean(self):
        self.get_fichier_complet()

    def get_media_info(self):
        # Force le fichier à être enregistré pour qu’il puisse être analysé.
        self._meta.get_field('fichier').pre_save(self, False)

        try:
            stdout = check_output([
                'avprobe', '-of', 'json', '-show_format', '-show_streams',
                self.fichier.path], stderr=PIPE)
        except CalledProcessError:
            return

        data = json.loads(stdout)

        format = data['format']['format_name']
        if format in self.FORMAT_BINDINGS:
            format = self.FORMAT_BINDINGS[format]
        codecs = tuple(s['codec_name'] for s in data['streams'])

        props = {}
        if data['streams'][0]['codec_type'] == 'video':
            props.update(width=data['streams'][0]['width'],
                         height=data['streams'][0]['height'])

        if format == 'image2':
            assert len(codecs) == 1
            return self.IMAGE, codecs[0], props

        if format in self.HTML5_AV_FORMATS \
                and codecs in self.HTML5_AV_FORMATS[format]:
            props['duration'] = int(float(data['format']['duration']))
            if len(codecs) == 1:
                return self.AUDIO, format, props
            elif len(codecs) == 2:
                return self.VIDEO, format, props

    def update_media_info(self):
        if getattr(self, 'updated_media_info', False):
            return
        data = self.get_media_info()
        if data is None:
            self.type = self.OTHER
        else:
            self.type, self.format, props = data
            for k, v in props.items():
                setattr(self, k, v)
        self.updated_media_info = True

    def update_extract_from(self):
        fichier_complet = self.get_fichier_complet()
        if fichier_complet is not None:
            fichier_complet.extract = self
            fichier_complet.save()

    def save(self, *args, **kwargs):
        self.update_media_info()
        super(Fichier, self).save(*args, **kwargs)
        self.update_extract_from()


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
            setattr(obj, field_name, sanitize_html(v.strip()))
    # Then we call the specific whitespace handler of the model (if it exists).
    if hasattr(obj, 'handle_whitespaces'):
        obj.handle_whitespaces()
