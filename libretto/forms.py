# coding: utf-8

from __future__ import unicode_literals
from collections import defaultdict
from ajax_select.fields import AutoCompleteSelectMultipleField, \
    AutoCompleteWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from datetime import timedelta
from django.db.models import Q
from django.forms import ValidationError, ModelForm, Form, CharField, TextInput
from django.utils.translation import ugettext_lazy as _
from .models import (
    Oeuvre, Source, Individu, ElementDeProgramme, ElementDeDistribution,
    Ensemble, Saison)
from range_slider.fields import RangeSliderField


__all__ = (b'IndividuForm', b'EnsembleForm', b'OeuvreForm',
           b'ElementDeDistributionForm', b'ElementDeProgrammeForm',
           b'SourceForm', b'SaisonForm', b'EvenementListForm')


class IndividuForm(ModelForm):
    class Meta(object):
        model = Individu
        widgets = {
            b'prenoms':
                AutoCompleteWidget('individu__prenoms',
                                   attrs={'style': 'width: 300px;'})
        }

    def __init__(self, *args, **kwargs):
        super(IndividuForm, self).__init__(*args, **kwargs)

        def apply_style(fieldname, style):
            self.fields[fieldname].widget.attrs['style'] = style

        apply_style('particule_nom', 'width: 50px;')
        apply_style('particule_nom_naissance', 'width: 50px;')

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
            b'coupe': AutoCompleteWidget('oeuvre__coupe',
                                         attrs={'style': 'width: 500px;'}),
        }


class ElementDeDistributionForm(ModelForm):
    class Meta(object):
        model = ElementDeDistribution

    def clean(self):
        data = super(ElementDeDistributionForm, self).clean()

        error_msgs = defaultdict(list)
        if not (data[b'individus'] or data[b'ensembles']):
            msg = _('Vous devez remplir au moins un individu ou un ensemble.')
            error_msgs[b'individus'].append(msg)
            error_msgs[b'ensembles'].append(msg)
        if data.get(b'pupitre') and data.get(b'profession'):
            msg = _('Vous ne pouvez remplir à la fois '
                    '« Pupitre » et « Profession ».')
            error_msgs[b'pupitre'].append(msg)
            error_msgs[b'profession'].append(msg)
        if data.get(b'pupitre', '') != '' \
                and data.get(b'profession') \
                and data[b'profession'].parties.exists():
            msg = _('Au moins un rôle ou instrument est lié à cette '
                    'profession. Remplissez donc « Pupitre » à la place.')
            error_msgs[b'profession'].append(msg)

        for k, v in error_msgs.items():
            self._errors[k] = self.error_class(v)
            del data[k]

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
            b'titre': AutoCompleteWidget('source__titre',
                                         attrs={'style': 'width: 600px;'}),
            b'numero': TextInput(attrs={'cols': 10}),
            b'folio': TextInput(attrs={'cols': 10}),
            b'page': TextInput(attrs={'cols': 10}),
        }

    def clean(self):
        data = super(SourceForm, self).clean()

        if not (data['titre'] or (data['lieu_conservation'] and data['cote'])):
            raise ValidationError(_('Vous devez remplir « Titre » ou '
                                    '« Lieu de conservation » et « Cote ».'))

        return data


class SaisonForm(ModelForm):
    class Meta(object):
        model = Source

    def clean(self):
        data = super(SaisonForm, self).clean()

        debut = data.get('debut')
        fin = data.get('fin')
        ensemble = data.get('ensemble')
        lieu = data.get('lieu')

        if not ((ensemble is None) ^ (lieu is None)):
            raise ValidationError(
                _('Vous devez remplir « Ensemble » '
                  'ou « Lieu ou Institution »'))

        if debut and fin:
            if debut > fin:
                raise ValidationError(_('La fin ne peut précéder le début.'))
            elif fin - debut > timedelta(365):
                raise ValidationError(_('La durée d’une saison ne peut excéder '
                                        'un an.'))

        overlapping_seasons = Saison.objects.filter(
            Q(debut__range=(debut, fin)) | Q(fin__range=(debut, fin))
            | Q(debut__lt=debut, fin__gt=fin),
            ensemble=ensemble, lieu=lieu)
        if overlapping_seasons.exists():
            raise ValidationError(
                _('Une saison existe déjà sur cette période pour « %s ».')
                % (ensemble or lieu))
        return data


class EvenementListForm(Form):
    q = CharField(label=_('Recherche libre'), required=False)
    dates = RangeSliderField(required=False)
    lieu = AutoCompleteSelectMultipleField('lieu', label=_('Lieu'),
                                           required=False, help_text='')
    oeuvre = AutoCompleteSelectMultipleField(
        'oeuvre', required=False, label=_('Œuvre'), help_text='')
    individu = AutoCompleteSelectMultipleField(
        'individu', required=False, label=_('Individu'), help_text='')
    ensemble = AutoCompleteSelectMultipleField(
        'ensemble', required=False, label=_('Ensemble'), help_text='')

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset')

        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_class = 'well well-sm'
        self.helper.layout = Layout(
            Field('q', css_class='input-lg'),
            HTML('<hr/>'),
            'dates',
            HTML('<hr/>'),
            'lieu', 'oeuvre', 'individu', 'ensemble',
            HTML('<hr/>'),
            Submit('', _('Filtrer'), css_class='btn-lg btn-block',
                   data_loading_text=_('Chargement…')),
        )

        super(EvenementListForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs[b'placeholder'] = (field.label or '') + '…'
            field.label = ''

        self.fields['dates'].widget.queryset = queryset
