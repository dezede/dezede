# coding: utf-8

from __future__ import unicode_literals
from rest_framework.fields import *
from rest_framework.serializers import *
from libretto.models import *


class IndividuSerializer(HyperlinkedModelSerializer):
    displayed_name = Field(source='__str__')
    naissance_lieu = RelatedField()
    deces_lieu = RelatedField()
    professions = RelatedField(many=True)
    parents = RelatedField(many=True)
    front_url = Field(source='get_absolute_url')

    class Meta(object):
        model = Individu
        fields = (
            'id', 'displayed_name', 
            'naissance_date', 'naissance_date_approx',
            'naissance_lieu', 'naissance_lieu_approx',
            'deces_date', 'deces_date_approx',
            'deces_lieu', 'deces_lieu_approx',
            'professions', 'parents', 'enfants',
            'front_url', 'url'
        )


class LieuSerializer(HyperlinkedModelSerializer):
    displayed_name = Field(source='__str__')
    nature = RelatedField()
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
    creation_lieu = RelatedField()
    evenements = RelatedField(many=True)
    pupitres = RelatedField(many=True)
    front_url = Field(source='get_absolute_url')

    class Meta(object):
        model = Oeuvre
        fields = (
            'id', 'displayed_name', 'titre', 'titre_secondaire', 'genre',
            'caracteristiques', 'pupitres', 'contenu_dans',
            'creation_date', 'creation_date_approx',
            'creation_heure', 'creation_heure_approx',
            'creation_lieu', 'creation_lieu_approx',
            'meres', 'filles', 'front_url', 'url'
        )
