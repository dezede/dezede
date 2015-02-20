# coding: utf-8

from __future__ import unicode_literals
from copy import copy
from django.db.models import FieldDoesNotExist
from django.db.models.query import QuerySet
from django.template import Library, Template
from django.contrib.sites.models import get_current_site
from django.utils.encoding import force_text
from libretto.models.common import PublishedQuerySet
from libretto.models.functions import capfirst


register = Library()


def build_permission(app_label, model_slug, action):
    return '%s.%s_%s' % (app_label, model_slug, action)


def build_admin_view_name(perm):
    return 'admin:%s' % perm.replace('.', '_')


@register.inclusion_tag('routines/front-end_admin.html', takes_context=True)
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

    return {
        'has_change_perm': has_change_perm,
        'has_delete_perm': has_delete_perm,
        'admin_change': admin_change,
        'admin_delete': admin_delete,
        'domain': domain,
        'object': obj,
        'size': size,
    }


@register.inclusion_tag('routines/data_table_attr.html', takes_context=True)
def data_table_attr(context, attr, verbose_name=None, obj=None, caps=False):
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
        return {}

    # Renders value using language preferences (as in a template).
    sub_context = copy(context)
    sub_context['value'] = value
    value = Template('{{ value }}').render(sub_context)

    if verbose_name is None:
        try:
            verbose_name = obj._meta.get_field(attr.split('.')[0]).verbose_name
        except FieldDoesNotExist:
            verbose_name = getattr(obj, attr).short_description

    if caps:
        value = capfirst(value.strip())
    return {
        'verbose_name': verbose_name,
        'value': value,
    }


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


@register.assignment_tag(takes_context=True)
def published(context, qs):
    return qs.published(context['request'])


@register.assignment_tag(takes_context=True)
def previous_sibling(context, obj):
    request = context['request']
    return obj.get_previous_sibling(PublishedQuerySet._get_filters(request))


@register.assignment_tag(takes_context=True)
def next_sibling(context, obj):
    request = context['request']
    return obj.get_next_sibling(PublishedQuerySet._get_filters(request))


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
    return object_list.exists()


@register.simple_tag(takes_context=True)
def data_table_list_header(context):
    count = context['pages'].total_count()
    has_count = context['has_count']
    has_count_if_one = context['has_count_if_one']
    verbose_name = context['verbose_name']
    verbose_name_plural = context['verbose_name_plural']
    out = ''
    if has_count and (count != 1 or has_count_if_one):
        out = '%s ' % count
    out += force_text(verbose_name if count == 1 else verbose_name_plural)
    return capfirst(out)


@register.inclusion_tag('routines/data_table_list.html', takes_context=True)
def data_table_list(context, object_list, attr='link',
                    verbose_name=None, verbose_name_plural=None, per_page=10,
                    has_count_if_one=True, has_count=True):

    # Only show what the connected user is allowed to see.
    if isinstance(object_list, PublishedQuerySet):
        object_list = object_list.published(request=context['request'])

        is_published_queryset = True
    else:
        is_published_queryset = False

    if isinstance(object_list, QuerySet):
        object_list = object_list.select_related('etat')

    verbose_name, verbose_name_plural = get_verbose_name_from_object_list(
        object_list, verbose_name=verbose_name,
        verbose_name_plural=verbose_name_plural)

    c = context.__copy__()
    c.update({
        'attr': attr,
        'object_list': object_list,
        'is_published_queryset': is_published_queryset,
        'verbose_name': verbose_name,
        'verbose_name_plural': verbose_name_plural,
        'per_page': per_page,
        'page_variable': verbose_name + '_page',
        'has_count_if_one': has_count_if_one,
        'has_count': has_count,
    })
    return c


@register.inclusion_tag('routines/evenement_list_def.html', takes_context=True)
def evenement_list_def(context, evenements, verbose_name=None,
                       verbose_name_plural=None):
    verbose_name, verbose_name_plural = get_verbose_name_from_object_list(
        evenements, verbose_name=verbose_name,
        verbose_name_plural=verbose_name_plural)
    counter = evenements.count
    name = force_text(verbose_name if counter == 1 else verbose_name_plural)
    c = context.__copy__()
    c.update({'name': name,
              'counter': counter,
              'evenements': evenements})
    return c


@register.inclusion_tag('routines/jqtree.html', takes_context=True)
def jqtree(context, model_path, attr='__str__', id=None):
    app_label, model_name = model_path.split('.')
    c = context.__copy__()
    c.update({
        'app_label': app_label,
        'model_name': model_name,
        'attr': attr,
        'id': id,
    })
    return c


@register.filter
def order_by(qs, fields):
    return qs.order_by(*fields.split(','))
