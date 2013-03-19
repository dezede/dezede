# coding: utf-8

from __future__ import unicode_literals
from django.contrib.contenttypes.generic import GenericRelation
from django.db.models import ManyToManyField, Manager, Model
from django.db.models.fields.related import RelatedField
from django.db.models.query import QuerySet
from django.utils import six
from django.utils.encoding import smart_text
from catalogue.api.utils.console import info, colored_diff, error
from typography.utils import replace
from ..utils import notify_send, print_info


# Python 2 & 3 compatibility.
if not six.PY3:
    input = raw_input


def get_obj_contents(obj):
    contents = {}
    for k in [f.name for f in obj._meta.fields if f is not obj._meta.pk]:
        v = getattr(obj, k)
        if v:
            contents[k] = v
    return contents


def pprintable_dict(d):
    return '(%s)' % ', '.join('%s=%s' % (k, smart_text(repr(v)))
                              for k, v in d.items())


def ask_for_choice(intro, choices, start=1, allow_empty=False, default=None):
    notify_send(intro)
    print_info(intro)

    question = 'Que choisir{} ? '.format(
        '' if default is None else ' (par défaut {})'.format(default))

    for i, obj in enumerate(choices, start=start):
        if isinstance(obj, tuple):
            obj, msg = obj
            s = '{} {}'.format(obj, info(msg))
        else:
            s = smart_text(obj)
        out = '{} {}'.format(info('{}.'.format(i)), s)
        if isinstance(obj, Model):
            out += ' ' + pprintable_dict(get_obj_contents(obj))
        print(out)

    while True:
        choice = input(info(question))
        if choice.isdigit():
            choice = int(choice)
            if 0 <= choice - start < len(choices):
                return choice - start
        elif allow_empty and not choice:
            return default if default is None else default - start
        print(error('Choix invalide !'))


def ask_for_old_new_or_create(obj, k, v, new_v):
    intro = 'Deux possibilités pour le champ {0} de {1}'.format(k, obj)
    v, new_v = colored_diff(smart_text(v), smart_text(new_v))
    choices = (
        (v, 'valeur actuelle'),
        (new_v, 'valeur importable'),
        'Créer un nouvel objet',
    )
    return ask_for_choice(intro, choices, allow_empty=True, default=1)


def get_field_class(object_or_Model, field_name):
    return object_or_Model._meta.get_field(field_name).__class__


MANY_RELATED_FIELDS = (ManyToManyField, GenericRelation)


def is_many_related_field(object_or_class, field_name):
    return get_field_class(object_or_class, field_name) in MANY_RELATED_FIELDS


def is_str(v):
    return isinstance(v, six.string_types)


def get_field_cmp_value(obj, k, v):
    if is_many_related_field(obj, k):
        return v.all()
    elif is_str(v):
        return smart_text(v)
    return v


def get_field_settable_value(new_v):
    if is_str(new_v):
        return replace(smart_text(new_v))
    return new_v


def get_changed_kwargs(obj, new_kwargs):
    changed_kwargs = {}

    for k, new_v in new_kwargs.items():
        v = getattr(obj, k)
        v = get_field_cmp_value(obj, k, v)
        new_v = get_field_settable_value(new_v)

        if not are_equal(v, new_v):
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
    qs = enlarged_filter(Model, filter_kwargs)
    n = qs.count()
    if n <= 1:
        return qs.get()
    intro = '%d objets trouvés pour les arguments %s' \
            % (n, pprintable_dict(filter_kwargs))
    return qs[ask_for_choice(intro, qs)]


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
        return enlarged_get(Model, unique_kwargs), False
    except Model.DoesNotExist:
        return enlarged_create(Model, filter_kwargs, commit=commit), True


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

    for seq_item, other_seq_item in map(None, tuple(seq), tuple(other_seq)):
        if seq_item != other_seq_item:
            return False
    return True


def are_equal(v1, v2):
    return v1 == v2 or are_sequences_equal(v1, v2)


def is_same_and_more_detailed(obj, ref_obj):
    if obj.__class__ is not ref_obj.__class__:
        return False
    for k in [f.name for f in obj._meta.fields if f is not obj._meta.pk]:
        v = getattr(ref_obj, k)
        if v:
            if getattr(obj, k, None) != v:
                return False
    return True


# Conflict handling variables.
INTERACTIVE = 'interactive'
KEEP = 'keep'
OVERRIDE = 'override'
CREATE = 'create'
CONFLICT_HANDLINGS = (INTERACTIVE, KEEP, OVERRIDE, CREATE)


def update_or_create(Model, filter_kwargs, unique_keys=(), commit=True,
                     conflict_handling=INTERACTIVE):

    if conflict_handling not in CONFLICT_HANDLINGS:
        raise Exception('`conflict_handling` must be in CONFLICT_HANDLINGS.')

    obj, created = get_or_create(Model, filter_kwargs, unique_keys=unique_keys,
                                 commit=commit)
    if created:
        return obj

    changed_kwargs = get_changed_kwargs(obj, filter_kwargs)
    if not changed_kwargs:
        return obj

    for k, new_v in changed_kwargs.items():
        if new_v in ('', None):
            continue

        old_v = getattr(obj, k)
        old_v = get_field_cmp_value(obj, k, old_v)

        if are_equal(old_v, new_v):
            continue

        new_is_more_detailed = isinstance(Model._meta.get_field(k),
                                          RelatedField) \
            and is_same_and_more_detailed(old_v, new_v)

        if old_v and not new_is_more_detailed:

            if conflict_handling == INTERACTIVE:
                choice = ask_for_old_new_or_create(obj, k, old_v, new_v)
                choice = {0: KEEP, 1: OVERRIDE, 2: CREATE}[choice]
            else:
                choice = conflict_handling

            if choice == KEEP:
                break
            elif choice == OVERRIDE:
                setattr(obj, k, new_v)
                break
            elif choice == CREATE:
                return enlarged_create(Model, filter_kwargs, commit=commit)

        else:
            if is_many_related_field(obj, k):
                getattr(obj, k).add(*new_v)
            else:
                setattr(obj, k, new_v)

    if commit:
        obj.save()
    return obj
