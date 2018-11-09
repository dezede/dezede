from django.core.cache import cache


def get_user_lock_cache_key(user):
    return f'dossiers__export_en_cours__{user.username}'


def is_user_locked(user):
    return cache.get(get_user_lock_cache_key(user), False)


def lock_user(user):
    cache.set(get_user_lock_cache_key(user), True)


def unlock_user(user):
    cache.set(get_user_lock_cache_key(user), False)
