from ajax_select.fields import AutoCompleteSelectMultipleField, \
    AutoCompleteWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from datetime import timedelta

from django.contrib.gis.geos import Point
from django.contrib.postgres.forms import RangeWidget, BaseRangeField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q
from django.forms import (
    ValidationError, ModelForm, Form, CharField, TextInput, BooleanField,
    FloatField, IntegerField, MultiValueField, MultiWidget, NumberInput,
    Select,
)
from django.utils.translation import ugettext_lazy as _
from psycopg2._range import NumericRange

from common.utils.text import capfirst, str_list_w_last
from .models import (
    Lieu, Oeuvre, Source, Individu, ElementDeProgramme, ElementDeDistribution,
    Ensemble, Saison, Partie)
from .models.oeuvre import Pitch
from range_slider.fields import RangeSliderField


__all__ = ('IndividuForm', 'EnsembleForm', 'OeuvreForm',
           'ElementDeDistributionForm', 'ElementDeProgrammeForm',
           'SourceForm', 'SaisonForm', 'EvenementListForm')


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
                    self.add_error(fieldname, msg)

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
            'prenoms':
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
        designation = data['designation']
        if designation == 'P' and not data['pseudonyme'] \
            or designation == 'B' and not data['nom_naissance'] \
                or designation == 'F' and not data['prenoms']:
            raise ValidationError(_('Il manque des données pour pouvoir '
                                    'choisir cette désignation.'))
        return designation


class EnsembleForm(ModelForm):
    class Meta(object):
        model = Ensemble
        exclude = ()
        widgets = {
            'particule_nom':
                AutoCompleteWidget('ensemble__particule_nom',
                                   attrs={'style': 'width: 50px;'})
        }


class PartieForm(ConstrainedModelForm):
    def clean(self):
        data = super(PartieForm, self).clean()

        type = data.get('type')

        if data.get('oeuvre') and type == Partie.INSTRUMENT:
            self.add_error(
                'oeuvre',
                _('« Œuvre » ne peut être saisi que pour les rôles.'))

        if data.get('professions') and type == Partie.ROLE:
            self.add_error(
                'professions',
                _('« Professions » ne peut être saisi '
                  'que pour les instruments.'))

        return data

    class Meta(object):
        model = Partie
        exclude = ()


class PitchWidget(MultiWidget):
    def __init__(self, *args, **kwargs):
        choices = [('', '---------')] + [
            (str(n), s) for n, s in enumerate(Pitch.OCTAVE_NOTES)
        ]
        widgets = [
            Select(choices=choices),
            NumberInput(attrs={'placeholder': _('octave')}),
        ]
        super().__init__(*args, widgets=widgets, **kwargs)

    def decompress(self, value):
        if not isinstance(value, int):
            return '', None
        return Pitch.database_to_form_values(value)


PITCH_HELP_TEXT = _(
    'Do 3 est le do central d’un piano. Suivent ré 3, mi 3… '
    'Jusqu’à si 3 (cf. '
    '<a href="https://en.wikipedia.org/wiki/Scientific_pitch_notation" '
    'target="_blank">notation scientifique</a>).'
)


class PitchField(MultiValueField):
    widget = PitchWidget

    def __init__(self, **kwargs):
        fields = [
            IntegerField(validators=[
                MinValueValidator(0),
                MaxValueValidator(Pitch.OCTAVE_LENGTH),
            ]),
            IntegerField(validators=[
                MinValueValidator(-5),
                MaxValueValidator(15),
            ]),
        ]
        super().__init__(fields, **kwargs, help_text=PITCH_HELP_TEXT)

    def compress(self, data_list):
        try:
            note, octave = data_list
        except ValueError:
            return None

        empty_values = self.empty_values
        if note in empty_values:
            if octave in empty_values:
                return None
            raise ValidationError(_('Il manque la note.'))
        if octave in empty_values:
            raise ValidationError(_('Il manque le numéro d’octave.'))
        return Pitch.form_to_database_value(note, octave)


def make_range_include_bounds(value):
    """
    By default, all PostgreSQL ranges are with '[)' bounds, which is wrong
    for an ambitus.
    """
    if isinstance(value, NumericRange):
        return NumericRange(
            lower=None if value.lower is None else (
                value.lower + (0 if value.lower_inc else 1)
            ),
            upper=None if value.upper is None else (
                value.upper - (0 if value.upper_inc else 1)
            ),
            bounds='[]',
            empty=value.isempty,
        )
    return value


class AmbitusWidget(RangeWidget):
    template_name = 'admin/ambitus_widget.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, base_widget=PitchWidget(), **kwargs)

    def decompress(self, value):
        return super().decompress(make_range_include_bounds(value))


class AmbitusField(BaseRangeField):
    base_field = PitchField
    range_type = NumericRange

    def __init__(self, *args, **kwargs):
        # We force pass the widget here, otherwise it is ignored when
        # specified as a class attribute.
        super().__init__(
            *args, widget=AmbitusWidget, help_text=PITCH_HELP_TEXT, **kwargs,
        )

    def prepare_value(self, value):
        return super().prepare_value(make_range_include_bounds(value))

    def clean(self, value):
        value = super().clean(value)
        if value:
            if not value.upper or not value.lower:
                raise ValidationError(
                    _('Veuillez saisir les deux extrémités de l’ambitus.'),
                )
            if value.upper == value.lower:
                raise ValidationError(
                    _(
                        'Les deux extrémités de l’ambitus '
                        'doivent être différentes.'
                    )
                )
        return value

    def compress(self, values):
        value = super().compress(values=values)
        if isinstance(value, NumericRange) and not (
            value.lower_inc and value.upper_inc  # bounds are not '[]'
        ):
            # We force the range to be fully inclusive.
            value = NumericRange(
                lower=value.lower, upper=value.upper, bounds='[]',
                empty=value.isempty,
            )
        return value


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
    ambitus = AmbitusField(label=_('Ambitus'), required=False)

    def clean(self):
        data = super(OeuvreForm, self).clean()

        # Ensures title look like "Le Tartuffe, ou l’Imposteur.".
        data['prefixe_titre'] = capfirst(data.get('prefixe_titre', ''))
        data['titre'] = capfirst(data.get('titre', ''))
        data['prefixe_titre_secondaire'] = data.get(
            'prefixe_titre_secondaire', '').lower()
        data['titre_secondaire'] = capfirst(data.get('titre_secondaire', ''))

        type_extrait = data.get('type_extrait')
        type_extrait_affiche = (
            type_extrait and type_extrait not in Oeuvre.TYPES_EXTRAIT_CACHES)

        if type_extrait_affiche:
            for fieldname in ('genre', 'tempo'):
                if data.get(fieldname):
                    msg = _('« %s » ne peut être saisi avec ce type '
                            'd’extrait.') % self.get_field_verbose(fieldname)
                    self.add_error(fieldname, msg)
                    self.add_error('type_extrait', msg)
        elif not (data.get('titre') or data.get('genre') or data.get('tempo')):
            msg = _('Un titre, un genre ou un tempo '
                    'doit au moins être précisé.')
            self.add_error('titre', msg)
            self.add_error('genre', msg)
            self.add_error('tempo', msg)

        if data.get('creation_type') is None and any(
            data.get(k) for k in (
                    'creation_date', 'creation_date_approx',
                    'creation_heure', 'creation_heure_approx',
                    'creation_lieu', 'creation_lieu_approx')):
            self.add_error('creation_type',
                           _('« Type de création » doit être rempli '
                             'lorsqu’on remplit la création.'))

        return data

    class Meta(object):
        model = Oeuvre
        exclude = ()
        widgets = {
            'prefixe_titre':
                AutoCompleteWidget('oeuvre__prefixe_titre',
                                   attrs={'style': 'width: 50px;'}),
            'coordination':
                AutoCompleteWidget('oeuvre__coordination',
                                   attrs={'style': 'width: 70px;'}),
            'prefixe_titre_secondaire':
                AutoCompleteWidget('oeuvre__prefixe_titre_secondaire',
                                   attrs={'style': 'width: 50px;'}),
            'coupe': AutoCompleteWidget('oeuvre__coupe',
                                         attrs={'style': 'width: 500px;'}),
            'tempo': AutoCompleteWidget('oeuvre__tempo',
                                         attrs={'style': 'width: 500px;'}),
            'numero_extrait': TextInput(attrs={'cols': 10}),
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

        if not (data.get('individu') or data.get('ensemble')):
            msg = _('Vous devez remplir « Individu » ou « Ensemble ».')
            self.add_error('individu', msg)
            self.add_error('ensemble', msg)
        if data.get('partie', '') != '' \
                and data.get('profession') \
                and data['profession'].parties.exists():
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


class SourceForm(ConstrainedModelForm):
    REQUIRED_BY = (
        (('date',), ('date_approx',)),
        (('lieu_conservation', 'cote'), ('lieu_conservation', 'cote')),
    )

    class Meta(object):
        model = Source
        exclude = ()
        widgets = {
            'titre': AutoCompleteWidget('source__titre',
                                        attrs={'style': 'width: 600px;'}),
            'numero': TextInput(attrs={'cols': 10}),
            'folio': TextInput(attrs={'cols': 10}),
            'page': TextInput(attrs={'cols': 10}),
            'lieu_conservation': AutoCompleteWidget(
                'source__lieu_conservation', attrs={'style': 'width: 600px;'}),
        }

    def clean(self):
        data = super(SourceForm, self).clean()

        if not (
            (data.get('parent') and data.get('position')) or data.get('titre')
            or (data.get('lieu_conservation') and data.get('cote'))
        ):
            msg = _('Vous devez remplir « Titre » ou '
                    '« Lieu de conservation » et « Cote » '
                    'ou « Parent » et « Position ».')
            for field in (
                'parent', 'position', 'titre', 'lieu_conservation', 'cote'
            ):
                if not data.get(field):
                    self.add_error(field, msg)

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
                raise ValidationError(
                    _('La durée d’une saison ne peut excéder un an.'))

        instance = self.save(commit=False)

        overlapping_seasons = Saison.objects.exclude(pk=instance.pk).filter(
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
    par_saison = BooleanField(required=False, initial=False)
    lieu = AutoCompleteSelectMultipleField('lieu', label=_('Lieu'),
                                           required=False, help_text='')
    oeuvre = AutoCompleteSelectMultipleField(
        'oeuvre', required=False, label=_('Œuvre'), help_text='')
    individu = AutoCompleteSelectMultipleField(
        'individu', required=False, label=_('Individu'), help_text='')
    ensemble = AutoCompleteSelectMultipleField(
        'ensemble', required=False, label=_('Ensemble'), help_text='')

    def __init__(self, *args, **kwargs):
        saison_select = """
            <div class="form-group btn-group btn-group-justified" data-toggle="buttons">
              <label class="radio-inline btn btn-default{%% if not by_season %%} active{%% endif %%}">
                <input name="par_saison" type="radio" autocomplete="off" disabled />
                %s
              </label>
              <label class="radio-inline btn btn-default{%% if by_season %%} active{%% endif %%}">
                <input name="par_saison", type="radio"
                autocomplete="off" value="True" {%% if by_season %%}checked {%% endif %%}/>
                %s
              </label>
            </div>
            """ % (_('Par année civile'), _('Par saison'))

        queryset = kwargs.pop('queryset')

        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.form_class = 'well well-sm'
        self.helper.layout = Layout(
            Field('q', css_class='input-lg'),
            HTML('<hr/>'),
            'dates',
            HTML(saison_select),
            HTML('<hr/>'),
            'lieu', 'oeuvre', 'individu', 'ensemble',
            HTML('<hr/>'),
            Submit('', _('Filtrer'), css_class='btn-lg btn-block',
                   data_loading_text=_('Chargement…')),
        )

        super(EvenementListForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['placeholder'] = (field.label or '') + '…'
            field.label = ''

        self.fields['dates'].widget.queryset = queryset


class LieuAdminForm(ModelForm):
    latitude = FloatField(
        min_value=-90, max_value=90, required=False, label=_('latitude'))
    longitude = FloatField(
        min_value=-180, max_value=180, required=False, label=_('longitude'))

    class Meta:
        model = Lieu
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        geometry = self.initial.get('geometry', None)
        if isinstance(geometry, Point):
            self.initial['longitude'], self.initial['latitude'] = \
                geometry.tuple

    def clean(self):
        data = super().clean()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        geometry = data.get('geometry')
        geometry_changed = geometry != self.initial.get('geometry')
        latlon_changed = (latitude != self.initial.get('latitude')
                          or longitude != self.initial.get('longitude'))
        if latitude and longitude and latlon_changed \
                and (not geometry or not geometry_changed):
            data['geometry'] = Point(longitude, latitude)
        return data
