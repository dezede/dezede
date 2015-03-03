# coding: utf-8

from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxLengthValidator
from django.db.models import (
    BooleanField, permalink, TextField, URLField,
    CharField, ForeignKey, PositiveIntegerField, get_models, ImageField)
from django.db.models.signals import class_prepared
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ungettext_lazy, ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from libretto.models.base import AutoriteModel, CommonTreeManager, \
    CommonTreeQuerySet
from common.utils.html import href, sc
from common.utils.text import str_list_w_last


#
# Hack to monkey patch the user model
#


LAST_NAME_MAX_LENGTH = 75


@receiver(class_prepared)
def longer_last_name(sender, *args, **kwargs):
    if sender.__name__ == 'HierarchicUser' \
            and sender.__module__ == 'accounts.models':
        last_name = sender._meta.get_field('last_name')
        last_name.max_length = LAST_NAME_MAX_LENGTH
        assert len(last_name.validators) == 1
        last_name.validators = [MaxLengthValidator(LAST_NAME_MAX_LENGTH)]


#
# Regular modelisation
#


class HierarchicUserQuerySet(CommonTreeQuerySet):
    def html(self, tags=True):
        return str_list_w_last([u.html(tags=tags) for u in self])


class HierarchicUserManager(CommonTreeManager, UserManager):
    queryset_class = HierarchicUserQuerySet

    def html(self, tags=True):
        return self.get_queryset().html(tags=tags)


def _is_polymorphic_child(models, model):
    return (getattr(model, 'polymorphic_model_marker', False)
            and set(model.__bases__) & models)


def _get_valid_modelnames_func(autorites_only=True):
    def is_valid(models, model):
        b = hasattr(model, 'link') and not _is_polymorphic_child(models, model)
        if autorites_only:
            b &= AutoriteModel in model.__bases__
        return b

    def get_valid_modelnames():
        models = frozenset(get_models())
        return [model.__name__.lower() for model in models
                if is_valid(models, model)]
    return get_valid_modelnames


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
        limit_choices_to={'model__in': _get_valid_modelnames_func()},
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

    avatar = ImageField(_('avatar'), upload_to='avatars/',
                        blank=True, null=True)

    presentation = TextField(
        _('présentation'), blank=True, validators=[MaxLengthValidator(5000)])
    fonctions = TextField(_('fonctions au sein de l’équipe'), blank=True,
                          validators=[MaxLengthValidator(200)])
    literature = TextField(_('publications'), blank=True)

    objects = HierarchicUserManager()

    class MPTTMeta(object):
        parent_attr = 'mentor'
        order_insertion_by = ('last_name', 'first_name', 'username')

    class Meta(object):
        ordering = ('last_name', 'first_name')
        verbose_name = ungettext_lazy('utilisateur', 'utilisateurs', 1)
        verbose_name_plural = ungettext_lazy('utilisateur', 'utilisateurs', 2)

    def __str__(self, tags=False):
        return self.html(tags=False)

    def get_full_name(self, tags=False):
        full_name = '%s %s' % (self.first_name, sc(self.last_name, tags=tags))
        return full_name.strip()

    def html(self, tags=True):
        txt = self.get_full_name(tags=tags) or self.get_username()
        return href(self.get_absolute_url(), txt, tags=tags)

    def link(self, tags=True):
        return self.html(tags=tags)

    @permalink
    def get_absolute_url(self):
        return 'user_profile', (self.username,)

    def website_link(self):
        return href(self.website, self.website_verbose or self.website,
                    new_tab=True)

    def email_link(self):
        return href('mailto:' + self.email, self.email)

    def dossiersdevenements_roots(self):
        return self.dossierdevenements.exclude(parent__owner=self)

    @staticmethod
    def autocomplete_search_fields():
        return 'first_name__icontains', 'last_name__icontains'
