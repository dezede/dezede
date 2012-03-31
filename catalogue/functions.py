# coding: utf-8
from django.template.defaultfilters import date
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.functional import allow_lazy

def date_html(d, tags=True):
    u'''
    Rendu HTML d’une date.

    >>> from datetime import date
    >>> date_html(date(1828, 1, 15))
    u'mardi 15 janvier 1828'
    >>> date_html(date(1828, 1, 1), False)
    u'mardi 1er janvier 1828'
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
    >>> str_list(l)
    u'Jeanne, Lola, Perrine, Marion'
    '''
    if not infix:
        infix = ugettext(', ')
    l = filter(bool, l)
    suffix = ''
    if len(l) > 1 and last_infix:
        suffix = last_infix + l.pop()
    return infix.join(l) + suffix


def str_list_w_last(l, infix=None, last_infix=None):
    u'''
    Concatène une liste de chaîne de caractères avec des virgules et un «\u00A0et\u00A0» final.

    >>> l = ['Jeanne', 'Lola', 'Perrine', 'Marion']
    >>> str_list_w_last(l)
    u'Jeanne, Lola, Perrine et Marion'
    '''
    if not infix:
        infix = ugettext(', ')
    if not last_infix:
        last_infix = ugettext(' et ')
    return str_list(l, infix, last_infix)

def calc_pluriel(obj):
    try:
        if obj.nom_pluriel:
            return obj.nom_pluriel
        return obj.nom + 's'
    except:
        return unicode(obj)

def ex(txt):
    '''
    >>> ex('30/01/1989')
    u'Exemple : « 30/01/1989 »'
    '''
    return _(u'Exemple : « %s »') % txt
ex = allow_lazy(ex, unicode)

def no(txt):
    '''
    >>> no('13')
    u'n°\u00A013'
    '''
    return _(u'n°\u00A0%s') % txt

# Fonctions HTML

def cite(txt, tags=True):
    '''
    >>> cite('Le Cid')
    u'<cite>Le Cid</cite>'
    >>> cite('The pillars of the earth', False)
    'The pillars of the earth'
    '''
    if tags:
        return u'<cite>%s</cite>' % txt
    return txt

def href(url, txt, tags=True):
    '''
    >>> href('truc.machin/bidule', 'Cliquez ici')
    u'<a href="truc.machin/bidule">Cliquez ici</a>'
    >>> href('a.b/c', "It's a trap!", tags=False)
    "It's a trap!"
    '''
    if tags:
        return u'<a href="%s">%s</a>' % (url, txt)
    return txt

def sc(txt, tags=True):
    '''
    >>> sc('gentle shout')
    u'<span class="sc">gentle shout</span>'
    >>> sc('I wish I could be in small caps', tags=False)
    'I wish I could be in small caps'
    '''
    if tags:
        return u'<span class="sc">%s</span>' % txt
    return txt

def hlp(txt, title, tags=True):
    '''
    >>> hlp('two years', 'period')
    u'<span title="period">two years</span>'
    >>> hlp('G minor', 'tonality', tags=False)
    'G minor'
    '''
    if tags:
        return u'<span title="%s">%s</span>' % (title, txt)
    return txt

def small(txt, tags=True):
    '''
    >>> small('I feel tiny')
    u'<small>I feel tiny</small>'
    >>> small('In a website I would be small...', tags=False)
    'In a website I would be small...'
    '''
    if tags:
        return u'<small>%s</small>' % txt
    return txt

