# coding: utf-8

from __future__ import unicode_literals
from django import template
from django.utils.text import capfirst
import sys


register = template.Library()


@register.simple_tag()
def software_versions():
    softwares = ('dezede', 'django', 'python')
    out = []
    for software in softwares:
        if software == 'python':
            name = software
            version = '.'.join(str(i) for i in sys.version_info[:3])
        else:
            module = __import__(software)
            name = getattr(module, '__verbose_name__', '') \
                or getattr(module, '__name__', '') or software
            version = module.get_version()
        name = capfirst(name)
        out.append('<span>%s %s</span>' % (name, version))
    return '<span>⋅</span>'.join(out)
