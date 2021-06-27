from html.parser import HTMLParser
import re
from bs4 import BeautifulSoup, Comment
from django.core.exceptions import EmptyResultSet
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection
from django.template import Library
from django.utils.encoding import smart_text
from django.utils.safestring import mark_safe
from common.utils.sql import get_raw_query
from ..models import Lieu
from common.utils.html import date_html as date_html_util
from common.utils.abbreviate import abbreviate as abbreviate_func


register = Library()


@register.filter
def stripchars(text):
    return HTMLParser().unescape(text)


def fix_strange_characters(text):
    return (text
            .replace('...\x1f', '…').replace('\x1c', '').replace('\x1b', '')
            .replace('\u2500', '—'))


compact_paragraph_re = re.compile(r'(?<![\n\s ])\n+[\s\n ]*\n+(?![\n\s ])')


@register.filter
def compact_paragraph(text):
    return mark_safe(compact_paragraph_re.sub('\u00A0/ ', text.strip('\n')))


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
    (dict(name='ul'), r'\begin{itemize}', r'\end{itemize}'),
    (dict(name='ol'), r'\begin{enumerate}', r'\end{enumerate}'),
    (dict(name='li'), r'\item{', r'}'),
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


@register.simple_tag(takes_context=True)
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
def abbreviate(string, min_len=1, tags=True, enabled=True):
    return abbreviate_func(string, min_len=min_len, tags=tags, enabled=enabled)


def get_data(evenements_qs, min_places, bbox):
    evenements_qs = evenements_qs.order_by()

    cursor = connection.cursor()

    valid_ancestors = Lieu.objects.filter(geometry__isnull=False).order_by()
    if bbox is not None:
        valid_ancestors = valid_ancestors.filter(geometry__contained=bbox)

    valid_ancestors_query, valid_ancestors_params = get_raw_query(
        valid_ancestors.values('id', 'path'))

    evenements_query, params = get_raw_query(
        evenements_qs.values('debut_lieu_id'))

    cursor.execute("""
    SELECT length(ancetre.path) / 4, COUNT(DISTINCT ancetre.id)
    FROM libretto_lieu AS lieu
    INNER JOIN (%s) AS ancetre ON lieu.path LIKE ancetre.path || '%%%%'
    WHERE lieu.id IN (%s)
    GROUP BY length(ancetre.path)
    ORDER BY length(ancetre.path) ASC;
    """ % (valid_ancestors_query, evenements_query),
        valid_ancestors_params + params)

    level = None
    for level, count in cursor.fetchall():
        if count >= min_places:
            break
        if count == 0:
            if level > 0:
                level -= 1
            break
    if level is None:
        return ()

    evenements_query, params = get_raw_query(
        evenements_qs.values('pk', 'debut_lieu_id'))
    params = list(params)
    if bbox is None:
        bbox_where = ''
    else:
        bbox_where = 'geometry @ ST_GeomFromEWKB(%s::bytea) AND '
        params.append(bbox.ewkb)

    params.append(level)

    cursor.execute("""
    SELECT ancetre.id, ancetre.nom, ancetre.geometry, COUNT(evenement.id) AS n
    FROM (%s) AS evenement
    INNER JOIN libretto_lieu AS lieu ON lieu.id = evenement.debut_lieu_id
    INNER JOIN (
        SELECT *
        FROM libretto_lieu
        WHERE (
            %s
            geometry IS NOT NULL
            AND length(path) / 4 = %%s
        )
        ORDER BY length(path) DESC
    ) AS ancetre ON lieu.path LIKE ancetre.path || '%%%%'
    GROUP BY ancetre.id, ancetre.nom, ancetre.geometry
    ORDER BY n DESC;
    """ % (evenements_query, bbox_where), params)
    return cursor.fetchall()


@register.simple_tag
def get_map_data(evenement_qs, min_places, bbox):
    try:
        return [(pk, nom, GEOSGeometry(geometry), n)
                for pk, nom, geometry, n in get_data(evenement_qs, min_places,
                                                     bbox)]
    except EmptyResultSet:
        return ()


@register.simple_tag(takes_context=True)
def map_request(context, lieu_pk=None, show_map=True):
    request = context['request']
    query_dict = request.GET.copy()
    if 'bbox' in query_dict:
        del query_dict['bbox']
    if 'min_places' in query_dict:
        del query_dict['min_places']
    if lieu_pk is not None:
        query_dict['lieu'] = '|%s|' % lieu_pk
    if show_map:
        query_dict['show_map'] = True
    else:
        del query_dict['show_map']
    return '?' + query_dict.urlencode()


@register.simple_tag(takes_context=True)
def export_request(context, export_format):
    request = context['request']
    query_dict = request.GET.copy()
    query_dict['format'] = export_format
    return context['export_url'] + '?' + query_dict.urlencode()


@register.simple_tag(takes_context=True)
def change_results_order(context, order_by='default'):
    query_dict = context['request'].GET.copy()
    if order_by == 'default' and 'order_by' in query_dict:
        del query_dict['order_by']
    elif order_by == 'reversed':
        query_dict['order_by'] = order_by
    return '?' + query_dict.urlencode()
