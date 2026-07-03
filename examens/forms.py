from django.forms import ModelForm
from tinymce.widgets import TinyMCE
from wagtail.admin.forms import WagtailAdminModelForm

from common.utils.html import sanitize_html
from typography.utils import replace

from .models import Level, TakenLevel


class LevelAdminForm(WagtailAdminModelForm):
    class Meta(WagtailAdminModelForm.Meta):
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
