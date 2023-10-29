from multiprocessing import Value
from typing import Type, List, Optional, Union

from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db import connection
from django.db.migrations.operations.models import ModelOperation
from django.db.models import Model


def get_raw_query(qs):
    return qs.query.get_compiler(connection=connection).as_sql()


def get_search_vector(
    search_fields: List[Union[str, Value]], config: str = settings.SEARCH_CONFIG,
) -> Optional[SearchVector]:
    if not search_fields:
        return None
    return SearchVector(*search_fields, config=config)


def update_all_search_vectors(
    model: Type[Model], search_fields: List[str],
) -> None:
    model.objects.update(
        search_vector=get_search_vector(search_fields),
        autocomplete_vector=get_search_vector(
            search_fields, config=settings.AUTOCOMPLETE_CONFIG,
        ),
    )


class UpdateAllSearchVectors(ModelOperation):
    def __init__(self, name: str, search_fields: List[str]):
        self.search_fields = search_fields
        super().__init__(name=name)

    def deconstruct(self):
        return {
            'name': self.name,
            'search_fields': self.search_fields,
        }

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(
        self, app_label, schema_editor, from_state, to_state,
    ):
        model = to_state.apps.get_model(app_label, self.name)
        update_all_search_vectors(model, self.search_fields)

    def database_backwards(
        self, app_label, schema_editor, from_state, to_state,
    ):
        pass


def escape_for_tsquery(word: str) -> str:
    for special_char in '()<!&|:':
        word = word.replace(special_char, fr'\{special_char}')
    return word


def get_autocomplete_query(value: str) -> SearchQuery:
    return SearchQuery(
        ' & '.join([
            f'{escape_for_tsquery(word)}:*' for word in value.split()
        ]),
        config=settings.AUTOCOMPLETE_CONFIG,
        search_type='raw',
    )
