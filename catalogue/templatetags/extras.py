# coding: utf-8
import re
import unicodedata
from django.template.defaultfilters import date

from django import template
register = template.Library()

def multiwordReplace(text, wordDic):
    rc = re.compile('|'.join(map(re.escape, wordDic)))
    def translate(match):
        return wordDic[match.group(0)]
    return rc.sub(translate, text)

@register.filter
def replace(string):
    return multiwordReplace(string, {"'": '&rsquo;', ' :': '&nbsp;:',
                                     ' ;': '&nbsp;;', ' !': '&#x202F;!',
                                     ' ?': '&#x202F;?',})

def remove_diacritics(string):
    return unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore')

def is_vowel(string):
    return remove_diacritics(string.lower()) in list('aeiouy')

@register.filter
def abbreviate(string, limit=0):
    out = ''
    for i, sub in enumerate(re.split('(-|\.|\s)', string)): # TODO: créer un catalogue COMPLET de ponctuations de séparation.
        init_sub = sub
        if not i % 2:
            tmp_limit = limit
            for j in range(len(sub)):
                try:
                    if is_vowel(sub[j]):
                        if tmp_limit == 0:
                            if j == 0:
                                sub = sub[:1]
                            else:
                                sub = sub[:j]
                            sub += '.'
                            if len(sub) == len(init_sub):
                                sub = init_sub
                            break
                        try:
                            if not is_vowel(sub[j+1]):
                                tmp_limit -= 1
                        except:
                            tmp_limit -= 1
                except:
                    pass
        out += sub
    return out

if __name__ == '__main__':
    print abbreviate(u'autéeur dramatique de la tour de babel', 1)
    print abbreviate(u'jeanöõ-françois du puy du fou', 0)
    print abbreviate(u'amélie')

