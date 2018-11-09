from accounts.models import HierarchicUser
from exporter.base import Exporter
from exporter.registry import exporter_registry


@exporter_registry.add
class HierarchicUserExporter(Exporter):
    model = HierarchicUser
    columns = ('id', 'first_name', 'last_name')
