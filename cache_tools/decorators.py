# coding: utf-8

from __future__ import unicode_literals
from django.core.cache import cache
from .utils import get_cache_key, get_group_cache_key


__all__ = ('model_method_cached',)


cache_get = cache.get
cache_set = cache.set


def model_method_cached(timeout, group=None, id_attr=b'pk'):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            cache_key = get_cache_key(id_attr, method, self, args, kwargs)
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
