from haystack .indexes import RealTimeSearchIndex, CharField, EdgeNgramField, \
                              DateField
from haystack import site
from .models import Oeuvre, Source, Individu, Lieu, Evenement, Partie


class OeuvreIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    suggestions = CharField()
    content_auto = EdgeNgramField(model_attr='titre_html')

    def get_model(self):
        return Oeuvre

    def index_queryset(self):
        return self.get_model().objects.all()

    def prepare(self, obj):
        prepared_data = super(OeuvreIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data
site.register(Oeuvre, OeuvreIndex)


class SourceIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    date = DateField(model_attr='date')
    suggestions = CharField()

    def get_model(self):
        return Source

    def index_queryset(self):
        return self.get_model().objects.all()

    def prepare(self, obj):
        prepared_data = super(SourceIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data
site.register(Source, SourceIndex)


class IndividuIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    suggestions = CharField()

    def get_model(self):
        return Individu

    def index_queryset(self):
        return self.get_model().objects.all()

    def prepare(self, obj):
        prepared_data = super(IndividuIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data
site.register(Individu, IndividuIndex)


class LieuIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    suggestions = CharField()
    content_auto = EdgeNgramField(model_attr='html')

    def get_model(self):
        return Lieu

    def index_queryset(self):
        return self.get_model().objects.all()

    def prepare(self, obj):
        prepared_data = super(LieuIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data
site.register(Lieu, LieuIndex)


class EvenementIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    suggestions = CharField()

    def get_model(self):
        return Evenement

    def index_queryset(self):
        return self.get_model().objects.all()

    def prepare(self, obj):
        prepared_data = super(EvenementIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data
site.register(Evenement, EvenementIndex)


class PartieIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    suggestions = CharField()

    def get_model(self):
        return Partie

    def index_queryset(self):
        return self.get_model().objects.all()

    def prepare(self, obj):
        prepared_data = super(PartieIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data
site.register(Partie, PartieIndex)
