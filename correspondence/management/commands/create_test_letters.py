from random import choice

from django.core.management import BaseCommand
from django.core.files.base import ContentFile
from django.db.models import Q
from tqdm import tqdm
from wagtail.images.models import Image

from common.utils.file import FileAnalyzer
from correspondence.models import Letter, LetterCorpus, LetterImage, LetterRecipient
from libretto.models.espace_temps import Lieu
from libretto.models.individu import Individu
from libretto.models.source import Source


class Command(BaseCommand):
    def handle(self, **options):
        corpus = LetterCorpus.objects.all()[0]
        corpus.get_children().delete()
        Image.objects.all().delete()
        for source in tqdm(
            Source.objects.filter(
                ~Q(transcription='') & Q(type_fichier=FileAnalyzer.IMAGE),
            )
        ):
            image = None
            try:
                if source.fichier:
                    image = Image(
                        title=source.fichier.name,
                        file=ContentFile(source.fichier.read(), name=source.fichier.name),
                    )
                    image.save()
            except FileNotFoundError:
                pass
            person_choice = choice(['sender', 'recipient', 'other'])
            letter = Letter(
                title=str(source)[:255],
                sender=(
                    corpus.person if person_choice == 'sender'
                    else Individu.objects.order_by('?')[0]
                ),
                writing_date=source.date,
                writing_lieu=Lieu.objects.order_by('?')[0],
                transcription=source.transcription,
            )
            corpus.add_child(instance=letter)
            if image is not None:
                LetterImage.objects.create(
                    letter=letter,
                    name=f"p. {source.page}" or "p. 1",
                    image=image,
                )
            LetterRecipient.objects.create(
                letter=letter,
                person=(
                    corpus.person if person_choice == 'recipient'
                    else Individu.objects.order_by('?')[0]
                ),
            )
            letter.save_revision().publish()
