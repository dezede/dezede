from django.urls import NoReverseMatch, reverse
from wagtail.admin.admin_url_finder import AdminURLFinder
from wagtail.permission_policies import ModelPermissionPolicy
from wagtail.snippets.models import get_snippet_models

from libretto.wagtail_hooks import scope_to_owner


def reverse_or_none(view_name, pk):
    try:
        return reverse(view_name, args=(pk,))
    except NoReverseMatch:
        return None


def has_owner_field(model):
    return any(f.name == 'owner' for f in model._meta.concrete_fields)


def is_owner_scoped(model):
    """True for CommonModel-based snippets, whose edit/delete views
    (CommonEditView/CommonDeleteView) restrict access to objects owned by the
    user or a descendant and return a 404 outside that scope.
    """
    return model in get_snippet_models() and has_owner_field(model)


def get_admin_urls(user, obj):
    """The edit and delete URLs of `obj` for `user`, as a pair.

    Each one is `None` when `user` may not use it, or when no admin serves it.
    """
    if user is None:
        return None, None

    model = obj._meta.model
    app_label = model._meta.app_label
    model_slug = model._meta.model_name
    is_snippet = model in get_snippet_models()

    # CommonModel-based snippets are scoped to objects owned by the user (or a
    # descendant): CommonEditView/CommonDeleteView return a 404 outside that
    # scope. The URLs must respect it too, otherwise they lead to a 404 even
    # though the user holds the model-level permission.
    if is_snippet and has_owner_field(model) and not scope_to_owner(
            model._default_manager.all(), user).filter(pk=obj.pk).exists():
        return None, None

    # Models are being migrated from the Django admin to Wagtail snippets, so
    # an object's edit/delete pages can live in either backend.
    # AdminURLFinder resolves the Wagtail (snippet/page) edit URL and already
    # respects the user's model-level permissions; we fall back to the Django
    # admin for models still registered there (e.g. dossiers).
    change_url = AdminURLFinder(user).get_edit_url(obj)
    if change_url is None and user.has_perm(f'{app_label}.change_{model_slug}'):
        change_url = reverse_or_none(
            f'admin:{app_label}_{model_slug}_change', obj.pk)

    # AdminURLFinder only resolves edit URLs, so for snippets we gate the
    # delete URL on the snippet's own permission policy (the same one Wagtail
    # uses) and fall back to the Django admin otherwise.
    delete_url = None
    if is_snippet:
        if ModelPermissionPolicy(model).user_has_permission(user, 'delete'):
            delete_url = reverse_or_none(
                f'wagtailsnippets_{app_label}_{model_slug}:delete', obj.pk)
    elif user.has_perm(f'{app_label}.delete_{model_slug}'):
        delete_url = reverse_or_none(
            f'admin:{app_label}_{model_slug}_delete', obj.pk)

    return change_url, delete_url
