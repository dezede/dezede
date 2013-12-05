# coding: utf-8

from __future__ import unicode_literals
from django.contrib import admin
from image_cropping import ImageCroppingMixin
from reversion import VersionAdmin
from cache_tools import cached_ugettext_lazy as _
from libretto.admin import PublishedAdmin
from .models import Diapositive


class DiapositiveAdmin(ImageCroppingMixin, VersionAdmin, PublishedAdmin):
    list_display = ('content_object', 'title', 'subtitle', 'thumbnail',
                    'position')
    list_editable = ('title', 'subtitle', 'position',)
    related_lookup_fields = {
        'generic': (('content_type', 'object_id'),),
    }
    radio_fields = {
        'text_align': admin.HORIZONTAL,
        'image_align': admin.HORIZONTAL,
        'opacity': admin.HORIZONTAL,
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


admin.site.register(Diapositive, DiapositiveAdmin)
