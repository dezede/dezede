# coding: utf-8

from __future__ import unicode_literals
from django.forms import BooleanField
from mptt.forms import MPTTAdminForm
from .models import DossierDEvenements


class DossierDEvenementsForm(MPTTAdminForm):
    statique = BooleanField(required=False)

    class Meta(object):
        model = DossierDEvenements

    class Media(object):
        css = {
            'all': ('css/custom_admin.css',),
        }

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            initial = kwargs.get('initial', {})
            initial['statique'] = kwargs['instance'].evenements.exists()
            kwargs['initial'] = initial
        super(DossierDEvenementsForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(DossierDEvenementsForm, self).clean()

        if cleaned_data['categorie'] is not None \
                and cleaned_data['parent'] is not None:
            msg = 'Ne pas saisir de catégorie si le dossier a un parent.'
            self._errors['categorie'] = self.error_class((msg,))
            self._errors['parent'] = self.error_class((msg,))

        if cleaned_data['statique']:
            if not cleaned_data['evenements']:
                cleaned_data['evenements'] = \
                    self.instance.get_queryset(dynamic=True)
                self.instance.evenements.add(*cleaned_data['evenements'])
        else:
            cleaned_data['evenements'] = []
            if self.instance.pk is not None:
                self.instance.evenements.clear()
        return cleaned_data
