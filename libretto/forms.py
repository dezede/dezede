# coding: utf-8

from __future__ import unicode_literals
from django.forms import ValidationError, ModelForm, Form, CharField, TextInput
from ajax_select.fields import AutoCompleteSelectMultipleField, \
    AutoCompleteWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from cache_tools import cached_ugettext_lazy as _
from .models import (
    Oeuvre, Source, Individu, ElementDeProgramme, ElementDeDistribution,
    Ensemble)
from .fields import RangeSliderField


__all__ = (b'IndividuForm', b'EnsembleForm', b'OeuvreForm',
           b'ElementDeProgrammeForm', b'SourceForm', b'EvenementListForm')


class IndividuForm(ModelForm):
    class Meta(object):
        model = Individu

    def clean_designation(self):
        # Anticipe si la désignation donnera un résultat nul.
        data = self.cleaned_data
        designation = data[b'designation']
        if designation == 'P' and not data[b'pseudonyme'] \
            or designation == 'B' and not data[b'nom_naissance'] \
                or designation == 'F' and not data[b'prenoms']:
            raise ValidationError(_('Il manque des données pour pouvoir '
                                    'choisir cette désignation.'))
        return designation


class EnsembleForm(ModelForm):
    class Meta(object):
        model = Ensemble
        widgets = {
            b'particule_nom':
                AutoCompleteWidget('ensemble__particule_nom',
                                   attrs={'style': 'width: 50px;'})
        }


class OeuvreForm(ModelForm):
    class Meta(object):
        model = Oeuvre
        widgets = {
            b'prefixe_titre':
                AutoCompleteWidget('oeuvre__prefixe_titre',
                                   attrs={'style': 'width: 50px;'}),
            b'coordination':
                AutoCompleteWidget('oeuvre__coordination',
                                   attrs={'style': 'width: 70px;'}),
            b'prefixe_titre_secondaire':
                AutoCompleteWidget('oeuvre__prefixe_titre_secondaire',
                                   attrs={'style': 'width: 50px;'}),
        }


class ElementDeDistributionForm(ModelForm):
    class Meta(object):
        model = ElementDeDistribution

    def clean(self):
        # TODO: Dans les distributions non-globales, interdire la saisie d'une
        # profession si la partie est liée à une profession.  Par exemple,
        # pour un élément de programme donné, interdire de saisir :
        # « Monsieur Truc [violoniste] », car la profession est au moins liée à
        # « violon ».
        data = super(ElementDeDistributionForm, self).clean()
        if not (data[b'individus'] or data[b'ensembles']):
            msg = _('Vous devez remplir au moins un individu ou un ensemble.')
            self._errors[b'individus'] = self.error_class([msg])
            self._errors[b'ensembles'] = self.error_class([msg])
            del data[b'individus']
            del data[b'ensembles']
        if data.get(b'pupitre', None) and data[b'profession']:
            msg = _('Vous ne pouvez remplir à la fois '
                    '« Pupitre » et « Profession ».')
            self._errors[b'pupitre'] = self.error_class([msg])
            self._errors[b'profession'] = self.error_class([msg])
            del data[b'pupitre']
            del data[b'profession']
        return data


class ElementDeProgrammeForm(ModelForm):
    class Meta(object):
        model = ElementDeProgramme
        # FIXME: Rendre fonctionnel ce qui suit.
        # widgets = {
        #     b'autre': AutoCompleteWidget('elementdeprogramme__autre',
        #                                  attrs={'style': 'width: 600px;'}),
        # }

    def clean(self):
        data = super(ElementDeProgrammeForm, self).clean()

        if not (data[b'autre'] or data[b'oeuvre'] or data[b'distribution']):
            raise ValidationError(_('Vous devez remplir au moins « Œuvre », '
                                    '« Autre » ou « Distribution ».'))

        if data[b'autre'] and data[b'oeuvre']:
            raise ValidationError(_('Vous ne pouvez remplir à la fois '
                                    '« Œuvre » et « Autre ».'))

        return data


class SourceForm(ModelForm):
    class Meta(object):
        model = Source
        widgets = {
            b'nom': AutoCompleteWidget('source__nom',
                                       attrs={'style': 'width: 600px;'}),
            b'numero': TextInput(attrs={'cols': 10}),
            b'page': TextInput(attrs={'cols': 10}),
        }


class EvenementListForm(Form):
    q = CharField(label=_('Recherche libre'), required=False)
    dates = RangeSliderField(required=False)
    lieu = AutoCompleteSelectMultipleField('lieu', label=_('Lieu'),
                                           required=False, help_text='')
    oeuvre = AutoCompleteSelectMultipleField(
        'oeuvre', required=False, label=_('Œuvre'), help_text='')
    individu = AutoCompleteSelectMultipleField(
        'individu', required=False, label=_('Individu'), help_text='')

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset')

        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_class = 'well well-small'
        self.helper.layout = Layout(
            Field('q', 'dates', HTML('<hr/>'), 'lieu', 'oeuvre', 'individu',
                  css_class='span12'),
            HTML('<hr/>'),
            Submit('', _('Filtrer'), css_class='btn-primary btn-block'),
        )

        super(EvenementListForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs[b'placeholder'] = (field.label or '') + '...'
            field.label = ''

        self.fields['dates'].widget.queryset = queryset
