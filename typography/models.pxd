import cython


@cython.locals(fields=list, field_names=list)
cpdef replace_in_kwargs(obj, dict kwargs_dict)
