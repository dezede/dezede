from collections import defaultdict
from functools import lru_cache, wraps
from itertools import batched
from typing import Iterator, OrderedDict, Type

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    F, CharField, Count, Expression, Func, Max, Model, OuterRef, QuerySet, Subquery
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


class FixedPostgresIndex(PostgresIndex):
    MODEL_BOOSTS = {
        ('libretto', 'oeuvre'): 4.0,
        ('libretto', 'source'): 0.5,
        ('libretto', 'individu'): 6.0,
        ('libretto', 'ensemble'): 4.0,
        ('libretto', 'lieu'): 5.0,
        ('libretto', 'profession'): 2.0,
        ('dossiers', 'dossier'): 8.0,
    }
    REFERENCE_BOOST = 0.01
    LEVEL_ATTENUATION = 0.1
    ROW_BOOSTS_CHUNK_SIZE = 1000

    def update_tree_boosts_from_descendants(self, model: Type[Model], batch: list[Model]) -> None:
        paths_by_level = defaultdict(list)
        for path, level in model.objects.filter(pk__in=[obj.pk for obj in batch]).values_list(
            'path', 'path__len' if issubclass(model, TreeModelMixin) else 'depth',
        ):
            paths_by_level[level].append(path)
        descendant_boosts_by_path = {}
        for level, paths in paths_by_level.items():
            for path, boost in model.objects.annotate(
                truncated_path=(
                    F(f'path__0_{level}') if issubclass(model, TreeModelMixin)
                    else Left('path', MP_Node.steplen * level)
                ),
            ).filter(
                **({'path__len__gt': level} if issubclass(model, TreeModelMixin) else {'depth': level}),
                truncated_path__in=paths,
            ).values_list('truncated_path').annotate(boost=Max('index_entries__extension__boost')):
                descendant_boosts_by_path[tuple(path)] = boost
        batch_data = model.objects.filter(
            path__in=descendant_boosts_by_path
        ).values_list(
            'index_entries', 'path', 'index_entries__extension__boost',
        )
        extensions = []
        for index_entry_id, path, boost in batch_data:
            descendant_boost = descendant_boosts_by_path.get(tuple(path))
            if descendant_boost is not None and descendant_boost > boost:
                extensions.append(
                    IndexEntryExtension(pk=index_entry_id, boost=descendant_boost)
                )
        IndexEntryExtension.objects.bulk_create(
            extensions,
            unique_fields=['pk'],
            update_fields=['boost'],
            update_conflicts=True,
        )

    def update_row_boosts(self, model: Type[Model], objs: list[Model], stdout=None) -> None:
        content_type = ContentType.objects.get_for_model(model)

        model_boost = self.MODEL_BOOSTS.get(model, 1.0)

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
                        ).values('path__len' if issubclass(model, TreeModelMixin) else 'depth')[:1]
                    ) - 1
                )
            )

        for batch in batched(objs, self.ROW_BOOSTS_CHUNK_SIZE):
            entries = IndexEntry.objects.filter(
                content_type=content_type,
                object_id__in=[f'{obj.pk}' for obj in batch],
            ).values_list('pk').annotate(
                boost=model_boost * references_boost / depth_penalty,
            )

            index_entry_extensions = [IndexEntryExtension(pk=pk, boost=boost) for pk, boost in entries]
            IndexEntryExtension.objects.bulk_create(
                index_entry_extensions,
                unique_fields=['pk'],
                update_fields=['boost'],
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
