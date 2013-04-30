import cython


@cython.locals(out=unicode)
cpdef unicode capfirst(text)


@cython.locals(pre=unicode, post=unicode, j=unicode, k=unicode)
cpdef date_html(d, bint tags=?, bint short=?)


@cython.locals(l=list, suffix=unicode)
cpdef unicode str_list(iterable, infix=?, last_infix=?)


@cython.locals(l=list)
cpdef unicode str_list_w_last(iterable, infix=?, last_infix=?,
                              oxfordian_last_infix=?, bint oxford_comma=?)


cpdef href(url, txt, bint tags=?, bint new_tab=?)


cpdef hlp(txt, title, bint tags=?)
