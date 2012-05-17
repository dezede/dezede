# coding: utf-8

import re
from unicodedata import normalize
from BeautifulSoup import BeautifulStoneSoup
from django.template import Library

register = Library()


@register.filter
def stripchars(text):
    return unicode(
            BeautifulStoneSoup(
                text,
                convertEntities=BeautifulStoneSoup.HTML_ENTITIES
                )
            )


def multiwordReplace(text, wordDic):
    rc = re.compile('|'.join(map(re.escape, wordDic)))

    def translate(match):
        return wordDic[match.group(0)]

    return rc.sub(translate, text)


@register.filter
def replace(string):
    return multiwordReplace(
            string,
            {
                u"'": u'’',        u' :': u'\u00A0:', u' ;': u'\u00A0;',
                u' !': u'\u202F!', u' ?': u'\u202F?', u'« ': u'«\u00A0',
                u' »': u'\u00A0»', u'“ ': u'“\u00A0', u' ”': u'\u00A0”',
                u'&laquo; ': u'«\u00A0', u' &raquo;': u'\u00A0»',
                u'&ldquo; ': u'“\u00A0', u' &rdquo;': u'\u00A0”',
            }
        )


def remove_diacritics(string):
    return normalize('NFKD', string).encode('ASCII', 'ignore')


def is_vowel(string):
    return remove_diacritics(string) in 'AEIOUYaeiouy'


@register.filter
def abbreviate(string, limit=0):
    '''
    Abrègre les mots avec une limite de longueur (par défaut 0).

    >>> abbreviate(u'amélie')
    u'a.'
    >>> abbreviate(u'jeanöõ-françois du puy du fou')
    u'j.-fr. du p. du f.'
    >>> abbreviate(u'autéeur dramatique de la tour de babel', 1)
    u'aut. dram. de la tour de bab.'
    '''
    out = ''
    # TODO: créer un catalogue COMPLET de ponctuations de séparation.
    for i, sub in enumerate(re.split('(-|\.|\s)', string)):
        if not i % 2:
            init_len = len(sub)
            tmp_limit = limit
            for j in xrange(init_len):
                if is_vowel(sub[j]):
                    if not tmp_limit:
                        l = j if j else 1
                        if l + 1 < init_len:
                            sub = sub[:l] + '.'
                        break
                    if j + 1 < init_len and not is_vowel(sub[j + 1]):
                        tmp_limit -= 1
        out += sub
    return out


@register.filter
def GET_add_page(request, page_number):
    answer = request.GET.copy()
    answer['page'] = page_number
    return answer.urlencode()