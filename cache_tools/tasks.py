# coding: utf-8

from __future__ import unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Manager
from djcelery_transactions import task
from .utils import get_object_cache_key, invalidate_object


__all__ = ('get_stale_objects', 'auto_invalidate',)


def get_stale_objects(instance, explored_instances, all_relations=False):
    if instance is None:
        raise StopIteration

    cache_key = get_object_cache_key(instance)
    if cache_key in explored_instances:
        raise StopIteration

    yield instance

    explored_instances.append(cache_key)

    relations = getattr(instance, 'invalidated_relations_when_saved',
                        lambda all_relations: ())(all_relations=all_relations)
    for relation in relations:
        try:
            related = getattr(instance, relation)
            if callable(related):
                related = related()
        except ObjectDoesNotExist:
            continue
        if isinstance(related, Manager):
            for obj in related.all():
                for sub_obj in get_stale_objects(
                        obj, explored_instances, all_relations=all_relations):
                    yield sub_obj
        else:
            for sub_related in get_stale_objects(
                    related, explored_instances, all_relations=all_relations):
                yield sub_related


@task
def auto_invalidate(instance):
    for stale_object in get_stale_objects(instance, []):
        invalidate_object(stale_object)
