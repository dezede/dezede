from traceback import print_exc

from django.apps import apps
from django.core.exceptions import FieldError
from django.core.management import BaseCommand
from tqdm import tqdm

from wagtail.images import get_image_model
from wagtail.images.models import Rendition
from wagtail.images.api.fields import ImageRenditionField


class Command(BaseCommand):
    help = (
        "Generates all the missing thumbnails to speed up the initial load"
        "of image-intensive pages."
    )

    def handle(self, *args, **options):
        image_model = get_image_model()

        for image in tqdm(image_model.objects.all(), desc='Admin thumbnails…'):
            try:
                image.get_rendition('max-165x165')
            except (Rendition.DoesNotExist, OSError):
                print_exc()

        for model in apps.get_models():
            for api_field in getattr(model, 'api_fields', []):
                # TODO: Handle images deeply nested in streamfields and rich texts.
                if not isinstance(api_field.serializer, ImageRenditionField):
                    continue
                try:
                    for image in tqdm(
                        image_model.objects.filter(
                            pk__in=model.objects.values(api_field.serializer.source or api_field.name),
                        ),
                        desc=f'{model.__name__}.{api_field.name} frontend thumbnails…',
                    ):
                        try:
                            api_field.serializer.to_representation(image)
                        except (image_model.DoesNotExist, OSError):
                            print_exc()
                except FieldError:
                    continue
