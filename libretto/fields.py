# coding: utf-8

from __future__ import unicode_literals
import datetime
from django.db.models import Q, Min, Max
from django.forms.fields import MultiValueField
from django.forms.widgets import MultiWidget, TextInput
from django.template.loader import render_to_string
from .models import Evenement, AncrageSpatioTemporel


__all__ = (b'RangeSliderWidget', b'RangeSliderField')


class RangeSliderWidget(MultiWidget):
    queryset = ()

    def __init__(self, attrs=None):
        widgets = [TextInput(attrs=attrs), TextInput(attrs=attrs)]
        super(RangeSliderWidget, self).__init__(widgets, attrs=attrs)

    def render(self, name, value, attrs=None):
        dates = AncrageSpatioTemporel.objects.filter(
            Q(evenements_debuts__in=self.queryset)
            | Q(evenements_fins__in=self.queryset)).aggregate(
                min=Min('date'), max=Max('date'))
        min_date = dates['min'] or datetime.date(1600, 1, 1)
        min_year = min_date.year
        max_date = dates['max'] or datetime.datetime.now().date()
        max_year = max_date.year
        try:
            int(value[0]), int(value[1])
        except (ValueError, TypeError):
            value = (min_year, max_year)
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
