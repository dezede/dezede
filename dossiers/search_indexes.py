from haystack.indexes import Indexable, EdgeNgramField
from libretto.search_indexes import CommonSearchIndex
from .models import DossierDEvenements


class DossierDEvenementsIndex(CommonSearchIndex, Indexable):
    BASE_BOOST = 4.0

    def get_model(self):
        return DossierDEvenements

    def prepare(self, obj):
        prepared_data = super(DossierDEvenementsIndex, self).prepare(obj)
        prepared_data['boost'] /= (obj.get_level() + 1)
        return prepared_data
