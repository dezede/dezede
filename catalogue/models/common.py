# coding: utf-8

from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericRelation
from django.db.models import Model, CharField, BooleanField, ManyToManyField, \
    ForeignKey
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from autoslug import AutoSlugField
from filebrowser.fields import FileBrowseField
from tinymce.models import HTMLField
from .functions import href
from typography.models import TypographicModel, TypographicManager, \
    TypographicQuerySet


__all__ = (b'LOWER_MSG', b'PLURAL_MSG', b'DATE_MSG', b'calc_pluriel',
           b'AutoriteModel', b'SlugModel', b'UniqueSlugModel', b'Document',
           b'Illustration', b'Etat')


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
    Sinon renvoie unicode(obj).
    """
    try:
        pluriel = getattr(obj, attr_base + attr_suffix)
        if pluriel:
            return pluriel
        return getattr(obj, attr_base) + 's'
    except (AttributeError, TypeError):
        return unicode(obj)


#
# Modélisation
#


class CommonQuerySet(TypographicQuerySet):
    pass


class CommonManager(TypographicManager):
    pass


class CommonModel(TypographicModel):
    """
    Modèle personnalisé, essentiellement pour les remplacements typographiques.
    """
    owner = ForeignKey(User, null=True, blank=True,
                       verbose_name=_('transcripteur'))
    objects = CommonManager()

    class Meta(object):
        abstract = True  # = prototype de modèle, et non un vrai modèle.

    @classmethod
    def class_name(cls):
        return unicode(cls.__name__)

    @classmethod
    def meta(cls):
        return cls._meta

    def related_label(self):
        return unicode(self)


class AutoriteQuerySet(CommonQuerySet):
    def published(self):
        return self.filter(etat__public=True)


class AutoriteManager(CommonManager):
    # TODO: Implement get_empty_query_set.
    def get_query_set(self):
        return AutoriteQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_query_set().published()


class AutoriteModel(CommonModel):
    etat = ForeignKey('Etat', null=True, blank=True, verbose_name=_('état'))
    documents = ManyToManyField('Document', blank=True, null=True)
    illustrations = ManyToManyField('Illustration', blank=True, null=True)
    notes = HTMLField(blank=True)
    objects = AutoriteManager()

    class Meta(object):
        abstract = True


class SlugModel(Model):
    slug = AutoSlugField(populate_from='get_slug', always_update=True)

    class Meta(object):
        abstract = True

    def get_slug(self):
        return unicode(self)


class UniqueSlugModel(Model):
    slug = AutoSlugField(populate_from='get_slug', unique=True,
                         always_update=True)

    class Meta(object):
        abstract = True

    def _perform_unique_checks(self, unique_checks):
        errors = super(UniqueSlugModel, self)._perform_unique_checks(
            unique_checks)
        for Model, unique_fields in unique_checks:
            qs = Model.objects.exclude(pk=self.pk)
            model_errors = []
            for field in unique_fields:
                if not qs.filter(
                        **{field + '__iexact': getattr(self, field)}).exists():
                    continue
                model_errors.append(field)
                error = self.unique_error_message(Model, model_errors)
                if error not in errors.get(field, ()):
                    errors.setdefault(field, []).append(error)
        return errors

    def get_slug(self):
        return unicode(self)


class Document(CommonModel):
    nom = CharField(_('nom'), max_length=300, blank=True)
    document = FileBrowseField(_('document'), max_length=400,
                               directory='documents/')
    description = HTMLField(_('description'), blank=True)
    auteurs = GenericRelation('Auteur')

    class Meta(object):
        verbose_name = ungettext_lazy('document', 'documents', 1)
        verbose_name_plural = ungettext_lazy('document', 'documents', 2)
        ordering = ('document',)
        app_label = 'catalogue'

    def __unicode__(self):
        if self.nom:
            return self.nom
        return unicode(self.document)

    def link(self):
        return href(self.document.url, unicode(self))

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'document__icontains',
                'description__icontains', 'auteurs__individu__nom',)


class Illustration(CommonModel):
    legende = CharField(_('légende'), max_length=300, blank=True)
    image = FileBrowseField(_('image'), max_length=400, directory='images/')
    commentaire = HTMLField(_('commentaire'), blank=True)
    GenericRelation('Auteur')

    class Meta(object):
        verbose_name = ungettext_lazy('illustration', 'illustrations', 1)
        verbose_name_plural = ungettext_lazy('illustration',
                                             'illustrations', 2)
        ordering = ('image',)
        app_label = 'catalogue'

    def __unicode__(self):
        if self.legende:
            return self.legende
        return unicode(self.image)

    def link(self):
        return href(self.image.url, unicode(self))

    @staticmethod
    def autocomplete_search_fields():
        return ('legende__icontains', 'image__icontains',
                'commentaire__icontains',)


class Etat(CommonModel):
    nom = CharField(_('nom'), max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
                            help_text=PLURAL_MSG)
    message = HTMLField(
        _('message'), blank=True,
        help_text=_('Message à afficher dans la partie consultation.'))
    public = BooleanField(_('publié'), default=True)
    slug = AutoSlugField(populate_from='nom')

    class Meta(object):
        verbose_name = ungettext_lazy('état', 'états', 1)
        verbose_name_plural = ungettext_lazy('état', 'états', 2)
        ordering = ('slug',)
        app_label = 'catalogue'

    def pluriel(self):
        return calc_pluriel(self)

    def __unicode__(self):
        return self.nom


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
