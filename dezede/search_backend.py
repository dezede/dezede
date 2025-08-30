from typing import OrderedDict

from django.db.models import Count
from wagtail.search.backends.database.postgres.postgres import (
    PostgresSearchBackend, PostgresSearchQueryCompiler, PostgresSearchResults
)


class FixedPostgresSearchQueryCompiler(PostgresSearchQueryCompiler):
    def _get_filters_from_where_node(self, where_node, check_only=False):
        # We use PostgreSQL, so FilterFields are pointless.
        # It's a Wagtail bug.
        pass


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
