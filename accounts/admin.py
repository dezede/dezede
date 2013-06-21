# coding: utf-8

from __future__ import unicode_literals
from django.contrib.admin import site
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from cache_tools.utils import cached_ugettext_lazy as _
from .models import HierarchicUser


class HierarchicUserChangeForm(UserChangeForm):
    class Meta(object):
        model = HierarchicUser


class HierarchicUserAdmin(UserAdmin):
    form = HierarchicUserChangeForm
    list_display = ('__str__',) + UserAdmin.list_display + (
        'mentor', 'willing_to_be_mentor', 'is_active')
    list_editable = ('first_name', 'last_name', 'mentor',
                     'willing_to_be_mentor', 'is_active')
    list_filter = ('mentor', 'willing_to_be_mentor') + UserAdmin.list_filter
    fieldsets = UserAdmin.fieldsets[:2] + (
        (_('Mentorat'), {'fields': ('mentor', 'willing_to_be_mentor')}),
    ) + UserAdmin.fieldsets[2:]
    ordering = ('last_name', 'first_name')


site.register(HierarchicUser, HierarchicUserAdmin)
