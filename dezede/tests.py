from io import BytesIO
from tempfile import TemporaryDirectory

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import SimpleTestCase, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from PIL import Image
from wagtail.admin.panels import MultiFieldPanel
from wagtail.snippets.models import get_snippet_models

from libretto.models import Etat, Individu

from .constants import LINKABLE_MODELS
from .forms import LinkedObjectTypeSelect
from .models import Diapositive


class DiapositiveViewSetTestCase(TestCase):
    def setUp(self):
        # The uploaded images and their thumbnails must not land in the real
        # media folder.
        media = TemporaryDirectory()
        self.addCleanup(media.cleanup)
        settings = override_settings(MEDIA_ROOT=media.name)
        settings.enable()
        self.addCleanup(settings.disable)

        self.client.force_login(get_user_model().objects.create_superuser(
            'super', 's@x.fr', 'pw'))
        self.etat = Etat.objects.create(nom='test public', public=True)
        self.individu = Individu.objects.create(nom='Individu lié', etat=self.etat)

    def _image(self, width=40, height=30):
        content = BytesIO()
        Image.new('RGB', (width, height)).save(content, 'PNG')
        return SimpleUploadedFile(
            'diapositive.png', content.getvalue(), 'image/png')

    def _diapositive(self, **kwargs):
        return Diapositive.objects.create(
            content_type=ContentType.objects.get_for_model(Individu),
            related_object_id=self.individu.pk, title='Titre test',
            image=self._image(), etat=self.etat, **kwargs)

    def testASlideWithoutCropGetsTheWholeImage(self):
        self.assertEqual(self._diapositive().cropping, '0,0,40,30')

    def testAGivenCropIsKept(self):
        diapositive = self._diapositive(cropping='5,5,25,20')
        self.assertEqual(diapositive.cropping, '5,5,25,20')

    def testTheContentIsGroupedInSections(self):
        content = Diapositive.edit_handler.children[0]
        sections = [str(panel.heading) for panel in content.children
                    if isinstance(panel, MultiFieldPanel)]
        self.assertEqual(sections, ['Objet lié', 'Texte', 'Arrière-plan'])

    def testNoFieldIsLeftOutOfTheForm(self):
        response = self.client.get(
            reverse('wagtailsnippets_dezede_diapositive:add'))
        # The owner is shown, but read-only, so it is not a form field. The
        # id of the linked object is set from the chooser of its type.
        champs = {field.name for field in Diapositive._meta.concrete_fields
                  if field.editable and not field.primary_key
                  } - {'owner', 'related_object_id'}
        self.assertLessEqual(champs, set(response.context['form'].fields))

    def testTheLabelsAreCapitalisedLikeTheOtherFields(self):
        response = self.client.get(
            reverse('wagtailsnippets_dezede_diapositive:add'))
        fields = response.context['form'].fields
        self.assertEqual(fields['content_type'].label, 'Type d’objet lié')
        self.assertEqual(fields['objet_oeuvre'].label, 'Œuvre')

    def testTheAddPageOpens(self):
        response = self.client.get(
            reverse('wagtailsnippets_dezede_diapositive:add'))
        self.assertEqual(response.status_code, 200)

    def _data(self):
        return {
            'content_type': ContentType.objects.get_for_model(Individu).pk,
            'objet_individu': self.individu.pk,
            'title': 'Titre test',
            'text_align': 'text-left',
            'image': self._image(),
            'image_align': 'text-right',
            'opacity': '0.6',
            'position': 0,
            'etat': self.etat.pk,
        }

    def testAddingASlide(self):
        response = self.client.post(
            reverse('wagtailsnippets_dezede_diapositive:add'), self._data())
        if response.status_code != 302:
            self.fail(response.context['form'].errors.as_text())
        diapositive = Diapositive.objects.get()
        self.assertEqual(diapositive.content_object, self.individu)
        self.assertEqual(diapositive.cropping, '0,0,40,30')

    def testTheListShowsTheSlide(self):
        self._diapositive()
        response = self.client.get(
            reverse('wagtailsnippets_dezede_diapositive:list'))
        self.assertContains(response, 'Titre test')
        self.assertContains(response, str(self.individu))

    def testTheEditPageOpens(self):
        diapositive = self._diapositive()
        response = self.client.get(reverse(
            'wagtailsnippets_dezede_diapositive:edit', args=(diapositive.pk,)))
        self.assertEqual(response.status_code, 200)

    def testAddingASlideWithoutItsObjectFails(self):
        data = self._data()
        del data['objet_individu']
        response = self.client.post(
            reverse('wagtailsnippets_dezede_diapositive:add'), data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('objet_individu', response.context['form'].errors)
        self.assertFalse(Diapositive.objects.exists())

    def testEditingShowsTheLinkedObject(self):
        diapositive = self._diapositive()
        response = self.client.get(reverse(
            'wagtailsnippets_dezede_diapositive:edit', args=(diapositive.pk,)))
        form = response.context['form']
        self.assertEqual(form.initial['objet_individu'], self.individu.pk)

    def testTheLinkableTypesAreTheSnippetsWithALink(self):
        # Every snippet has a chooser. The other types that can be linked,
        # such as users, are left out on purpose.
        linkable = {apps.get_model(label) for label in LINKABLE_MODELS.values()}
        snippets_with_a_link = {
            model for model in get_snippet_models() if hasattr(model, 'link')}
        self.assertEqual(snippets_with_a_link, linkable)

    def testABadCropIsRefused(self):
        for cropping in ('abc', '10,20', '5,5,5,5', '0,0,100,100', '30,0,10,20'):
            with self.subTest(cropping):
                data = self._data()
                data['cropping'] = cropping
                response = self.client.post(
                    reverse('wagtailsnippets_dezede_diapositive:add'), data)
                self.assertEqual(response.status_code, 200)
                self.assertIn('cropping', response.context['form'].errors)
        self.assertFalse(Diapositive.objects.exists())

    def testAValidCropIsKeptAndTidied(self):
        data = self._data()
        data['cropping'] = '5, 5,25,20'
        response = self.client.post(
            reverse('wagtailsnippets_dezede_diapositive:add'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Diapositive.objects.get().cropping, '5,5,25,20')

    def _edit(self, diapositive, **changes):
        data = {**self._data(), **changes}
        data = {key: value for key, value in data.items() if value is not None}
        return self.client.post(reverse(
            'wagtailsnippets_dezede_diapositive:edit', args=(diapositive.pk,)),
            data)

    def testReplacingTheImageResetsTheCrop(self):
        diapositive = self._diapositive(cropping='5,5,25,20')
        response = self._edit(
            diapositive, image=self._image(60, 50), cropping='5,5,25,20')
        self.assertEqual(response.status_code, 302)
        diapositive.refresh_from_db()
        self.assertEqual(diapositive.cropping, '0,0,60,50')

    def testKeepingTheImageKeepsTheCrop(self):
        diapositive = self._diapositive(cropping='5,5,25,20')
        response = self._edit(diapositive, image=None, cropping='5,5,25,20')
        self.assertEqual(response.status_code, 302)
        diapositive.refresh_from_db()
        self.assertEqual(diapositive.cropping, '5,5,25,20')

    def testTheListDoesNotQueryEachLinkedObject(self):
        for number in range(3):
            individu = Individu.objects.create(
                nom=f'Individu {number}', etat=self.etat)
            Diapositive.objects.create(
                content_type=ContentType.objects.get_for_model(Individu),
                related_object_id=individu.pk, title=f'Titre {number}',
                image=self._image(), etat=self.etat)
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                reverse('wagtailsnippets_dezede_diapositive:list'))
        self.assertEqual(response.status_code, 200)
        individu_queries = [
            query for query in queries.captured_queries
            if 'FROM "libretto_individu"' in query['sql']]
        self.assertLessEqual(len(individu_queries), 1)


class LinkedObjectTypeSelectTestCase(SimpleTestCase):
    def testItsScriptCannotBeClosedByItsData(self):
        widget = LinkedObjectTypeSelect()
        widget.chooser_fields = {'1': '</script><b>'}
        html = widget.render(
            'content_type', '', attrs={'id': 'id_content_type'})
        self.assertNotIn('</script><b>', html)
        self.assertIn('\\u003C/script\\u003E', html)
