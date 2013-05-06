# coding: utf-8

from __future__ import unicode_literals
from django.template import Library


register = Library()


@register.assignment_tag(takes_context=True)
def get_fieldsets_and_inlines(context):
    adminform = context['adminform']
    model_admin = adminform.model_admin
    adminform = iter(adminform)
    inlines = iter(context['inline_admin_formsets'])

    fieldsets_and_inlines = []
    for choice in model_admin.fieldsets_and_inlines_order:
        if choice == 'f':
            fieldsets_and_inlines.append(('f', adminform.next()))
        elif choice == 'i':
            fieldsets_and_inlines.append(('i', inlines.next()))

    for fieldset in adminform:
        fieldsets_and_inlines.append(('f', fieldset))
    for inline in inlines:
        fieldsets_and_inlines.append(('i', inline))

    return fieldsets_and_inlines
