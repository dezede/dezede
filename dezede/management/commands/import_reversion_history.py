import time

from django.core.management import BaseCommand, CommandError

from libretto import reversion_import as ri


class Command(BaseCommand):
    help = (
        'Imports the old django-reversion history of the authority models as '
        'Wagtail revisions, with a log entry each. It can be run again: '
        'versions already imported are skipped.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--model', action='append', choices=sorted(ri.FAMILIES),
            help='Only this model (repeatable). Source includes Audio and '
                 'Video. Default: all of them.')
        parser.add_argument(
            '--sample', type=int, metavar='N',
            help='Only N objects per model, always the same ones.')
        parser.add_argument(
            '--pk', type=int, action='append',
            help='Only the object with this primary key (repeatable).')
        parser.add_argument(
            '--batch-size', type=int, default=300,
            help='Objects per transaction (default 300).')
        parser.add_argument(
            '--reset', action='store_true',
            help='Do not import. Delete what an import made (its revisions '
                 'and log entries). Revisions made by Wagtail stay.')
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Do everything, then roll back.')

    def handle(
            self, *args, model, sample, pk, batch_size, dry_run, reset,
            **options):
        if sample is not None and sample < 1:
            raise CommandError('--sample must be positive.')
        if reset:
            counts = ri.reset_imported(dry_run=dry_run)
            for key, value in counts.items():
                self.stdout.write(f'  {key}: {value}')
            if dry_run:
                self.stdout.write(self.style.WARNING('Dry run: rolled back.'))
            return
        started = time.monotonic()
        self.last_line = 0
        ctx = ri.Context()

        def progress(family, done, total, stats):
            now = time.monotonic()
            if done < total and now - self.last_line < 10:
                return
            self.last_line = now
            self.stdout.write(
                f'  {family}: {done}/{total} objects, '
                f'{stats["revisions"]} revisions, {stats["log_only"]} log '
                f'only, {stats["doubtful"]} doubtful, '
                f'{now - started:.0f} s')

        total = {}
        for family in model or ri.FAMILIES:
            self.stdout.write(f'{family}...')
            begin = time.monotonic()
            stats, unknown = ri.import_family(
                family, sample=sample, only=pk, batch_size=batch_size,
                dry_run=dry_run, progress=progress, ctx=ctx)
            self.stdout.write(self.style.SUCCESS(
                f'{family}: done in {time.monotonic() - begin:.0f} s'))
            for key in sorted(stats):
                self.stdout.write(f'    {key}: {stats[key]}')
            for (label, key), count in unknown.most_common():
                self.stdout.write(self.style.WARNING(
                    f'    unknown key {label}.{key}: {count}'))
            total[family] = stats
        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run: rolled back.'))
