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
from common.utils.text import capfirst
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
    def clean(self):
        data = super(OeuvreForm, self).clean()

        type_extrait = data['type_extrait']
        type_extrait_affiche = (
            type_extrait and type_extrait not in Oeuvre.TYPES_EXTRAIT_CACHES)

        if not type_extrait_affiche and \
                not data['titre'] and not data['genre'] and not data['tempo']:
            msg = _('Un titre, un genre ou un tempo '
                    'doit au moins être précisé.')
            self._errors['titre'] = self.error_class([msg])
            self._errors['genre'] = self.error_class([msg])
            self._errors['tempo'] = self.error_class([msg])

        # Ensures title look like "Le Tartuffe, ou l’Imposteur.".
        data['prefixe_titre'] = capfirst(data['prefixe_titre'])
        data['titre'] = capfirst(data['titre'])
        data['prefixe_titre_secondaire'] = data['prefixe_titre_secondaire'].lower()
        data['titre_secondaire'] = capfirst(data['titre_secondaire'])

        if data['titre_secondaire'] and not data['titre']:
            self._errors['titre_secondaire'] = self.error_class([
                _('« Titre secondaire » ne peut être saisi sans « Titre ».')
            ])
        if data['titre_secondaire'] and not data['coordination']:
            self._errors['titre_secondaire'] = self.error_class([
                _('« Titre secondaire » ne peut être saisi '
                  'sans « Coordination ».')
            ])
        if data['coordination'] and not data['titre_secondaire']:
            self._errors['coordination'] = self.error_class([
                _('« Coordination » ne peut être saisi '
                  'sans « Titre secondaire ».')
            ])
        if data['prefixe_titre'] and not data['titre']:
            self._errors['prefixe_titre'] = self.error_class([
                _('« Article » ne peut être saisi sans « Titre ».')
            ])
        if data['prefixe_titre_secondaire'] and not data['titre_secondaire']:
            self._errors['prefixe_titre_secondaire'] = self.error_class([
                _('« Article » ne peut être saisi sans « Titre secondaire ».')
            ])

        if type_extrait or data['numero_extrait']:
            if data['titre']:
                self._errors['titre'] = self.error_class([
                    _('Impossible de saisir un titre significatif '
                      'pour un extrait.')
                ])
            if not type_extrait:
                self._errors['type_extrait'] = self.error_class([
                    _('Ce champ doit être rempli '
                      'pour pouvoir utiliser « Numéro d’extrait ».')])
            if not data['numero_extrait']:
                self._errors['numero_extrait'] = self.error_class([
                    _('Ce champ doit être rempli '
                      'pour pouvoir utiliser « Type d’extrait ».')])
            if not data['extrait_de']:
                self._errors['extrait_de'] = self.error_class([
                    _('Ce champ doit être rempli pour pouvoir utiliser '
                      '« Type d’extrait » et « Numéro d’extrait ».')])

        if not data['genre']:
            if data['numero']:
                self._errors['numero'] = self.error_class([
                    _('Vous ne pouvez remplir « Numéro » sans « Genre »')])
            if data['coupe']:
                self._errors['coupe'] = self.error_class([
                    _('Vous ne pouvez remplir « Coupe » sans « Genre »')])

        return data

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
            b'tempo': AutoCompleteWidget('oeuvre__tempo',
                                         attrs={'style': 'width: 500px;'}),
            b'numero_extrait': TextInput(attrs={'cols': 10})
        }


class ElementDeDistributionForm(ModelForm):
    class Meta(object):
        model = ElementDeDistribution

    def clean(self):
        data = super(ElementDeDistributionForm, self).clean()

        error_msgs = defaultdict(list)
        if not (data[b'individu'] or data[b'ensemble']):
            msg = _('Vous devez remplir « Individu » ou « Ensemble ».')
            error_msgs[b'individu'].append(msg)
            error_msgs[b'ensemble'].append(msg)
        if data[b'individu'] and data[b'ensemble']:
            msg = _('Vous ne pouvez remplir à la fois '
                    '« Individu » et « Ensemble ».')
            error_msgs[b'individu'].append(msg)
            error_msgs[b'ensemble'].append(msg)
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
            if k in data:
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
