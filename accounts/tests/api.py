from django.test import TestCase
from rest_framework.test import APIRequestFactory

from accounts.models import HierarchicUser
from accounts.serializers import UserSerializer


class UserSerializerTestCase(TestCase):
    def test_serializes_user(self):
        user = HierarchicUser.objects.create_user(username='u', password='p')
        request = APIRequestFactory().get('/')
        data = UserSerializer(user, context={'request': request}).data
        self.assertEqual(data['username'], 'u')
        self.assertNotIn('path', data)
