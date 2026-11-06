from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from ..models import Lieu
from ..wagtail_hooks import scope_to_owner


__all__ = ('ScopeToOwnerTestCase',)


class ScopeToOwnerTestCase(TestCase):
    def testAnonymousUserOwnsNothing(self):
        self.assertFalse(
            scope_to_owner(Lieu.objects.all(), AnonymousUser()).exists())
