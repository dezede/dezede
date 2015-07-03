# coding: utf-8

from __future__ import unicode_literals
from collections import OrderedDict


class OrderedDefaultDict(OrderedDict):
    def __missing__(self, k):
        self[k] = l = []
        return l
