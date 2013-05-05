#!python
#cython: boundscheck=False
#cython: wraparound=False
#cython: nonecheck=False


import cython


cdef str CONTROL_CHARACTERS
cdef CONTROL_CHARACTERS_RE
cdef CONTROL_CHARACTERS_RE_SUB


@cython.locals(hashed_key=str)
cpdef sanitize_memcached_key(key, int max_length=?)


cpdef str get_group_cache_key(str group)

@cython.locals(group_cache_key=str, group_keys=list)
cpdef invalidate_group(str group)


cdef dict PGETTEXT_CACHE


@cython.locals(cache_key=tuple, out=unicode)
cpdef unicode cached_pgettext(unicode context, unicode message)


cdef dict UGETTEXT_CACHE


@cython.locals(cache_key=tuple, out=unicode)
cpdef unicode cached_ugettext(unicode message)
