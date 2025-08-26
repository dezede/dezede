from django.apps import apps
from django.core.management import BaseCommand

from db_search.models import SearchVectorAbstractModel


class Command(BaseCommand):
    def handle(self, *args, **options):
        for model in apps.get_models():
            if issubclass(model, SearchVectorAbstractModel) and model.dezede_search_fields:
                self.stdout.write(f'Indexing {model.__name__}…')
                model.update_all_search_vectors()
                self.stdout.write('Done.')
                self.stdout.write('-----')
