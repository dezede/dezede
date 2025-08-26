from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db.models import Model, Value

from db_search.sql import update_all_search_vectors, get_search_vector
from typography.utils import replace


class SearchVectorAbstractModel(Model):
    search_vector = SearchVectorField(null=True, blank=True, editable=False)
    autocomplete_vector = SearchVectorField(
        null=True, blank=True, editable=False,
    )
    dezede_search_fields = []

    class Meta:
        abstract = True
        indexes = [
            GinIndex('search_vector', name='%(class)s_search'),
            GinIndex('autocomplete_vector', name='%(class)s_autocomplete'),
        ]

    @classmethod
    def update_all_search_vectors(cls):
        update_all_search_vectors(cls, cls.dezede_search_fields)

    def set_search_vectors(self) -> None:
        search_fields = self.dezede_search_fields

        search_fields = [
            getattr(self, field_name)
            for field_name in search_fields
        ]
        search_fields = [
            Value(value) for value in search_fields if value is not None
        ]
        self.search_vector = get_search_vector(search_fields)
        self.autocomplete_vector = get_search_vector(
            search_fields, config=settings.AUTOCOMPLETE_CONFIG,
        )

    @staticmethod
    def autocomplete_term_adjust(term):
        return replace(term)

    @staticmethod
    def autocomplete_search_fields():
        return ['autocomplete_vector__autocomplete']
