# coding: utf-8

from __future__ import unicode_literals
import json

from django.db.models import FieldDoesNotExist, Q
from django.db.models.query import ValuesListQuerySet
from django.http import HttpResponse
from django.utils.encoding import force_text
from django.utils.text import capfirst
from django.views.generic import ListView


class TableView(ListView):
    columns = ()
    columns_widths = {}
    verbose_columns = {}
    search_lookups = ()
    orderings = {}
    filters = {}
    template_name = 'tablature/table_page.html'
    results_per_page = 15

    def get_columns(self):
        if self.columns:
            return self.columns
        return [f.name for f in self.model._meta.fields]

    def get_field(self, column):
        try:
            return self.model._meta.get_field(column)
        except FieldDoesNotExist:
            pass

    def get_verbose_columns(self, column):
        if column in self.verbose_columns:
            return self.verbose_columns[column]
        field = self.get_field(column)
        if field is None:
            method = getattr(self.model, column)
            if hasattr(method, 'short_description'):
                column = method.short_description
        else:
            column = field.verbose_name
        return capfirst(column)

    def get_column_width(self, column):
        if column in self.columns_widths:
            return self.columns_widths[column]
        return 'initial'

    def get_context_data(self, **kwargs):
        context = super(TableView, self).get_context_data(**kwargs)
        context.update(
            verbose_name_plural=self.model._meta.verbose_name_plural,
            columns=map(self.get_verbose_columns, self.get_columns()),
            columns_widths=map(self.get_column_width, self.get_columns()),
            search_lookups=self.search_lookups,
            sortables=['true' if self.get_ordering(c, 1) else 'false'
                       for c in self.get_columns()],
            filters=map(self.get_filter, self.get_columns()),
            results_per_page=self.results_per_page)
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

    def get_filter(self, column):
        if column not in self.filters:
            return ()
        values = self.filters[column]
        if isinstance(values, ValuesListQuerySet):
            values = tuple(values.all())
        assert len(values[0]) == 2, 'Each filter must be a value/verbose pair.'
        return values

    def search(self, queryset, q):
        if not q:
            return queryset
        filters = Q()
        for lookup in self.search_lookups:
            filters |= Q(**{lookup: q})
        if filters:
            return queryset.filter(filters)
        return queryset.none()

    def get_results_queryset(self):
        qs = self.get_queryset()
        GET = self.request.GET
        qs = self.search(qs, GET.get('q'))

        filter_choices = GET.get('choices', '').split(',')
        for column, choice in zip(self.get_columns(), filter_choices):
            if choice:
                method = getattr(self, 'filter_' + column, None)
                qs = (qs.filter(**{column: choice}) if method is None
                      else method(qs, choice))

        order_directions = map(int, GET.get('orderings', '').split(','))
        order_by = []
        for column, direction in zip(self.get_columns(), order_directions):
            order_by.extend(self.get_ordering(column, direction))
        if order_by:
            qs = qs.order_by(*order_by)
        return qs.distinct()

    def get_limited_results_queryset(self):
        qs = self.get_results_queryset()
        current_page = int(self.request.GET.get('page', '0'))
        offset = current_page * self.results_per_page
        return qs[offset:offset + self.results_per_page]

    def get_results(self):
        results = []
        for obj in self.get_limited_results_queryset():
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
                'count': self.get_results_queryset().count()}

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return HttpResponse(json.dumps(self.get_data()),
                                content_type='application/json')
        return super(TableView, self).get(request, *args, **kwargs)
