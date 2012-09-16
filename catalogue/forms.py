from django import forms
from .models import *


class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
