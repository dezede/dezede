from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TransactionTestCase as OriginalTransactionTestCase
from django.utils import six
import johnny.cache


def new(Model, **kwargs):
    return Model.objects.get_or_create(**kwargs)[0]


class TransactionTestCase(OriginalTransactionTestCase):
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
        super(TransactionTestCase, self)._pre_setup()
        self.log_as_superuser()
        johnny.cache.disable()

    def assertURL(self, url, data=None, method='get'):
        if data is None:
            data = {}
        response = getattr(self.client, method)(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.content, six.string_types)

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
        self.assertURL(reverse('admin:libretto_%s_add' % model_name))
        for obj in self.model.objects.all():
            self.assertURL(reverse(
                'admin:libretto_%s_history' % model_name, args=[obj.pk]))
            self.assertURL(reverse(
                'admin:libretto_%s_delete' % model_name, args=[obj.pk]))
            self.assertURL(reverse(
                'admin:libretto_%s_change' % model_name, args=[obj.pk]))

    def testTemplateRenders(self):
        if not hasattr(self.model, 'get_absolute_url'):
            return
        for obj in self.model.objects.all():
            self.assertURL(obj.get_absolute_url())
