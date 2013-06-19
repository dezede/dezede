# coding: utf-8

from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import BooleanField
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ungettext_lazy
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from cache_tools import cached_ugettext_lazy as _


class HierarchicUserManager(TreeManager, UserManager):
    pass


@python_2_unicode_compatible
class HierarchicUser(MPTTModel, AbstractUser):
    mentor = TreeForeignKey(
        'self', null=True, blank=True, related_name='disciples',
        verbose_name=_('mentor'),
        limit_choices_to={'willing_to_be_mentor__exact': True})
    willing_to_be_mentor = BooleanField(
        _('Veut être mentor'), default=False)

    objects = HierarchicUserManager()

    class MPTTMeta(object):
        parent_attr = 'mentor'
        order_insertion_by = ('username',)

    class Meta(object):
        verbose_name = ungettext_lazy('utilisateur', 'utilisateurs', 1)
        verbose_name_plural = ungettext_lazy('utilisateur', 'utilisateurs', 2)

    def __str__(self):
        return self.get_full_name() or self.get_username()
