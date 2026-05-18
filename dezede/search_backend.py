from functools import wraps
from typing import Iterator, OrderedDict

from django.db.models import F, Count, QuerySet
from django.db.models.constants import LOOKUP_SEP
from grappelli.views.related import AutocompleteLookup
from wagtail.search.backends.database.postgres.postgres import (
    IndexEntry, PostgresSearchBackend, PostgresSearchQueryCompiler, PostgresSearchResults, PostgresAutocompleteQueryCompiler
)
from wagtail.search.index import BaseField, Indexed, RelatedFields, class_is_indexed
from wagtail.search.backends import get_search_backend
from wagtail.search.backends.base import EmptySearchResults


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


class FixedPostgresSearchBackend(PostgresSearchBackend):
    query_compiler_class = FixedPostgresSearchQueryCompiler
    autocomplete_query_compiler_class = FixedPostgresAutocompleteQueryCompiler
    results_class = FixedPostgresSearchResults

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


@wraps(Indexed.get_indexed_objects)
def faster_get_indexed_objects(cls):
    def recursive_relations_iterator(search_fields: list[BaseField | RelatedFields]) -> Iterator[list[str]]:
        for search_field in search_fields:
            if isinstance(search_field, RelatedFields):
                has_nested_relations = False
                for child_lookup_list in recursive_relations_iterator(search_field.fields):
                    yield [search_field.field_name, *child_lookup_list]
                    has_nested_relations = True
                if not has_nested_relations:
                    yield [search_field.field_name]

    return cls.objects.prefetch_related(
        *[
            LOOKUP_SEP.join(lookup_list)
            for lookup_list in recursive_relations_iterator(cls.get_search_fields())
        ]
    )

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


AutocompleteLookup.get_searched_queryset = wagtail_grappelli_get_searched_queryset
