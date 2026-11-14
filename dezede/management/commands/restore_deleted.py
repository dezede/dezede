from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from wagtail.models import Revision, RevisionMixin


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
        except IntegrityError as e:
            raise CommandError(
                f'Cannot restore: a linked object was probably deleted ({e}).')
        self.stdout.write(self.style.SUCCESS('Restored.'))

    def build(self, source):
        # `Revision.as_object` needs the live object, which is gone.
        obj = source.content_type.model_class().from_serializable_data(
            source.content)
        obj.pk = obj._meta.pk.to_python(source.object_id)
        obj.latest_revision = None
        return obj

    def list_deleted(self, model, revisions):
        existing = {str(pk) for pk in model._base_manager.values_list(
            'pk', flat=True)}
        seen = set()
        for revision in revisions.only('object_id', 'object_str', 'created_at'):
            if revision.object_id in existing or revision.object_id in seen:
                continue
            seen.add(revision.object_id)
            self.stdout.write(
                f'{revision.object_id}\t{revision.created_at:%Y-%m-%d %H:%M}'
                f'\t{revision.object_str}')
