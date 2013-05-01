# coding: utf-8

from __future__ import unicode_literals
from hashlib import md5
import re
from django.core.cache import cache
from django.utils.translation import get_language, ugettext, pgettext


__all__ = (
    'CONTROL_CHARACTERS', 'sanitize_memcached_key', 'get_group_cache_key',
    'invalidate_group', 'cached_ugettext', 'cached_pgettext',
)


CONTROL_CHARACTERS = b''.join(chr(i) for i in range(33))
CONTROL_CHARACTERS += chr(127)
CONTROL_CHARACTERS_RE = re.compile('[%s]' % CONTROL_CHARACTERS)
CONTROL_CHARACTERS_RE_SUB = CONTROL_CHARACTERS_RE.sub


def sanitize_memcached_key(key, max_length=250):
    # Derived from django-cache-utils.
    try:
        key = bytes(key).translate(None, CONTROL_CHARACTERS)
    except:  # When key contains unicode or in any other unexpected case,
             # we fallback on the regular expression that shouldn't fail.
        key = CONTROL_CHARACTERS_RE_SUB('', key)
    if len(key) > max_length:
        hashed_key = md5(key).hexdigest()
        key = key[:max_length - 33] + '-' + hashed_key
    return key


def get_group_cache_key(group):
    return 'group:' + group


def invalidate_group(group):
    group_cache_key = get_group_cache_key(group)
    group_keys = cache.get(group_cache_key, ())
    cache.delete_many(group_keys)
    cache.delete(group_cache_key)


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
