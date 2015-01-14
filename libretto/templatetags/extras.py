# coding: utf-8

from __future__ import unicode_literals
from HTMLParser import HTMLParser
import re
from bs4 import BeautifulSoup, Comment
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection
from django.template import Library
from django.utils.encoding import smart_text
from django.utils.safestring import mark_safe
from ..models import Evenement, Lieu
from ..models.functions import date_html as date_html_util
from ..utils import abbreviate as abbreviate_func


register = Library()


@register.filter
def stripchars(text):
    return HTMLParser().unescape(text)


@register.filter
def striptags_n_chars(text):
    return smart_text(BeautifulSoup(text, 'html.parser').get_text())


def fix_strange_characters(text):
    return (text
            .replace('...\x1f', '…').replace('\x1c', '').replace('\x1b', '')
            .replace('\u2500', '—'))


compact_paragraph_re = re.compile(r'(?<![\n\s ])\n+[\s\n ]*\n+(?![\n\s ])')


@register.filter
def compact_paragraph(text):
    return mark_safe(compact_paragraph_re.sub(r'\u00A0/ ', text.strip('\n')))


escaped_chars_re = re.compile(r'([#$%&_{}])')


def escape_latex(text):
    text = (text.replace('\\', '\\char`\\\\')
            .replace('^', '\\^{}'))
    return escaped_chars_re.sub(r'\\\1', text)


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


@register.assignment_tag(takes_context=True)
def get_prev_event_counter(context, source, event_counter):
    if 'source_dict' not in context:
        context['source_dict'] = {}
    source_dict = context['source_dict']
    if source.pk not in source_dict:
        source_dict[source.pk] = event_counter
    return source_dict[source.pk]


@register.filter
def date_html(date, short=False):
    return date_html_util(date, short=short)


@register.filter
def abbreviate(string, min_vowels=0, min_len=1, tags=True, enabled=True):
    return abbreviate_func(string, min_vowels=min_vowels, min_len=min_len,
                           tags=tags, enabled=enabled)


def get_raw_query(qs):
    return qs.query.get_compiler(connection=connection).as_sql()


def get_data(evenements_qs, bbox):
    evenements_qs = evenements_qs.order_by()

    cursor = connection.cursor()

    valid_ancestors = Lieu.objects.filter(geometry__isnull=False).order_by()
    if bbox is not None:
        valid_ancestors = valid_ancestors.filter(geometry__contained=bbox)

    valid_ancestors_query, valid_ancestors_params = get_raw_query(
        valid_ancestors.values('pk'))

    evenements_query, params = get_raw_query(
        evenements_qs.values('debut_lieu_id'))

    cursor.execute("""
    SELECT ancetre.level, COUNT(DISTINCT ancetre.id) FROM libretto_lieu AS lieu
    INNER JOIN libretto_lieu AS ancetre ON (
        ancetre.id IN (%s)
        AND ancetre.tree_id = lieu.tree_id
        AND lieu.lft BETWEEN ancetre.lft AND ancetre.rght)
    WHERE lieu.id IN (%s)
    GROUP BY ancetre.level
    ORDER BY ancetre.level ASC;
    """ % (valid_ancestors_query, evenements_query),
        valid_ancestors_params + params)

    level = None
    for level, count in cursor.fetchall():
        if count > 5:
            break
        if count == 0:
            if level > 0:
                level -= 1
            break
    if level is None:
        return ()

    evenements_query, params = get_raw_query(
        evenements_qs.values('pk', 'debut_lieu_id'))

    cursor.execute("""
    SELECT ancetre.id, ancetre.nom, ancetre.geometry, COUNT(evenement.id) AS n
    FROM (%s) AS evenement
    INNER JOIN libretto_lieu AS lieu ON lieu.id = evenement.debut_lieu_id
    INNER JOIN libretto_lieu AS ancetre ON (
        ancetre.id IN (%s)
        AND ancetre.tree_id = lieu.tree_id AND ancetre.level = %s
        AND lieu.lft BETWEEN ancetre.lft AND ancetre.rght)
    GROUP BY ancetre.id
    ORDER BY n DESC;
    """ % (evenements_query, valid_ancestors_query, level),
        params + valid_ancestors_params)
    return cursor.fetchall()


@register.filter
def get_map_data(evenement_qs, bbox):
    return [(pk, nom, GEOSGeometry(geometry), n)
            for pk, nom, geometry, n in get_data(evenement_qs, bbox)]


@register.simple_tag(takes_context=True)
def map_request(context, lieu_pk=None, show_map=True):
    request = context['request']
    new_request = request.GET.copy()
    if 'bbox' in new_request:
        del new_request['bbox']
    if lieu_pk is not None:
        new_request['lieu'] = '|%s|' % lieu_pk
    if show_map:
        new_request['show_map'] = 'true'
    else:
        del new_request['show_map']
    return '?' + new_request.urlencode()
