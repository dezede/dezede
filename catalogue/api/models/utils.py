# coding: utf-8

from django.utils.encoding import smart_unicode
from ..utils import notify_send, print_info


def ask_for_choice(object, k, v, new_v):
    intro = 'Deux possibilités pour le champ %s de %s.' % (k, object)
    notify_send(intro)
    print_info(intro)
    print_info('1. %s (valeur actuelle)' % v)
    print_info('2. %s (valeur importable)' % new_v)
    print_info('3. Créer un nouvel objet')
    return raw_input('Que faire ? (par défaut 2) ')


def update_or_create(Model, unique_keys, **kwargs):
    unique_kwargs = {k: kwargs[k] for k in unique_keys}
    try:
        object = Model.objects.get(**unique_kwargs)
    except Model.DoesNotExist:
        return Model.objects.create(**kwargs)
    changed_kwargs = {k: smart_unicode(v) if isinstance(v, str or unicode)
    else v for k, v in kwargs.items()
                      if smart_unicode(getattr(object, k)) != smart_unicode(v)}
    if not changed_kwargs:
        return object
    for k, new_v in changed_kwargs.items():
        v = getattr(object, k)
        if v:
            setattr(object, k, new_v)
        else:
            while True:
                choice = ask_for_choice(object, k, v, new_v)
                if choice in ('2', ''):
                    setattr(object, k, new_v)
                    break
                elif choice == '3':
                    return Model.objects.create(**kwargs)
                elif choice == '1':
                    break
    object.save()
    return object
