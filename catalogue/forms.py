# coding: utf-8

from django.forms import ModelForm, Form, CharField, TextInput, MultiValueField, SplitDateTimeWidget, SplitDateTimeField
from .models import Oeuvre, Source
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from django.utils.translation import ugettext_lazy as _
from ajax_select.fields import AutoCompleteSelectMultipleField, \
                               AutoCompleteWidget
from .fields import RangeSliderField


class OeuvreForm(ModelForm):
    class Meta:
        model = Oeuvre
        widgets = {
            'prefixe_titre': AutoCompleteWidget('oeuvre__prefixe_titre',
                                            attrs={'style': 'width: 50px;'}),
            'coordination': AutoCompleteWidget('oeuvre__coordination',
                                            attrs={'style': 'width: 70px;'}),

            'prefixe_titre_secondaire': AutoCompleteWidget(
                                         'oeuvre__prefixe_titre_secondaire',
                                         attrs={'style': 'width: 50px;'}),

        }


class SourceForm(ModelForm):
    class Meta:
        model = Source
        widgets = {
            'nom': AutoCompleteWidget('source__nom', attrs={'style': 'width: 600px;'}),
            'numero': TextInput(attrs={'cols': 10}),
            'page': TextInput(attrs={'cols': 10}),
        }


class EvenementListForm(Form):
    q = CharField(label=_('Recherche libre'), required=False)
    dates = RangeSliderField(required=False)
    lieu = AutoCompleteSelectMultipleField('lieu', label=_('Lieu'),
                                           required=False, help_text='')
    oeuvre = AutoCompleteSelectMultipleField('oeuvre', required=False,
                                             label=_(u'Œuvre'), help_text='')

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_class = 'well well-small'
        self.helper.layout = Layout(
            Field('q', 'dates', HTML('<hr/>'), 'lieu', 'oeuvre',
                  css_class='span12'),
            HTML('<hr/>'),
            Submit('', _('Filtrer'), css_class='btn-primary span12'),
        )
        super(EvenementListForm, self).__init__(*args, **kwargs)
        for field in self.fields.itervalues():
            field.widget.attrs['placeholder'] = (field.label or '') + '...'
            field.label = ''
