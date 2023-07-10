from typing import Type, List, Optional

from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.db import connection
from django.db.migrations.operations.models import ModelOperation
from django.db.models import Model


def get_raw_query(qs):
    return qs.query.get_compiler(connection=connection).as_sql()


def get_search_vector(search_fields: List[str]) -> Optional[SearchVector]:
    if not search_fields:
        return None
    return SearchVector(*search_fields, config=settings.SEARCH_CONFIG)


def update_all_search_vectors(
    model: Type[Model], search_fields: List[str],
) -> None:
    model.objects.update(
        search_vector=get_search_vector(search_fields),
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
