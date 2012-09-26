# coding: utf-8

from django.template import Library
from django.template.loader import render_to_string

register = Library()


@register.simple_tag(takes_context=True)
def frontend_admin(context, object):
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
    return render_to_string('catalogue/front-end_admin.html', c)
