from time import time

from django.apps import apps
from django.core.management import BaseCommand
from wagtail.search.index import Indexed

from dezede.search_backend import FixedPostgresIndex


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('model_label', nargs='*')

    def handle(self, *args, **options):
        for model in apps.get_models():
            if not issubclass(model, Indexed) or (
                options['model_label'] and model._meta.label not in options['model_label']
            ):
                continue
            self.stdout.write(f'Updating {model._meta.label} boosts ', ending='')
            start = time()
            FixedPostgresIndex('default').update_row_boosts(
                model,
                model.objects.only('pk').iterator(chunk_size=1000),
                stdout=self.stdout,
            )
            self.stdout.write(f' Done in {time() - start:.2f} seconds.')
