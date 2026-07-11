import re

from django.apps import apps
from django.core.management import BaseCommand, CommandError
from django.db import models
from tinymce.models import HTMLField

DEFAULT_APP_LABELS = [
    'accounts', 'afo', 'common', 'dezede', 'dossiers', 'examens', 'libretto',
]

TAG_RE = re.compile(r'<\s*/?\s*[a-zA-Z][a-zA-Z0-9]*(?:\s[^<>]*)?>')


class Command(BaseCommand):
    help = (
        "Scans every HTMLField/TextField of every model in "
        f"{', '.join(DEFAULT_APP_LABELS)} (or the given app_label) and lists "
        "the ones whose stored data actually contains HTML markup, along "
        "with how many rows are affected."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label',
            nargs='?',
            help="App label, e.g. 'libretto'. If omitted, all apps are scanned.",
        )

    def handle(self, *args, **options):
        app_label = options['app_label']

        if app_label:
            try:
                app_config = apps.get_app_config(app_label)
            except LookupError as e:
                raise CommandError(f'Unknown app {app_label!r}: {e}')
            models_list = list(app_config.get_models())
        else:
            models_list = [
                model for model in apps.get_models()
                if model._meta.app_label in DEFAULT_APP_LABELS
            ]

        found_any = False
        for model in models_list:
            for field in model._meta.get_fields():
                if not isinstance(field, models.TextField):
                    continue
                matches, total = self._scan(model, field)
                if matches:
                    found_any = True
                    field_type = (
                        'HTMLField' if isinstance(field, HTMLField)
                        else 'TextField'
                    )
                    self.stdout.write(
                        f'{model._meta.label}.{field.name} ({field_type}): '
                        f'{matches}/{total} rows contain HTML'
                    )

        if not found_any:
            self.stdout.write(self.style.WARNING('No HTML found in any field.'))

    def _scan(self, model, field):
        matches = 0
        total = 0
        queryset = model._default_manager.values_list(
            'pk', field.name
        ).iterator(chunk_size=1000)
        for pk, value in queryset:
            total += 1
            if value and TAG_RE.search(str(value)):
                matches += 1
        return matches, total
