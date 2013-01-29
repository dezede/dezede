# coding: utf-8

from __future__ import unicode_literals
from django.forms.fields import MultiValueField
from django.forms.widgets import MultiWidget, TextInput
from django.template.loader import render_to_string
from .models import Evenement


__all__ = (b'RangeSliderWidget', b'RangeSliderField')


class RangeSliderWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = [TextInput(attrs=attrs), TextInput(attrs=attrs)]
        super(RangeSliderWidget, self).__init__(widgets, attrs=attrs)

    def render(self, name, value, attrs=None):
        evenements = Evenement.objects.filter(
                        ancrage_debut__date__isnull=False)
        if evenements.exists():
            min = evenements.order_by(
                             b'ancrage_debut__date')[0].ancrage_debut.date.year
            max = evenements.order_by(
                            b'-ancrage_debut__date')[0].ancrage_debut.date.year
        else:
            min, max = 1600, 2012
        try:
            int(value[0]), int(value[1])
        except (ValueError, TypeError):
            value = (min, max)
        start, end = value
        t = b'widgets/range_slider_widget.html'
        return render_to_string(t, locals())

    def decompress(self, value):
        if value:
            return value.split('-')
        return [None, None]


class RangeSliderField(MultiValueField):
    widget = RangeSliderWidget

    def compress(self, data_list):
        if data_list:
            return '-'.join(data_list)
        return None
