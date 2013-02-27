# coding: utf-8

from __future__ import unicode_literals
from hashlib import md5
import re
from django.core.cache import cache


__all__ = ('CONTROL_CHARACTERS', 'sanitize_memcached_key',
           'get_group_cache_key', 'invalidate_group')


CONTROL_CHARACTERS = ''.join(chr(i) for i in range(33))
CONTROL_CHARACTERS += chr(127)
CONTROL_CHARACTERS_RE = re.compile('[%s]' % CONTROL_CHARACTERS)
CONTROL_CHARACTERS_RE_SUB = CONTROL_CHARACTERS_RE.sub


def sanitize_memcached_key(key, max_length=250):
    # Taken from django-cache-utils.
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
