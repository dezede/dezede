# coding: utf-8

from __future__ import unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Manager
from djcelery_transactions import task
from .utils import get_object_cache_key, invalidate_object


__all__ = ('auto_invalidate',)


@task
def auto_invalidate(instance, explored_instances=()):
    if instance is None:
        return
    cache_key = get_object_cache_key(instance)

    if cache_key in explored_instances:
        return

    invalidate_object(instance)
    explored_instances.append(cache_key)

    relations = getattr(instance, 'invalidated_relations_when_saved',
                        lambda: ())()
    for relation in relations:
        try:
            related = getattr(instance, relation)
        except ObjectDoesNotExist:
            continue
        if callable(related):
            related = related()
        if isinstance(related, Manager):
            for obj in related.all():
                auto_invalidate(obj, explored_instances)
        else:
            auto_invalidate(related, explored_instances)
