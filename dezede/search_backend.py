from functools import wraps
from typing import Iterator, OrderedDict

from django.db.models import Count
from django.db.models.constants import LOOKUP_SEP
from grappelli.views.related import AutocompleteLookup
from wagtail.search.backends.database.postgres.postgres import (
    PostgresSearchBackend, PostgresSearchQueryCompiler, PostgresSearchResults
)
from wagtail.search.index import BaseField, Indexed, RelatedFields
from wagtail.search.backends import get_search_backend


class FixedPostgresSearchQueryCompiler(PostgresSearchQueryCompiler):
    def _get_filters_from_where_node(self, where_node, check_only=False):
        # We use PostgreSQL, so FilterFields are pointless.
        # It's a Wagtail bug.
        pass

    def _get_order_by(self):
        # We use PostgreSQL, so FilterFields are pointless.
        # It's a Wagtail bug.
        yield from []


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
    results_class = FixedPostgresSearchResults


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
