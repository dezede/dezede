from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin
from tinymce.widgets import TinyMCE

from libretto.admin import CommonAdmin
from .models import HierarchicUser


class HierarchicUserCreationForm(UserCreationForm):
    class Meta(object):
        model = HierarchicUser
        fields = ('username',)

    def clean_username(self):
        # Taken from the overriden method.
        username = self.cleaned_data["username"]
        try:
            self._meta.model._default_manager.get(username=username)
        except self._meta.model.DoesNotExist:
            return username
        raise ValidationError(self.error_messages['duplicate_username'])


class HierarchicUserChangeForm(UserChangeForm):
    class Meta(object):
        model = HierarchicUser
        exclude = ()
        widgets = {
            'presentation': TinyMCE,
            'fonctions': TinyMCE,
            'literature': TinyMCE,
        }


@register(HierarchicUser)
class HierarchicUserAdmin(VersionAdmin, CommonAdmin, UserAdmin):
    add_form = HierarchicUserCreationForm
    form = HierarchicUserChangeForm
    list_display = ('__str__',) + UserAdmin.list_display + (
        'mentor', 'willing_to_be_mentor', 'is_active')
    list_editable = ('first_name', 'last_name', 'mentor',
                     'willing_to_be_mentor', 'is_active')
    list_filter = ('mentor', 'willing_to_be_mentor') + UserAdmin.list_filter
    additional_fields = ()
    additional_readonly_fields = ()
    additional_list_display = ()
    additional_list_filters = ()
    related_lookup_fields = {
        'generic': [['content_type', 'object_id'],],
    }
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Informations personnelles'), {'fields': (
            ('first_name', 'last_name'),
            ('email', 'show_email'),
            ('website', 'website_verbose'),
            'legal_person')}),
        (_('Autorité associée'), {
            'classes': ('grp-collapse grp-closed',),
            'description': _('À saisir s’il existe une autorité sur vous '
                             'dans la base de données.'),
            'fields': (('content_type', 'object_id'),)}),
        (_('Responsabilité scientifique'), {
            'fields': (('mentor', 'willing_to_be_mentor'),)}),
        (_('Informations complémentaires'), {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('avatar', 'presentation', 'fonctions', 'literature',)}),
        (_('Permissions'), {'fields': ('is_active',
                                       ('is_staff', 'is_superuser'),
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    ordering = HierarchicUser._meta.ordering
