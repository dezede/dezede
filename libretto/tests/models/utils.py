from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django_nose import TransactionTestCase as OriginalTransactionTestCase
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
    response = test_case.client.post(reverse('admin:index'),
                                     {'username': username,
                                      'password': password,
                                      'this_is_the_login_form': 1})
    test_case.assertEqual(response.status_code, 302)


class TransactionTestCase(OriginalTransactionTestCase):
    cleans_up_after_itself = True

    def _pre_setup(self):
        super(TransactionTestCase, self)._pre_setup()
        johnny.cache.disable()
