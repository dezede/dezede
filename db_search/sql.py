from multiprocessing import Value
from typing import List, Union, Optional, Type

from django.conf import settings
from django.contrib.postgres.search import SearchVector, SearchQuery

from django.db.migrations.operations.models import ModelOperation
from django.db.models import Model


class UpdateAllSearchVectors(ModelOperation):
    def __init__(self, name: str, search_fields: List[str]):
        self.search_fields = search_fields
        super().__init__(name=name)
        self._constructor_args = ((), {
            'name': self.name,
            'search_fields': self.search_fields,
        })

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


def get_search_vector(
    search_fields: List[Union[str, Value]], config: str = settings.WAGTAILSEARCH_BACKENDS['default']['SEARCH_CONFIG'],
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
