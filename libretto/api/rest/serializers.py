# coding: utf-8

from __future__ import unicode_literals
from collections import OrderedDict

from rest_framework.fields import ReadOnlyField, Field
from rest_framework.relations import (
    HyperlinkedIdentityField, StringRelatedField)
from rest_framework.reverse import reverse
from rest_framework.serializers import HyperlinkedModelSerializer

from ...models import *


class AncrageSpatioTemporelSerializer(Field):
    def to_representation(self, obj):
        d = OrderedDict()
        for fieldname in sorted(obj.fields):
            d[fieldname] = getattr(obj, fieldname)
        lieu = d.get('lieu')
        if lieu is not None:
            d['lieu'] = reverse('lieu-detail', (lieu.pk,),
                                request=self.context.get('request'))
        return d


class IndividuSerializer(HyperlinkedModelSerializer):
    str = ReadOnlyField(source='__str__')
    naissance = AncrageSpatioTemporelSerializer()
    deces = AncrageSpatioTemporelSerializer()
    professions = StringRelatedField(many=True)
    front_url = HyperlinkedIdentityField(view_name='individu_detail',
                                         lookup_field='slug')

    class Meta(object):
        model = Individu
        fields = (
            'id', 'str', 'nom', 'prenoms',
            'naissance', 'deces',
            'professions', 'parents',
            'front_url', 'url'
        )


class EnsembleSerializer(HyperlinkedModelSerializer):
    str = ReadOnlyField(source='__str__')
    type = StringRelatedField()
    front_url = HyperlinkedIdentityField(view_name='ensemble_detail',
                                         lookup_field='slug')

    class Meta(object):
        model = Ensemble
        fields = (
            'id', 'str', 'type', 'front_url', 'url'
        )


class LieuSerializer(HyperlinkedModelSerializer):
    str = ReadOnlyField(source='__str__')
    nature = StringRelatedField()
    front_url = HyperlinkedIdentityField(view_name='lieu_detail',
                                         lookup_field='slug')

    class Meta(object):
        model = Lieu
        fields = (
            'id', 'str', 'nom', 'nature', 'parent', 'front_url', 'url'
        )


class AuteurSerializer(HyperlinkedModelSerializer):
    profession = StringRelatedField()

    class Meta(object):
        model = Auteur
        fields = ('individu', 'profession')


class OeuvreSerializer(HyperlinkedModelSerializer):
    str = ReadOnlyField(source='__str__')
    titre_significatif = ReadOnlyField(source='get_titre_significatif')
    titre_non_significatif = ReadOnlyField(source='get_titre_non_significatif')
    description = ReadOnlyField(source='get_description')
    genre = StringRelatedField()
    auteurs = AuteurSerializer(many=True, read_only=True)
    creation = AncrageSpatioTemporelSerializer()
    front_url = HyperlinkedIdentityField(view_name='oeuvre_detail',
                                         lookup_field='slug')

    class Meta(object):
        model = Oeuvre
        fields = (
            'id', 'str', 'extrait_de',
            'titre_significatif', 'titre_non_significatif', 'description',
            'genre', 'auteurs', 'creation',
            'front_url', 'url'
        )
