from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


def new(Model, **kwargs):
    return Model.objects.get_or_create(**kwargs)[0]


def log_as_superuser(test_case):
    username = 'test_superuser'
    password = 'test_password'
    email = 'a@b.com'
    try:
        User.objects.get(username=username, is_staff=True, is_superuser=True)
    except User.DoesNotExist:
        User.objects.create_superuser(username, email, password)
    response = test_case.client.post(reverse('admin:index'),
                                     {'username': username,
                                      'password': password,
                                      'this_is_the_login_form': 1})
    test_case.assertEqual(response.status_code, 302)
