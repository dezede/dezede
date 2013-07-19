# coding: utf-8

from __future__ import unicode_literals
import cython
from django.core.cache import cache
from .utils cimport get_cache_key, get_group_cache_key


__all__ = ('model_method_cached',)


cdef cache_get = cache.get
cdef cache_set = cache.set


def model_method_cached(int timeout, bytes group=None, bytes id_attr=b'pk'):
    def decorator(method):
        @cython.locals(args=tuple, kwargs=dict)
        def wrapper(self, *args, **kwargs):
            cdef bytes group_cache_key
            cdef list group_keys
            cdef cache_key = get_cache_key(id_attr, method, self, args, kwargs)
            out = cache_get(cache_key)
            if out is None:
                if group is not None:
                    group_cache_key = get_group_cache_key(group)
                    group_keys = cache_get(group_cache_key, [])
                    group_keys.append(cache_key)
                    cache_set(group_cache_key, group_keys, 0)
                out = method(self, *args, **kwargs)
                cache_set(cache_key, out, timeout)
            return out
        return wrapper
    return decorator
