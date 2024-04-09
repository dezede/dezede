from django.apps import AppConfig


class DbSearchConfig(AppConfig):
    name = 'db_search'

    def ready(self):
        # Registers signal receivers.
        from . import signals
