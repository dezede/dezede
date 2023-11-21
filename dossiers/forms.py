from django import forms
from django.utils.translation import ugettext_lazy as _

from tree.forms import TreeChoiceField

from .models import DossierDEvenements, Dossier, DossierDOeuvres


class DossierForm(forms.ModelForm):
    statique = forms.BooleanField(required=False)

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

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance is not None:
            initial = kwargs.get('initial', {})
            initial['statique'] = getattr(
                instance, self.static_manager_name,
            ).exists()
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    @property
    def static_manager_name(self) -> str:
        raise NotImplementedError

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['categorie'] is not None \
                and cleaned_data['parent'] is not None:
            msg = 'Ne pas saisir de catégorie si le dossier a un parent.'
            self.add_error('categorie', msg)
            self.add_error('parent', msg)

        static_data = cleaned_data.get(self.static_manager_name)

        if cleaned_data['statique']:
            if not static_data:
                static_data = list(self.instance.dynamic_queryset)
                if static_data:
                    cleaned_data[self.static_manager_name] = static_data
                    static_manager = getattr(self.instance, self.static_manager_name)
                    static_manager.add(*static_data)
        else:
            cleaned_data[self.static_manager_name] = []
            if self.instance.pk is not None:
                static_manager = getattr(self.instance, self.static_manager_name)
                static_manager.clear()
        return cleaned_data


class DossierDEvenementsForm(DossierForm):
    static_manager_name = 'evenements'

    class Meta(DossierForm.Meta):
        model = DossierDEvenements

class DossierDOeuvresForm(DossierForm):
    static_manager_name = 'oeuvres'

    class Meta(DossierForm.Meta):
        model = DossierDOeuvres


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
