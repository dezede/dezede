# coding: utf-8

from __future__ import unicode_literals

from collections import defaultdict
from math import isnan
from StringIO import StringIO
from zipfile import ZipFile

from django.contrib.sites.models import Site
from django.db.models import IntegerField, ForeignKey, DateTimeField
from django.http import HttpResponse
from django.utils.encoding import force_text
import pandas
from slugify import slugify


class Exporter(object):
    model = None
    columns = ()
    verbose_overrides = {}
    CONTENT_TYPES = {
        'zip': 'application/zip',
        'json': 'application/json',
        'csv': 'text/csv',
        'xlsx': 'application/vnd.openxmlformats-officedocument'
                '.spreadsheetml.sheet',
    }

    def __init__(self, queryset=None):
        self.queryset = queryset
        if queryset is not None:
            if self.model is None:
                self.model = queryset.model
            elif self.model is not queryset.model:
                raise ValueError('`queryset` does not match '
                                 'the model defined in the exporter')

        if not self.columns:
            self.columns = [field.name for field in self.model._meta.fields]

        self.method_names = []
        self.lookups = []
        for column in self.columns:
            if hasattr(self, 'get_' + column):
                self.method_names.append(column)
            else:
                self.lookups.append(column)
        self.fields = {lookup: self.get_field(lookup)
                       for lookup in self.lookups}
        self.final_fields = {lookup: self.get_final_field(lookup)
                             for lookup in self.lookups}
        self.null_int_lookups = []
        self.datetime_lookups = []
        for lookup, field in self.final_fields.items():
            if isinstance(field, (IntegerField, ForeignKey)) and field.null:
                self.null_int_lookups.append(lookup)
            elif isinstance(field, DateTimeField):
                self.datetime_lookups.append(lookup)

    def get_field(self, lookup):
        return self.model._meta.get_field(lookup.split('__')[0])

    def get_final_field(self, lookup):
        model = self.model
        for part in lookup.split('__'):
            field = model._meta.get_field(part)
            if field.rel is not None:
                model = field.rel.to
        return field

    def get_verbose_name(self, column):
        if column in self.verbose_overrides:
            return self.verbose_overrides[column]
        if column in self.fields:
            return force_text(self.fields[column].verbose_name)
        return column

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        return self.model.objects.all()

    def _get_related_exporters(self, parent_fk_ids=None, is_root=True):
        from .registry import exporter_registry

        fk_ids = defaultdict(set)
        if parent_fk_ids is None:
            parent_fk_ids = fk_ids
        for lookup, field in self.final_fields.items():
            if isinstance(field, ForeignKey):
                model = field.rel.to
                ids = frozenset(
                    self.get_queryset().exclude(**{lookup: None})
                    .order_by().distinct().values_list(lookup, flat=True))
                if ids:
                    fk_ids[model].update(ids)
        for model, ids in fk_ids.items():
            qs = model.objects.filter(pk__in=ids)
            if qs.exists():
                parent_fk_ids[model].update(ids)
                exporter = exporter_registry[model](qs)
                exporter._get_related_exporters(parent_fk_ids, is_root=False)

        if not is_root:
            return

        return [exporter_registry[model](model.objects.filter(pk__in=ids))
                for model, ids in fk_ids.items()]

    def _get_dataframe(self, qs):
        df = pandas.DataFrame.from_records(
            list(qs.values_list(*self.lookups)),
            columns=self.lookups,
        )

        def clean_null_int(x):
            if x is None or isnan(x):
                return ''
            return int(x)

        # Avoids float representation of nullable integer fields
        for lookup in self.null_int_lookups:
            df[lookup] = df[lookup].apply(clean_null_int)

        def remove_timezone(dt):
            if dt is None:
                return ''
            return dt.replace(tzinfo=None)

        # Removes timezones to allow datetime serialization in some formats
        for lookup in self.datetime_lookups:
            df[lookup] = df[lookup].apply(remove_timezone)

        # Display verbose value of fields with `choices`
        for lookup, field in self.fields.items():
            if field.choices:
                df[lookup] = df[lookup].replace({k: force_text(v)
                                                 for k, v in field.choices})

        # Adds columns calculated from methods
        if self.method_names:
            methods_data = defaultdict(list)
            for obj in self.get_queryset():
                for method_name in self.method_names:
                    v = getattr(self, 'get_' + method_name)(obj)
                    methods_data[method_name].append(v)
            for method_name in self.method_names:
                df[method_name] = methods_data[method_name]

        # Reorders columns after adding those using methods
        df = df[list(self.columns)]
        # Adds verbose column names
        df.columns = [self.get_verbose_name(column) for column in df.columns]
        # Sets the first column (usually pk) as index
        df.set_index(df.columns[0], inplace=True)
        return df

    def get_dataframes(self, is_root=True):
        qs = self.get_queryset()
        dfs = [(self.model, self._get_dataframe(qs))]
        if not is_root:
            return dfs

        for exporter in self._get_related_exporters():
            dfs.extend(exporter.get_dataframes(is_root=False))
        return dfs

    @staticmethod
    def _compress_to_zip(contents):
        f = StringIO()
        zip_file = ZipFile(f, 'w')
        for filename, body in contents:
            zip_file.writestr(filename, body)
        zip_file.close()
        out = f.getvalue()
        f.close()
        return 'zip', out

    def _conditionally_compress(self, extension, format_dataframe):
        dfs = self.get_dataframes()
        assert len(dfs) > 0

        if len(dfs) == 1:
            return extension, format_dataframe(dfs[0][1])
        return self._compress_to_zip([
            ('%s.%s' % (slugify(force_text(model._meta.verbose_name_plural)),
                        extension),
             format_dataframe(df)) for model, df in dfs])

    def to_json(self):
        return self._conditionally_compress(
            'json',
            lambda df: df.to_json(None, orient='records', date_format='iso'))

    def to_csv(self):
        return self._conditionally_compress(
            'csv', lambda df: df.to_csv(None, encoding='utf-8'))

    def to_xlsx(self):
        f = StringIO()
        # We have to specify a temporary file name,
        # but no file will be created.
        writer = pandas.ExcelWriter('temp.xlsx', engine='xlsxwriter')
        writer.book.filename = f
        for model, df in self.get_dataframes():
            sheet_name = force_text(model._meta.verbose_name_plural)
            df.to_excel(writer, sheet_name)
        writer.save()
        out = f.getvalue()
        f.close()
        return out

    def _to_response(self, extension, content, attachment=True):
        content_type = self.CONTENT_TYPES[extension]
        response = HttpResponse(content, content_type=content_type)
        filename = '[%s] %s %s' % (Site.objects.get_current().name,
                                   self.get_queryset().count(),
                                   self.model._meta.verbose_name_plural)
        disposition = 'filename="%s.%s"' % (slugify(filename), extension)
        if attachment:
            disposition += '; attachment'
        response['Content-Disposition'] = disposition
        return response

    def to_json_response(self):
        extension, content = self.to_json()
        return self._to_response(extension, content)

    def to_csv_response(self):
        extension, content = self.to_csv()
        return self._to_response(extension, content)

    def to_xlsx_response(self):
        return self._to_response('xlsx', self.to_xlsx())
