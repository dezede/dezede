from collections import defaultdict
from functools import lru_cache, wraps
from itertools import batched
from typing import Iterator, OrderedDict, Type

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db.models import (
    F, CharField, Count, Expression, Func, Max, Model, OuterRef, QuerySet,
    Subquery, Value,
)
from django.db.models.functions import Cast, Coalesce, Left
from django.db.models.constants import LOOKUP_SEP
from grappelli.views.related import AutocompleteLookup
from tree.models import TreeModelMixin
from treebeard.mp_tree import MP_Node
from wagtail.models import ReferenceIndex
from wagtail.search.backends.database.postgres.postgres import (
    IndexEntry, PostgresIndex, PostgresSearchBackend, PostgresSearchQueryCompiler,
    PostgresSearchResults, PostgresAutocompleteQueryCompiler,
)
from wagtail.search.index import BaseField, Indexed, RelatedFields, class_is_indexed
from wagtail.search.backends import get_search_backend
from wagtail.search.backends.base import EmptySearchResults

from dezede.models import IndexEntryExtension


class FixedSearchCompilerMixin:
    def _get_filters_from_where_node(self, where_node, check_only=False):
        # We use PostgreSQL, so FilterFields are pointless.
        # It's a Wagtail bug.
        pass

    def _get_order_by(self):
        # We use PostgreSQL, so FilterFields are pointless.
        # It's a Wagtail bug.
        yield from []

    def get_search_fields_for_model(self):
        if self.queryset.model is IndexEntry:
            return []
        return super().get_search_fields_for_model()

    def _get_filterable_field(self, field_attname):
        if self.queryset.model is IndexEntry:
            return None
        return super()._get_filterable_field(field_attname)

    def build_tsrank(self, vector, query, config=None, boost=1) -> Expression:
        return F(
            'extension__boost' if self.queryset.model is IndexEntry
            else 'index_entries__extension__boost'
        ) * super().build_tsrank(vector, query, config, boost)


class FixedPostgresSearchQueryCompiler(FixedSearchCompilerMixin, PostgresSearchQueryCompiler):
    def get_index_vectors(self, search_query):
        if self.queryset.model is IndexEntry:
            return [
                (F("title"), F("title_norm")),
                (F("body"), 1.0),
            ]
        return super().get_index_vectors(search_query)


class FixedPostgresAutocompleteQueryCompiler(FixedSearchCompilerMixin, PostgresAutocompleteQueryCompiler):
    def get_index_vectors(self, search_query):
        if self.queryset.model is IndexEntry:
            return [(F("autocomplete"), F("title_norm"))]
        return [(F("index_entries__autocomplete"), F("index_entries__title_norm"))]


class FixedPostgresSearchResults(PostgresSearchResults):
    def facet(self, field_name):
        # Same method as the original, but skip the pointless FilterField check.

        query = self.query_compiler.search(
            self.query_compiler.get_config(self.backend), None, None
        )
        results = (
            query.values(field_name).annotate(count=Count("pk")).order_by("-count")
        )

        return OrderedDict(
            [(result[field_name], result["count"]) for result in results]
        )


def has_visibility(model: Type[Model]) -> bool:
    local_names = {f.name for f in model._meta.local_fields}
    return {'etat', 'owner'} <= local_names


def refresh_visibility(etat_pk=None) -> None:
    """Copies `etat.public` and `owner` of every indexed object to its index
    entry, optionally only for the objects with the given état.

    Needed when an Etat changes: the objects themselves aren't saved, so
    nothing reindexes them.
    """
    quote = connection.ops.quote_name
    ext = quote(IndexEntryExtension._meta.db_table)
    entry = quote(IndexEntry._meta.db_table)
    etat_table = quote(apps.get_model('libretto', 'Etat')._meta.db_table)
    for model in apps.get_models():
        if not issubclass(model, Indexed) or not has_visibility(model):
            continue
        etat_column = quote(model._meta.get_field('etat').column)
        params = [ContentType.objects.get_for_model(model).pk]
        extra = ''
        if etat_pk is not None:
            extra = f' AND obj.{etat_column} = %s'
            params.append(etat_pk)
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE {ext} AS ext
                SET public = etat.public,
                    owner_pk = obj.{quote(model._meta.get_field('owner').column)}
                FROM {entry} AS entry,
                     {quote(model._meta.db_table)} AS obj,
                     {etat_table} AS etat
                WHERE ext.index_entry_ptr_id = entry.id
                  AND entry.content_type_id = %s
                  AND entry.object_id = obj.{quote(model._meta.pk.column)}::text
                  AND etat.id = obj.{etat_column}{extra}
                """,
                params,
            )


class FixedPostgresIndex(PostgresIndex):
    MODEL_BOOSTS = {
        ('libretto.Œuvre'): 4.0,
        ('libretto.Source'): 0.5,
        ('libretto.Individu'): 6.0,
        ('libretto.Ensemble'): 4.0,
        ('libretto.Lieu'): 5.0,
        ('libretto.Profession'): 2.0,
        ('dossiers.Dossier'): 8.0,
    }
    REFERENCE_BOOST = 0.01
    LEVEL_ATTENUATION = 0.1
    ROW_BOOSTS_CHUNK_SIZE = 1000

    def update_tree_boosts_from_descendants(self, model: Type[Model], batch: list[Model]) -> None:
        # django-tree and treebeard store paths differently, so each computes the
        # "max boost among my strict descendants" map its own way; the map is then
        # applied identically.
        if issubclass(model, TreeModelMixin):
            descendant_boosts_by_path = self._django_tree_descendant_boosts(model, batch)
            path_key = lambda path: path.value
        else:
            descendant_boosts_by_path = self._mp_tree_descendant_boosts(model, batch)
            path_key = tuple
        batch_data = model.objects.filter(
            path__in=descendant_boosts_by_path
        ).values_list(
            'index_entries', 'path', 'index_entries__extension__boost',
        )
        extensions = []
        for index_entry_id, path, boost in batch_data:
            descendant_boost = descendant_boosts_by_path.get(path_key(path))
            if descendant_boost is not None and descendant_boost > boost:
                extensions.append(
                    IndexEntryExtension(pk=index_entry_id, boost=descendant_boost)
                )
        # This is an upsert. An existing row only gets its `boost` changed, so
        # `public` and `owner_pk` stay. A missing row would be created with the
        # default `public=False`, and its object would be hidden from search.
        IndexEntryExtension.objects.bulk_create(
            extensions,
            unique_fields=['pk'],
            update_fields=['boost'],
            update_conflicts=True,
        )

    def _django_tree_descendant_boosts(self, model: Type[Model], batch: list[Model]) -> dict:
        # django-tree >= 1.0: a path is an opaque bytea key (no array slicing), so
        # descendants are selected with the `strict_descendant_of` lookup. A single
        # correlated subquery yields, per batch node, the max boost among its strict
        # descendants — no per-level grouping needed. Keyed by the raw bytes value
        # (a `Path` is unhashable), which is also a valid `path__in` operand.
        descendant_boost = Subquery(
            model.objects
            .filter(path__strict_descendant_of=OuterRef('path'))
            .order_by()
            .values(_group=Value(1))
            .annotate(_max=Max('index_entries__extension__boost'))
            .values('_max')
        )
        return {
            path.value: boost
            for path, boost in (
                model.objects
                .filter(pk__in=[obj.pk for obj in batch])
                .annotate(descendant_boost=descendant_boost)
                .values_list('path', 'descendant_boost')
            )
            if boost is not None
        }

    def _mp_tree_descendant_boosts(self, model: Type[Model], batch: list[Model]) -> dict:
        paths_by_level = defaultdict(list)
        for path, level in model.objects.filter(
            pk__in=[obj.pk for obj in batch]
        ).values_list('path', 'depth'):
            paths_by_level[level].append(path)
        descendant_boosts_by_path = {}
        for level, paths in paths_by_level.items():
            for path, boost in model.objects.annotate(
                truncated_path=Left('path', MP_Node.steplen * level),
            ).filter(
                depth=level,
                truncated_path__in=paths,
            ).values_list('truncated_path').annotate(boost=Max('index_entries__extension__boost')):
                descendant_boosts_by_path[tuple(path)] = boost
        return descendant_boosts_by_path

    @staticmethod
    def get_visibility(model: Type[Model], batch: list[Model]) -> dict[str, tuple]:
        # One query per batch is cheaper than two correlated subqueries per
        # index entry.
        if not has_visibility(model):
            return {}
        return {
            str(pk): (public, owner_pk)
            for pk, public, owner_pk in model.objects.filter(
                pk__in=[obj.pk for obj in batch],
            ).values_list('pk', 'etat__public', 'owner_id')
        }

    def update_row_boosts(self, model: Type[Model], objs: list[Model], stdout=None) -> None:
        content_type = ContentType.objects.get_for_model(model)

        model_boost = self.MODEL_BOOSTS.get((model._meta.label), 1.0)

        references_boost = 1.0 + self.REFERENCE_BOOST * Coalesce(
            ReferenceIndex.objects.filter(
                to_content_type=content_type,
                to_object_id=Cast(OuterRef('object_id'), CharField()),
            ).order_by().annotate(n=Func('pk', function='COUNT')).values('n'),
            0,
        )

        depth_penalty = 1.0
        if issubclass(model, (TreeModelMixin, MP_Node)):
            depth_penalty = (
                1.0 + self.LEVEL_ATTENUATION * (
                    Subquery(
                        model.objects.filter(
                            pk=Cast(OuterRef('object_id'), model._meta.pk)
                        ).values('path__level' if issubclass(model, TreeModelMixin) else 'depth')[:1]
                    ) - 1
                )
            )

        for batch in batched(objs, self.ROW_BOOSTS_CHUNK_SIZE):
            entries = IndexEntry.objects.filter(
                content_type=content_type,
                object_id__in=[f'{obj.pk}' for obj in batch],
            ).values_list('pk', 'object_id').annotate(
                boost=model_boost * references_boost / depth_penalty,
            )

            visibility_by_object_id = self.get_visibility(model, batch)
            # A model with an état hides an object missing from the map (it was
            # deleted meanwhile); a model without one is always public.
            fallback = (not has_visibility(model), None)
            index_entry_extensions = []
            for index_entry_id, object_id, boost in entries:
                public, owner_pk = visibility_by_object_id.get(object_id, fallback)
                index_entry_extensions.append(IndexEntryExtension(
                    pk=index_entry_id, boost=boost,
                    public=public, owner_pk=owner_pk))
            IndexEntryExtension.objects.bulk_create(
                index_entry_extensions,
                unique_fields=['pk'],
                update_fields=['boost', 'public', 'owner_pk'],
                update_conflicts=True,
            )
            if issubclass(model, (TreeModelMixin, MP_Node)):
                self.update_tree_boosts_from_descendants(model, batch)
            if stdout is not None:
                stdout.write('.', ending='')

    def add_items(self, model, objs) -> None:
        super().add_items(model, objs)
        self.update_row_boosts(model, objs)


class FixedPostgresSearchBackend(PostgresSearchBackend):
    query_compiler_class = FixedPostgresSearchQueryCompiler
    autocomplete_query_compiler_class = FixedPostgresAutocompleteQueryCompiler
    results_class = FixedPostgresSearchResults
    index_class = FixedPostgresIndex

    def _search(self, query_compiler_class, query, model_or_queryset, **kwargs):
        # Copied from the BaseSearchBackend, with a condition changed to support querying IndexEntry directly.

        # Find model/queryset
        if isinstance(model_or_queryset, QuerySet):
            model = model_or_queryset.model
            queryset = model_or_queryset
        else:
            model = model_or_queryset
            queryset = model_or_queryset.objects.all()

        # Model must be a class that is in the index
        if model is not IndexEntry and not class_is_indexed(model):
            return EmptySearchResults()

        # Check that there's still a query string after the clean up
        if query == "":
            return EmptySearchResults()

        # Search
        search_query_compiler = query_compiler_class(queryset, query, **kwargs)

        # Check the query
        search_query_compiler.check()

        return self.results_class(self, search_query_compiler)


def recursive_relations_iterator(search_fields: list[BaseField | RelatedFields]) -> Iterator[list[str]]:
    for search_field in search_fields:
        if isinstance(search_field, RelatedFields):
            has_nested_relations = False
            for child_lookup_list in recursive_relations_iterator(search_field.fields):
                yield [search_field.field_name, *child_lookup_list]
                has_nested_relations = True
            if not has_nested_relations:
                yield [search_field.field_name]


@lru_cache
def get_search_relations():
    relations = defaultdict(lambda: {
        'contained_relations': [],
        'related': defaultdict(set),
    })
    for model in apps.get_models():
        if not issubclass(model, Indexed):
            continue
        contained_relations = []
        for lookups in recursive_relations_iterator(model.get_search_fields()):
            contained_relations.append(LOOKUP_SEP.join(lookups))
            related_model = model
            for i, lookup in enumerate(lookups):
                related_model = related_model._meta.get_field(lookup).related_model
                relations[related_model]['related'][model].add(LOOKUP_SEP.join(lookups[:i+1]))
        relations[model]['contained_relations'] = contained_relations
    return relations


@wraps(Indexed.get_indexed_objects)
def faster_get_indexed_objects(cls):
    return cls.objects.prefetch_related(*get_search_relations()[cls]['contained_relations'])

Indexed.get_indexed_objects = classmethod(faster_get_indexed_objects)


@wraps(AutocompleteLookup.get_searched_queryset)
def wagtail_grappelli_get_searched_queryset(self, qs):
    model = self.model
    term = self.GET["term"]

    try:
        term = model.autocomplete_term_adjust(term)
    except AttributeError:
        pass

    s = get_search_backend()

    return s.autocomplete(term, model).get_queryset()


@wraps(AutocompleteLookup.get_queryset)
def wagtail_grappelli_search_get_queryset(self):
    qs = super(AutocompleteLookup, self).get_queryset()
    qs = self.get_searched_queryset(qs)
    return qs.distinct()


AutocompleteLookup.get_searched_queryset = wagtail_grappelli_get_searched_queryset
AutocompleteLookup.get_queryset = wagtail_grappelli_search_get_queryset
