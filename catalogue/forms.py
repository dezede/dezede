# coding: utf-8

from django.forms import ModelForm, Form, CharField, ModelChoiceField
from mptt.forms import TreeNodeChoiceField
from .models import Source, Lieu, Oeuvre
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Reset, Fieldset
from crispy_forms.bootstrap import FormActions
from django.utils.translation import ugettext_lazy as _


class SourceForm(ModelForm):
    class Meta:
        model = Source


class EvenementListForm(Form):
    q = CharField(label=_('Recherche libre'), required=False)
    lieu = TreeNodeChoiceField(queryset=Lieu.objects.all(), label=_('Lieu'),
                               to_field_name='slug', required=False)
    oeuvre = ModelChoiceField(queryset=Oeuvre.objects.all(), required=False,
                                 label=_(u'Œuvre'), to_field_name='slug')

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_class = 'well well-small'
        self.helper.layout = Layout(
            Fieldset(
                _('Filtres'),
                Field('q', 'lieu', 'oeuvre'),
            ),
            FormActions(
                Submit('', _('Filtrer'),
                       css_class="btn-primary"),
                Reset('', _(u'Réinitialiser')),
            ),
        )
        super(EvenementListForm, self).__init__(*args, **kwargs)
        self.fields['q'].widget.attrs['placeholder'] = _(u'Tapez ici…')
