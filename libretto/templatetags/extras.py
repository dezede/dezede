# coding: utf-8

from __future__ import unicode_literals
from HTMLParser import HTMLParser
import re
from bs4 import BeautifulSoup, Comment
from django.template import Library
from django.utils.encoding import smart_text
from django.utils.safestring import mark_safe
from ..utils import abbreviate as abbreviate_func


register = Library()


@register.filter
def stripchars(text):
    return HTMLParser().unescape(text)


@register.filter
def striptags_n_chars(text):
    return smart_text(BeautifulSoup(text, 'html.parser').get_text())


def fix_strange_characters(text):
    return text.replace('...\x1f', '…').replace('\x1c', '').replace('\x1b', '')


compact_paragraph_re = re.compile(r'(?<![\n\s ])\n+[\s\n ]*\n+(?![\n\s ])')


@register.filter
def compact_paragraph(text):
    return mark_safe(compact_paragraph_re.sub(r'\u00A0/ ', text.strip('\n')))


escaped_chars_re = re.compile(r'([#$%&_{}])')


def escape_latex(text):
    return escaped_chars_re.sub(r'\\\1', text.replace('\\', '\\textbackslash'))


html_latex_bindings = (
    (dict(name='h1'), r'\part*{', r'}'),
    (dict(name='h2'), r'\chapter*{', r'}'),
    (dict(name='h3'), r'\section*{', r'}'),
    (dict(name='p'), '\n\n', '\n\n'),
    (dict(name='cite'), r'\textit{', r'}'),
    (dict(name='em'), r'\textit{', r'}'),
    (dict(name='i'), r'\textit{', r'}'),
    (dict(name='strong'), r'\textbf{', r'}'),
    (dict(name='b'), r'\textbf{', r'}'),
    (dict(name='small'), r'\small{', r'}'),
    (dict(name='sup'), r'\textsuperscript{', r'}'),
    (dict(class_='sc'), r'\textsc{', r'}'),
    (dict(style=re.compile(r'.*font-variant:\s*'
                           r'small-caps;.*')), r'\textsc{', r'}'),
)


@register.filter
def html_to_latex(html):
    r"""
    Permet de convertir du HTML en syntaxe LaTeX.

    Attention, ce convertisseur est parfaitement incomplet et ne devrait pas
    être utilisé en dehors d'un contexte très précis.

    >>> print(html_to_latex('<h1>Bonjour à tous</h1>'))
    \part*{Bonjour à tous}
    >>> print(html_to_latex('<span style="font-series: bold; '
    ... 'font-variant: small-caps;">Écriture romaine</span>'))
    \textsc{Écriture romaine}
    >>> print(html_to_latex('Vive les <!-- cons -->poilus !'))
    Vive les poilus !
    """
    html = escape_latex(stripchars(fix_strange_characters(html)))
    soup = BeautifulSoup(html, 'html.parser')
    for html_selectors, latex_open_tag, latex_close_tag in html_latex_bindings:
        for tag in soup.find_all(**html_selectors):
            tag.insert(0, latex_open_tag)
            tag.append(latex_close_tag)
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    return mark_safe(smart_text(soup.get_text()))


@register.filter
def abbreviate(string, min_vowels=0, min_len=1, tags=True, enabled=True):
    return abbreviate_func(string, min_vowels=min_vowels, min_len=min_len,
                           tags=tags, enabled=enabled)
