from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .registry import exporter_registry


def export_csv(modeladmin, request, queryset):
    exporter = exporter_registry[queryset.model]
    return exporter(queryset).to_csv_response()
export_csv.short_description = _('Exporter en CSV')

admin.site.add_action(export_csv, 'export_csv')


def export_xlsx(modeladmin, request, queryset):
    exporter = exporter_registry[queryset.model]
    return exporter(queryset).to_xlsx_response()
export_xlsx.short_description = _('Exporter en XLSX')

admin.site.add_action(export_xlsx, 'export_xlsx')


def export_json(modeladmin, request, queryset):
    exporter = exporter_registry[queryset.model]
    return exporter(queryset).to_json_response()
export_json.short_description = _('Exporter en JSON')

admin.site.add_action(export_json, 'export_json')
