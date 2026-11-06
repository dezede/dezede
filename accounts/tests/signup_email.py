from allauth.account.models import EmailAddress
from django.contrib.auth.models import Group
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from ..models import HierarchicUser


__all__ = ('SignupTakenEmailTestCase',)


class SignupTakenEmailTestCase(TestCase):
    email = 'taken@example.com'

    def setUp(self):
        self.mentor = HierarchicUser.objects.create_user(
            'mentor', 'mentor@example.com', 'empty')
        self.mentor.willing_to_be_mentor = True
        self.mentor.save()
        self.group = Group.objects.create(name='test')

    def sign_up(self):
        response = self.client.post(reverse('account_signup'), {
            'first_name': 'This-Is',
            'last_name': 'A-Test',
            'email': self.email,
            'username': 'this-is-a-test',
            'password1': 'empty-password',
            'password2': 'empty-password',
            'mentor': self.mentor.pk,
            'groups': [self.group.pk],
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['form'].errors)
        self.assertFalse(
            HierarchicUser.objects.filter(username='this-is-a-test').exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_email_with_an_email_address_row(self):
        user = HierarchicUser.objects.create_user(
            'owner', self.email, 'empty')
        EmailAddress.objects.create(
            user=user, email=self.email, primary=True, verified=True)
        self.sign_up()

    def test_email_without_an_email_address_row(self):
        # What a signup that failed halfway leaves behind.
        HierarchicUser.objects.create_user('leftover', self.email, 'empty')
        self.sign_up()
