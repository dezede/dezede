# coding: utf-8

from __future__ import unicode_literals
from django.template import Library
from django.template.loader import render_to_string
from django.contrib.sites.models import get_current_site
from copy import copy

register = Library()


def build_permission(app_label, model_slug, action):
    return '%s.%s_%s' % (app_label, model_slug, action)


def build_admin_view_name(perm):
    return 'admin:%s' % perm.replace('.', '_')


@register.simple_tag(takes_context=True)
def frontend_admin(context, object=None, autorite=False):
    request = context['request']
    if object is None:
        object = context['object']
    Model = object.__class__
    app_label = Model._meta.app_label
    model_slug = Model.__name__.lower()
    change_perm = build_permission(app_label, model_slug, 'change')
    delete_perm = build_permission(app_label, model_slug, 'delete')
    user = request.user
    has_change_perm = user.has_perm(change_perm)
    has_delete_perm = user.has_perm(delete_perm)
    admin_change = build_admin_view_name(change_perm)
    admin_delete = build_admin_view_name(delete_perm)
    domain = get_current_site(request)
    c = {
        'has_change_perm': has_change_perm,
        'has_delete_perm': has_delete_perm,
        'admin_change': admin_change,
        'admin_delete': admin_delete,
        'domain': domain,
        'object': object,
    }
    t = 'routines/%sfront-end_admin.html' % ('autorite_' if autorite else '')
    return render_to_string(t, c)


@register.simple_tag(takes_context=True)
def attr_in_dl(context, attr, verbose_name=None, object=None):
    if object is None:
        object = context['object']
    value = object
    for attr_part in attr.split('.'):
        if value is None:
            break
        value = getattr(value, attr_part)
        if callable(value):
            value = value()
    if not value:
        return ''
    if verbose_name is None:
        verbose_name = object._meta.get_field(attr).verbose_name
    c = {
        'verbose_name': verbose_name,
        'value': value,
    }
    return render_to_string('routines/attr_in_dl.html', c)


def get_verbose_name_from_object_list(object_list, verbose_name=None,
                                      verbose_name_plural=None):
    Model = object_list[0].__class__
    if verbose_name is None:
        verbose_name = Model._meta.verbose_name
    if verbose_name_plural is None:
        verbose_name_plural = Model._meta.verbose_name_plural
    return verbose_name, verbose_name_plural


@register.filter
def get_property(object, properties_name):
    """
    >>> get_property('a', 'split')
    [u'a']
    >>> get_property('abcd', '__len__')
    4
    >>> class Class(object):
    ...     property = 8
    >>> get_property(Class(), 'property')
    8
    """
    for property_name in properties_name.split('.'):
        object = getattr(object, property_name)
        if callable(object):
            object = object()
    return object


def build_display_list(object_list, properties_name):
    display_list = []
    for object in object_list:
        object = get_property(object, properties_name)
        display_list.append(object)
    return display_list


@register.simple_tag(takes_context=True)
def list_in_dl(context, object_list, properties_name='link', verbose_name=None,
                                                  verbose_name_plural=None):
    if not object_list:
        return ''
    verbose_name, verbose_name_plural = get_verbose_name_from_object_list(
                                    object_list, verbose_name=verbose_name,
                                    verbose_name_plural=verbose_name_plural)
    display_list = build_display_list(object_list, properties_name)
    c = copy(context)
    c.update({
        'count': len(display_list),
        'display_list': display_list,
        'verbose_name': verbose_name,
        'verbose_name_plural': verbose_name_plural,
    })
    return render_to_string('routines/list_in_dl.html', c)


@register.simple_tag()
def jstree(queryset, properties_name='__unicode__', id=None):
    if not queryset:
        return ''
    if id is None:
        id = queryset[0].__class__.__name__.lower()
    c = {
        'queryset': queryset,
        'id': id,
        'properties_name': properties_name,
    }
    return render_to_string('routines/jstree.html', c)
