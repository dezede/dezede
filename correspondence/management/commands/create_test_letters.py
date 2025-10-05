from functools import lru_cache
from random import choice, choices, randrange, random
from typing import List, Union
from uuid import uuid4

from django.core.management import BaseCommand, call_command
from django.core.files.base import ContentFile
from django.utils.html import format_html_join
from django.utils.lorem_ipsum import words, paragraphs
from django.utils.safestring import mark_safe
from tqdm import tqdm
from wagtail.images.models import Image
from willow.image import UnrecognisedImageFormatError

from common.utils.file import FileAnalyzer
from correspondence.models import Letter, LetterCorpus, LetterImage, LetterRecipient, LetterSender
from libretto.models.espace_temps import Lieu
from libretto.models.evenement import Evenement
from libretto.models.individu import Individu
from libretto.models.oeuvre import Oeuvre, Partie
from libretto.models.personnel import Ensemble
from libretto.models.source import Source


class Command(BaseCommand):
    def create_image(self, source: Source) -> Union[Image, None]:
        try:
            if source.fichier:
                image = Image(
                    title=source.fichier.name,
                    file=ContentFile(source.fichier.read(), name=source.fichier.name),
                )
                image.save()
                return image
        except (FileNotFoundError, UnrecognisedImageFormatError):
            pass

    @lru_cache(maxsize=1000)
    def get_children_sources(self, source: Source) -> List[Source]:
        if source.fichier and source.type_fichier == FileAnalyzer.IMAGE:
            return [source]
        return [child for child in source.children_images()] or [source]

    def create_images(self, source: Source) -> List[Image]:
        return filter(bool, [self.create_image(child) for child in self.get_children_sources(source)[:randrange(1, 20)]])

    def get_transcription(self, source: Source) -> str:
        return format_html_join('\n', '{}', [[mark_safe(child.transcription)] for child in self.get_children_sources(source)])

    def handle(self, **options):
        corpus = LetterCorpus.objects.all()[0]
        corpus.get_children().delete()
        Image.objects.all().delete()
        call_command('fixtree')
        for source in tqdm(
                Source.objects.exclude(transcription='').filter(type_fichier__isnull=True).order_by('?')[:100]
                | Source.objects.exclude(transcription='').filter(type_fichier=FileAnalyzer.IMAGE).order_by('?')[:100]
                | Source.objects.filter(
                    children__type_fichier=FileAnalyzer.IMAGE,
                ).order_by('?')[:100]
        ):
            person_choice = choice(['sender', 'recipient', 'other'])
            storage_choice = choice([True, False])
            letter = Letter(
                title=str(source)[:255],
                writing_date=source.date,
                writing_lieu=Lieu.objects.order_by('?')[0],
                edition=choice([words(3, common=False), '']),
                storage_place=Lieu.objects.order_by('?').first() if storage_choice else None,
                storage_call_number=source.cote if storage_choice else '',
                source_url=source.url,
                transcription=self.get_transcription(source),
                description=format_html_join('\n', '<p>{}</p>', [[text] for text in paragraphs(3, common=False)]) if random() > 0.8 else '',
            )
            corpus.add_child(instance=letter)

            letter_images = []
            for i, image in enumerate(self.create_images(source)):
                reference_models = choices([Individu, Lieu, Partie, Oeuvre, Evenement, Ensemble], k=randrange(0, 10))
                letter_images.append(
                    LetterImage(
                        letter=letter,
                        image=image,
                        name=f"p. {source.page}" if source.page else f"p. {len(letter_images) + 1}",
                        sort_order=i,
                    )
                )
            LetterImage.objects.bulk_create(letter_images)

            LetterSender.objects.create(
                letter=letter,
                person=(
                    corpus.person if person_choice == 'sender'
                    else Individu.objects.order_by('?')[0]
                ),
            )
            LetterRecipient.objects.create(
                letter=letter,
                person=(
                    corpus.person if person_choice == 'recipient'
                    else Individu.objects.order_by('?')[0]
                ),
            )
            letter.save_revision().publish()

        call_command('generate_thumbnails')
