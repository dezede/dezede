from django.apps import apps
from django.core.management import BaseCommand
from tqdm import tqdm

from libretto.models.base import CommonModel


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'model_label',
            nargs='*',
            choices=[model._meta.label for model in apps.get_models()],
        )

    def handle(self, *args, **options):
        model_labels = options['model_label']
        models = [
            model for model in apps.get_models()
            if model._meta.label in model_labels
        ]

        for model in models:
            if issubclass(model, CommonModel):
                for instance in tqdm(
                    model.objects.all(), total=model.objects.count(),
                    desc=model._meta.label
                ):
                    instance.update_cached_related_label()
