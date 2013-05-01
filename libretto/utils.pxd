import cython


cdef remove_diacritics(string)


cdef bint is_vowel(string)


cdef ABBREVIATION_RE


@cython.locals(out=unicode, i=int, sub=unicode,
               vowels_count=int, vowel_first=bint, j0=int, c0=unicode,
               j1=int, c1=unicode, general_case=bint, particular_case=bint)
cpdef abbreviate(string, int min_vowels=?, int min_len=?, bint tags=?,
                 bint enabled=?)
