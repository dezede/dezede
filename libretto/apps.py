from django.apps import AppConfig


class LibrettoConfig(AppConfig):
    name = 'libretto'

    def ready(self):
        # Register signals
        from . import signals
