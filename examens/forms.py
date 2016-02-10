# coding: utf-8

from __future__ import unicode_literals
from django.forms import ModelForm
from tinymce.widgets import TinyMCE

from common.utils.html import sanitize_html
from typography.utils import replace

from .models import Level, TakenLevel


class LevelAdminForm(ModelForm):
    class Meta:
        model = Level
        exclude = ()
        widgets = {
            'help_message': TinyMCE,
        }


class TakenLevelForm(ModelForm):
    class Meta:
        model = TakenLevel
        fields = ('transcription',)
        widgets = {
            'transcription': TinyMCE,
        }

    def clean_transcription(self):
        return sanitize_html(replace(self.cleaned_data['transcription']))
