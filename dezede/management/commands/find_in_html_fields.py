from bs4 import BeautifulSoup

from django.apps import apps
from django.core.management import BaseCommand, CommandError

# Fields echoed by list_html_fields (app_label, model_name, field_name).
FIELDS = [
    ('accounts', 'HierarchicUser', 'presentation'),
    ('accounts', 'HierarchicUser', 'fonctions'),
    ('accounts', 'HierarchicUser', 'literature'),
    ('libretto', 'Etat', 'message'),
    ('libretto', 'Evenement', 'notes_publiques'),
    ('libretto', 'Evenement', 'notes_privees'),
    ('libretto', 'Individu', 'notes_publiques'),
    ('libretto', 'Individu', 'notes_privees'),
    ('libretto', 'Individu', 'biographie'),
    ('libretto', 'Profession', 'notes_publiques'),
    ('libretto', 'Profession', 'notes_privees'),
    ('libretto', 'Ensemble', 'notes_publiques'),
    ('libretto', 'Ensemble', 'notes_privees'),
    ('libretto', 'Source', 'notes_publiques'),
    ('libretto', 'Source', 'notes_privees'),
    ('libretto', 'Source', 'transcription'),
    ('libretto', 'Source', 'publications'),
    ('libretto', 'Source', 'developpements'),
    ('libretto', 'Source', 'presentation'),
    ('libretto', 'Source', 'contexte'),
    ('libretto', 'Source', 'sources_et_protocole'),
    ('libretto', 'Source', 'bibliographie'),
    ('libretto', 'Audio', 'notes_publiques'),
    ('libretto', 'Audio', 'notes_privees'),
    ('libretto', 'Video', 'notes_publiques'),
    ('libretto', 'Partie', 'notes_publiques'),
    ('libretto', 'Partie', 'notes_privees'),
    ('libretto', 'Oeuvre', 'notes_publiques'),
    ('libretto', 'Oeuvre', 'notes_privees'),
    ('libretto', 'Lieu', 'notes_publiques'),
    ('libretto', 'Lieu', 'notes_privees'),
    ('libretto', 'Lieu', 'historique'),
    ('dossiers', 'Dossier', 'publications'),
    ('dossiers', 'Dossier', 'developpements'),
    ('dossiers', 'Dossier', 'presentation'),
    ('dossiers', 'Dossier', 'contexte'),
    ('dossiers', 'Dossier', 'sources_et_protocole'),
    ('dossiers', 'Dossier', 'bibliographie'),
    ('examens', 'Level', 'help_message'),
    ('examens', 'TakenLevel', 'transcription'),
]


class Command(BaseCommand):
    help = (
        "Searches every field listed in FIELDS using BeautifulSoup's "
        "soup.select(), with the given CSS selector, and prints the field "
        "and object ID for each match."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'selector', help="CSS selector to search for, e.g. 'span.sc'.",
        )

    def handle(self, *args, **options):
        selector = options['selector']

        found_any = False
        for app_label, model_name, field_name in FIELDS:
            try:
                model = apps.get_model(app_label, model_name)
            except LookupError as e:
                raise CommandError(
                    f'Unknown model {model_name!r} in app {app_label!r}: {e}'
                )
            try:
                model._meta.get_field(field_name)
            except Exception as e:
                raise CommandError(
                    f'Unknown field {field_name!r} on {model._meta.label}: {e}'
                )

            queryset = model._default_manager.values_list(
                'pk', field_name
            ).iterator(chunk_size=1000)
            for pk, value in queryset:
                if not value:
                    continue
                soup = BeautifulSoup(str(value), 'html.parser')
                for tag in soup.select(selector):
                    found_any = True
                    self.stdout.write(
                        f'{model._meta.label}.{field_name} (pk={pk}): {tag}'
                    )

        if not found_any:
            self.stdout.write(self.style.WARNING('No match found.'))
