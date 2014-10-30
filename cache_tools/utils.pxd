#!python
#cython: boundscheck=False
#cython: wraparound=False
#cython: nonecheck=False

from __future__ import unicode_literals


cpdef get_cache_key(method, self, tuple args, dict kwargs, bytes id_attr=?)


cpdef get_obj_cache_key(obj, bytes id_attr=?)


cpdef invalidate_object(obj, bytes id_attr=?)
