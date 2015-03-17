# coding: utf-8

from __future__ import unicode_literals
from django import template
from django.apps import apps
from django.core.urlresolvers import reverse
from django.utils.text import capfirst
import dezede


register = template.Library()


@register.simple_tag
def dezede_version():
    name = capfirst(apps.get_app_config('dezede').verbose_name)
    version = dezede.get_version()
    return '%s\u00A0%s' % (name, version)


@register.simple_tag(takes_context=True)
def nav_link(context, view_name, text):
    request = context.get('request')
    requested_url = '' if request is None else request.path
    url = reverse(view_name)
    css_class = ' class="active"' if requested_url.startswith(url) else ''
    return '<li%s><a href="%s">%s</a></li>' % (css_class, url, capfirst(text))
