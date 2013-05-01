# coding: utf-8

from __future__ import unicode_literals
from django.template import Library
from ..utils import replace as replace_util


__all__ = ()


register = Library()


@register.filter
def replace(string):
    return replace_util(string)
