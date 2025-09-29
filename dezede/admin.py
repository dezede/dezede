from django.contrib.admin import register, HORIZONTAL
from django.utils.translation import gettext_lazy as _
from image_cropping import ImageCroppingMixin
from reversion.admin import VersionAdmin
from libretto.admin import PublishedAdmin
from .models import Diapositive


@register(Diapositive)
class DiapositiveAdmin(ImageCroppingMixin, VersionAdmin, PublishedAdmin):
    list_display = ('content_object', 'title', 'subtitle', 'thumbnail',
                    'position')
    list_editable = ('title', 'subtitle', 'position',)
    related_lookup_fields = {
        'generic': (('content_type', 'object_id'),),
    }
    radio_fields = {
        'text_align': HORIZONTAL,
        'image_align': HORIZONTAL,
        'opacity': HORIZONTAL,
    }
    fieldsets = (
        (_('Objet lié'), {
            'fields': (('content_type', 'object_id'),),
            'description': _('La diapositive renverra à l’objet '
                             'que vous devez choisir de lier ici.'),
        }),
        (_('Texte'), {
            'fields': ('title', 'subtitle', 'text_align', 'text_background'),
        }),
        (_('Arrière-plan'), {
            'fields': ('image', 'cropping', 'image_align', 'opacity'),
        }),
        (None, {
            'fields': ('position',),
        }),
    )
