# coding: utf-8

from django.db.models import Model, Manager, CharField, SlugField, \
                             BooleanField, ManyToManyField
from django.db.models.query import QuerySet
from tinymce.models import HTMLField
from django.template.defaultfilters import slugify
from filebrowser.fields import FileBrowseField
from ..templatetags.extras import replace
from django.utils.translation import ungettext_lazy, ugettext_lazy as _

#
# Définitions globales du fichier
#

LOWER_MSG = _(u'En minuscules.')
PLURAL_MSG = _(u'''À remplir si le pluriel n'est pas un simple '''
               u'''ajout de « s ». Exemple : « animal » devient « animaux » '''
               u'''et non « animals ».''')
DATE_MSG = _(u'Ex. : « 6/6/1944 » pour le 6 juin 1944.')
# Champs dans lesquels effectuer les remplacements typographiques.
REPLACE_FIELDS = (CharField, HTMLField,)


def replace_in_kwargs(obj, **kwargs):
    u'''
    Renvoie kwargs avec remplacements typographiques.

    Si une clé de kwargs est un nom de champ d'obj
    et que la classe de ce champ est dans REPLACE_FIELDS,
    effectue les remplacements dans la valeur du kwarg.
    '''
    fields = obj._meta.fields
    keys = (field.attname for field in fields
                          if field.__class__ in REPLACE_FIELDS)
    for key in keys:
        if key in kwargs:
            kwargs[key] = replace(kwargs[key])
    return kwargs


def autoslugify(obj, nom):
    u'''
    Crée automatiquement un slug à partir de nom
    et des objets de la classe d'obj.
    Si le slug est déjà pris par un autre objet, rajoute un nombre à la suite.
    '''
    nom_slug = slug_orig = slugify(nom[:50])
    n = 0
    objects = obj.__class__.objects
    while objects.filter(slug=nom_slug).exists() and nom_slug != obj.slug:
        n += 1
        nom_slug = slug_orig + str(n)
    return nom_slug


def calc_pluriel(obj):
    '''
    Renvoie le nom au pluriel d'obj, si possible.
    Sinon renvoie unicode(obj).
    '''
    try:
        if obj.nom_pluriel:
            return obj.nom_pluriel
        return obj.nom + 's'
    except:
        return unicode(obj)


#
# Modélisation
#

class CustomQuerySet(QuerySet):
    '''
    QuerySet personnalisé pour chercher
    des objets avec remplacements typographiques.
    '''
    def get(self, *args, **kwargs):
        kwargs = replace_in_kwargs(self.model, **kwargs)
        return super(CustomQuerySet, self).get(*args, **kwargs)


class CustomManager(Manager):
    '''
    Manager personnalisé pour utiliser CustomQuerySet par défaut.
    '''
    def get_query_set(self):
        return CustomQuerySet(self.model, using=self._db)


class CustomModel(Model):
    '''
    Modèle personnalisé, essentiellement pour les remplacements typographiques.
    '''
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
    def meta(self):
        return self._meta

SlugField.unique = True


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
    # FIXME: publie -> public
    publie = BooleanField(_(u'publié'), default=True)
    slug = SlugField(blank=True)

    class Meta:
        verbose_name = ungettext_lazy(u'état', u'états', 1)
        verbose_name_plural = ungettext_lazy(u'état', u'états', 2)
        ordering = ['slug']
        app_label = 'catalogue'

    def save(self, *args, **kwargs):
        self.slug = autoslugify(self, unicode(self))
        super(Etat, self).save(*args, **kwargs)

    def pluriel(self):
        return calc_pluriel(self)

    def __unicode__(self):
        return self.nom
