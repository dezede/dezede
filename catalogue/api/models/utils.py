# coding: utf-8

from __future__ import unicode_literals
from django.db.models import ManyToManyField
from django.utils.encoding import smart_unicode
from ..utils import notify_send, print_info


def ask_for_choice(object, k, v, new_v):
    intro = 'Deux possibilités pour le champ {0} de {1}'.format(k, object)
    notify_send(intro)
    print_info(intro)
    print_info('1. {} (valeur actuelle)'.format(v))
    print_info('2. {} (valeur importable)'.format(new_v))
    print_info('3. Créer un nouvel objet')
    return raw_input('Que faire ? (par défaut 2) ')


def get_field_class(object_or_Model, field_name):
    try:
        Meta = object_or_Model.__class__._meta
    except AttributeError:
        Meta = object_or_Model._meta
    return Meta.get_field_by_name(field_name)[0].__class__


def is_many_to_many_field(object_or_class, field_name):
    return get_field_class(object_or_class, field_name) == ManyToManyField


def is_str(v):
    return isinstance(v, str or unicode)


def get_field_cmp_value(object, k, v):
    if is_many_to_many_field(object, k):
        return v.all()
    elif is_str(v):
        return smart_unicode(v)
    return v


def get_field_settable_value(new_v):
    if is_str(new_v):
        return smart_unicode(new_v)
    return new_v


def get_changed_kwargs(object, new_kwargs):
    changed_kwargs = {}

    for k, new_v in new_kwargs.iteritems():
        v = getattr(object, k)
        v = get_field_cmp_value(object, k, v)
        new_v = get_field_settable_value(new_v)

        if v != new_v:
            changed_kwargs[k] = new_v

    return changed_kwargs


def enlarged_get(Model, **kwargs):
    new_kwargs = {}
    for k, v in kwargs.iteritems():
        if is_many_to_many_field(Model, k):
            new_kwargs[k + '__in'] = v
        else:
            new_kwargs[k] = v
    return Model.objects.get(**new_kwargs)


def enlarged_create(Model, **kwargs):
    kwargs = kwargs.copy()
    m2m_kwargs = {k: v for k, v in kwargs.iteritems()
                  if is_many_to_many_field(Model, k)}
    for k in m2m_kwargs:
        del kwargs[k]
    object = Model.objects.create(**kwargs)
    for k, v in m2m_kwargs.iteritems():
        getattr(object, k).add(*v)
    return object


def update_or_create(Model, unique_keys, **kwargs):
    unique_kwargs = {k: kwargs[k] for k in unique_keys}

    try:
        object = enlarged_get(Model, **unique_kwargs)
    except Model.DoesNotExist:
        return enlarged_create(Model, **kwargs)
    changed_kwargs = get_changed_kwargs(object, kwargs)
    if not changed_kwargs:
        return object
    for k, new_v in changed_kwargs.iteritems():
        v = getattr(object, k)
        v = get_field_cmp_value(object, k, v)
        if v == new_v:
            continue
        if v:
            while True:
                choice = ask_for_choice(object, k, v, new_v)
                if choice in ('2', ''):
                    setattr(object, k, new_v)
                    break
                elif choice == '3':
                    return enlarged_create(Model, **kwargs)
                elif choice == '1':
                    break
        else:
            if is_many_to_many_field(object, k):
                getattr(object, k).add(*new_v)
            else:
                setattr(object, k, new_v)
    object.save()
    return object
