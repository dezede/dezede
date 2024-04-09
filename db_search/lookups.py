from django.contrib.postgres.search import SearchVectorField, SearchVectorExact

from db_search.sql import get_autocomplete_query


@SearchVectorField.register_lookup
class Autocomplete(SearchVectorExact):
    lookup_name = 'autocomplete'

    def process_rhs(self, compiler, connection):
        if isinstance(self.rhs, str):
            self.rhs = get_autocomplete_query(self.rhs)
        return super().process_rhs(compiler, connection)
