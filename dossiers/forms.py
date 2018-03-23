# coding: utf-8

from __future__ import unicode_literals

from django.forms import BooleanField, ModelForm
from tree.forms import TreeChoiceField

from .models import DossierDEvenements


class DossierDEvenementsForm(ModelForm):
    statique = BooleanField(required=False)

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
                cleaned_data['evenements'] = \
                    self.instance.get_queryset(dynamic=True)
                self.instance.evenements.add(*evenements)
        else:
            cleaned_data['evenements'] = []
            if self.instance.pk is not None:
                self.instance.evenements.clear()
        return cleaned_data
