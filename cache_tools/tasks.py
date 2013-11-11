# coding: utf-8

from __future__ import unicode_literals
from celery.task import task
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Manager
from .utils import invalidate_object, get_cache_pattern


__all__ = ('get_stale_objects', 'auto_invalidate_cache',)


def get_stale_objects(instance, explored=None, all_relations=False):
    if explored is None:
        explored = []

    if instance is None:
        raise StopIteration

    cache_pattern = get_cache_pattern(instance)
    if cache_pattern in explored:
        raise StopIteration

    yield instance

    explored.append(cache_pattern)

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
                        obj, explored, all_relations=all_relations):
                    yield sub_obj
        else:
            for sub_related in get_stale_objects(
                    related, explored, all_relations=all_relations):
                yield sub_related


@task
def auto_invalidate_cache(instance):
    for stale_object in get_stale_objects(instance):
        invalidate_object(stale_object)
