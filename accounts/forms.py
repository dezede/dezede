from crispy_forms.bootstrap import PrependedText, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Reset, Fieldset, HTML
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.forms import (
    Form, CharField, ModelMultipleChoiceField, BooleanField)
from django.forms.widgets import CheckboxSelectMultiple, HiddenInput
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from tree.forms import TreeChoiceField


def get_mentors():
    return get_user_model().objects.filter(willing_to_be_mentor=True)


def get_groups():
    return Group.objects.all()


class HierarchicUserSignupForm(Form):
    first_name = CharField(label=_('Prénom(s)'))
    last_name = CharField(label=_('Nom'))
    mentor = TreeChoiceField(queryset=get_mentors(), label=_('Responsable'))
    willing_to_be_mentor = BooleanField(
        required=False, label=_('Souhaite devenir responsable scientifique'))
    groups = ModelMultipleChoiceField(
        queryset=get_groups(), widget=CheckboxSelectMultiple,
        label=_('Groupes'))
    next = CharField(widget=HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'account_signup'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8'
        self.helper.layout = Layout(
            Field('first_name', 'last_name'),
            PrependedText('email',
                          '<i class="fa fa-envelope-o fa-fw"></i>'),
            PrependedText('username', '<i class="fa fa-user fa-fw"></i>'),
            PrependedText('password1', '<i class="fa fa-key fa-fw"></i>'),
            PrependedText('password2', '<i class="fa fa-key fa-fw"></i>'),
            Fieldset(
                _('Responsable scientifique'),
                'mentor',
                Field('willing_to_be_mentor'),
                'groups',
            ),
            Field('next'),
            FormActions(
                Submit('save_changes', _('Enregistrer')),
                Reset('reset', _('Réinitialiser'), css_class='btn-default'),
                css_class='row',
            ),
        )
        super(HierarchicUserSignupForm, self).__init__(*args, **kwargs)

    def signup(self, request, user):
        site_url = 'https://' + Site.objects.get_current(request).domain
        email_content = render_to_string(
            'accounts/grant_to_admin_demand_email.txt',
            {'user': user, 'site_url': site_url, 'mentor': user.mentor})
        user.mentor.email_user(
            _('Demande de responsabilité scientifique'),
            email_content)


from allauth.account.forms import LoginForm as OriginalLoginForm


class LoginForm(OriginalLoginForm):
    next = CharField(widget=HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_action = 'account_login'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-8'

        self.helper.layout = Layout(
            PrependedText('login', '<i class="fa fa-user fa-fw"></i>'),
            PrependedText('password', '<i class="fa fa-key fa-fw"></i>'),
            Field('next'),
            FormActions(
                Submit('submit', _('Sign In')),
                HTML('{% load i18n %}'
                     '<a class="btn btn-link" '
                     'href="{% url "account_reset_password" %}">'
                     '{% trans "Forgot Password?" %}</a>'),
                css_class='row',
            ),
        )

        super(LoginForm, self).__init__(*args, **kwargs)
