from django.apps import apps
from django.db.models import Count
from django.http import JsonResponse
from wagtail.admin.auth import require_admin_access


# ``app_label.model_name`` (lower-case) -> the CharField names the Wagtail admin
# may autocomplete. Acts as a whitelist so arbitrary model/field values cannot
# be probed through the public ``model``/``field`` query params.
AUTOCOMPLETE_FIELDS = {
    'libretto.individu': {'prenoms'},
    'libretto.oeuvre': {
        'prefixe_titre', 'coordination', 'prefixe_titre_secondaire',
        'coupe', 'tempo',
    },
    'libretto.source': {'titre', 'lieu_conservation'},
}

MAX_RESULTS = 10


@require_admin_access
def autocomplete_charfield(request):
    """
    Return up to ``MAX_RESULTS`` distinct existing values of a CharField that
    start with ``q``, ranked by frequency. Powers the free-text autocomplete
    widgets of the libretto Wagtail admin forms (see ``AjaxAutocompleteInput``
    in ``libretto/forms.py``).

    Reuses the query shape of the legacy ``CharFieldLookupChannel`` in
    ``libretto/lookups.py`` but served behind the Wagtail admin rather than
    django-ajax-select.
    """
    model_label = request.GET.get('model', '').lower()
    field = request.GET.get('field', '')
    q = request.GET.get('q', '')

    allowed = AUTOCOMPLETE_FIELDS.get(model_label)
    if not allowed or field not in allowed or not q:
        return JsonResponse({'results': []})

    model = apps.get_model(model_label)
    results = (
        model._default_manager
        .filter(**{f'{field}__istartswith': q})
        .values_list(field)
        .order_by(field)
        .annotate(n=Count('pk'))
        .order_by('-n')[:MAX_RESULTS]
    )
    return JsonResponse({'results': [value for value, n in results]})
