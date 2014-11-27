# coding: utf-8

from __future__ import unicode_literals
from time import time

from django.core.cache import cache

from .utils import get_cache_key, get_obj_cache_key


__all__ = ('model_method_cached',)


def model_method_cached(id_attr=b'pk'):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            cache_key = get_cache_key(method, self, args, kwargs, id_attr)

            if cache_key is None:  # Happens when the object has no id.
                return method(self, *args, **kwargs)

            object_cache_key = get_obj_cache_key(self, id_attr)
            data = cache.get_many((cache_key, object_cache_key))
            if object_cache_key not in data:
                cache.add(object_cache_key, time(), None)
            elif cache_key in data:
                object_timestamp = data[object_cache_key]
                timestamp, out = data[cache_key]
                if timestamp > object_timestamp:
                    return out

            out = method(self, *args, **kwargs)
            cache.set(cache_key, (time(), out), None)
            return out
        return wrapper
    return decorator
