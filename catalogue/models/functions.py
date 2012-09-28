# coding: utf-8

from django.template.defaultfilters import date
from django.utils.translation import pgettext, ugettext, ugettext_lazy as _
from django.utils.functional import allow_lazy
from django.utils.safestring import mark_safe


def date_html(d, tags=True):
    u'''
    Rendu HTML d’une date.

    >>> from datetime import date
    >>> print date_html(date(1828, 1, 15))
    mardi 15 janvier 1828
    >>> print date_html(date(1828, 1, 1), False)
    mardi 1er janvier 1828
    '''
    pre = date(d, 'l')
    post = date(d, 'F Y')
    j = date(d, 'j')
    if j == '1':
        k = ugettext('er')
        if tags:
            k = '<sup>%s</sup>' % k
        j += k
    return '%s %s %s' % (pre, j, post)


def str_list(l, infix=None, last_infix=None):
    u'''
    Concatène une liste de chaîne de caractères avec des virgules.

    >>> l = ['Jeanne', 'Lola', 'Perrine', 'Marion']
    >>> print str_list(l)
    Jeanne, Lola, Perrine, Marion
    '''
    if infix is None:
        infix = pgettext(u'infix d’une liste', ', ')
    l = [e for e in l if e]
    suffix = ''
    if last_infix and len(l) > 1:
        suffix = last_infix + l.pop()
    return infix.join(l) + suffix


def str_list_w_last(l, infix=None, last_infix=None, oxfordian_last_infix=None,
        oxford_comma=True):
    u'''
    Concatène une liste de chaîne de caractères avec des virgules
    et un «,\u00A0et\u00A0» final («\u00A0et\u00A0» pour deux éléments).
    Pour désactiver la virgule d’Oxford, passer oxford_comma=False en argument.

    >>> l = ['Jeanne', 'Marion', 'Lola', 'Perrine']
    >>> print str_list_w_last(l)
    Jeanne, Marion, Lola,\u00A0et\u00A0Perrine
    >>> print str_list_w_last(l[:2])
    Jeanne\u00A0et\u00A0Marion
    '''
    l = tuple(l)
    if infix is None:
        infix = pgettext(u'infix d’une liste', ', ')
    if last_infix is None:
        last_infix = pgettext(u'dernier infix pour 2 éléments',
                              u'\u00A0et\u00A0')
    if oxford_comma and len(l) > 2:
        if oxfordian_last_infix is None:
            oxfordian_last_infix = \
                pgettext(u'dernier infix pour plus de 2 éléments',
                         u',\u00A0et\u00A0')
        last_infix = oxfordian_last_infix
    return str_list(l, infix, last_infix)


def calc_pluriel(obj):
    try:
        if obj.nom_pluriel:
            return obj.nom_pluriel
        return obj.nom + 's'
    except:
        return unicode(obj)


def ex(txt):
    u'''
    >>> print ex('30/01/1989')
    Exemple : « 30/01/1989 »
    '''
    return _(u'Exemple : « %s »') % txt
ex = allow_lazy(ex, unicode)


def no(txt):
    u'''
    >>> print no('13')
    n°\u00A013
    '''
    return _(u'n°\u00A0%s') % txt


#
# Fonctions HTML
#


def cite(txt, tags=True):
    '''
    >>> print cite('Le Cid')
    <cite>Le Cid</cite>
    >>> print cite('The pillars of the earth', False)
    The pillars of the earth
    '''
    if not txt:
        return ''
    if tags:
        return mark_safe(u'<cite>' + txt + '</cite>')
    return txt


def href(url, txt, tags=True):
    '''
    >>> print href('truc.machin/bidule', 'Cliquez ici')
    <a href="truc.machin/bidule">Cliquez ici</a>
    >>> print href('a.b/c', "It's a trap!", tags=False)
    It's a trap!
    '''
    if not txt:
        return ''
    if tags:
        return mark_safe(u'<a href="%s">%s</a>' % (url, txt))
    return txt


def sc(txt, tags=True):
    '''
    >>> print sc('gentle shout')
    <span class="sc">gentle shout</span>
    >>> print sc('I wish I could be in small caps', tags=False)
    I wish I could be in small caps
    '''
    if not txt:
        return ''
    if tags:
        return mark_safe(u'<span class="sc">' + txt + '</span>')
    return txt


def hlp(txt, title, tags=True):
    '''
    >>> print hlp('two years', 'period')
    <span title="period">two years</span>
    >>> print hlp('G minor', 'tonality', tags=False)
    G minor
    '''
    if not txt:
        return ''
    if tags:
        return mark_safe(u'<span title="%s">%s</span>' % (title, txt))
    return txt


def small(txt, tags=True):
    '''
    >>> print small('I feel tiny')
    <small>I feel tiny</small>
    >>> print small('In a website I would be small...', tags=False)
    In a website I would be small...
    '''
    if not txt:
        return ''
    if tags:
        return mark_safe(u'<small>' + txt + '</small>')
    return txt
