from haystack import indexes, site
from .models import *


class OeuvreIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    suggestions = indexes.CharField()

    def get_model(self):
        return Oeuvre

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def prepare(self, obj):
        prepared_data = super(OeuvreIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data
site.register(Oeuvre, OeuvreIndex)


class SourceIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    date = indexes.DateField(model_attr='date')
    suggestions = indexes.CharField()

    def get_model(self):
        return Source

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def prepare(self, obj):
        prepared_data = super(SourceIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data
site.register(Source, SourceIndex)


class IndividuIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    suggestions = indexes.CharField()

    def get_model(self):
        return Individu

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def prepare(self, obj):
        prepared_data = super(IndividuIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data
site.register(Individu, IndividuIndex)


class LieuIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    suggestions = indexes.CharField()

    def get_model(self):
        return Lieu

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def prepare(self, obj):
        prepared_data = super(LieuIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data
site.register(Lieu, LieuIndex)


class EvenementIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    suggestions = indexes.CharField()

    def get_model(self):
        return Evenement

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def prepare(self, obj):
        prepared_data = super(EvenementIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data
site.register(Evenement, EvenementIndex)

