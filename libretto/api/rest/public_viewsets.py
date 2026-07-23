"""
Public, read-only index/detail endpoints for the Next.js (musicaLetters)
frontend's standalone entity pages (works, persons, ensembles, places,
roles/instruments, professions, sources).

Each viewset returns the public "chip"/row shapes from ``public_serializers`` and
supports, all server-side so the React MUI X grids stay virtualised:

* ``?q=`` free-text prefix search (Wagtail ``autocomplete()`` backend), matching
  as the user types in the grid filter boxes;
* ``?ordering=<col>`` / ``-<col>`` sorting over the same columns the Django
  ``*TableView`` allow (see ``authority_tables.ORDERING_MAPS``);
* the same column filters as those tables — centuries, FK types, source content
  types (see ``authority_tables.FILTER_SPECS``);
* ``?limit=&offset=`` pagination.

It also exposes a ``filters/`` action (the option lists the grid filter UI needs)
and, for places, a lazy ``tree/`` action mirroring the Django jqTree endpoint.

These live under ``/api/public/`` so they do not collide with the admin-flavoured
``/api/<model>/`` viewsets in ``viewsets.py``.
"""
from django.db.models import (
    BooleanField, Case, Count, Exists, F, IntegerField, Min, OuterRef, Q,
    Subquery, Value, When,
)
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import capfirst
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from wagtail.search.backends import get_search_backend

from . import public_serializers as ps
from .authority_tables import (
    CENTURIES_DATE_RANGES, FILTER_SPECS, ORDERING_MAPS, centuries_options,
    data_type_options,
)
from ...models import (
    Auteur, Individu, Ensemble, Lieu, Oeuvre, Partie, Profession, Source,
    TypeDeSource,
)
from common.utils.file import FileAnalyzer


class PublicPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


# Prefetch paths a ``WorkSerializer`` chip needs, shared by every related
# collection that serializes œuvres (mirrors ``PublicOeuvreViewSet``'s list
# prefetch) so each lazily-loaded page stays cheap.
WORK_PREFETCH = ('genre', 'pupitres__partie', 'auteurs__individu',
                 'auteurs__ensemble', 'auteurs__profession')


class WagtailSearchFilter(BaseFilterBackend):
    """Apply ``?q=`` free-text search using the Wagtail search backend.

    Uses the backend's prefix ``autocomplete()`` mode so the list filter boxes
    match as the user types (the dedicated faceted search at ``/api/public/search``
    keeps ranked full-text ``search()``). ``?autocomplete=1`` is accepted for
    backwards compatibility but is now the default behaviour.
    """

    def filter_queryset(self, request, queryset, view):
        q = request.query_params.get('q', '').strip()
        if not q:
            return queryset
        backend = get_search_backend()
        return backend.autocomplete(q, queryset).get_queryset()


class ColumnFilter(BaseFilterBackend):
    """Apply the per-model column filters declared in ``view.filter_spec``.

    Mirrors the ``filter_*`` methods of the Django ``*TableView`` classes.
    """

    def filter_queryset(self, request, queryset, view):
        for param, conf in getattr(view, 'filter_spec', {}).items():
            value = request.query_params.get(param)
            if not value:
                continue
            kind = conf['kind']
            if kind == 'century':
                date_range = CENTURIES_DATE_RANGES.get(value)
                if date_range is not None:
                    queryset = queryset.filter(
                        **{f"{conf['field']}__range": date_range})
            elif kind == 'fk':
                queryset = queryset.filter(**{f"{conf['field']}_id": value})
            elif kind == 'choice':
                queryset = queryset.filter(**{conf['field']: value})
            elif kind == 'data_type':
                if value in Source.DATA_TYPES:
                    queryset = queryset.filter(
                        pk__in=Source.objects.with_data_type(value))
        return queryset


class OrderingFilter(BaseFilterBackend):
    """Apply ``?ordering=<col>`` using ``view.ordering_map`` (column -> ORM field).

    Runs after the search filter so an explicit sort overrides relevance order.
    Relational (M2M / reverse) sorts are wrapped in ``Min(...)`` so the join does
    not duplicate rows; ``pk`` is always appended for a stable pagination order.
    """

    def filter_queryset(self, request, queryset, view):
        raw = request.query_params.get('ordering', '').strip()
        if not raw:
            return queryset
        descending = raw.startswith('-')
        col = raw[1:] if descending else raw
        field = getattr(view, 'ordering_map', {}).get(col)
        if field is None:
            return queryset
        if self._is_relational(queryset.model, field):
            queryset = queryset.annotate(_order_val=Min(field))
            field = '_order_val'
        prefix = '-' if descending else ''
        return queryset.order_by(f'{prefix}{field}', 'pk')

    @staticmethod
    def _is_relational(model, field):
        if '__' in field:
            return True
        try:
            model_field = model._meta.get_field(field)
        except Exception:
            return False
        return model_field.many_to_many or model_field.one_to_many


def lookup_autocomplete(request, queryset):
    """Type-ahead options for a small lookup table (genre d'œuvre, type de
    source…) whose value list is too long for a plain ``<select>``.

    Returns the ``{value, label}`` shape the frontend filter UI already consumes
    (see ``FilterOption``):

    - ``?ids=<pipe/comma pks>`` restores the labels for a selection stored in the
      URL (so a reloaded page can show the picked option);
    - ``?q=`` prefix-matches via the Wagtail ``autocomplete()`` backend;

    capped at 20 rows.
    """
    ids = request.query_params.get('ids')
    if ids:
        pk_list = [pk for pk in ids.replace('|', ',').split(',') if pk.isdigit()]
        queryset = queryset.filter(pk__in=pk_list)
    else:
        q = request.query_params.get('q', '').strip()
        if q:
            queryset = get_search_backend().autocomplete(
                q, queryset).get_queryset()
        queryset = queryset[:20]
    return Response(
        [{'value': obj.pk, 'label': capfirst(str(obj))} for obj in queryset])


class PublicEntityViewSet(ReadOnlyModelViewSet):
    pagination_class = PublicPagination
    filter_backends = (WagtailSearchFilter, ColumnFilter, OrderingFilter)
    detail_serializer_class = None
    # Key into ORDERING_MAPS / FILTER_SPECS (set per subclass).
    authority_key = None
    # Heavy related collections fetched a page at a time by the ``related/``
    # action (see below). Each subclass maps ``<name> -> {queryset, serializer,
    # select_related?, prefetch?}``; the matching detail serializer exposes only
    # ``<name>_count`` so the frontend can size a bounded, virtualised chip grid
    # without inlining thousands of nested rows.
    RELATED_COLLECTIONS = {}

    @property
    def ordering_map(self):
        return ORDERING_MAPS.get(self.authority_key, {})

    @property
    def filter_spec(self):
        return FILTER_SPECS.get(self.authority_key, {})

    def get_queryset(self):
        return super().get_queryset().published(request=self.request)

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return self.serializer_class

    @action(detail=False)
    def filters(self, request):
        """Option lists for this model's filter UI (see ``filter_spec``)."""
        options = {}
        for param, conf in self.filter_spec.items():
            kind = conf['kind']
            if kind == 'century':
                options[param] = centuries_options()
            elif kind == 'data_type':
                options[param] = data_type_options()
            elif kind == 'choice':
                choices = self.queryset.model._meta.get_field(
                    conf['field']).choices or ()
                options[param] = [
                    {'value': value, 'label': str(label)}
                    for value, label in choices]
            elif kind == 'fk':
                related = self.queryset.model._meta.get_field(
                    conf['field']).related_model
                options[param] = [
                    {'value': pk, 'label': nom}
                    for pk, nom in related.objects.order_by('nom').values_list(
                        'pk', 'nom')]
        return Response(options)

    def children_tree(self, request):
        """Children of ``?parent=<pk>`` as ``{id, label, has_children}`` nodes.

        Lazy-tree counterpart of ``PublicLieuViewSet.tree`` for the other
        self-nesting authority models (œuvre extraits, partie/profession
        children). Published-aware so drafts stay hidden.
        """
        parent_pk = request.query_params.get('parent')
        if not parent_pk:
            return Response([])
        parent = get_object_or_404(self.queryset.model, pk=parent_pk)
        children = parent.get_children().published(request)
        return Response([{
            'id': child.pk,
            'label': capfirst(str(child)),
            'has_children': child.get_children().published(request).exists(),
        } for child in children])

    @action(detail=True, url_path='related')
    def related(self, request, pk=None):
        """One page of a heavy related collection (``?collection=oeuvres``).

        Returns the standard LimitOffset shape (``{count, next, previous,
        results}``) so the frontend's virtualised chip grid can size its scroll
        area to ``count`` and lazy-load chunks via ``?limit=&offset=``. The
        collection is resolved against the subclass's ``RELATED_COLLECTIONS``.
        """
        spec = self.RELATED_COLLECTIONS.get(
            request.query_params.get('collection'))
        if spec is None:
            return Response({'count': 0, 'results': []})
        obj = self.get_object()
        qs = spec['queryset'](obj).published(request=request)
        if spec.get('select_related'):
            qs = qs.select_related(*spec['select_related'])
        if spec.get('prefetch'):
            qs = qs.prefetch_related(*spec['prefetch'])
        paginator = PublicPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        data = spec['serializer'](
            page, many=True, context={'request': request}).data
        return paginator.get_paginated_response(data)


class PublicOeuvreViewSet(PublicEntityViewSet):
    queryset = Oeuvre.objects.filter(extrait_de=None).prefetch_related(
        'genre', 'pupitres__partie', 'auteurs__individu', 'auteurs__ensemble',
        'auteurs__profession',
    )
    serializer_class = ps.WorkSerializer
    detail_serializer_class = ps.WorkDetailSerializer
    authority_key = 'oeuvres'

    RELATED_COLLECTIONS = {
        'dedicataires': {
            'queryset': lambda o: o.dedicataires,
            'serializer': ps.PersonSerializer,
        },
    }

    def get_queryset(self):
        # The detail view needs the full tree of extraits, so it must not be
        # restricted to top-level works like the index list is.
        if self.action == 'retrieve':
            # An excerpt's label prepends its parent-work chain (``extrait_de``),
            # so pull a few ancestor levels in one go (work trees are shallow:
            # opera → acte → scène → morceau).
            ancestor_genres = [
                'extrait_de__' * depth + 'genre' for depth in range(5)
            ]
            return Oeuvre.objects.all().select_related(
                *ancestor_genres).published(request=self.request)
        return super().get_queryset()

    @action(detail=False)
    def children(self, request):
        return self.children_tree(request)


class PublicIndividuViewSet(PublicEntityViewSet):
    queryset = Individu.objects.select_related(
        'naissance_lieu', 'deces_lieu').prefetch_related('professions')
    serializer_class = ps.PersonRowSerializer
    detail_serializer_class = ps.PersonDetailSerializer
    authority_key = 'individus'

    # The heavy related collections shown on a person's page: each can fan out
    # into thousands of fully-nested rows, so they are no longer inlined in the
    # detail response (``PersonDetailSerializer`` exposes only their counts) and
    # are instead fetched a page at a time from the ``related/`` action below.
    # One registry keeps the queryset + serializer in sync between the count
    # fields and the paginated endpoint. Prefetches mirror the matching list
    # viewsets so each page stays cheap.
    RELATED_COLLECTIONS = {
        'oeuvres': {
            'queryset': lambda o: o.oeuvres(),
            'serializer': ps.WorkSerializer,
            'prefetch': ('genre', 'pupitres__partie', 'auteurs__individu',
                         'auteurs__ensemble', 'auteurs__profession'),
        },
        'parties_creees': {
            'queryset': lambda o: o.parties_creees.all(),
            'serializer': ps.PartSerializer,
        },
        'publications': {
            'queryset': lambda o: o.publications(),
            'serializer': ps.SourceSerializer,
            'select_related': ('type',),
        },
        'dedicaces': {
            'queryset': lambda o: o.dedicaces.all(),
            'serializer': ps.WorkSerializer,
            'prefetch': ('genre', 'pupitres__partie', 'auteurs__individu',
                         'auteurs__ensemble', 'auteurs__profession'),
        },
    }


class PublicEnsembleViewSet(PublicEntityViewSet):
    queryset = Ensemble.objects.select_related('type', 'siege')
    serializer_class = ps.EnsembleRowSerializer
    detail_serializer_class = ps.EnsembleDetailSerializer
    authority_key = 'ensembles'

    RELATED_COLLECTIONS = {
        'membres': {
            'queryset': lambda o: Individu.objects.filter(
                membres__ensemble=o).distinct(),
            'serializer': ps.PersonSerializer,
        },
        'oeuvres': {
            'queryset': lambda o: o.oeuvres(),
            'serializer': ps.WorkSerializer,
            'prefetch': WORK_PREFETCH,
        },
    }


class PublicLieuViewSet(PublicEntityViewSet):
    queryset = Lieu.objects.select_related('nature', 'parent')
    serializer_class = ps.PlaceSerializer
    detail_serializer_class = ps.PlaceDetailSerializer
    authority_key = 'lieux'

    RELATED_COLLECTIONS = {
        'individus_nes': {
            'queryset': lambda o: o.individus_nes(),
            'serializer': ps.PersonSerializer,
        },
        'individus_decedes': {
            'queryset': lambda o: o.individus_decedes(),
            'serializer': ps.PersonSerializer,
        },
        'oeuvres_creees': {
            'queryset': lambda o: o.oeuvres_creees(),
            'serializer': ps.WorkSerializer,
            'prefetch': WORK_PREFETCH,
        },
    }

    @action(detail=False)
    def tree(self, request):
        """Lazy place tree: roots (no ``?parent=``) or a node's children.

        Mirrors ``libretto.views.TreeNode`` — published-aware, with a per-row
        ``has_children`` flag so the frontend can render expand toggles lazily.
        """
        parent = request.query_params.get('parent')
        if parent:
            node = get_object_or_404(Lieu, pk=parent)
            children = node.get_children()
        else:
            children = Lieu.objects.filter_roots()
        children = children.published(request).select_related('nature')
        data = [{
            'id': child.pk,
            'nom': child.nom,
            'nature': child.nature.nom if child.nature_id else None,
            'is_institution': child.is_institution,
            'has_children': child.get_children().published(request).exists(),
        } for child in children]
        return Response(data)


class PublicPartieViewSet(PublicEntityViewSet):
    queryset = Partie.objects.all()
    serializer_class = ps.PartRowSerializer
    detail_serializer_class = ps.PartDetailSerializer
    authority_key = 'parties'

    RELATED_COLLECTIONS = {
        'interpretes': {
            'queryset': lambda o: o.interpretes(),
            'serializer': ps.PersonSerializer,
        },
        'repertoire': {
            'queryset': lambda o: o.repertoire(),
            'serializer': ps.WorkSerializer,
            'prefetch': WORK_PREFETCH,
        },
    }

    @action(detail=False)
    def children(self, request):
        return self.children_tree(request)


class PublicProfessionViewSet(PublicEntityViewSet):
    # The individus/œuvres counts shown on each row come from two independent
    # multi-valued relations. Annotating both with ``Count(distinct=True)`` in a
    # single query joins them together, so the rows multiply into a cartesian
    # product the COUNTs then have to de-duplicate — ~3.5 s for one page. Each
    # count is instead computed by a correlated subquery (no join fan-out);
    # ``Coalesce(..., 0)`` keeps professions with no rows at 0 rather than NULL.
    queryset = Profession.objects.annotate(
        individus_count=Coalesce(Subquery(
            Individu.objects.filter(professions=OuterRef('pk')).order_by()
            .values('professions').annotate(c=Count('pk')).values('c'),
            output_field=IntegerField()), 0),
        oeuvres_count=Coalesce(Subquery(
            Auteur.objects.filter(profession=OuterRef('pk'),
                                  oeuvre__isnull=False).order_by()
            .values('profession').annotate(c=Count('oeuvre', distinct=True))
            .values('c'),
            output_field=IntegerField()), 0),
    )
    serializer_class = ps.ProfessionRowSerializer
    detail_serializer_class = ps.ProfessionDetailSerializer
    authority_key = 'professions'

    RELATED_COLLECTIONS = {
        'parties': {
            'queryset': lambda o: o.parties.all(),
            'serializer': ps.PartSerializer,
        },
        'individus': {
            'queryset': lambda o: o.individus,
            'serializer': ps.PersonSerializer,
        },
        'oeuvres': {
            'queryset': lambda o: o.auteurs.oeuvres(),
            'serializer': ps.WorkSerializer,
            'prefetch': WORK_PREFETCH,
        },
    }

    @action(detail=False)
    def children(self, request):
        return self.children_tree(request)


class PublicSourceViewSet(PublicEntityViewSet):
    queryset = Source.objects.select_related('type')
    serializer_class = ps.SourceRowSerializer
    detail_serializer_class = ps.SourceDetailSerializer
    authority_key = 'sources'

    @action(detail=False)
    def source_types(self, request):
        """Type-ahead options for the grid's ``type`` filter (the source-type
        list is too long for a plain ``<select>``)."""
        return lookup_autocomplete(request, TypeDeSource.objects.all())

    @action(detail=False)
    def bibliotheque(self, request):
        """The curated library: promoted sources, image-rich ones first.

        Ports ``libretto.views.BibliothequeView`` (``est_promu=True``, then
        ``position``) but leads with the sources that carry a preview image — the
        same ``is_image`` / descendant-image test as ``Source.preview_image`` — so
        the gallery opens on its visual content instead of burying it. Django's
        bare ``order_by('position')`` only surfaces images early by accident of
        heap order (and not at all once a stable tiebreaker is added); ordering on
        a ``_has_preview`` flag makes it deterministic and pagination-stable.
        ``get_queryset`` already restricts to published rows, so drafts stay
        hidden. Returns the standard LimitOffset envelope for infinite scroll.
        """
        descendant_images = Source.objects.filter(
            Q(parent_id=OuterRef('pk')) | Q(parent__parent_id=OuterRef('pk')),
            type_fichier=FileAnalyzer.IMAGE,
        )
        # Number of scanned page-images a promoted source carries, so the gallery
        # can flag multi-page books (vs a one-shot image). Mirrors
        # ``Source.images``: the descendant image pages, plus the source itself
        # when it is an image. Grouped on a constant so the subquery collapses to
        # one row per outer source.
        descendant_image_count = Coalesce(Subquery(
            descendant_images.order_by().values(_g=Value(1))
            .annotate(c=Count('pk')).values('c'),
            output_field=IntegerField()), 0)
        qs = self.get_queryset().filter(est_promu=True).annotate(
            _has_preview=Case(
                When(type_fichier=FileAnalyzer.IMAGE, then=Value(True)),
                default=Exists(descendant_images),
                output_field=BooleanField(),
            ),
            _pages_count=descendant_image_count + Case(
                When(type_fichier=FileAnalyzer.IMAGE, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
        ).order_by('-_has_preview', F('position').asc(nulls_last=True), 'pk')
        paginator = PublicPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        data = ps.SourceGallerySerializer(
            page, many=True, context={'request': request}).data
        return paginator.get_paginated_response(data)
