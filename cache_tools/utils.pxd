import cython


cdef public str CONTROL_CHARACTERS
cdef CONTROL_CHARACTERS_RE
cdef CONTROL_CHARACTERS_RE_SUB


@cython.locals(hashed_key=str)
cpdef unicode sanitize_memcached_key(unicode key, int max_length=?)


cpdef unicode get_group_cache_key(unicode group)

@cython.locals(group_cache_key=unicode, group_keys=list)
cpdef invalidate_group(unicode group)


cdef dict PGETTEXT_CACHE


@cython.locals(cache_key=tuple, out=unicode)
cpdef unicode cached_pgettext(unicode context, unicode message)


cdef dict UGETTEXT_CACHE


@cython.locals(cache_key=tuple, out=unicode)
cpdef unicode cached_ugettext(unicode message)
