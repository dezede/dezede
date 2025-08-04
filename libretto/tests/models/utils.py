from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import six


def new(Model, **kwargs):
    return Model.objects.get_or_create(**kwargs)[0]


class CommonTestCase(TestCase):
    cleans_up_after_itself = True
    model = None

    def log_as_superuser(self):
        username = 'test_superuser'
        password = 'test_password'
        email = 'a@b.com'
        User = get_user_model()
        try:
            User.objects.get(username=username, is_staff=True,
                             is_superuser=True)
        except User.DoesNotExist:
            User.objects.create_superuser(username, email, password)
        is_logged = self.client.login(username=username,
                                      password=password)
        self.assertTrue(is_logged)

    def _pre_setup(self):
        # We clear the cache in order to clear cached methods
        cache.clear()
        super(CommonTestCase, self)._pre_setup()
        self.log_as_superuser()
        if self.model is not None:
            self.model_name = self.model._meta.model_name

    def assertURL(self, url, data=None, method='get', status_codes=(200,),
                  follow=False):
        if data is None:
            data = {}
        response = getattr(self.client, method)(url, data=data, follow=follow)
        self.assertIn(response.status_code, status_codes)
        self.assertIsInstance(response.content, six.string_types)
        return response

    def assertSendForm(self, url, method='post'):
        soup = BeautifulSoup(self.client.get(url).content, 'html.parser')

        forms = soup.find_all('form')
        self.assertEqual(len(forms), 1)
        inputs = forms[0].find_all('input',
                                   attrs={'name': True, 'value': True})

        data = {input['name']: input['value']
                for input in inputs if input['type'] not in ['submit']}

        self.assertURL(url, data=data, method=method, status_codes=[200, 302])

    def testClean(self, excluded=()):
        if self.model is None:
            return

        for obj in self.model.objects.all():
            if obj not in excluded:
                obj.clean()

    def testAdminRenders(self):
        if self.model is None:
            return

        model_name = self.model_name
        self.assertURL(reverse(f'admin:libretto_{model_name}_changelist'))
        add_url = reverse(f'admin:libretto_{model_name}_add')
        self.assertURL(add_url)
        self.assertSendForm(add_url)
        for obj in self.model.objects.all():
            self.assertURL(reverse(
                f'admin:libretto_{model_name}_history', args=[obj.pk]))
            self.assertURL(reverse(
                f'admin:libretto_{model_name}_delete', args=[obj.pk]))
            change_url = reverse(
                f'admin:libretto_{model_name}_change', args=[obj.pk])
            self.assertURL(change_url)
            self.assertSendForm(change_url)

    def testAdminAutocomplete(self):
        if self.model is None \
                or not hasattr(self.model, 'autocomplete_search_fields'):
            return

        self.assertURL(reverse('grp_autocomplete_lookup'), {
            'app_label': self.model._meta.app_label,
            'model_name': self.model_name,
            'term': 'et',
        })

    def testTemplateRenders(self):
        if not hasattr(self.model, 'get_absolute_url'):
            return
        for obj in self.model.objects.all():
            self.assertURL(obj.get_absolute_url())
