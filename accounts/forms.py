# coding: utf-8

from django.forms import CharField, ModelChoiceField, ModelMultipleChoiceField
from django.forms.widgets import CheckboxSelectMultiple
# FIXME: Remplacer ceci par RegistrationFormUniqueEmail quand Joann aura fini
# de faire mumuse.
from registration.forms import RegistrationForm
from django.utils.translation import ugettext_lazy as _
from .models import StudentProfile
from django.contrib.auth.models import User, Group
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Reset, Fieldset
from crispy_forms.bootstrap import PrependedText, FormActions
from django.contrib.sites.models import get_current_site
from django.template.loader import render_to_string



def get_professors():
    return User.objects.filter(is_superuser=True)


def get_groups():
    return Group.objects.all()


class UserField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or unicode(obj)


class UserRegistrationForm(RegistrationForm):
    first_name = CharField(label=_(u'Prénom(s)'))
    last_name = CharField(label=_('Nom'))
    professor = UserField(queryset=get_professors(), label=_('Professeur'))
    groups = ModelMultipleChoiceField(queryset=get_groups(),
                             widget=CheckboxSelectMultiple, label=_('Groupes'))

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            Fieldset(
                _(u'Général'),
                Field('first_name', 'last_name', css_class='input-xlarge'),
                PrependedText('email', '<i class="icon-envelope"></i>', active=True),
            ),
            Fieldset(
                _('Utilisateur'),
                PrependedText('username', '<i class="icon-user"></i>', active=True),
                'password1', 'password2',
            ),
            Fieldset(
                _(u'Étudiant'),
                'professor',
                'groups',
            ),
            FormActions(
                Submit('save_changes', _('Enregistrer'), css_class="btn-primary"),
                Reset('reset', _(u'Réinitialiser')),
            ),
        )
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

    def save(self, request, user):
        data = self.cleaned_data

        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.groups = data['groups']
        user.save()

        professor = data['professor']
        profile = StudentProfile.objects.create(
            user=user,
            professor=professor)
        profile.save()

        site_url = 'http://' + get_current_site(request).domain
        email_content = render_to_string(
            'accounts/grant_to_admin_demand_email.txt',
            {'user': user, 'site_url': site_url})
        professor.email_user(_(u'Demande d’accès étudiant'),
            email_content)
