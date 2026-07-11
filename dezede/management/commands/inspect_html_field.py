from collections import Counter
from html.parser import HTMLParser

from django.apps import apps
from django.core.management import BaseCommand, CommandError
from django.db import models

DEFAULT_APP_LABELS = [
    'accounts', 'afo', 'common', 'dezede', 'dossiers', 'examens', 'libretto',
]

INTERNAL_HREF_PREFIX = 'https://dezede.org/'
EXTERNAL_HREF_PLACEHOLDER = '<external link>'


class _Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.combos = Counter()
        self.examples = {}

    def _handle(self, tag, attrs):
        attrs = [
            (name, EXTERNAL_HREF_PLACEHOLDER)
            if name == 'href' and value and not value.startswith(INTERNAL_HREF_PREFIX)
            else (name, value)
            for name, value in attrs
        ]
        key = (tag, tuple(sorted(attrs)))
        self.combos[key] += 1
        if key not in self.examples:
            self.examples[key] = self.get_starttag_text()

    def handle_starttag(self, tag, attrs):
        self._handle(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._handle(tag, attrs)


class Command(BaseCommand):
    help = (
        "Lists an example of each tag/attributes/values combination, and the "
        "number of '\\n' newlines found in a field of a model. "
        "By default (no app_label given), inspects every TextField/HTMLField of "
        f"every model in {', '.join(DEFAULT_APP_LABELS)}."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label',
            nargs='?',
            help="App label, e.g. 'libretto'. If omitted, all apps are inspected.",
        )
        parser.add_argument(
            'model_name',
            nargs='?',
            help="Model name, e.g. 'Oeuvre'. If omitted, all models are inspected.",
        )
        parser.add_argument(
            'field_name',
            nargs='?',
            help=(
                "Name of the field to inspect. If omitted, every "
                "TextField/HTMLField of the selected model(s) is inspected."
            ),
        )
        parser.add_argument(
            '--per-field',
            action='store_true',
            help=(
                "Also display the results for each field individually, in "
                "addition to the global results. By default, only the "
                "global results are displayed."
            ),
        )

    def handle(self, *args, **options):
        app_label = options['app_label']
        model_name = options['model_name']
        field_name = options['field_name']

        if model_name and not app_label:
            raise CommandError('model_name requires app_label to be given as well.')
        if field_name and not model_name:
            raise CommandError('field_name requires model_name to be given as well.')

        fields = list(self._iter_fields(app_label, model_name, field_name))
        show_per_field = options['per_field'] or len(fields) <= 1

        global_collector = _Collector()
        global_newlines = 0
        global_rows = 0

        for model, field in fields:
            collector, rows, newlines = self._inspect(model, field, show_per_field)
            global_collector.combos.update(collector.combos)
            for key, example in collector.examples.items():
                global_collector.examples.setdefault(key, example)
            global_rows += rows
            global_newlines += newlines

        if len(fields) > 1:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n=== GLOBAL ({len(fields)} fields, {global_rows} rows) ==='
                )
            )
            self._dump_combos(global_collector)
            self.stdout.write(f"'\\n' newlines: {global_newlines}")

    def _iter_fields(self, app_label, model_name, field_name):
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

        if model_name:
            models_list = [m for m in models_list if m.__name__ == model_name]
            if not models_list:
                raise CommandError(
                    f'Unknown model {model_name!r} in app {app_label!r}.'
                )

        for model in models_list:
            if field_name:
                try:
                    field = model._meta.get_field(field_name)
                except Exception as e:
                    raise CommandError(
                        f'Unknown field {field_name!r} on {model._meta.label}: {e}'
                    )
                yield model, field
                continue

            for field in model._meta.get_fields():
                if isinstance(field, models.TextField):
                    yield model, field

    def _inspect(self, model, field, show=True):
        model_label = model._meta.label
        field_name = field.name

        collector = _Collector()
        newlines = 0
        rows = 0

        queryset = model._default_manager.values_list('pk', field_name).iterator(
            chunk_size=1000
        )
        for pk, value in queryset:
            rows += 1
            if not value:
                continue
            value = str(value)
            newlines += value.count('\n')
            collector.feed(value)
        collector.close()

        if show:
            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    f'\n=== {model_label}.{field_name} ({rows} rows) ==='
                )
            )

            self._dump_combos(collector)

            self.stdout.write(f"'\\n' newlines: {newlines}")

        return collector, rows, newlines

    def _dump_combos(self, collector):
        combos = collector.combos
        title = 'Tag/attributes/values combinations'
        self.stdout.write(f'{title} ({len(combos)} distinct):')
        if not combos:
            self.stdout.write('  (none)')
            return
        for key, count in combos.most_common():
            example = collector.examples[key]
            self.stdout.write(f'  {count}: {example}')
