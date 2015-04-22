# coding: utf-8

from __future__ import unicode_literals
from ajax_select.fields import AutoCompleteSelectMultipleField, \
    AutoCompleteWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from datetime import timedelta
from django.db.models import Q
from django.forms import ValidationError, ModelForm, Form, CharField, TextInput
from django.utils.translation import ugettext_lazy as _
from common.utils.text import capfirst, str_list_w_last
from .models import (
    Oeuvre, Source, Individu, ElementDeProgramme, ElementDeDistribution,
    Ensemble, Saison)
from range_slider.fields import RangeSliderField


__all__ = (b'IndividuForm', b'EnsembleForm', b'OeuvreForm',
           b'ElementDeDistributionForm', b'ElementDeProgrammeForm',
           b'SourceForm', b'SaisonForm', b'EvenementListForm')


class ConstrainedModelForm(ModelForm):
    REQUIRED_BY = ()
    INCOMPATIBLES = ()

    def get_field_verbose(self, fieldname):
        return capfirst(
            self._meta.model._meta.get_field(fieldname).verbose_name)

    def clean(self):
        data = super(ConstrainedModelForm, self).clean()

        for required_fieldnames, fieldnames in self.REQUIRED_BY:
            for required_fieldname in required_fieldnames:
                verbose_required = self.get_field_verbose(required_fieldname)
                for fieldname in fieldnames:
                    verbose = self.get_field_verbose(fieldname)
                    if data.get(fieldname) and not data.get(required_fieldname):
                        msg = _('« %(field)s » ne peut être saisi '
                                'sans « %(required)s ».') % {
                            'field': verbose,
                            'required': verbose_required}
                        for k in (fieldname, required_fieldname):
                            self.add_error(k, msg)

        for fieldnames in self.INCOMPATIBLES:
            if all(data.get(fieldname) for fieldname in fieldnames):
                for fieldname in fieldnames:
                    verbose = self.get_field_verbose(fieldname)
                    other_fields = [_('« %s »') % self.get_field_verbose(k)
                                    for k in fieldnames if k != fieldname]
                    msg = _('« %(field)s » ne peut être saisi '
                            'avec %(other_fields)s.') % {
                        'field': verbose,
                        'other_fields': str_list_w_last(other_fields)}
                    self.add_error_1_6(fieldname, msg)

        return data


class IndividuForm(ConstrainedModelForm):
    REQUIRED_BY = (
        (('naissance_date',), ('naissance_date_approx',)),
        (('deces_date',), ('deces_date_approx',)),
    )

    class Meta(object):
        model = Individu
        exclude = ()
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
        exclude = ()
        widgets = {
            b'particule_nom':
                AutoCompleteWidget('ensemble__particule_nom',
                                   attrs={'style': 'width: 50px;'})
        }


class OeuvreForm(ConstrainedModelForm):
    REQUIRED_BY = (
        (('titre',), ('prefixe_titre', 'coordination',
                      'prefixe_titre_secondaire', 'titre_secondaire')),
        (('titre_secondaire',), ('prefixe_titre_secondaire',
                                 'coordination')),
        (('coordination',), ('prefixe_titre_secondaire',
                             'titre_secondaire')),
        (('genre',), ('numero', 'coupe')),
        (('extrait_de', 'numero_extrait',
          'type_extrait'), ('numero_extrait', 'type_extrait')),
        (('creation_date',), ('creation_date_approx',)),
    )
    INCOMPATIBLES = (
        ('coupe', 'numero'),
    )

    def clean(self):
        data = super(OeuvreForm, self).clean()

        type_extrait = data['type_extrait']
        type_extrait_affiche = (
            type_extrait and type_extrait not in Oeuvre.TYPES_EXTRAIT_CACHES)

        if type_extrait_affiche:
            for fieldname in ('genre', 'tempo'):
                if data[fieldname]:
                    msg = _('« %s » ne peut être saisi avec ce type '
                            'd’extrait.') % self.get_field_verbose(fieldname)
                    self.add_error(fieldname, msg)
                    self.add_error('type_extrait', msg)
        elif not data['titre'] and not data['genre'] and not data['tempo']:
            msg = _('Un titre, un genre ou un tempo '
                    'doit au moins être précisé.')
            self.add_error('titre', msg)
            self.add_error('genre', msg)
            self.add_error('tempo', msg)

        # Ensures title look like "Le Tartuffe, ou l’Imposteur.".
        data['prefixe_titre'] = capfirst(data['prefixe_titre'])
        data['titre'] = capfirst(data['titre'])
        data['prefixe_titre_secondaire'] = data['prefixe_titre_secondaire'].lower()
        data['titre_secondaire'] = capfirst(data['titre_secondaire'])

        return data

    class Meta(object):
        model = Oeuvre
        exclude = ()
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


class ElementDeDistributionForm(ConstrainedModelForm):
    INCOMPATIBLES = (
        ('individu', 'ensemble'),
        ('partie', 'profession'),
    )

    class Meta(object):
        model = ElementDeDistribution
        exclude = ()

    def clean(self):
        data = super(ElementDeDistributionForm, self).clean()

        if not (data[b'individu'] or data[b'ensemble']):
            msg = _('Vous devez remplir « Individu » ou « Ensemble ».')
            self.add_error('individu', msg)
            self.add_error('ensemble', msg)
        if data.get(b'partie', '') != '' \
                and data.get(b'profession') \
                and data[b'profession'].parties.exists():
            self.add_error(
                'profession',
                _('Au moins un rôle ou instrument est lié à cette profession. '
                  'Remplissez donc « Rôle ou instrument » à la place.'))

        return data


class ElementDeProgrammeForm(ConstrainedModelForm):
    INCOMPATIBLES = (('oeuvre', 'autre'),)

    class Meta(object):
        model = ElementDeProgramme
        exclude = ()
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

        return data


class SourceForm(ConstrainedModelForm):
    REQUIRED_BY = (
        (('date',), ('date_approx',)),
        (('lieu_conservation', 'cote'), ('lieu_conservation', 'cote')),
    )

    class Meta(object):
        model = Source
        exclude = ()
        widgets = {
            b'titre': AutoCompleteWidget('source__titre',
                                         attrs={'style': 'width: 600px;'}),
            b'numero': TextInput(attrs={'cols': 10}),
            b'folio': TextInput(attrs={'cols': 10}),
            b'page': TextInput(attrs={'cols': 10}),
        }

    def clean(self):
        data = super(SourceForm, self).clean()

        if not (data['titre'] or data['lieu_conservation'] or data['cote']):
            msg = _('Vous devez remplir « Titre » ou '
                    '« Lieu de conservation » et « Cote ».')
            self.add_error('titre', msg)
            if not data['lieu_conservation']:
                self.add_error('lieu_conservation', msg)
            if not data['cote']:
                self.add_error('cote', msg)

        return data


class SaisonForm(ModelForm):
    class Meta(object):
        model = Saison
        exclude = ()

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
