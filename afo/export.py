# coding: utf-8

from __future__ import unicode_literals
from exporter import exporter_registry
from libretto.export import CommonModelExporter
from .models import EvenementAFO, LieuAFO


@exporter_registry.add
class EvenementAFOExporter(CommonModelExporter):
    model = EvenementAFO


@exporter_registry.add
class LieuAFOExporter(CommonModelExporter):
    model = LieuAFO
