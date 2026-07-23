"""
Génère un jeu de correspondance d’exemple crédible pour le sous-site
« musicaLetters » (application ``correspondence``).

Pendant qu’elle peuple la base, cette commande corrige aussi la configuration
structurelle nécessaire pour que ``/musicaletters/`` réponde : elle crée (ou
réutilise) une page ``LetterIndex`` publiée et la désigne comme page racine du
``Site`` Wagtail par défaut. Sans cela, la racine du site reste la page d’accueil
Wagtail par défaut (sans propriétaire), ce qui fait planter
``dezede.viewsets.CustomPagesAPIViewSet.find_view`` et renvoie une 404 côté front.

Cette commande s’inscrit dans la continuité de ``generate_sample_data`` (mêmes
options, même propriétaire « sample_data », même approche sans dépendance
supplémentaire) et est d’ailleurs appelée par elle. Elle suppose que des
``Individu`` et des ``Lieu`` existent déjà (lancez ``generate_sample_data``
d’abord).

Exemples ::

    ./manage.py generate_sample_letters
    ./manage.py generate_sample_letters --scale 0.2 --seed 1 --flush

Pensez à lancer ``./manage.py update_index`` ensuite pour rendre la recherche
cohérente.
"""

from contextlib import contextmanager
from datetime import date
from urllib.parse import urlsplit
import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.signals import post_save
from django.utils.html import format_html_join, mark_safe
from django.utils.lorem_ipsum import paragraphs, words
from tqdm import tqdm
from wagtail.models import Page, Site

from correspondence.models import (
    Letter, LetterCorpus, LetterIndex, LetterRecipient, LetterSender,
)
from libretto.models.espace_temps import Lieu
from libretto.models.individu import Individu
from libretto.models.source import Source
from libretto.signals import update_related_search_items


# Même propriétaire que ``generate_sample_data``.
OWNER_USERNAME = 'sample_data'

# Volumétrie de base (échelle « medium »), multipliée par --scale.
BASE_COUNTS = {
    'corpus': 10,
    'lettres': 300,
}

INDEX_TITLE = 'musicaLetters'


@contextmanager
def search_indexing_disabled():
    """Débranche le signal d’indexation lié de ``libretto`` pendant la génération."""
    post_save.disconnect(update_related_search_items)
    try:
        yield
    finally:
        post_save.connect(update_related_search_items)


class Command(BaseCommand):
    help = ('Remplit le sous-site « musicaLetters » (correspondence) avec un '
            'corpus de lettres d’exemple et configure la page racine du site.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--scale', type=float, default=1.0,
            help='Multiplie les volumes de base (défaut : 1.0 ≈ medium).')
        parser.add_argument(
            '--seed', type=int, default=None,
            help='Graine aléatoire pour un jeu de données reproductible.')
        parser.add_argument(
            '--flush', action='store_true',
            help='Supprime d’abord les corpus et lettres générés '
                 'précédemment (limités au propriétaire « %s ») ; la page '
                 'd’index est conservée.' % OWNER_USERNAME)

    # -- Helpers ----------------------------------------------------------

    def n(self, key):
        return max(1, int(BASE_COUNTS[key] * self.scale))

    def random_date(self, start_year, end_year):
        start = date(start_year, 1, 1).toordinal()
        end = date(end_year, 12, 31).toordinal()
        return date.fromordinal(random.randint(start, end))

    def get_owner(self):
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=OWNER_USERNAME,
            defaults={'email': 'sample-data@example.com',
                      'first_name': 'Données', 'last_name': 'd’exemple'})
        if created:
            user.set_password(OWNER_USERNAME)
            user.save()
        return user

    # -- Étapes -----------------------------------------------------------

    def ensure_letter_index(self):
        """Crée (ou réutilise) la page d’index et la place en racine du site."""
        index = LetterIndex.objects.first()
        if index is None:
            root = Page.objects.get(depth=1)  # vraie racine de l’arbre Wagtail
            index = LetterIndex(title=INDEX_TITLE, owner=self.owner)
            root.add_child(instance=index)
            index.save_revision().publish()
        elif index.owner_id is None:
            index.owner = self.owner
            index.save(update_fields=['owner'])

        site = Site.objects.filter(is_default_site=True).first()
        if site is not None:
            # Aligne la racine et le hostname du site sur la configuration
            # réelle : une base neuve crée un site « localhost », d’où des URL
            # absolues pointant vers le mauvais hôte (clic → 404). On dérive le
            # hostname de WAGTAILADMIN_BASE_URL (dev : dezede.localhost,
            # prod : dezede.org), ce qui reste valable hors développement.
            base = urlsplit(settings.WAGTAILADMIN_BASE_URL)
            hostname = base.hostname or site.hostname
            port = base.port or (443 if base.scheme == 'https' else 80)
            changed = []
            if site.root_page_id != index.pk:
                site.root_page = index
                changed.append('root_page')
            if site.hostname != hostname:
                site.hostname = hostname
                changed.append('hostname')
            if site.port != port:
                site.port = port
                changed.append('port')
            if changed:
                site.save(update_fields=changed)

        # Supprime les pages Wagtail par défaut résiduelles (ex. « Welcome to
        # your new Wagtail site! ») restées au sommet de l’arbre : en tant que
        # sœurs de l’index, leur URL nulle casse le rendu du front. On ne touche
        # qu’aux pages génériques wagtailcore.Page, jamais aux pages typées.
        plain_page_ct = ContentType.objects.get_for_model(Page)
        for sibling in Page.objects.get(depth=1).get_children().exclude(pk=index.pk):
            if sibling.content_type_id == plain_page_ct.pk:
                sibling.delete()
        return index

    def create_corpus(self, index):
        """Crée ~N corpus, chacun rattaché à un individu distinct."""
        # Recharge l’index : un éventuel ``flush`` a pu invalider le cache
        # treebeard (``numchild``) de l’instance reçue.
        index = LetterIndex.objects.get(pk=index.pk)
        self.corpus = []
        individus = list(
            Individu.objects.filter(owner=self.owner).order_by('?')
            [:self.n('corpus')])
        for individu in tqdm(individus, desc='corpus'):
            corpus = LetterCorpus(
                title=str(individu)[:255], person=individu, owner=self.owner)
            index.add_child(instance=corpus)
            corpus.save_revision().publish()
            self.corpus.append(corpus)

    def make_transcription(self, source):
        if source is not None and source.transcription:
            return mark_safe(source.transcription)
        return format_html_join(
            '\n', '<p>{}</p>',
            [[text] for text in paragraphs(random.randint(1, 3), common=False)])

    def create_letters(self):
        sources = list(
            Source.objects.filter(owner=self.owner).exclude(transcription=''))
        lieux = list(Lieu.objects.filter(owner=self.owner))
        individus = list(Individu.objects.filter(owner=self.owner))

        for _i in tqdm(range(self.n('lettres')), desc='lettres'):
            corpus = random.choice(self.corpus)
            source = random.choice(sources) if sources else None
            role = random.choice(['sender', 'recipient', 'other'])
            storage = random.random() < 0.5

            title = (str(source)[:255] if source is not None
                     else 'Lettre — %s' % words(4, common=False))
            letter = Letter(
                title=title,
                owner=self.owner,
                writing_date=(source.date if source is not None and source.date
                              else self.random_date(1750, 1950)),
                writing_lieu=random.choice(lieux) if lieux else None,
                storage_place=random.choice(lieux) if storage and lieux else None,
                storage_call_number=(source.cote if storage and source is not None
                                     and source.cote else ''),
                source_url=source.url if source is not None and source.url else '',
                transcription=self.make_transcription(source),
                description=(format_html_join(
                    '\n', '<p>{}</p>',
                    [[t] for t in paragraphs(1, common=False)])
                    if random.random() < 0.2 else ''),
            )
            corpus.add_child(instance=letter)

            sender = (corpus.person if role == 'sender'
                      else random.choice(individus))
            recipient = (corpus.person if role == 'recipient'
                         else random.choice(individus))
            LetterSender.objects.create(letter=letter, person=sender)
            LetterRecipient.objects.create(letter=letter, person=recipient)
            letter.save_revision().publish()

    def flush(self):
        self.stdout.write('Suppression des corpus et lettres d’exemple existants…')
        # Supprimer un corpus efface son sous-arbre (lettres) via treebeard.
        for corpus in LetterCorpus.objects.filter(owner=self.owner):
            corpus.delete()

    # -- Entrée -----------------------------------------------------------

    @transaction.atomic
    def handle(self, **options):
        self.scale = options['scale']
        if options['seed'] is not None:
            random.seed(options['seed'])

        self.owner = self.get_owner()

        if not Individu.objects.filter(owner=self.owner).exists():
            self.stdout.write(self.style.WARNING(
                'Aucun individu « %s » trouvé : lancez d’abord '
                '« ./manage.py generate_sample_data ».' % OWNER_USERNAME))
            return

        index = self.ensure_letter_index()

        if options['flush']:
            self.flush()

        with search_indexing_disabled():
            self.create_corpus(index)
            self.create_letters()

        self.stdout.write(self.style.SUCCESS(
            'Correspondance d’exemple créée : %d corpus, %d lettres '
            '(index « %s » défini comme racine du site).' % (
                len(self.corpus),
                Letter.objects.filter(owner=self.owner).count(),
                index.title)))
        self.stdout.write(
            'Pensez à lancer « ./manage.py update_index » pour rendre '
            'la recherche cohérente.')
