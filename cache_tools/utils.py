# coding: utf-8

from __future__ import unicode_literals
from django.core.cache import cache
from django.utils.functional import lazy
from django.utils.translation import get_language, ugettext, pgettext


__all__ = (
    'get_cache_key', 'get_cache_pattern', 'invalidate_object',
    'cached_ugettext', 'cached_pgettext', 'cached_ugettext_lazy',
    'cached_pgettext_lazy',
)


def get_cache_key(method, obj, args, kwargs, id_attr=b'pk'):
    _id = getattr(obj, id_attr)
    if _id is None:
        return None
    return b'%s:%s.%s.%s:%s(%s,%s)' % (
        get_language(), obj.__module__, obj.__class__.__name__,
        method.__name__, _id, args, kwargs)


def get_cache_pattern(obj, id_attr=b'pk'):
    return b'*:%s.%s.*:%s(*,*)' % (
        obj.__module__, obj.__class__.__name__, getattr(obj, id_attr))


def invalidate_object(obj, id_attr=b'pk'):
    cache.delete_pattern(get_cache_pattern(obj, id_attr))


UGETTEXT_CACHE = {}


def cached_ugettext(message):
    lang = get_language()
    cache_key = (lang, message)
    try:
        return UGETTEXT_CACHE[cache_key]
    except KeyError:
        out = UGETTEXT_CACHE[cache_key] = ugettext(message)
        return out


PGETTEXT_CACHE = {}


def cached_pgettext(context, message):
    lang = get_language()
    cache_key = (lang, context, message)
    try:
        return PGETTEXT_CACHE[cache_key]
    except KeyError:
        out = PGETTEXT_CACHE[cache_key] = pgettext(context, message)
        return out


cached_ugettext_lazy = lazy(cached_ugettext, unicode)
cached_pgettext_lazy = lazy(cached_pgettext, unicode)
