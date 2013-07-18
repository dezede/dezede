#!python
#cython: boundscheck=False

import cython


cdef str remove_diacritics(unicode string)


cdef bint is_vowel(unicode string)


@cython.locals(i0=Py_ssize_t, c0=unicode, i1=Py_ssize_t, c1=unicode, out=list)
cdef list chars_iterator(unicode s)


cdef ABBREVIATION_RE


@cython.locals(out=unicode, i=Py_ssize_t, sub=unicode,
               vowels_count=int, vowel_first=bint, j0=Py_ssize_t, c0=unicode,
               j1=Py_ssize_t, c1=unicode, general_case=bint,
               particular_case=bint)
cpdef abbreviate(string, int min_vowels=?, Py_ssize_t min_len=?, bint tags=?,
                         bint enabled=?)
