# coding: utf-8

from __future__ import unicode_literals
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from .base import Exporter


class Registry(dict):
    module_name = 'export'

    def autodiscover(self):
        for app in settings.INSTALLED_APPS:
            mod = import_module(app)
            try:
                import_module('%s.%s' % (app, self.module_name))
            except:
                if module_has_submodule(mod, self.module_name):
                    raise

    def add(self, exporter):
        model = exporter.model
        if model in exporter_registry:
            raise ValueError('An exporter is already registered '
                             'for this model')
        self[model] = exporter
        return exporter

    def __missing__(self, key):
        return Exporter


exporter_registry = Registry()
