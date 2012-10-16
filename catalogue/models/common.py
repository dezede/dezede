# coding: utf-8

from django.db.models import Model, Manager, CharField, \
                             BooleanField, ManyToManyField, ForeignKey
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from filebrowser.fields import FileBrowseField
from ..templatetags.extras import replace
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from autoslug import AutoSlugField
from .functions import href

#
# Définitions globales du fichier
#

LOWER_MSG = _(u'En minuscules.')
PLURAL_MSG = _(u'À remplir si le pluriel n’est pas un simple '
               u'ajout de « s ». Exemple : « animal » devient « animaux » '
               u'et non « animals ».')
DATE_MSG = _(u'Exemple : « 6/6/1944 » pour le 6 juin 1944.')
# Champs dans lesquels effectuer les remplacements typographiques.
REPLACE_FIELDS = (CharField, HTMLField,)


def replace_in_kwargs(obj, **kwargs):
    u"""
    Renvoie kwargs avec remplacements typographiques.

    Si une clé de kwargs est un nom de champ d'obj
    et que la classe de ce champ est dans REPLACE_FIELDS,
    effectue les remplacements dans la valeur du kwarg.
    """
    fields = obj._meta.fields
    keys = (field.attname for field in fields
                          if field.__class__ in REPLACE_FIELDS)
    for key in keys:
        if key in kwargs:
            kwargs[key] = replace(kwargs[key])
    return kwargs


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

class CustomQuerySet(QuerySet):
    """
    QuerySet personnalisé pour chercher
    des objets avec remplacements typographiques.
    """
    def get(self, *args, **kwargs):
        kwargs = replace_in_kwargs(self.model, **kwargs)
        return super(CustomQuerySet, self).get(*args, **kwargs)


class CustomManager(Manager):
    """
    Manager personnalisé pour utiliser CustomQuerySet par défaut.
    """
    def get_query_set(self):
        return CustomQuerySet(self.model, using=self._db)


class CustomModel(Model):
    """
    Modèle personnalisé, essentiellement pour les remplacements typographiques.
    """
    owner = ForeignKey(User, null=True, blank=True,
                                               verbose_name=_('transcripteur'))
    objects = CustomManager()

    class Meta:
        abstract = True  # = prototype de modèle, et non un vrai modèle.

    def __init__(self, *args, **kwargs):
        kwargs = replace_in_kwargs(self, **kwargs)
        super(CustomModel, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.__dict__ = replace_in_kwargs(self, **self.__dict__)
        super(CustomModel, self).save(*args, **kwargs)

    @classmethod
    def class_name(cls):
        return unicode(cls.__name__)

    @classmethod
    def meta(cls):
        return cls._meta

    def related_label(self):
        return unicode(self)


class AutoriteManager(CustomManager):
    def published(self):
        return self.get_query_set().filter(etat__public=True)


class AutoriteModel(CustomModel):
    etat = ForeignKey('Etat', null=True, blank=True, verbose_name=_(u'état'))
    documents = ManyToManyField('Document', blank=True, null=True)
    illustrations = ManyToManyField('Illustration', blank=True, null=True)
    notes = HTMLField(blank=True)
    objects = AutoriteManager()

    class Meta:
        abstract = True


class SlugModel(Model):
    slug = AutoSlugField(populate_from=lambda o: o.get_slug())

    class Meta:
        abstract = True

    def get_slug(self):
        return unicode(self)


class UniqueSlugModel(Model):
   slug = AutoSlugField(populate_from=lambda o: o.get_slug(), unique=True)

   class Meta:
       abstract = True

   def get_slug(self):
       return unicode(self)


class Document(CustomModel):
    nom = CharField(_('nom'), max_length=300, blank=True)
    document = FileBrowseField(_('document'), max_length=400,
        directory='documents/')
    description = HTMLField(_('description'), blank=True)
    auteurs = ManyToManyField('Auteur', related_name='documents', blank=True,
        null=True, verbose_name=_('auteurs'))

    class Meta:
        verbose_name = ungettext_lazy('document', 'documents', 1)
        verbose_name_plural = ungettext_lazy('document', 'documents', 2)
        ordering = ['document']
        app_label = 'catalogue'

    def __unicode__(self):
        if self.nom:
            return self.nom
        return unicode(self.document)

    @staticmethod
    def autocomplete_search_fields():
        return ('nom__icontains', 'document__icontains',
                'description__icontains', 'auteurs__individus__nom',)


class Illustration(CustomModel):
    legende = CharField(_(u'légende'), max_length=300, blank=True)
    image = FileBrowseField(_('image'), max_length=400, directory='images/')
    commentaire = HTMLField(_('commentaire'), blank=True)
    auteurs = ManyToManyField('Auteur', related_name='illustrations',
        blank=True, null=True, verbose_name=_('auteurs'))

    class Meta:
        verbose_name = ungettext_lazy('illustration', 'illustrations', 1)
        verbose_name_plural = ungettext_lazy('illustration',
                                             'illustrations', 2)
        ordering = ['image']
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
                'commentaire__icontains', 'auteurs__individus__nom',)


class Etat(CustomModel):
    nom = CharField(_('nom'), max_length=200, help_text=LOWER_MSG, unique=True)
    nom_pluriel = CharField(_('nom (au pluriel)'), max_length=230, blank=True,
        help_text=PLURAL_MSG)
    message = HTMLField(_('message'), blank=True,
        help_text=_(u'Message à afficher dans la partie consultation.'))
    public = BooleanField(_(u'publié'), default=True)
    slug = AutoSlugField(populate_from='nom')

    class Meta:
        verbose_name = ungettext_lazy(u'état', u'états', 1)
        verbose_name_plural = ungettext_lazy(u'état', u'états', 2)
        ordering = ['slug']
        app_label = 'catalogue'

    def pluriel(self):
        return calc_pluriel(self)

    def __unicode__(self):
        return self.nom
