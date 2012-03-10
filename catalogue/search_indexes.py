import datetime
from haystack import indexes, site
from musicologie.catalogue.models import *

class OeuvreIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Oeuvre

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
site.register(Oeuvre, OeuvreIndex)

class SourceIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    date = indexes.DateField(model_attr='date')

    def get_model(self):
        return Source

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
site.register(Source, SourceIndex)

