"""
Public, read-only **global** search endpoint for the Next.js frontend.

Ports ``dezede.views.SearchView`` to DRF: a single ``?q=`` query across the nine
catalogue content models, faceted by entity type (model) with live per-type
counts, mirroring the site's own search page. Every hit is returned in a uniform
``{id, meta: {type}, label}`` shape (the same ``meta.type`` the React chips key
on) so the frontend can render and route all types — including Dossier and
Événement — without a per-type serializer.

Registered at ``/api/public/search/`` (see ``routers.py``).
"""
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from wagtail.search.backends import get_search_backend
from wagtail.search.backends.base import EmptySearchResults
from wagtail.search.models import IndexEntry

from dossiers.models import Dossier
from typography.utils import replace
from ...models import (
    Ensemble, Evenement, Individu, Lieu, Oeuvre, Partie, Profession, Source,
)

# Same nine models as ``dezede.views.SearchView.content_models``.
CONTENT_MODELS = [
    Dossier, Ensemble, Individu, Lieu, Oeuvre, Profession, Partie, Source,
    Evenement,
]

DEFAULT_LIMIT = 20
MAX_LIMIT = 100

# Public text accessors per content model, used to build the highlighted result
# snippet. These mirror the public text fields each model feeds to the Wagtail
# search index (biography, public notes, descriptions, transcription…), so the
# snippet highlights the very content that caused the match. Private fields
# (``notes_privees``) are deliberately excluded.
SNIPPET_FIELDS = {
    Individu: ('biographie_text', 'notes_publiques_text'),
    Ensemble: ('notes_publiques_text',),
    Lieu: ('historique_text', 'notes_publiques_text'),
    Oeuvre: ('get_description', 'notes_publiques_text'),
    Profession: ('notes_publiques_text',),
    Partie: ('notes_publiques_text',),
    Source: ('transcription_text', 'notes_publiques_text'),
    Evenement: ('notes_publiques_text',),
    Dossier: ('presentation', 'contexte', 'sources_et_protocole',
              'bibliographie'),
}


def build_snippet(obj, q):
    """Highlighted excerpt of ``obj``'s public text where ``q`` was found.

    Concatenates the model's public, searchable text fields and runs the same
    ``highlight`` filter the Django search page uses. Returns ``''`` when the
    query is not present in that text (i.e. it matched the title or a related
    field, already shown as the heading), so we never render an unrelated,
    unhighlighted block of content.
    """
    from ...templatetags.extras import highlight, stripchars
    parts = []
    for attr in SNIPPET_FIELDS.get(type(obj), ()):
        value = getattr(obj, attr, '')
        if callable(value):
            value = value()
        value = str(value or '').strip()
        if value:
            parts.append(value)
    if not parts:
        return ''
    snippet = highlight(stripchars('\n'.join(parts)), q)
    return snippet if '<mark>' in snippet else ''


class PublicSearchViewSet(ViewSet):
    """``GET /api/public/search/?q=&models=<label>&models=<label>&limit=&offset=``."""

    def _int_param(self, request, name, default, minimum, maximum):
        try:
            value = int(request.query_params.get(name, default))
        except (TypeError, ValueError):
            return default
        return max(minimum, min(value, maximum))

    def list(self, request):
        q = replace(request.query_params.get('q', '')).strip()
        if not q:
            return Response({'results': [], 'facets': [], 'count': 0})

        backend = get_search_backend()
        content_types = {
            model: ContentType.objects.get_for_model(model)
            for model in CONTENT_MODELS
        }
        base_qs = IndexEntry.objects.filter(
            content_type__in=list(content_types.values()))
        # The navbar type-ahead passes ``autocomplete=1`` to query the prefix
        # ``AutocompleteField`` index; the full search page omits it and matches
        # whole terms via ``search()`` (mirrors ``WagtailSearchFilter``).
        autocomplete = (request.query_params.get('autocomplete')
                        in ('1', 'true', 'True'))
        if autocomplete:
            results = backend.autocomplete(q, base_qs)
        else:
            results = backend.search(q, base_qs)
        if isinstance(results, EmptySearchResults):
            return Response({'results': [], 'facets': [], 'count': 0})

        # Per-type counts over the whole query (independent of the model
        # selection, so toggling a facet still shows every type's count).
        facet_counts = results.facet('content_type')
        facets = []
        for model in CONTENT_MODELS:
            count = facet_counts.get(content_types[model].id, 0)
            if count:
                facets.append({
                    'value': model._meta.label,
                    'label': str(model._meta.verbose_name_plural),
                    'count': count,
                })

        # Narrow the result list (not the facet counts) by the selected models.
        selected = request.query_params.getlist('models')
        selected_models = [
            model for model in CONTENT_MODELS if model._meta.label in selected
        ] or CONTENT_MODELS
        selected_ct_ids = [content_types[model].id for model in selected_models]
        count = sum(facet_counts.get(ct_id, 0) for ct_id in selected_ct_ids)

        offset = self._int_param(request, 'offset', 0, 0, 10 ** 9)
        limit = self._int_param(request, 'limit', DEFAULT_LIMIT, 1, MAX_LIMIT)
        page = (results.get_queryset()
                .filter(content_type__in=selected_ct_ids)[offset:offset + limit])

        # The full search page shows a highlighted snippet of where the query was
        # found in the entity's public text; the navbar type-ahead only needs the
        # label, and building the snippet is too costly to run per keystroke.
        items = []
        for entry in page:
            obj = entry.content_object
            if obj is None:
                continue
            item = {
                'id': obj.pk,
                'meta': {
                    'type': f'{obj._meta.app_label}.{obj._meta.object_name}',
                },
                # The navbar type-ahead shows full prénoms (Individu.title() ->
                # related_label() -> html(abbr=False)), matching the Django
                # navbar autocomplete; the full search page keeps the
                # abbreviated str(obj), matching the Django search page.
                'label': obj.title() if autocomplete else str(obj),
            }
            if not autocomplete:
                try:
                    item['snippet'] = build_snippet(obj, q)
                except Exception:
                    item['snippet'] = ''
            items.append(item)
        return Response({'results': items, 'facets': facets, 'count': count})
