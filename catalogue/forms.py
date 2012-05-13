from django import forms
from musicologie.catalogue.models import *


class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
