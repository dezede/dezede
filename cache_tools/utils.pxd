#!python
#cython: boundscheck=False
#cython: wraparound=False
#cython: nonecheck=False

from __future__ import unicode_literals
import cython


cdef str CONTROL_CHARACTERS
cdef CONTROL_CHARACTERS_RE
cdef CONTROL_CHARACTERS_RE_SUB


cpdef sanitize_memcached_key(key, int max_length=?)


cpdef get_cache_key(method, self, tuple args, dict kwargs, bytes id_attr=?)


cpdef bytes get_object_cache_key(obj, bytes id_attr=?)


@cython.locals(object_cache_key=bytes, object_keys=list)
cpdef invalidate_object(obj, bytes id_attr=?)


cdef dict PGETTEXT_CACHE


@cython.locals(cache_key=tuple, out=unicode)
cpdef unicode cached_pgettext(unicode context, unicode message)


cdef dict UGETTEXT_CACHE


@cython.locals(cache_key=tuple, out=unicode)
cpdef unicode cached_ugettext(unicode message)
