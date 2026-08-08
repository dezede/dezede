from django import forms
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from wagtail.admin.forms import WagtailAdminModelForm

from tree.forms import TreeChoiceField

from .models import Dossier, KIND_CHOICES


class DossierForm(forms.ModelForm):
    # Unlike model fields (whose ``formfield()`` capfirsts the verbose name),
    # an explicitly declared form field shows its label as-is.
    types_de_donnees = forms.MultipleChoiceField(
        choices=KIND_CHOICES, required=False,
        widget=forms.CheckboxSelectMultiple,
        label=capfirst(_('types de données')),
        help_text=_('Types de données présentés par ce dossier.'))

    class Meta(object):
        model = Dossier
        exclude = ()
        field_classes = {
            'parent': TreeChoiceField,
        }

    class Media(object):
        css = {
            'all': ('css/custom_admin.css',),
        }
        js = ('js/dossier_admin.js',)


class DossierWagtailForm(WagtailAdminModelForm):
    types_de_donnees = forms.MultipleChoiceField(
        choices=KIND_CHOICES, required=False,
        widget=forms.CheckboxSelectMultiple,
        label=capfirst(_('types de données')),
        help_text=_('Types de données présentés par ce dossier.'))

    class Meta(WagtailAdminModelForm.Meta):
        model = Dossier
        exclude = ()


SCENARIOS = (
    ('scenario-1', _('1. Événements : répartition chronologique')),
    ('scenario-2', _('2. Événements : répartition géographique')),
    ('scenario-3', _('3. Œuvres : répartition chronologique')),
    ('scenario-4', _('4. Œuvres : répartition géographique')),
    ('scenario-5', _('5. Auteurs : répartition chronologique')),
    ('scenario-6', _('6. Interprètes : répartition chronologique')),
    ('scenario-7', _('7. Auteurs et œuvres : répartition chronologique')),
    ('scenario-8', _('8. Recettes')),
)


class ScenarioForm(forms.Form):
    """ScenarioForm definition."""

    scenario = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=SCENARIOS, required=True)


ScenarioFormSet = forms.formset_factory(ScenarioForm)
