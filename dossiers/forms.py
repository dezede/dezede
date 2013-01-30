# coding: utf-8

from __future__ import unicode_literals
from django.forms import ModelForm
from tinymce.widgets import TinyMCE
from .models import DossierDEvenements


class DossierDEvenementsForm(ModelForm):
    class Meta:
        model = DossierDEvenements
        widgets = {
            'contenu': TinyMCE,
        }
