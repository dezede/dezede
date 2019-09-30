from collections import OrderedDict

from rest_framework.fields import ReadOnlyField, Field, SerializerMethodField
from rest_framework.relations import (
    HyperlinkedIdentityField, StringRelatedField, PrimaryKeyRelatedField
)
from rest_framework.reverse import reverse
from rest_framework.serializers import (
    HyperlinkedModelSerializer, ModelSerializer,
)

from accounts.models import HierarchicUser
from ...models import *


class CommonSerializer(ModelSerializer):
    str = ReadOnlyField(source='__str__')
    change_url = SerializerMethodField()
    delete_url = SerializerMethodField()
    can_add = SerializerMethodField()
    can_change = SerializerMethodField()
    can_delete = SerializerMethodField()

    def _get_base_admin_url(self, obj):
        return f'admin:{obj._meta.app_label}_{obj._meta.model_name}'

    def get_url(self, viewname, *args, **kwargs):
        return self.context['request'].build_absolute_uri(reverse(
            viewname, args=args, kwargs=kwargs,
        ))

    def get_change_url(self, obj):
        return self.get_url(
            f'{self._get_base_admin_url(obj)}_change', obj.pk,
        )

    def get_delete_url(self, obj):
        return self.get_url(
            f'{self._get_base_admin_url(obj)}_delete', obj.pk,
        )

    def has_perm(self, permission, obj):
        return self.context['request'].user.has_perm(permission, obj=obj)

    def get_can_add(self, obj):
        return self.has_perm(
            f'libretto.add_{obj._meta.model_name}', obj,
        )

    def get_can_change(self, obj):
        return self.has_perm(
            f'libretto.change_{obj._meta.model_name}', obj,
        )

    def get_can_delete(self, obj):
        return self.has_perm(
            f'libretto.delete_{obj._meta.model_name}', obj,
        )


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
    professions = PrimaryKeyRelatedField(many=True, read_only=True)
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


class SourceSerializer(CommonSerializer):
    children = SerializerMethodField()
    small_thumbnail = SerializerMethodField()
    medium_thumbnail = SerializerMethodField()
    front_url = HyperlinkedIdentityField(view_name='source_permanent_detail',
                                         lookup_field='pk')

    class Meta:
        model = Source
        exclude = ()

    def get_children(self, obj):
        return list(
            obj.children.order_by('position').values_list('pk', flat=True)
        )

    def get_small_thumbnail(self, obj):
        return self.context['request'].build_absolute_uri(obj.small_thumbnail)

    def get_medium_thumbnail(self, obj):
        return self.context['request'].build_absolute_uri(obj.medium_thumbnail)


class EvenementSerializer(CommonSerializer):
    front_url = HyperlinkedIdentityField(
        view_name='evenement_pk', lookup_field='pk',
    )

    class Meta:
        model = Evenement
        exclude = ()


class PartieSerializer(CommonSerializer):
    front_url = HyperlinkedIdentityField(view_name='partie_detail',
                                         lookup_field='slug')

    class Meta:
        model = Partie
        exclude = ()


class UserSerializer(CommonSerializer):
    front_url = HyperlinkedIdentityField(view_name='user_profile',
                                         lookup_field='username')

    class Meta:
        model = HierarchicUser
        exclude = (
            'password', 'email', 'last_login', 'date_joined', 'show_email',
            'willing_to_be_mentor', 'is_superuser', 'is_staff', 'is_active',
            'groups', 'user_permissions',
        )
