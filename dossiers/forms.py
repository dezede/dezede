from django import forms
from django.utils.translation import ugettext_lazy as _

from tree.forms import TreeChoiceField

from .models import DossierDEvenements


class DossierDEvenementsForm(forms.ModelForm):
    statique = forms.BooleanField(required=False)

    class Meta(object):
        model = DossierDEvenements
        exclude = ()
        field_classes = {
            'parent': TreeChoiceField,
        }

    class Media(object):
        css = {
            'all': ('css/custom_admin.css',),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance is not None:
            initial = kwargs.get('initial', {})
            initial['statique'] = instance.evenements.exists()
            kwargs['initial'] = initial
        super(DossierDEvenementsForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(DossierDEvenementsForm, self).clean()

        if cleaned_data['categorie'] is not None \
                and cleaned_data['parent'] is not None:
            msg = 'Ne pas saisir de catégorie si le dossier a un parent.'
            self.add_error('categorie', msg)
            self.add_error('parent', msg)

        evenements = cleaned_data.get('evenements')

        if cleaned_data['statique']:
            if not evenements:
                cleaned_data['evenements'] = self.instance.dynamic_queryset
                self.instance.evenements.add(*evenements)
        else:
            cleaned_data['evenements'] = []
            if self.instance.pk is not None:
                self.instance.evenements.clear()
        return cleaned_data


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
