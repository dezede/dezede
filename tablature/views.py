# coding: utf-8

from __future__ import unicode_literals
import json
from django.db.models import FieldDoesNotExist
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.utils.text import capfirst
from django.views.generic import ListView


class TableView(ListView):
    columns = ()
    template_name = 'table.html'
    results_per_page = 15

    def get_columns(self):
        if self.columns:
            return self.columns
        return [f.attname for f in self.model._meta.fields]

    def get_verbose_columns(self):
        verbose_columns = []
        for column in self.get_columns():
            try:
                column = self.model._meta.get_field(column).verbose_name
            except FieldDoesNotExist:
                method = getattr(self.model, column)
                if hasattr(method, 'short_description'):
                    column = method.short_description
            verbose_columns.append(capfirst(column))
        return verbose_columns

    def get_context_data(self, **kwargs):
        context = super(TableView, self).get_context_data(**kwargs)
        context['columns'] = self.get_verbose_columns()
        context['results_per_page'] = self.results_per_page
        return context

    def get_results(self):
        current_page = int(self.request.GET.get('currentPage', 0))
        offset = current_page * self.results_per_page
        qs = self.get_queryset()[offset:offset + self.results_per_page]
        results = []
        for obj in qs:
            row = []
            for attr in self.get_columns():
                verbose_attr = 'get_' + attr + '_display'
                if hasattr(obj, verbose_attr):
                    attr = verbose_attr
                v = getattr(obj, attr)
                if callable(v):
                    v = v()
                v = '' if v is None else force_text(v)
                row.append(v)
            results.append(row)
        return results

    def get(self, request, *args, **kwargs):
        if request.GET.get('format') == 'json':
            return HttpResponse(json.dumps(self.get_results()),
                                content_type='application/json')
        return super(TableView, self).get(request, *args, **kwargs)
