import cython


@cython.locals(cache_key=unicode, group_cache_key=unicode, group_keys=list)
cpdef inner_model_method_cached(timout, unicode group, method, self,
                                tuple args, dict kwargs)
