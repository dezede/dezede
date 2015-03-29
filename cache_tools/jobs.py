# coding: utf-8

from __future__ import unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Manager, QuerySet
from django_rq import job
from .utils import invalidate_object, get_obj_cache_key


__all__ = ('get_stale_objects', 'auto_invalidate_cache',)


def get_stale_objects(instance, explored=None, all_relations=False):
    if explored is None:
        explored = []

    if instance is None:
        raise StopIteration

    obj_cache_key = get_obj_cache_key(instance)
    if obj_cache_key in explored:
        raise StopIteration

    yield instance

    explored.append(obj_cache_key)

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


@job
def auto_invalidate_cache(instance):
    for stale_object in get_stale_objects(instance):
        invalidate_object(stale_object)
