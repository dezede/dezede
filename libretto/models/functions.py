# coding: utf-8

from __future__ import unicode_literals
from django.template.defaultfilters import date
from django.utils.encoding import smart_text
from django.utils.functional import allow_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _
from ..utils import cached_pgettext as pgettext


__all__ = (b'capfirst', b'date_html', b'str_list', b'str_list_w_last', b'ex',
           b'no', b'html_decorator', b'cite', b'href', b'sc', b'hlp', b'small',
           b'strong')


def capfirst(text):
    out = smart_text(text)
    if not out:
        return out
    return out[0].upper() + out[1:]


def date_html(d, tags=True, short=False):
    """
    Rendu HTML d’une date.

    >>> from datetime import date
    >>> print(date_html(date(1828, 1, 15)))
    mardi 15 janvier 1828
    >>> print(date_html(date(1828, 1, 1), tags=False))
    mardi 1er janvier 1828
    >>> print(date_html(date(1828, 1, 1)))
    mardi 1<sup>er</sup> janvier 1828
    >>> print(date_html(date(1828, 1, 1), tags=False, short=True))
    1er janvier 1828
    """
    pre = '' if short else date(d, 'l')
    post = date(d, 'F Y')
    j = date(d, 'j')
    if j == '1':
        k = ugettext('er')
        if tags:
            k = '<sup>%s</sup>' % k
        j += k
    return ' '.join([s for s in (pre, j, post) if s])


def str_list(iterable, infix=None, last_infix=None):
    """
    Concatène une liste de chaîne de caractères avec des virgules.

    >>> l = ['Jeanne', 'Lola', 'Perrine', 'Marion']
    >>> print(str_list(l))
    Jeanne, Lola, Perrine, Marion
    """

    if infix is None:
        infix = pgettext('infix d’une liste', ', ')

    l = [e for e in iterable if e]

    if last_infix is None:
        return infix.join(l)

    suffix = ''
    if len(l) > 1:
        suffix = last_infix + l.pop()
    return infix.join(l) + suffix


def str_list_w_last(iterable, infix=None, last_infix=None,
                    oxfordian_last_infix=None, oxford_comma=True):
    """
    Concatène une liste de chaîne de caractères avec des virgules
    et un «,\u00A0et\u00A0» final («\u00A0et\u00A0» pour deux éléments).
    Pour désactiver la virgule d’Oxford, passer oxford_comma=False en argument.

    >>> l = ['Jeanne', 'Marion', 'Lola', 'Perrine']
    >>> print(str_list_w_last(l))
    Jeanne, Marion, Lola\u00A0et\u00A0Perrine
    >>> print(str_list_w_last(l[:2]))
    Jeanne\u00A0et\u00A0Marion
    """

    l = [e for e in iterable if e]

    if infix is None:
        infix = pgettext('infix d’une liste', ', ')

    if oxford_comma and len(l) > 2:
        if oxfordian_last_infix is None:
            oxfordian_last_infix = pgettext(
                'dernier infix pour plus de 2 éléments', ' et ')
        last_infix = oxfordian_last_infix
    elif last_infix is None:
        last_infix = pgettext('dernier infix pour 2 éléments', ' et ')

    return str_list(l, infix, last_infix)


def ex(txt, pre='', post=''):
    """
    >>> print(ex('30/01/1989'))
    Exemple : « 30/01/1989 ».
    """
    return _('Exemple : %(pre)s« %(txt)s »%(post)s.') % {
        'pre': pre,
        'txt': txt,
        'post': post,
    }
ex = allow_lazy(ex, unicode)


def no(txt):
    """
    >>> print(no('13'))
    n°\u00A013
    """
    return _('n° %s') % txt


#
# Fonctions HTML
#


def html_decorator(function):
    def wrapper(txt, tags):
        if not txt:
            return ''
        if tags:
            return mark_safe(function(txt))
        return txt

    return wrapper


@html_decorator
def cite(txt):
    """
    >>> print(cite('Le Cid'))
    <cite>Le Cid</cite>
    >>> print(cite('The pillars of the earth', False))
    The pillars of the earth
    """
    return '<cite>' + txt + '</cite>'


def href(url, txt, tags=True, new_tab=False):
    """
    >>> print(href('truc.machin/bidule', 'Cliquez ici'))
    <a href="truc.machin/bidule">Cliquez ici</a>
    >>> print(href('a.b/c', "It's a trap!", tags=False))
    It's a trap!
    >>> href('', '')
    u''
    """
    if not txt:
        return ''
    if tags:
        if new_tab:
            url += '" target="_blank'
        return mark_safe(smart_text('<a href="%s">%s</a>' % (url, txt)))
    return txt


@html_decorator
def sc(txt):
    """
    >>> print(sc('gentle shout'))
    <span class="sc">gentle shout</span>
    >>> print(sc('I wish I could be in small caps', tags=False))
    I wish I could be in small caps
    """
    return '<span class="sc">' + txt + '</span>'


def hlp(txt, title, tags=True):
    """
    >>> print(hlp('two years', 'period'))
    <span title="Period">two years</span>
    >>> print(hlp('G minor', 'tonality', tags=False))
    G minor
    >>> hlp('', '')
    u''
    """
    if not txt:
        return ''
    if tags:
        return mark_safe('<span title="%s">%s</span>' % (capfirst(title),
                                                         txt))
    return txt


@html_decorator
def small(txt):
    """
    >>> print(small('I feel tiny'))
    <small>I feel tiny</small>
    >>> print(small('In a website I would be small...', tags=False))
    In a website I would be small...
    """
    return '<small>' + txt + '</small>'


@html_decorator
def strong(txt):
    """
    >>> print(strong('I are STROOoOONG!!!'))
    <strong>I are STROOoOONG!!!</strong>
    """
    return '<strong>' + txt + '</strong>'
