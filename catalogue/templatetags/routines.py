# coding: utf-8

from django.template import Library
from django.template.loader import render_to_string

register = Library()


@register.simple_tag(takes_context=True)
def frontend_admin(context, object=None):
    if object is None:
        object = context['object']
    Model = object.__class__
    app_label = Model._meta.app_label
    model_slug = Model.__name__.lower()
    change_perm = '%s.%s_%s' % (app_label, model_slug, 'change')
    has_change_permission = context['request'].user.has_perm(change_perm)
    admin_change = 'admin:%s' % change_perm.replace('.', '_')
    pk = object.pk
    c = {
        'has_change_permission': has_change_permission,
        'admin_change': admin_change,
        'pk': pk,
    }
    return render_to_string('routines/front-end_admin.html', c)


@register.simple_tag
def list_in_dl(object_list, property_name='link', verbose_name=None,
                                                  verbose_name_plural=None):
    if not object_list:
        return ''
    Model = object_list[0].__class__
    if verbose_name is None:
        verbose_name = Model._meta.verbose_name
    if verbose_name_plural is None:
        verbose_name_plural = Model._meta.verbose_name_plural
    display_list = [getattr(o, property_name)() for o in object_list]
    c = {
        'display_list': display_list,
        'verbose_name': verbose_name,
        'verbose_name_plural': verbose_name_plural,
    }
    return render_to_string('routines/list_in_dl.html', c)
