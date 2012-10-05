from haystack import indexes, site
from .models import *


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


class IndividuIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Individu

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
site.register(Individu, IndividuIndex)


class LieuIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Lieu

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
site.register(Lieu, LieuIndex)


class EvenementIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Evenement

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
site.register(Evenement, EvenementIndex)

