from itertools import batched
from typing import Type
from django.apps import apps
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session
from django.db import connections
from django.db.backends.signals import connection_created
from django.db.models import QuerySet, Model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_rq import job
import django_rq
from reversion.models import Revision, Version
from wagtail.models import Page, Orderable
from wagtail.search.backends import get_search_backend

from common.utils.html import sanitize_html
from dezede.search_backend import get_search_relations
from .forms import FasterModelChoiceIterator


def is_sender_ignored(sender: Type[Model]) -> bool:
    # We skip LogEntry because the logged entry has already been saved
    # (and sanitized). Skip also all the wagtail models.
    return issubclass(
        sender, (LogEntry, Page, Session, Revision, Version, Orderable)
    ) or sender._meta.label in {
        'migrations.Migration',
    } or 'wagtail' in sender._meta.app_label or any(
        is_sender_ignored(base) for base in sender.__bases__
        # Skip bases that are not subclasses of Model,
        # and skip Model itself as it has no _meta defined.
        if issubclass(base, Model) and base is not Model and not base._meta.abstract
    )


@receiver(pre_save)
def handle_whitespaces(sender, **kwargs):
    if is_sender_ignored(sender):
        return

    # We start by stripping all leading and trailing whitespaces.
    obj = kwargs['instance']
    for field_name in [f.attname for f in obj._meta.fields]:
        v = getattr(obj, field_name)
        if hasattr(v, 'strip'):
            setattr(obj, field_name, sanitize_html(v.strip()))
    # Then we call the specific whitespace handler of the model (if it exists).
    if hasattr(obj, 'handle_whitespaces'):
        obj.handle_whitespaces()


# FIXME: remove workaround when upgrading django-tree
def _register_tree_path_dumper(connection):
    """
    Make django-tree's ``Path`` type adaptable on a single DB connection.

    django-tree registers its psycopg ``Path`` dumper on the *global*
    ``psycopg.adapters`` map (in ``TreeAppConfig.ready()``), but Django's
    psycopg3 connections build their own adapter map and do not inherit that
    global registration. Without this, saving any tree model (e.g. ``Oeuvre``,
    ``Lieu``) raises ``cannot adapt type 'Path'`` because the raw ``Path``
    reaches psycopg (``ArrayField.get_db_prep_value`` skips non-list values, so
    ``PathField.get_prep_value`` is never called). Mirrors
    ``tree.types.Path.register_psycopg3`` but targets the connection's adapters.
    """
    if connection.vendor != 'postgresql' or connection.connection is None:
        return
    import psycopg
    from psycopg.types.string import StrDumper
    from tree.types import Path

    class PathDumper(StrDumper):
        def quote(self, obj):
            return psycopg.sql.quote(obj.value).encode()

    connection.connection.adapters.register_dumper(Path, PathDumper)


# FIXME: remove workaround when upgrading django-tree
@receiver(connection_created)
def register_tree_path_psycopg_dumper(sender, connection, **kwargs):
    # Register on every newly-opened connection (the idiomatic place for
    # custom psycopg types).
    _register_tree_path_dumper(connection)


# FIXME: remove workaround when upgrading django-tree
# Also cover any connection already open before this receiver was connected
# (persistent connections — ``CONN_MAX_AGE`` is unset — would otherwise never
# pick up the dumper, since ``connection_created`` only fires on new ones).
for _conn in connections.all():
    _register_tree_path_dumper(_conn)


def get_stale_objects(instance) -> list[QuerySet]:
    model_querysets = {}
    for related_model, lookups in get_search_relations()[instance._meta.model]['related'].items():
        for lookup in lookups:
            qs = related_model.objects.filter(**{lookup: instance})
            if related_model in model_querysets:
                model_querysets[related_model] |= qs
            else:
                model_querysets[related_model] = qs

    return [qs.distinct() for qs in model_querysets.values()]


def auto_update_wagtail_search(instance: Model):
    s = get_search_backend()
    for qs in get_stale_objects(instance):
        qs = qs.prefetch_related(*get_search_relations()[qs.model]['contained_relations'])
        index = s.get_index_for_model(qs.model)
        for batch in batched(qs.iterator(chunk_size=1000), n=1000):
            index.add_items(qs.model, batch)


@job
def auto_invalidate(app_label, model_name, pk):
    model = apps.get_model(app_label, model_name)
    try:
        auto_update_wagtail_search(model._default_manager.get(pk=pk))
    except model.DoesNotExist:
        pass  # The object was deleted in the meantime.


@receiver(post_save)
def update_related_search_items(sender, instance, **kwargs):
    if is_sender_ignored(sender):
        return

    django_rq.enqueue(
        auto_invalidate,
        args=(instance._meta.app_label, instance._meta.model_name, instance.pk),
        result_ttl=0,  # Don’t store the result.
    )


FasterModelChoiceIterator.register_cleanup_signal()
