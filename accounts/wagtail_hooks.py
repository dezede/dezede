from django import forms
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.views.account import BaseSettingsPanel
from wagtail.admin.viewsets.chooser import ChooserViewSet
from .models import HierarchicUser


class HierarchicUserChooserViewSet(ChooserViewSet):
    model = HierarchicUser


@hooks.register("register_admin_viewset")
def register_user_chooser_viewset():
    return HierarchicUserChooserViewSet("hierarchicuser_chooser")


class UsernameForm(forms.ModelForm):
    username = forms.CharField(required=True, label=_("Nom d'utilisateur"))

    class Meta:
        model = HierarchicUser
        fields = ['username']


class UsernameSettingsPanel(BaseSettingsPanel):
    name = 'username'
    order = 90
    title = _("Nom d'utilisateur")
    form_class = UsernameForm


@hooks.register("register_account_settings_panel")
def register_username_settings_panel(request, user, profile):
    return UsernameSettingsPanel(request, user, profile)
