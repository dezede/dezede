from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import six
import johnny.cache


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
        super(CommonTestCase, self)._pre_setup()
        self.log_as_superuser()
        johnny.cache.disable()

    def assertURL(self, url, data=None, method='get', status_codes=(200,),
                  follow=False):
        if data is None:
            data = {}
        response = getattr(self.client, method)(url, data=data, follow=follow)
        self.assertIn(response.status_code, status_codes)
        self.assertIsInstance(response.content, six.string_types)
        return response

    def assertSendForm(self, url, method='post'):
        soup = BeautifulSoup(self.client.get(url).content)

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

        model_name = self.model.__name__.lower()
        self.assertURL(reverse('admin:libretto_%s_changelist' % model_name))
        add_url = reverse('admin:libretto_%s_add' % model_name)
        self.assertURL(add_url)
        self.assertSendForm(add_url)
        for obj in self.model.objects.all():
            self.assertURL(reverse(
                'admin:libretto_%s_history' % model_name, args=[obj.pk]))
            self.assertURL(reverse(
                'admin:libretto_%s_delete' % model_name, args=[obj.pk]))
            change_url = reverse(
                'admin:libretto_%s_change' % model_name, args=[obj.pk])
            self.assertURL(change_url)
            self.assertSendForm(change_url)

    def testTemplateRenders(self):
        if not hasattr(self.model, 'get_absolute_url'):
            return
        for obj in self.model.objects.all():
            self.assertURL(obj.get_absolute_url())
