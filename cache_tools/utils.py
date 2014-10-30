# coding: utf-8

from __future__ import unicode_literals
from django.core.cache import cache
from django.utils.translation import get_language


__all__ = (
    'get_cache_key', 'get_cache_pattern', 'invalidate', 'invalidate_object',
    'cached_ugettext', 'cached_pgettext', 'cached_ugettext_lazy',
    'cached_pgettext_lazy',
)


def get_cache_key(method, obj, args, kwargs, id_attr=b'pk'):
    _id = getattr(obj, id_attr)
    if _id is None:
        return None
    meta = obj._meta
    return b'%s:%s.%s.%s:%s(%s,%s)' % (
        get_language(), meta.app_label, meta.module_name,
        method.__name__, _id, args, kwargs)


def get_obj_cache_key(obj, id_attr=b'pk'):
    meta = obj._meta
    return b'%s.%s.%s' % (
        meta.app_label, meta.module_name, getattr(obj, id_attr))


def invalidate_object(obj, id_attr=b'pk'):
    object_cache_key = get_obj_cache_key(obj, id_attr)
    object_keys = cache.get(object_cache_key, [])
    cache.delete_many(object_keys)
    cache.delete(object_cache_key)
