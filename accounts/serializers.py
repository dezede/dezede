from rest_framework.serializers import HyperlinkedIdentityField

from libretto.api.rest.serializers import CommonSerializer
from .models import HierarchicUser


class UserSerializer(CommonSerializer):
    front_url = HyperlinkedIdentityField(view_name='user_profile',
                                         lookup_field='username')

    class Meta:
        model = HierarchicUser
        exclude = (
            'password', 'email', 'last_login', 'date_joined', 'show_email',
            'willing_to_be_mentor', 'is_superuser', 'is_staff', 'is_active',
            'groups', 'user_permissions',
            'path', 'search_vector', 'autocomplete_vector',
            'content_type', 'object_id',
        )
