from collections import OrderedDict
from functools import wraps
import json
from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.core import serializers
from django.db import transaction, connection
from django.db.models import ManyToManyField, Manager, Model
from django.db.models.constants import LOOKUP_SEP
from django.db.models.fields.related import ForeignObjectRel
from django.db.models.query import QuerySet
from typography.utils import replace
from ...models.base import PublishedModel, CommonModel, SpaceTimeValue
from ..utils import notify_send, print_info
from ..utils.console import info, colored_diff, error


def clean_string(string):
    return string.strip()


def get_obj_contents(obj):
    contents = {}
    for k in [f.name for f in obj._meta.fields if f is not obj._meta.pk]:
        v = getattr(obj, k)
        if v:
            contents[k] = v
    return contents


def pprintable_dict(d):
    return f"({', '.join(f'{k}={v!r}' for k, v in d.items())})"


def ask_for_choice(intro, choices, start=1, allow_empty=False, default=None):
    notify_send(intro)
    print_info(intro)

    default_message = '' if default is None else f' (par défaut {default})'
    question = f"Que choisir{default_message} ? "

    for i, obj in enumerate(choices, start=start):
        if isinstance(obj, tuple):
            obj, msg = obj
            s = f'{obj} {info(msg)}'
        else:
            s = f'{obj}'
        out = f"{info(f'{i}.')} {s}"
        if isinstance(obj, Model):
            out += f' {pprintable_dict(get_obj_contents(obj))}'
        print(out)

    while True:
        choice = input(info(question).encode('utf-8'))
        if choice.isdigit():
            choice = int(choice)
            if 0 <= choice - start < len(choices):
                return choice - start
        elif allow_empty and not choice:
            return default if default is None else default - start
        print(error('Choix invalide !'))


def serialize(l):
    serializations = []
    for item in l:
        if isinstance(item, QuerySet):
            serializations.append(serializers.serialize('json', item))
        elif isinstance(item, Model):
            serializations.append(serializers.serialize('json', [item]))
        elif isinstance(item, (list, tuple)):
            serializations.append(serialize(item))
        elif isinstance(item, dict):
            item = OrderedDict(item)
            serializations.append(
                '{%s}' % ', '.join(f'{k}: {v}' for k, v in
                                   zip(item.keys(), serialize(item.values()))))
        else:
            serializations.append(json.dumps(item))
    return ','.join(serializations)


OLD_NOW_OR_CREATE_CACHE = {}


def ask_for_old_new_or_create(obj, k, v, new_v):
    cache_key = serialize([obj, k, v, new_v])
    if cache_key in OLD_NOW_OR_CREATE_CACHE:
        return OLD_NOW_OR_CREATE_CACHE[cache_key]

    intro = 'Deux possibilités pour le champ {0} de {1}'.format(k, obj)
    v, new_v = colored_diff(str(v), str(new_v))
    choices = (
        (v, 'valeur actuelle'),
        (new_v, 'valeur importable'),
        'Créer un nouvel objet',
    )
    result = ask_for_choice(intro, choices, allow_empty=True, default=1)
    OLD_NOW_OR_CREATE_CACHE[cache_key] = result
    return result


MANY_RELATED_FIELDS = (ManyToManyField, GenericRelation)


def is_many_related_field(object_or_model, field_name):
    field = object_or_model._meta.get_field(field_name)
    if isinstance(field, ForeignObjectRel):
        field = field.field
    return isinstance(field, MANY_RELATED_FIELDS)


def get_field_cmp_value(obj, k, v):
    if is_many_related_field(obj, k):
        return v.all()
    elif isinstance(v, str):
        return v
    return v


def get_field_settable_value(new_v):
    if isinstance(new_v, str):
        return replace(new_v)
    return new_v


def get_changed_kwargs(obj, new_kwargs):
    changed_kwargs = {}

    for k, new_v in new_kwargs.items():
        old_v = getattr(obj, k)
        old_v = get_field_cmp_value(obj, k, old_v)
        new_v = get_field_settable_value(new_v)

        if old_v != new_v or not are_sequences_equal(old_v, new_v):
            changed_kwargs[k] = new_v

    return changed_kwargs


def separate_m2m_kwargs(Model, filter_kwargs):
    filter_kwargs = filter_kwargs.copy()
    m2m_kwargs = {k: v for k, v in filter_kwargs.items()
                  if is_many_related_field(Model, k.split(LOOKUP_SEP)[0])}
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


ENLARGED_GET_CACHE = {}


def enlarged_get(Model, filter_kwargs):
    qs = enlarged_filter(Model, filter_kwargs)
    n = qs.count()
    if n <= 1:
        return qs.get()

    cache_key = serialize([filter_kwargs, qs])
    if cache_key in ENLARGED_GET_CACHE:
        return ENLARGED_GET_CACHE[cache_key]

    intro = (f'{n} objets trouvés '
             f'pour les arguments {pprintable_dict(filter_kwargs)}')
    ENLARGED_GET_CACHE[cache_key] = result = qs[ask_for_choice(intro, qs)]
    return result


def enlarged_create(Model, filter_kwargs, commit=True):
    filter_kwargs, m2m_kwargs = separate_m2m_kwargs(Model, filter_kwargs)
    obj = Model(**filter_kwargs)
    if commit:
        obj.save()
    for k, v in m2m_kwargs.items():
        getattr(obj, k).add(*v)
    return obj


def access_related(v, lookup):
    base_k = lookup.split(LOOKUP_SEP)[0]
    new_lookup = LOOKUP_SEP.join(lookup.split(LOOKUP_SEP)[1:])
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
            base_k = k.split(LOOKUP_SEP)[0]
            lookup = LOOKUP_SEP.join(k.split(LOOKUP_SEP)[1:])
            if base_k not in filter_kwargs:
                continue
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


def are_sequences_equal(seq, other_seq):
    if not (is_sequence(seq) and is_sequence(other_seq)):
        return

    seq = list(seq)
    other_seq = list(other_seq)

    if len(seq) != len(other_seq):
        return False

    for seq_item in seq:
        if seq_item not in other_seq:
            return False
        seq.remove(seq_item)
        other_seq.remove(seq_item)
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

        if old_v == new_v or are_sequences_equal(old_v, new_v):
            continue

        if old_v:

            choice = None
            if isinstance(old_v, SpaceTimeValue):
                if old_v.is_more_precise_than(new_v):
                    choice = KEEP

            if choice is None and conflict_handling == INTERACTIVE:
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


class SetDefaultOwner(object):
    model = CommonModel
    fieldname = 'owner'

    def __init__(self, obj):
        self.obj = obj
        self.originals = {}

    def field_iterator(self):
        for model in apps.get_models(include_auto_created=True):
            if issubclass(model, self.model):
                field = model._meta.get_field(self.fieldname)
                key = (model._meta.app_label, model._meta.model_name, field)
                yield key, field

    def __enter__(self):
        for key, field in self.field_iterator():
            self.originals[key] = field.default
            field.default = lambda: self.obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key, field in self.field_iterator():
            field.default = self.originals[key]

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return inner


class SetDefaultEtat(SetDefaultOwner):
    model = PublishedModel
    fieldname = 'etat'


def _get_queryset(field, obj):
    return field.model.objects.filter(**{field.name: obj}).distinct()


def _related_queryset_iterator(duplicate_relations, reference_relations, duplicate, reference):
    for relation in duplicate_relations:
        field = relation.field
        qs = _get_queryset(field, duplicate)
        duplicate_n = qs.count()
        if duplicate_n == 0:
            continue
        if relation not in reference_relations:
            raise TypeError('Relations to the duplicate cannot be moved to the reference.')
        reference_n = _get_queryset(field, reference).count()
        yield field, qs
        assert _get_queryset(field, duplicate).count() == 0
        assert _get_queryset(field, reference).count() == reference_n + duplicate_n


def are_mergeable_models(model_a, model_b):
    parent_models_a = set(model_a._meta.parents.keys())
    parent_models_a.add(model_a)
    parent_models_b = set(model_b._meta.parents.keys())
    parent_models_b.add(model_b)
    return not parent_models_a.isdisjoint(parent_models_b)


def get_related_fks_and_1to1(model):
    return [f for f in model._meta.get_fields()
            if (f.one_to_many or f.one_to_one)
            and f.auto_created and not f.concrete]


def get_related_m2ms(model):
    return [f for f in model._meta.get_fields(include_hidden=True)
            if f.many_to_many and f.auto_created]


@transaction.atomic
def merge_duplicate(duplicate, reference, dry_run=False):
    duplicate_model = duplicate._meta.model
    reference_model = reference._meta.model
    if not are_mergeable_models(duplicate_model, reference_model):
        raise TypeError('Duplicate and reference are from different models.')

    # Updating related ForeignKeys & OneToOneFields.
    fk_relations = get_related_fks_and_1to1(duplicate_model)
    reference_fk_relations = get_related_fks_and_1to1(reference_model)
    for field, qs in _related_queryset_iterator(
            fk_relations, reference_fk_relations, duplicate, reference):
        # We use `obj.save` instead of `qs.update` to trigger save events
        # such as checks, updates and signals.
        for obj in qs:
            setattr(obj, field.name, reference)
            obj.save()

    # Updating related ManyToManyFields.
    m2m_relations = get_related_m2ms(duplicate_model)
    reference_m2m_relations = get_related_m2ms(reference_model)
    for field, qs in _related_queryset_iterator(
            m2m_relations, reference_m2m_relations, duplicate, reference):
        for obj in qs:
            manager = getattr(obj, field.name)
            manager.add(reference)
            manager.remove(duplicate)

    duplicate.delete()

    if dry_run:
        connection.needs_rollback = True
