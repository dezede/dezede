from django import template
from django.apps import apps
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.text import capfirst
import dezede


register = template.Library()


@register.simple_tag
def dezede_version():
    name = capfirst(apps.get_app_config('dezede').verbose_name)
    version = dezede.get_version()
    return f'{name}\u00A0{version}'


@register.simple_tag(takes_context=True)
def nav_link(context, view_name, text):
    request = context.get('request')
    requested_url = '' if request is None else request.path
    url = reverse(view_name)
    css_class = ' class="active"' if requested_url.startswith(url) else ''
    return format_html(f'<li{css_class}><a href="{{}}">{{}}</a></li>',
                       url, capfirst(text))


@register.simple_tag()
def meta(namespace, name, content, **attrs):
    attrs = format_html_join(' ', '{}="{}"', attrs.items())
    return format_html(
        '<meta name="{}.{}" content="{}" {}/>'
        '<meta property="{}:{}" content="{}" {}/>',
        namespace.upper(), name, content, attrs,
        namespace.lower(), name, content, attrs,
    )
