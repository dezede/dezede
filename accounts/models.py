# coding: utf-8

from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxLengthValidator
from django.db.models import BooleanField, permalink, TextField, URLField, \
    CharField, ForeignKey, PositiveIntegerField, get_models
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.translation import ungettext_lazy
from filebrowser.fields import FileBrowseField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from cache_tools import cached_ugettext_lazy as _
from libretto.models.common import AutoriteModel, CommonTreeManager
from libretto.models.functions import href


class HierarchicUserManager(CommonTreeManager, UserManager):
    pass


def _is_polymorphic_child(models, model):
    return (getattr(model, 'polymorphic_model_marker', False)
            and set(model.__bases__) & models)


def _get_valid_modelnames():
    models = frozenset(get_models())
    return [model.__name__.lower() for model in models
            if hasattr(model, 'link') and AutoriteModel in model.__bases__
            and not _is_polymorphic_child(models, model)]


@python_2_unicode_compatible
class HierarchicUser(MPTTModel, AbstractUser):
    show_email = BooleanField(_('afficher l’email'), default=False)
    website = URLField(_('site internet'), blank=True)
    website_verbose = CharField(
        _('nom affiché du site internet'), max_length=50, blank=True)

    legal_person = BooleanField(
        _('personne morale'), default=False,
        help_text=_('Cochez si vous êtes une institution ou un ensemble.'))
    content_type = ForeignKey(
        ContentType, blank=True, null=True,
        limit_choices_to={'model__in': _get_valid_modelnames},
        verbose_name=_('type d’autorité associée'))
    object_id = PositiveIntegerField(_('identifiant de l’autorité associée'),
                                     blank=True, null=True)
    content_object = GenericForeignKey()

    mentor = TreeForeignKey(
        'self', null=True, blank=True, related_name='disciples',
        verbose_name=_('mentor'),
        limit_choices_to={'willing_to_be_mentor__exact': True})
    willing_to_be_mentor = BooleanField(
        _('Veut être mentor'), default=False)

    avatar = FileBrowseField(_('avatar'), max_length=400, directory='avatars/',
                             blank=True, null=True)

    presentation = TextField(
        _('présentation'), blank=True, validators=[MaxLengthValidator(1000)])
    fonctions = TextField(_('fonctions au sein de l’équipe'), blank=True,
                          validators=[MaxLengthValidator(200)])
    literature = TextField(_('publications'), blank=True)

    objects = HierarchicUserManager()

    class MPTTMeta(object):
        parent_attr = 'mentor'
        order_insertion_by = ('last_name', 'first_name', 'username')

    class Meta(object):
        verbose_name = ungettext_lazy('utilisateur', 'utilisateurs', 1)
        verbose_name_plural = ungettext_lazy('utilisateur', 'utilisateurs', 2)

    def __str__(self):
        return self.get_full_name() or self.get_username()

    def link(self):
        return href(self.get_absolute_url(), smart_text(self))

    def html(self):
        return self.link()

    @permalink
    def get_absolute_url(self):
        return 'user_profile', (self.username,)

    def website_link(self):
        return href(self.website, self.website_verbose or self.website)

    def email_link(self):
        return href('mailto:' + self.email, self.email)

    def dossiersdevenements_roots(self):
        return self.dossierdevenements.exclude(parent__owner=self)
