from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase as OriginalTransactionTestCase
import johnny.cache


def new(Model, **kwargs):
    return Model.objects.get_or_create(**kwargs)[0]


def log_as_superuser(test_case):
    username = 'test_superuser'
    password = 'test_password'
    email = 'a@b.com'
    User = get_user_model()
    try:
        User.objects.get(username=username, is_staff=True, is_superuser=True)
    except User.DoesNotExist:
        User.objects.create_superuser(username, email, password)
    is_logged = test_case.client.login(username=username, password=password)
    test_case.assertTrue(is_logged)


class TransactionTestCase(OriginalTransactionTestCase):
    cleans_up_after_itself = True

    def _pre_setup(self):
        super(TransactionTestCase, self)._pre_setup()
        johnny.cache.disable()

    def fetch_page(self, url, data=None):
        if data is None:
            data = {}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)
        return response.content
