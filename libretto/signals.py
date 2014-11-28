# coding: utf-8

from __future__ import unicode_literals
from django.contrib.admin.models import LogEntry
from django.contrib.sessions.models import Session
from django.db import connection
from django.db.models import get_model
from django.db.models.signals import post_save, pre_delete
from django_rq import job
import django_rq
from haystack.signals import BaseSignalProcessor
from polymorphic import PolymorphicModel
from reversion.models import Version, Revision
from cache_tools.jobs import auto_invalidate_cache, get_stale_objects
from .search_indexes import get_haystack_index


def is_polymorphic_model(model):
    return issubclass(model, PolymorphicModel)


def get_polymorphic_parent_model(model):
    if is_polymorphic_model(model):
        parent_model = [p for p in model.__bases__ if is_polymorphic_model(p)]
        assert len(parent_model) == 1
        parent_model = parent_model[0]
        if not parent_model._meta.abstract:
            return parent_model
    return model


def is_polymorphic_child_model(model):
    return get_polymorphic_parent_model(model) != model


def auto_update_haystack(action, instance):
    for obj in get_stale_objects(instance, all_relations=True):
        model = obj.__class__

        if is_polymorphic_child_model(model):
            model = get_polymorphic_parent_model(model)
            obj = model._default_manager.non_polymorphic().get(pk=obj.pk)

        index = get_haystack_index(model)
        if index is None:
            continue

        if action == 'delete':
            index.remove_object(obj)
        else:
            index.update_object(obj)


@job
def auto_invalidate(action, app_label, model_name, pk):
    model = get_model(app_label, model_name)

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

    instance = model._default_manager.get(pk=pk)

    auto_invalidate_cache(instance)
    auto_update_haystack(action, instance)


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
        if sender in (LogEntry, Session, Revision, Version):
            return

        django_rq.enqueue(
            auto_invalidate,
            args=(action,
                  instance._meta.app_label, instance._meta.model_name,
                  instance.pk),
            result_ttl=0,  # Doesn't store result
            timeout=3600,  # Avoids never-ending jobs
        )
