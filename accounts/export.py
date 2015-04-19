# coding: utf-8

from __future__ import unicode_literals
from accounts.models import HierarchicUser
from exporter import exporter_registry, Exporter


@exporter_registry.add
class HierarchicUserExporter(Exporter):
    model = HierarchicUser
    columns = ('id', 'first_name', 'last_name')