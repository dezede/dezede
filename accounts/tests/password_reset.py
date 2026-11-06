from allauth.account.models import EmailAddress
from django.core import mail
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from ..models import HierarchicUser


__all__ = ('PasswordResetSharedEmailTestCase',)


class PasswordResetSharedEmailTestCase(TestCase):
    email = 'shared@example.com'

    def setUp(self):
        self.owner = HierarchicUser.objects.create_user(
            'owner', self.email, 'empty')
        EmailAddress.objects.create(
            user=self.owner, email=self.email, primary=True, verified=True)
        # No EmailAddress row, as left by a signup that failed halfway.
        self.other = HierarchicUser.objects.create_user(
            'other', self.email, 'empty')

    def test_database_rejects_duplicate_email_address(self):
        # Guards the test below: it only means something if the table
        # enforces unique e-mails, as production does.
        with self.assertRaises(IntegrityError), transaction.atomic():
            EmailAddress.objects.create(user=self.other, email=self.email)

    def test_reset_with_email_owned_by_another_user(self):
        response = self.client.post(
            reverse('account_reset_password'), {'email': self.email})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 2)
        self.assertFalse(
            EmailAddress.objects.filter(user=self.other).exists())
