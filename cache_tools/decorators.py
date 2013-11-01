# coding: utf-8

from __future__ import unicode_literals
from django.core.cache import cache
from .utils import get_cache_key


__all__ = ('model_method_cached',)


cache_get = cache.get
cache_set = cache.set


def model_method_cached(id_attr=b'pk'):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            cache_key = get_cache_key(method, self, args, kwargs, id_attr)
            out = cache_get(cache_key)
            if out is None:
                out = method(self, *args, **kwargs)
                cache_set(cache_key, out, 0)
            return out
        return wrapper
    return decorator
