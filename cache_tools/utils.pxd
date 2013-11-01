#!python
#cython: boundscheck=False
#cython: wraparound=False
#cython: nonecheck=False

from __future__ import unicode_literals
import cython


cpdef get_cache_key(method, self, tuple args, dict kwargs, bytes id_attr=?)


cpdef invalidate_object(obj, bytes id_attr=?)


cdef dict PGETTEXT_CACHE


@cython.locals(cache_key=tuple, out=unicode)
cpdef unicode cached_pgettext(unicode context, unicode message)


cdef dict UGETTEXT_CACHE


@cython.locals(cache_key=tuple, out=unicode)
cpdef unicode cached_ugettext(unicode message)
