# coding: utf-8

from __future__ import unicode_literals
from collections import defaultdict, OrderedDict

from django.utils.encoding import force_text
from rest_framework.fields import *
from rest_framework.serializers import *

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
    displayed_name = Field(source='__str__')
    naissance = AncrageSpatioTemporelSerializer()
    deces = AncrageSpatioTemporelSerializer()
    professions = RelatedField(many=True)
    parents = RelatedField(many=True)
    front_url = HyperlinkedIdentityField(view_name='individu_detail')

    class Meta(object):
        model = Individu
        fields = (
            'id', 'displayed_name', 'nom', 'prenoms',
            'naissance', 'deces',
            'professions', 'parents', 'enfants',
            'front_url', 'url'
        )


class EnsembleSerializer(HyperlinkedModelSerializer):
    displayed_name = Field(source='__str__')
    front_url = HyperlinkedIdentityField(view_name='ensemble_detail')

    class Meta(object):
        model = Individu
        fields = (
            'id', 'displayed_name',
            'front_url', 'url'
        )


class LieuSerializer(HyperlinkedModelSerializer):
    displayed_name = Field(source='__str__')
    nature = RelatedField()
    front_url = HyperlinkedIdentityField(view_name='lieu_detail')

    class Meta(object):
        model = Lieu
        fields = (
            'id', 'displayed_name', 'nom', 'nature', 'parent', 'enfants',
            'front_url', 'url'
        )


class CaracteristiquesSerializer(RelatedField):
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
    displayed_name = Field(source='__str__')
    titre = SerializerMethodField('get_titre')
    genre = RelatedField()
    caracteristiques = CaracteristiquesSerializer()
    auteurs = AuteurSerializer()
    creation = AncrageSpatioTemporelSerializer()
    evenements = RelatedField(many=True)
    front_url = HyperlinkedIdentityField(view_name='oeuvre_detail')

    class Meta(object):
        model = Oeuvre
        fields = (
            'id', 'displayed_name', 'titre', 'genre', 'caracteristiques',
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
