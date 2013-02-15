# coding: utf-8

from __future__ import unicode_literals
from django.contrib.contenttypes.generic import GenericRelation
from django.db.models import ManyToManyField, Manager
from django.db.models.query import QuerySet
from django.utils.encoding import smart_unicode
from ..utils import notify_send, print_info


def ask_for_choice(obj, k, v, new_v):
    intro = 'Deux possibilités pour le champ {0} de {1}'.format(k, obj)
    notify_send(intro)
    print_info(intro)
    print_info('1. {} (valeur actuelle)'.format(smart_unicode(v)))
    print_info('2. {} (valeur importable)'.format(smart_unicode(new_v)))
    print_info('3. Créer un nouvel objet')
    return raw_input('Que faire ? (par défaut 2) ')


def get_field_class(object_or_Model, field_name):
    try:
        Meta = object_or_Model.__class__._meta
    except AttributeError:
        Meta = object_or_Model._meta
    return Meta.get_field_by_name(field_name)[0].__class__


MANY_RELATED_FIELDS = (ManyToManyField, GenericRelation)


def is_many_related_field(object_or_class, field_name):
    return get_field_class(object_or_class, field_name) in MANY_RELATED_FIELDS


def is_str(v):
    return isinstance(v, str or unicode)


def get_field_cmp_value(obj, k, v):
    if is_many_related_field(obj, k):
        return v.all()
    elif is_str(v):
        return smart_unicode(v)
    return v


def get_field_settable_value(new_v):
    if is_str(new_v):
        return smart_unicode(new_v)
    return new_v


def get_changed_kwargs(obj, new_kwargs):
    changed_kwargs = {}

    for k, new_v in new_kwargs.items():
        v = getattr(obj, k)
        v = get_field_cmp_value(obj, k, v)
        new_v = get_field_settable_value(new_v)

        if v != new_v or not are_sequences_equal(v, new_v):
            changed_kwargs[k] = new_v

    return changed_kwargs


def separate_m2m_kwargs(Model, filter_kwargs):
    filter_kwargs = filter_kwargs.copy()
    m2m_kwargs = {k: v for k, v in filter_kwargs.items()
                  if is_many_related_field(Model, k.split('__')[0])}
    for k in m2m_kwargs:
        del filter_kwargs[k]
    return filter_kwargs, m2m_kwargs


def enlarged_filter(Model, filter_kwargs):
    filter_kwargs, m2m_kwargs = separate_m2m_kwargs(Model, filter_kwargs)
    qs = Model.objects.filter(**filter_kwargs)
    excluded_pk_list = []
    for k, v in m2m_kwargs.items():
        for obj in qs:
            if not are_sequences_equal(access_related(obj, k), v):
                excluded_pk_list.append(obj.pk)
    return qs.exclude(pk__in=excluded_pk_list)


def enlarged_get(Model, filter_kwargs):
    return enlarged_filter(Model, filter_kwargs).get()


def enlarged_create(Model, filter_kwargs, commit=True):
    filter_kwargs, m2m_kwargs = separate_m2m_kwargs(Model, filter_kwargs)
    obj = Model(**filter_kwargs)
    if commit:
        obj.save()
    for k, v in m2m_kwargs.items():
        getattr(obj, k).add(*v)
    return obj


def access_related(v, lookup):
    base_k = lookup.split('__')[0]
    new_lookup = '__'.join(lookup.split('__')[1:])
    if isinstance(v, Manager):
        v = v.all()
    if is_sequence(v):
        new_v = []
        for item in v:
            item = access_related(item, lookup)
            if is_sequence(item):
                new_v.extend(item)
            else:
                new_v.append(item)
        return new_v
    v = getattr(v, base_k)
    if isinstance(v, Manager):
        v = v.all()
    if not new_lookup:
        return v
    return access_related(v, new_lookup)


def get_or_create(Model, filter_kwargs, unique_keys=(), commit=True):
    if unique_keys:
        unique_kwargs = {}
        for k in unique_keys:
            base_k = k.split('__')[0]
            lookup = '__'.join(k.split('__')[1:])
            v = filter_kwargs[base_k]
            if lookup:
                v = access_related(v, lookup)
            unique_kwargs[k] = v
    else:
        unique_kwargs = filter_kwargs
    try:
        return enlarged_get(Model, unique_kwargs)
    except Model.DoesNotExist:
        return enlarged_create(Model, filter_kwargs, commit=commit)


def is_sequence(v):
    return isinstance(v, (QuerySet, list, tuple))


def try_to_order(seq):
    if isinstance(seq, QuerySet):
        return seq.order_by(*seq.model._meta.ordering)
    return seq


def are_sequences_equal(seq, other_seq):
    if not (is_sequence(seq) and is_sequence(other_seq)):
        return

    seq = try_to_order(seq)
    other_seq = try_to_order(other_seq)

    for seq_item, other_seq_item in map(None,
                                        tuple(seq), tuple(other_seq)):
        if seq_item != other_seq_item:
            return False
    return True


def update_or_create(Model, filter_kwargs, unique_keys=(), commit=True):
    obj = get_or_create(Model, filter_kwargs, unique_keys=unique_keys,
                        commit=commit)
    changed_kwargs = get_changed_kwargs(obj, filter_kwargs)
    if not changed_kwargs:
        return obj
    for k, new_v in changed_kwargs.items():
        v = getattr(obj, k)
        v = get_field_cmp_value(obj, k, v)
        if v == new_v or are_sequences_equal(v, new_v):
            continue
        if v:
            while True:
                choice = ask_for_choice(obj, k, v, new_v)
                if choice in ('2', ''):
                    setattr(obj, k, new_v)
                    break
                elif choice == '3':
                    return enlarged_create(Model, filter_kwargs, commit=commit)
                elif choice == '1':
                    break
        else:
            if is_many_related_field(obj, k):
                getattr(obj, k).add(*new_v)
            else:
                setattr(obj, k, new_v)
    if commit:
        obj.save()
    return obj
