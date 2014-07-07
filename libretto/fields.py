# coding: utf-8

from __future__ import unicode_literals
import datetime
from django.db.models import Q, Min, Max
from django.forms.fields import MultiValueField
from django.forms.widgets import MultiWidget, TextInput
from django.template.loader import render_to_string
from .models import Evenement


__all__ = (b'RangeSliderWidget', b'RangeSliderField')


class RangeSliderWidget(MultiWidget):
    queryset = Evenement.objects.none()

    def __init__(self, attrs=None):
        widgets = [TextInput(attrs=attrs), TextInput(attrs=attrs)]
        super(RangeSliderWidget, self).__init__(widgets, attrs=attrs)

    def get_default_range(self):
        dates = self.queryset.aggregate(
            min=Min('debut_date'), max=Max('debut_date'),
            max_fin=Max('fin_date'))

        min_date = dates['min']
        max_date = dates['max']
        max_fin_date = dates['max_fin']

        if max_fin_date is not None and max_date is not None:
            max_date = max(max_date, max_fin_date)

        if max_date is None:
            max_date = datetime.datetime.now().date()
        if min_date is None:
            min_date = datetime.date(1600, 1, 1)

        return min_date.year, max_date.year

    def render(self, name, value, attrs=None):
        min_year, max_year = self.get_default_range()
        try:
            int(value[0]), int(value[1])
        except (ValueError, TypeError):
            value = min_year, max_year
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
