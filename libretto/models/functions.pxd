import cython


@cython.locals(out=unicode)
cpdef unicode capfirst(text)


@cython.locals(pre=unicode, post=unicode, j=unicode, k=unicode)
cpdef date_html(d, bint tags=?, bint short=?)


@cython.locals(l=list, suffix=unicode)
cpdef unicode str_list(iterable, unicode infix=?, unicode last_infix=?)


cpdef href(url, txt, bint tags=?, bint new_tab=?)


cpdef hlp(txt, title, bint tags=?)
