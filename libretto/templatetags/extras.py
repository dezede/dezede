# coding: utf-8

from __future__ import unicode_literals
from bs4 import BeautifulSoup
from django.template import Library
from django.utils.encoding import smart_text
from ..utils import abbreviate as abbreviate_func


register = Library()


@register.filter
def stripchars(text):
    return smart_text(BeautifulSoup(text, 'html.parser'))


@register.filter
def striptags_n_chars(text):
    return smart_text(BeautifulSoup(text, 'html.parser').get_text())


@register.filter
def abbreviate(*args, **kwargs):
    return abbreviate_func(*args, **kwargs)
