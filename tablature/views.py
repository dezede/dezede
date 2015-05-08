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
    orderings = {}
    template_name = 'table.html'
    results_per_page = 15

    def get_columns(self):
        if self.columns:
            return self.columns
        return [f.attname for f in self.model._meta.fields]

    def get_field(self, column):
        try:
            return self.model._meta.get_field(column)
        except FieldDoesNotExist:
            pass

    def get_verbose_columns(self, column):
        field = self.get_field(column)
        if field is None:
            method = getattr(self.model, column)
            if hasattr(method, 'short_description'):
                column = method.short_description
        else:
            column = field.verbose_name
        return capfirst(column)

    def get_context_data(self, **kwargs):
        context = super(TableView, self).get_context_data(**kwargs)
        context['columns'] = [self.get_verbose_columns(column)
                              for column in self.get_columns()]
        context['sortables'] = [
            'true' if self.get_ordering(column, 1) else 'false'
            for column in self.get_columns()]
        context['results_per_page'] = self.results_per_page
        return context

    def get_ordering(self, column, direction):
        """
        Returns a tuple of lookups to order by for the given column
        and direction. Direction is an integer, either -1, 0 or 1.
        """
        if direction == 0:
            return ()
        if column in self.orderings:
            ordering = self.orderings[column]
        else:
            field = self.get_field(column)
            if field is None:
                return ()
            ordering = column
        if not isinstance(ordering, (tuple, list)):
            ordering = [ordering]
        if direction == 1:
            return ordering
        return [lookup[1:] if lookup[0] == '-' else '-' + lookup
                for lookup in ordering]

    def get_queryset(self):
        qs = super(TableView, self).get_queryset()
        GET = self.request.GET
        if 'currentPage' not in GET or 'orderings' not in GET:
            return qs

        order_directions = map(int, GET['orderings'].split(','))
        order_by = []
        for column, direction in zip(self.columns, order_directions):
            order_by.extend(self.get_ordering(column, direction))
        if order_by:
            qs = qs.order_by(*order_by)
        return qs

    def get_limited_queryset(self):
        qs = self.get_queryset()
        current_page = int(self.request.GET['currentPage'])
        offset = current_page * self.results_per_page
        return qs[offset:offset + self.results_per_page]

    def get_results(self):
        results = []
        for obj in self.get_limited_queryset():
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

    def get_data(self):
        return {'results': self.get_results(),
                'count': self.get_queryset().count()}

    def get(self, request, *args, **kwargs):
        if request.GET.get('format') == 'json':
            return HttpResponse(json.dumps(self.get_data()),
                                content_type='application/json')
        return super(TableView, self).get(request, *args, **kwargs)
