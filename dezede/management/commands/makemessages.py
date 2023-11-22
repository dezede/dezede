from django.core.management.commands import makemessages


class Command(makemessages.Command):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--no-fuzzy-matching', action='store_true')

    def handle(self, *args, **options):
        if options['no_fuzzy_matching']:
            self.msgmerge_options = self.msgmerge_options[:] + [
                '--no-fuzzy-matching',
            ]
        super().handle(*args, **options)
