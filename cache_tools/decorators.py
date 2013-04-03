# coding: utf-8

from __future__ import unicode_literals
from django.core.cache import cache
from django.utils.translation import get_language
from .utils import sanitize_memcached_key, get_group_cache_key


__all__ = ('model_method_cached',)


def model_method_cached(timeout, group=None):
    def decorator(method):
        def wrapper(self, *args, **kwargs):
            cache_key = '%s:%s.%s.%s:%s(%s,%s)' % (
                get_language(), self.__module__, self.__class__.__name__,
                method.__name__, self.pk, args, kwargs)
            cache_key = sanitize_memcached_key(cache_key)
            out = cache.get(cache_key)
            if out is None:
                if group is not None:
                    group_cache_key = get_group_cache_key(group)
                    group_keys = cache.get(group_cache_key, [])
                    group_keys.append(cache_key)
                    cache.set(group_cache_key, group_keys, 0)
                out = method(self, *args, **kwargs)
                cache.set(cache_key, out, timeout)
            return out
        return wrapper
    return decorator
