import json
import re

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, Select
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.snippets.widgets import AdminSnippetChooser

from .constants import LINKABLE_MODELS

CROP_PATTERN = re.compile(r'\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*')

# What makes a JSON text unsafe inside a <script> tag.
SCRIPT_ESCAPES = {
    ord('<'): '\\u003C', ord('>'): '\\u003E', ord('&'): '\\u0026',
}


def json_for_script(value):
    return json.dumps(value).translate(SCRIPT_ESCAPES)


def get_image_size(image):
    # An upload carries the image that Pillow opened, a stored file its size.
    if hasattr(image, 'image'):
        return image.image.size
    return image.width, image.height


class LinkedObjectTypeSelect(Select):
    """Selects the type of the linked object, and shows only its chooser."""

    # The chooser fields by content type id, set by the form.
    chooser_fields = None

    # The choosers come after this widget in the page, so they are only
    # hidden once it is entirely loaded.
    SCRIPT = '''<script>
(function () {
  var select = document.getElementById(__ID__);
  var fields = __FIELDS__;
  function wrapper(name) {
    var input = document.getElementById('id_' + name);
    // The panel wrapper holds the label as well as the field.
    return input && (input.closest('.w-panel__wrapper')
                     || input.closest('.w-field__wrapper'));
  }
  function sync() {
    Object.keys(fields).forEach(function (typeId) {
      var element = wrapper(fields[typeId]);
      if (element) {
        element.style.display = typeId === select.value ? '' : 'none';
      }
    });
  }
  select.addEventListener('change', sync);
  document.addEventListener('DOMContentLoaded', sync);
})();
</script>'''

    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        field_id = (attrs or {}).get('id') or f'id_{name}'
        script = (
            self.SCRIPT
            .replace('__ID__', json_for_script(field_id))
            .replace('__FIELDS__', json_for_script(self.chooser_fields or {}))
        )
        return html + mark_safe(script)


class BaseDiapositiveForm(WagtailAdminModelForm):
    content_type = ModelChoiceField(
        ContentType.objects.none(), widget=LinkedObjectTypeSelect,
        label=capfirst(_('type d’objet lié')))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        models = {
            name: apps.get_model(label)
            for name, label in LINKABLE_MODELS.items()
        }
        content_types = ContentType.objects.get_for_models(*models.values())
        field = self.fields['content_type']
        field.queryset = ContentType.objects.filter(
            pk__in=[content_type.pk for content_type in content_types.values()])
        field.label_from_instance = (
            lambda content_type: capfirst(
                content_type.model_class()._meta.verbose_name))
        self.chooser_fields = {
            str(content_types[model].pk): name for name, model in models.items()
        }
        field.widget.chooser_fields = self.chooser_fields

        if self.instance.pk:
            name = self.chooser_fields.get(str(self.instance.content_type_id))
            if name is not None:
                self.initial[name] = self.instance.related_object_id

    def clean(self):
        cleaned_data = super().clean()
        self._check_linked_object(cleaned_data)
        self._check_crop(cleaned_data)
        return cleaned_data

    def _check_linked_object(self, cleaned_data):
        content_type = cleaned_data.get('content_type')
        if content_type is None:
            return
        name = self.chooser_fields[str(content_type.pk)]
        linked_object = cleaned_data.get(name)
        if linked_object is None:
            self.add_error(name, self.fields[name].error_messages['required'])
        else:
            self.instance.related_object_id = linked_object.pk

    def _check_crop(self, cleaned_data):
        image = cleaned_data.get('image')
        if not image:
            return

        if 'image' in self.changed_data and 'cropping' not in self.changed_data:
            # The crop is made of the pixels of the previous image. Left empty,
            # it becomes the whole new image when the slide is saved.
            cleaned_data['cropping'] = ''
            return

        cropping = cleaned_data.get('cropping')
        if not cropping:
            return
        width, height = get_image_size(image)
        match = CROP_PATTERN.fullmatch(cropping)
        x1, y1, x2, y2 = map(int, match.groups()) if match else (0, 0, 0, 0)
        if x1 < x2 <= width and y1 < y2 <= height:
            cleaned_data['cropping'] = f'{x1},{y1},{x2},{y2}'
        else:
            self.add_error('cropping', ValidationError(
                _('Le découpage doit être de la forme « x1,y1,x2,y2 », à '
                  'l’intérieur de l’image (%(width)s × %(height)s).'),
                params={'width': width, 'height': height}))


def _chooser_field(model):
    return ModelChoiceField(
        model._default_manager.all(), required=False,
        label=capfirst(model._meta.verbose_name),
        widget=AdminSnippetChooser(model))


# The slide form, with one chooser field per type of linked object.
DiapositiveForm = type('DiapositiveForm', (BaseDiapositiveForm,), {
    name: _chooser_field(apps.get_model(label))
    for name, label in LINKABLE_MODELS.items()
})
