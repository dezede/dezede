# coding: utf-8

from __future__ import unicode_literals
from django.core.cache import cache
from django.utils.translation import get_language
from .utils cimport sanitize_memcached_key, get_group_cache_key


__all__ = ('model_method_cached',)


cdef cache_get = cache.get
cdef cache_set = cache.set


def model_method_cached(int timeout, str group=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            cdef str group_cache_key
            cdef list group_keys
            cdef str cache_key = b'%s:%s.%s.%s:%s(%s,%s)' % (
                get_language(), self.__module__, self.__class__.__name__,
                method.__name__, self.pk, args, kwargs)
            cache_key = sanitize_memcached_key(cache_key)
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
