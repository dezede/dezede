# coding: utf-8

from __future__ import unicode_literals
from copy import copy
from django.db.models.query import QuerySet
from django.template import Library, Template
from django.template.loader import render_to_string
from django.contrib.sites.models import get_current_site
from django.utils.encoding import force_text
from django.utils.text import capfirst
from libretto.models.common import PublishedQuerySet


register = Library()


def build_permission(app_label, model_slug, action):
    return '%s.%s_%s' % (app_label, model_slug, action)


def build_admin_view_name(perm):
    return 'admin:%s' % perm.replace('.', '_')


@register.simple_tag(takes_context=True)
def frontend_admin(context, obj=None, size='xs'):
    request = context['request']
    if obj is None:
        obj = context['object']
    Model = obj.__class__
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

    assert size in ('', 'xs', 'sm', 'md', 'lg')

    c = {
        'has_change_perm': has_change_perm,
        'has_delete_perm': has_delete_perm,
        'admin_change': admin_change,
        'admin_delete': admin_delete,
        'domain': domain,
        'object': obj,
        'size': size,
    }
    return render_to_string('routines/front-end_admin.html', c)


@register.simple_tag(takes_context=True)
def data_table_attr(context, attr, verbose_name=None, obj=None):
    if obj is None:
        obj = context['object']
    value = obj
    for attr_part in attr.split('.'):
        if value is None:
            break
        value = getattr(value, attr_part)
        if callable(value):
            value = value()

    if not value:
        return ''

    # Renders value using language preferences (as in a template).
    sub_context = copy(context)
    sub_context['value'] = value
    value = Template('{{ value }}').render(sub_context)

    if verbose_name is None:
        verbose_name = obj._meta.get_field(attr.split('.')[0]).verbose_name
    c = {
        'verbose_name': verbose_name,
        'value': value,
    }
    return render_to_string('routines/data_table_attr.html', c)


def get_verbose_name_from_object_list(object_list, verbose_name=None,
                                      verbose_name_plural=None):
    if isinstance(object_list, QuerySet):
        Model = object_list.model
    else:
        Model = object_list[0].__class__

    if verbose_name is None:
        verbose_name = Model._meta.verbose_name
    if verbose_name_plural is None:
        verbose_name_plural = Model._meta.verbose_name_plural
    return verbose_name, verbose_name_plural


@register.filter
def get_property(obj, attr):
    """
    >>> get_property('a', 'split')
    [u'a']
    >>> get_property('abcd', '__len__')
    4
    >>> class Class(object):
    ...     attribute = 8
    >>> get_property(Class(), 'attribute')
    8
    """
    for property_name in attr.split('.'):
        obj = getattr(obj, property_name)
        if callable(obj):
            obj = obj()
    return obj


@register.filter
def has_elements(object_list, request):
    if isinstance(object_list, PublishedQuerySet):
        object_list = object_list.published(request=request)
    return bool(object_list)


@register.simple_tag(takes_context=True)
def data_table_list_header(context):
    count = context['count']
    has_count = context['has_count']
    has_count_if_one = context['has_count_if_one']
    verbose_name = context['verbose_name']
    verbose_name_plural = context['verbose_name_plural']
    out = ''
    if has_count and (count != 1 or has_count_if_one):
        out = '%s ' % count
    if count == 1:
        out += force_text(verbose_name)
    else:
        out += force_text(verbose_name_plural)
    return capfirst(out)


@register.simple_tag(takes_context=True)
def data_table_list(context, object_list, attr='link',
                    verbose_name=None, verbose_name_plural=None, per_page=10,
                    has_count_if_one=True, has_count=True):

    if not object_list:
        return ''

    # Only show what the connected user is allowed to see.
    if isinstance(object_list, PublishedQuerySet):
        object_list = object_list.published(request=context['request'])

        is_published_queryset = True
    else:
        is_published_queryset = False

    if not object_list:
        return ''

    verbose_name, verbose_name_plural = get_verbose_name_from_object_list(
        object_list, verbose_name=verbose_name,
        verbose_name_plural=verbose_name_plural)
    c = {
        'request': context['request'],
        'attr': attr,
        'count': len(object_list),
        'object_list': object_list,
        'is_published_queryset': is_published_queryset,
        'verbose_name': verbose_name,
        'verbose_name_plural': verbose_name_plural,
        'per_page': per_page,
        'page_variable': verbose_name + '_page',
        'has_count_if_one': has_count_if_one,
        'has_count': has_count,
    }
    return render_to_string('routines/data_table_list.html', c)


@register.simple_tag(takes_context=True)
def jstree(context, model_name, attr='__str__'):
    c = {
        'model_name': model_name,
        'attr': attr,
        'object': context.get('object'),
    }
    return render_to_string('routines/jstree.html', c)


@register.filter
def order_by(qs, fields):
    return qs.order_by(*fields.split(','))
