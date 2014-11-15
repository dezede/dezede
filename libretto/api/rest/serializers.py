# coding: utf-8

from __future__ import unicode_literals
from collections import defaultdict, OrderedDict

from django.utils.encoding import force_text
from rest_framework.fields import Field, SerializerMethodField
from rest_framework.relations import RelatedField, HyperlinkedIdentityField
from rest_framework.reverse import reverse
from rest_framework.serializers import HyperlinkedModelSerializer

from ...models import *


class AncrageSpatioTemporelSerializer(Field):
    def to_native(self, value):
        d = OrderedDict()
        for fieldname in sorted(value.fields):
            d[fieldname] = getattr(value, fieldname)
        lieu = d.get('lieu')
        if lieu is not None:
            d['lieu'] = reverse('lieu-detail', (lieu.pk,),
                                request=self.context.get('request'))
        return d


class IndividuSerializer(HyperlinkedModelSerializer):
    str = Field(source='__str__')
    naissance = AncrageSpatioTemporelSerializer()
    deces = AncrageSpatioTemporelSerializer()
    professions = RelatedField(many=True)
    front_url = HyperlinkedIdentityField(view_name='individu_detail')

    class Meta(object):
        model = Individu
        fields = (
            'id', 'str', 'nom', 'prenoms',
            'naissance', 'deces',
            'professions', 'parents', 'enfants',
            'front_url', 'url'
        )


class EnsembleSerializer(HyperlinkedModelSerializer):
    str = Field(source='__str__')
    front_url = HyperlinkedIdentityField(view_name='ensemble_detail')

    class Meta(object):
        model = Individu
        fields = (
            'id', 'str', 'front_url', 'url'
        )


class LieuSerializer(HyperlinkedModelSerializer):
    str = Field(source='__str__')
    nature = Field()
    front_url = HyperlinkedIdentityField(view_name='lieu_detail')

    class Meta(object):
        model = Lieu
        fields = (
            'id', 'str', 'nom', 'nature', 'parent', 'enfants',
            'front_url', 'url'
        )


class CaracteristiquesSerializer(Field):
    def to_native(self, value):
        d = defaultdict(list)
        for c in value.all():
            d[force_text(c.type)].append(c.valeur)
        return d


class AuteurSerializer(HyperlinkedModelSerializer):
    profession = Field()

    class Meta(object):
        model = Auteur
        fields = ('individu', 'profession')


class OeuvreSerializer(HyperlinkedModelSerializer):
    str = Field(source='__str__')
    titre = SerializerMethodField('get_titre')
    genre = Field()
    caracteristiques = CaracteristiquesSerializer()
    auteurs = AuteurSerializer()
    creation = AncrageSpatioTemporelSerializer()
    evenements = RelatedField(many=True)
    front_url = HyperlinkedIdentityField(view_name='oeuvre_detail')

    class Meta(object):
        model = Oeuvre
        fields = (
            'id', 'str', 'titre', 'genre', 'caracteristiques',
            'auteurs', 'creation', 'contenu_dans',
            'front_url', 'url'
        )

    def get_titre(self, obj):
        return OrderedDict((
            ('prefixe_principal', obj.prefixe_titre),
            ('principal', obj.titre),
            ('coordination', obj.coordination),
            ('prefixe_secondaire', obj.prefixe_titre_secondaire),
            ('secondaire', obj.titre_secondaire),
        ))
