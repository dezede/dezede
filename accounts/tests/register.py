from allauth.account.models import EmailConfirmation
from django.contrib.auth.models import Group, Permission
from django.core import mail
from django.urls import reverse
from libretto.tests.models.utils import CommonTestCase
from ..models import HierarchicUser


__all__ = ('RegisterTestCase',)


class RegisterTestCase(CommonTestCase):
    cleans_up_after_itself = True

    def setUp(self):
        self.mentor_password = 'empty'
        self.mentor = HierarchicUser.objects.create_user(
            'mentor', 'a@b.com', self.mentor_password)
        self.mentor.willing_to_be_mentor = True
        self.mentor.save()
        self.group = Group.objects.create(name='test')
        self.group.permissions.add(*Permission.objects.all()[:2])

        # We ensure no-one is logged in as we may fetch a non-test session.
        self.client.get(reverse('account_logout'))

    def testRegister(self):
        user_data = {
            'first_name': 'This-Is',
            'last_name': 'A-Test',
            'email': 'a@b.com',
            'username': 'this-is-a-test',
            'password1': 'empty-password',
            'password2': 'empty-password',
            'mentor': self.mentor.pk,
            'groups': [self.group.pk],
        }

        def get_new_user():
            return HierarchicUser.objects.get(username=user_data['username'])

        # Tests the empty form.
        form_url = reverse('account_signup')
        self.client.get(form_url)

        # Fills and sends the form.
        self.assertEqual(len(mail.outbox), 0)

        self.assertURL(form_url, user_data, method='post', follow=True)
        # Two messages must have been sent: one to the created user, and
        # another to the mentor.
        self.assertEqual(len(mail.outbox), 2)
        new_user = get_new_user()
        self.assertFalse(new_user.is_active)
        self.assertFalse(new_user.is_staff)
        self.assertFalse(new_user.is_superuser)

        # Does the same as opening both mails and clicking on links.
        # New user mail:
        activation_url = reverse(
            'account_confirm_email',
            args=[EmailConfirmation.objects.get().key])
        self.assertURL(activation_url, follow=True)
        new_user = get_new_user()
        self.assertTrue(new_user.is_active)
        self.assertFalse(new_user.is_staff)
        self.assertFalse(new_user.is_superuser)
        # Mentor mail:
        grant_url = reverse('grant_to_admin', args=[new_user.pk])
        self.assertURL(grant_url, status_codes=[403])
        self.client.login(username=self.mentor.username,
                          password=self.mentor_password)
        self.assertURL(grant_url)
        new_user = get_new_user()
        self.assertTrue(new_user.is_active)
        self.assertTrue(new_user.is_staff)
        self.assertFalse(new_user.is_superuser)
        # Tests if both links are useless now :
        self.assertURL(activation_url, follow=True)
        self.assertURL(grant_url)
