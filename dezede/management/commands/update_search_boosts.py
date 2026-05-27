from django.apps import apps
from django.core.management import BaseCommand
from wagtail.search.index import Indexed

from dezede.search_backend import FixedPostgresIndex


class Command(BaseCommand):
    def handle(self, *args, **options):
        for model in apps.get_models():
            if not issubclass(model, Indexed):
                continue
            self.stdout.write(f'Updating {model._meta.label} boosts… ', ending='')
            FixedPostgresIndex('default').update_row_boosts(model, model.objects.iterator(chunk_size=1000))
            self.stdout.write('Done.')
