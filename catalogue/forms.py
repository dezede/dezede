# coding: utf-8

from django.forms import ModelForm, Form, CharField
from .models import Source
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Fieldset
from crispy_forms.bootstrap import FormActions
from django.utils.translation import ugettext_lazy as _
from ajax_select.fields import AutoCompleteSelectMultipleField
from ajax_select import make_ajax_field


class SourceForm(ModelForm):
    class Meta:
        model = Source

    nom = make_ajax_field(Source, 'nom', 'source')


class EvenementListForm(Form):
    q = CharField(label=_('Recherche libre'), required=False)
    lieu = AutoCompleteSelectMultipleField('lieu', label=_('Lieu'),
                                           required=False, help_text='')
    oeuvre = AutoCompleteSelectMultipleField('oeuvre', required=False,
                                             label=_(u'Œuvre'), help_text='')

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_class = 'well'
        self.helper.layout = Layout(
            Fieldset(
                _('Filtres'),
                Field('q', 'lieu', 'oeuvre', css_class='span12'),
            ),
            FormActions(
                Submit('', _('Filtrer'), css_class='btn-primary span12'),
            ),
        )
        super(EvenementListForm, self).__init__(*args, **kwargs)
        for key in ('q', 'lieu', 'oeuvre'):
            self.fields[key].widget.attrs['placeholder'] = _(u'Tapez ici…')
