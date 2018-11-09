from time import time

from django.core.cache import cache
from django.utils.translation import get_language


__all__ = (
    'get_cache_key', 'get_cache_pattern', 'invalidate', 'invalidate_object',
)


def get_cache_key(method, obj, args, kwargs, id_attr='pk'):
    _id = getattr(obj, id_attr)
    if _id is None:
        return
    meta = obj._meta
    return '%s:%s.%s.%s:%s(%s,%s)' % (
        get_language(), meta.app_label, meta.model_name,
        method.__name__, _id, args, kwargs)


def get_obj_cache_key(obj, id_attr='pk'):
    meta = obj._meta
    return '%s.%s.%s' % (
        meta.app_label, meta.model_name, getattr(obj, id_attr))


def invalidate_object(obj, id_attr='pk'):
    object_cache_key = get_obj_cache_key(obj, id_attr)
    cache.set(object_cache_key, time(), None)
