from django.apps import apps
from django.contrib.admin.models import LogEntry
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import Manager, QuerySet
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django_rq import job
import django_rq
from haystack.signals import BaseSignalProcessor
from wagtail.models import Page

from common.utils.html import sanitize_html
from .forms import FasterModelChoiceIterator
from .search_indexes import get_haystack_index


@receiver(pre_save)
def handle_whitespaces(sender, **kwargs):
    # We skip LogEntry because the logged entry has already been saved
    # (and sanitized). Skip also all the wagtail models.
    if issubclass(sender, (LogEntry, Page)) or 'wagtail' in sender._meta.app_label:
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


def get_obj_key(obj, id_attr='pk'):
    meta = obj._meta
    return '%s.%s.%s' % (
        meta.app_label, meta.model_name, getattr(obj, id_attr),
    )


def get_stale_objects(instance, explored=None, all_relations=False):
    if explored is None:
        explored = []

    if instance is None:
        return

    obj_key = get_obj_key(instance)
    if obj_key in explored:
        return

    yield instance

    explored.append(obj_key)

    relations = getattr(instance, 'invalidated_relations_when_saved',
                        lambda all_relations: ())(all_relations=all_relations)
    for relation in relations:
        try:
            related = getattr(instance, relation)
        except ObjectDoesNotExist:
            continue
        if isinstance(related, Manager):
            related = related.all()
        if callable(related):
            related = related()
        if isinstance(related, QuerySet):
            for obj in related:
                for sub_obj in get_stale_objects(
                        obj, explored, all_relations=all_relations):
                    yield sub_obj
        else:
            for sub_related in get_stale_objects(
                    related, explored, all_relations=all_relations):
                yield sub_related


def auto_update_haystack(action, instance):
    for obj in get_stale_objects(instance, all_relations=True):
        model = obj.__class__

        index = get_haystack_index(model)
        if index is None:
            continue

        if action == 'delete':
            index.remove_object(obj)
        else:
            index.update_object(obj)


@job
def auto_invalidate(action, app_label, model_name, pk):
    model = apps.get_model(app_label, model_name)

    if action == 'delete':
        # Quand un objet est supprimé, la seule chose à faire est de supprimer
        # l'entrée du moteur de recherche.  En effet, aucun autre objet ne
        # de devrait être impacté car on a protégé les FK pour éviter
        # les suppressions en cascade.
        # WARNING: À surveiller tout de même.
        index = get_haystack_index(model)
        if index is not None:
            index.remove_object('%s.%s.%s' % (app_label, model_name, pk))
        return

    try:
        auto_update_haystack(action, model._default_manager.get(pk=pk))
    except model.DoesNotExist:
        pass  # The object was deleted in the meantime.


class AutoInvalidatorSignalProcessor(BaseSignalProcessor):
    def setup(self):
        post_save.connect(self.enqueue_save)
        pre_delete.connect(self.enqueue_delete)

    def teardown(self):
        post_save.disconnect(self.enqueue_save)
        pre_delete.disconnect(self.enqueue_delete)

    def enqueue_save(self, sender, instance, created, **kwargs):
        def inner():
            if created:
                return self.enqueue('create', instance, sender, **kwargs)
            return self.enqueue('save', instance, sender, **kwargs)
        return connection.on_commit(inner)

    def enqueue_delete(self, sender, instance, **kwargs):
        return self.enqueue('delete', instance, sender, **kwargs)

    def enqueue(self, action, instance, sender, **kwargs):
        if sender._meta.label in {
            'admin.LogEntry', 'sessions.Session', 'reversion.Revision',
            'reversion.Version', 'migrations.Migration',
            'wagtailimages.Image', 'wagtailimages.Rendition',
        }:
            return

        django_rq.enqueue(
            auto_invalidate,
            args=(action,
                  instance._meta.app_label, instance._meta.model_name,
                  instance.pk),
            result_ttl=0,  # Don’t store the result.
        )


FasterModelChoiceIterator.register_cleanup_signal()
