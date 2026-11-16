from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand, CommandError
from django.db import DatabaseError, connection, transaction
from modelcluster.fields import ParentalKey
from modelcluster.models import get_all_child_relations
from wagtail.models import ModelLogEntry, Revision, RevisionMixin

from libretto.reversion_import import doubtful_entry, doubtful_message


class Command(BaseCommand):
    help = (
        'Restores a deleted object from its last Wagtail revision. '
        'Without a primary key, lists the deleted objects of the model.'
    )

    def add_arguments(self, parser):
        parser.add_argument('model_label', help='For example libretto.Evenement')
        parser.add_argument('pk', nargs='?')
        parser.add_argument(
            '--revision', type=int,
            help='Revision id to restore, instead of the last one.')
        parser.add_argument(
            '--user',
            help='Username shown in the history as the one who restored.')
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Show what would be restored, without saving.')

    def handle(
            self, *args, model_label, pk, revision, user, dry_run, **options):
        try:
            model = apps.get_model(model_label)
        except (LookupError, ValueError) as e:
            raise CommandError(e)
        if not issubclass(model, RevisionMixin):
            raise CommandError(f'{model._meta.label} has no revisions.')
        if user is not None:
            User = get_user_model()
            try:
                user = User.objects.get_by_natural_key(user)
            except User.DoesNotExist:
                raise CommandError(f'No user “{user}”.')

        # Revisions of a multi-table child (Audio) are stored under its
        # parent's base content type, like Wagtail does.
        parents = model._meta.get_parent_list()
        revisions = Revision.objects.filter(
            base_content_type=ContentType.objects.get_for_model(
                parents[-1] if parents else model),
        ).order_by('-created_at', '-pk')
        if parents:
            revisions = revisions.filter(
                content_type=ContentType.objects.get_for_model(model))

        if pk is None:
            self.list_deleted(model, revisions)
            return

        if model._base_manager.filter(pk=pk).exists():
            raise CommandError(f'{model._meta.label} {pk} is not deleted.')
        revisions = revisions.filter(object_id=str(pk))
        if revision is not None:
            revisions = revisions.filter(pk=revision)
        source = revisions.first()
        if source is None:
            raise CommandError(
                f'No revision found for {model._meta.label} {pk}.')

        doubtful = doubtful_entry(source.pk)
        if doubtful:
            raise CommandError(
                f'Revision {source.pk} is doubtful. '
                + doubtful_message(doubtful) +
                ' Choose another one with --revision.')

        missing = self.missing_targets(
            source.content_type.model_class(), source.content)
        if missing:
            raise CommandError(
                'Cannot restore: linked objects are gone or missing (%s). '
                'Choose an older revision with --revision.' % ', '.join(missing[:8])
                + (' …' if len(missing) > 8 else ''))
        obj = self.build(source)

        self.stdout.write(
            f'Revision {source.pk} of {source.created_at:%Y-%m-%d %H:%M}: '
            f'{type(obj)._meta.label} {pk} “{source.object_str}”')
        if dry_run:
            return

        try:
            with transaction.atomic():
                obj.save()
                # Children whose parent row is missing are dropped when the
                # object is built. Building it again once the row exists keeps
                # them.
                obj = self.build(source)
                obj.save()
                obj.save_revision(
                    user=user, previous_revision=source, log_action=True,
                    clean=False)
                # Foreign keys are checked at the end of the transaction,
                # which would be outside this try.
                connection.check_constraints()
        except DatabaseError as e:
            raise CommandError(f'Cannot restore: {e}')
        self.stdout.write(self.style.SUCCESS('Restored.'))

    def build(self, source):
        # `Revision.as_object` needs the live object, which is gone.
        obj = source.content_type.model_class().from_serializable_data(
            source.content)
        obj.pk = obj._meta.pk.to_python(source.object_id)
        obj.latest_revision = None
        self.free_row_ids(obj)
        return obj

    def missing_targets(self, model, content):
        """
        The linked objects that no longer exist. ``from_serializable_data``
        would quietly empty those links, losing data.
        """
        wanted = {}
        empty = []

        def walk(model, row):
            for field in model._meta.concrete_fields:
                if (not field.many_to_one or field.primary_key
                        or isinstance(field, ParentalKey)):
                    continue
                value = row.get(field.name)
                if value is not None:
                    wanted.setdefault(field.related_model, set()).add(value)
                elif not field.null:
                    # Old snapshots from before the field existed.
                    empty.append(f'{model._meta.label}.{field.name} is empty')
            for rel in get_all_child_relations(model):
                for child in row.get(rel.get_accessor_name(), ()):
                    walk(rel.related_model, child)
        walk(model, content)
        missing = sorted(set(empty))
        for target, pks in wanted.items():
            found = set(target._base_manager.filter(
                pk__in=pks).values_list('pk', flat=True))
            missing += [
                f'{target._meta.label} {pk}' for pk in sorted(pks - found)]
        return missing

    def free_row_ids(self, obj):
        """
        A row id that exists is another parent's row now: the row would be
        moved. It is saved as a new row instead.
        """
        rows = {}

        def walk(instance):
            for rel in get_all_child_relations(type(instance)):
                for child in getattr(instance, rel.get_accessor_name()).all():
                    if child.pk is not None:
                        rows.setdefault(type(child), []).append(child)
                    walk(child)
        walk(obj)
        for model, children in rows.items():
            taken = set(model._base_manager.filter(
                pk__in=[c.pk for c in children],
            ).values_list('pk', flat=True))
            for child in children:
                if child.pk in taken:
                    child.pk = None

    def list_deleted(self, model, revisions):
        existing = {str(pk) for pk in model._base_manager.values_list(
            'pk', flat=True)}
        seen = {}
        for revision in revisions.only(
                'object_id', 'object_str', 'created_at'):
            if revision.object_id in existing or revision.object_id in seen:
                continue
            seen[revision.object_id] = revision
        doubtful = set(ModelLogEntry.objects.filter(
            revision_id__in=[r.pk for r in seen.values()],
            data__doubtful=True,
        ).values_list('revision_id', flat=True))
        for revision in seen.values():
            mark = '\t(douteuse)' if revision.pk in doubtful else ''
            self.stdout.write(
                f'{revision.object_id}\t{revision.created_at:%Y-%m-%d %H:%M}'
                f'\t{revision.object_str}{mark}')
