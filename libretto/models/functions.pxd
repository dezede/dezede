import cython


@cython.locals(out=unicode)
cpdef unicode capfirst(text)


@cython.locals(pre=unicode, post=unicode, j=unicode, k=unicode)
cpdef date_html(d, bint tags=?, bint short=?)


cpdef href(url, txt, bint tags=?, bint new_tab=?)


cpdef hlp(txt, title, bint tags=?)
