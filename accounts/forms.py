# coding: utf-8

from __future__ import unicode_literals
from crispy_forms.bootstrap import PrependedText, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Reset, Fieldset
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sites.models import get_current_site
from django.forms import CharField, ModelMultipleChoiceField, BooleanField
from django.forms.widgets import CheckboxSelectMultiple
from django.template.loader import render_to_string
from mptt.forms import TreeNodeChoiceField
# FIXME: Remplacer ceci par RegistrationFormUniqueEmail quand Joann aura fini
# de faire mumuse.
from registration.forms import RegistrationForm
from cache_tools import cached_ugettext_lazy as _


def get_mentors():
    return get_user_model().objects.filter(willing_to_be_mentor=True)


def get_groups():
    return Group.objects.all()


class UserRegistrationForm(RegistrationForm):
    first_name = CharField(label=_('Prénom(s)'))
    last_name = CharField(label=_('Nom'))
    mentor = TreeNodeChoiceField(queryset=get_mentors(), label=_('Mentor'))
    willing_to_be_mentor = BooleanField(
        required=False, label=_('Souhaite devenir mentor'))
    groups = ModelMultipleChoiceField(
        queryset=get_groups(), widget=CheckboxSelectMultiple,
        label=_('Groupes'))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8'
        self.helper.layout = Layout(
            Fieldset(
                _('Général'),
                Field('first_name', 'last_name'),
                PrependedText(
                    'email', '<i class="glyphicon glyphicon-envelope"></i>',
                    active=True),
                PrependedText(
                    'username', '<i class="glyphicon glyphicon-user"></i>',
                    active=True),
                'password1', 'password2',
            ),
            Fieldset(
                _('Mentorat'),
                'mentor',
                Field('willing_to_be_mentor', wrapper_class='col-sm-offset-2'),
                'groups',
            ),
            FormActions(
                Submit('save_changes', _('Enregistrer')),
                Reset('reset', _('Réinitialiser')),
            ),
        )
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

    def save(self, request, user):
        data = self.cleaned_data

        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.groups = data['groups']
        user.mentor = data['mentor']
        user.willing_to_be_mentor = data['willing_to_be_mentor']
        user.save()

        site_url = 'http://' + get_current_site(request).domain
        email_content = render_to_string(
            'accounts/grant_to_admin_demand_email.txt',
            {'user': user, 'site_url': site_url, 'mentor': user.mentor})
        user.mentor.email_user(_('[Dezède] Demande de mentorat'),
                               email_content)
