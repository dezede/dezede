# coding: utf-8

from __future__ import unicode_literals
from rest_framework.fields import *
from rest_framework.serializers import *
from libretto.models import *


class AncrageSpatioTemporelSerializer(ModelSerializer):
    lieu = HyperlinkedRelatedField(view_name='lieu-detail')

    class Meta(object):
        model = AncrageSpatioTemporel
        exclude = ('owner', 'id')


class IndividuSerializer(HyperlinkedModelSerializer):
    displayed_name = Field(source='__str__')
    prenoms = RelatedField(many=True)
    ancrage_naissance = AncrageSpatioTemporelSerializer()
    ancrage_deces = AncrageSpatioTemporelSerializer()
    ancrage_approx = AncrageSpatioTemporelSerializer()
    professions = RelatedField(many=True)
    parents = RelatedField(many=True)
    front_url = Field(source='get_absolute_url')

    class Meta(object):
        model = Individu
        fields = (
            'id', 'displayed_name', 'ancrage_naissance', 'ancrage_deces',
            'ancrage_approx', 'professions', 'parents', 'enfants',
            'front_url', 'url'
        )


class LieuSerializer(HyperlinkedModelSerializer):
    displayed_name = Field(source='__str__')
    nature = RelatedField()
    individus_nes = IndividuSerializer(many=True)
    individus_decedes = IndividuSerializer(many=True)
    front_url = Field(source='get_absolute_url')

    class Meta(object):
        model = Lieu
        fields = (
            'id', 'displayed_name', 'nom', 'nature', 'parent', 'enfants',
            'front_url', 'url'
        )


class OeuvreSerializer(HyperlinkedModelSerializer):
    displayed_name = Field(source='__str__')
    genre = RelatedField()
    caracteristiques = RelatedField(many=True)
    ancrage_creation = AncrageSpatioTemporelSerializer()
    evenements = RelatedField(many=True)
    pupitres = RelatedField(many=True)
    front_url = Field(source='get_absolute_url')

    class Meta(object):
        model = Oeuvre
        fields = (
            'id', 'displayed_name', 'titre', 'titre_secondaire', 'genre',
            'caracteristiques', 'ancrage_creation', 'pupitres', 'contenu_dans',
            'meres', 'filles', 'front_url', 'url'
        )
