from haystack.indexes import Indexable
from libretto.search_indexes import CommonSearchIndex
from .models import Dossier


class DossierIndex(CommonSearchIndex, Indexable):
    BASE_BOOST = 4.0

    def get_model(self):
        return Dossier

    def prepare(self, obj):
        prepared_data = super(DossierIndex, self).prepare(obj)
        prepared_data['boost'] /= (obj.get_level() + 1)
        return prepared_data
