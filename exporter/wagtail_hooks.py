from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.snippets.bulk_actions.snippet_bulk_action import SnippetBulkAction

from .registry import exporter_registry


class ExportBulkAction(SnippetBulkAction):
    template_name = 'exporter/bulk_actions/confirm_export.html'
    action_priority = 10
    response_method = None  # name of the ``Exporter`` method returning an HttpResponse
    export_format = None    # human-readable format name, shown on the confirmation page

    def get_scoped_queryset(self):
        """Base queryset restricted to what the user is allowed to see."""
        qs = self.model._default_manager.all()
        if is_owner_scoped(self.model):
            qs = scope_to_owner(qs, self.request.user)
        return qs

    def get_all_objects_in_listing_query(self, parent_id):
        return self.get_scoped_queryset().values_list('pk', flat=True)

    def get_queryset(self, model, object_ids):
        return self.get_scoped_queryset().filter(pk__in=object_ids)

    def prepare_action(self, objects, objects_without_access):
        queryset = self.model._default_manager.filter(
            pk__in=[obj.pk for obj in objects])
        exporter = exporter_registry[self.model](queryset)
        return getattr(exporter, self.response_method)()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['export_format'] = self.export_format
        return context


@hooks.register('register_bulk_action')
class ExportCSVBulkAction(ExportBulkAction):
    display_name = _('Exporter en CSV')
    aria_label = _('Exporter en CSV les éléments sélectionnés')
    action_type = 'export_csv'
    export_format = 'CSV'
    response_method = 'to_csv_response'


@hooks.register('register_bulk_action')
class ExportXLSXBulkAction(ExportBulkAction):
    display_name = _('Exporter en XLSX')
    aria_label = _('Exporter en XLSX les éléments sélectionnés')
    action_type = 'export_xlsx'
    export_format = 'XLSX'
    response_method = 'to_xlsx_response'


@hooks.register('register_bulk_action')
class ExportJSONBulkAction(ExportBulkAction):
    display_name = _('Exporter en JSON')
    aria_label = _('Exporter en JSON les éléments sélectionnés')
    action_type = 'export_json'
    export_format = 'JSON'
    response_method = 'to_json_response'
