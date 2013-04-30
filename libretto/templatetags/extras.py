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
def abbreviate(string, min_vowels=0, min_len=1, tags=True, enabled=True):
    return abbreviate_func(string, min_vowels=min_vowels, min_len=min_len,
                           tags=tags, enabled=enabled)
