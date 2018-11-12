from __future__ import unicode_literals

import haystack
from django.conf import settings
from elasticsearch import NotFoundError

from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend, \
    ElasticsearchSearchEngine


class ConfigurableElasticBackend(ElasticsearchSearchBackend):
    DEFAULT_ANALYZER = 'default'

    def __init__(self, connection_alias, **connection_options):
        super(ConfigurableElasticBackend, self).__init__(
            connection_alias, **connection_options)
        user_settings = getattr(settings, 'ELASTICSEARCH_INDEX_SETTINGS', None)
        if user_settings:
            setattr(self, 'DEFAULT_SETTINGS', user_settings)

    def build_schema(self, fields):
        content_field_name, mapping = super(ConfigurableElasticBackend,
                                            self).build_schema(fields)

        for field_name, field_class in fields.items():
            field_mapping = mapping[field_class.index_fieldname]

            if field_mapping['type'] == 'string' and field_class.indexed:
                if not hasattr(field_class, 'facet_for') \
                        and field_class.field_type not in ('ngram',
                                                           'edge_ngram'):
                    field_mapping['analyzer'] = getattr(
                        field_class, 'analyzer', self.DEFAULT_ANALYZER)
            mapping.update({field_class.index_fieldname: field_mapping})
        return content_field_name, mapping

    def setup(self):
        """
                Defers loading until needed.
                """
        # Get the existing mapping & cache it. We'll compare it
        # during the ``update`` & if it doesn't match, we'll put the new
        # mapping.
        try:
            self.existing_mapping = self.conn.indices.get_mapping(
                index=self.index_name)
        except NotFoundError:
            pass
        except Exception:
            if not self.silently_fail:
                raise

        unified_index = haystack.connections[
            self.connection_alias].get_unified_index()
        self.content_field_name, field_mapping = self.build_schema(
            unified_index.all_searchfields())
        current_mapping = {
            'modelresult': {
                'properties': field_mapping,
                '_boost': {
                    'name': 'boost',
                    'null_value': 1.0
                },
            },
        }

        if current_mapping != self.existing_mapping:
            try:
                # Make sure the index is there first.
                self.conn.indices.create(index=self.index_name,
                                         body=self.DEFAULT_SETTINGS,
                                         ignore=400)
                self.conn.indices.put_mapping(index=self.index_name,
                                              doc_type='modelresult',
                                              body=current_mapping)
                self.existing_mapping = current_mapping
            except Exception:
                if not self.silently_fail:
                    raise

        self.setup_complete = True


class ConfigurableElasticSearchEngine(ElasticsearchSearchEngine):
    backend = ConfigurableElasticBackend
