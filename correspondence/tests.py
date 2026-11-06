from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse
from wagtail.coreutils import get_supported_content_language_variant
from wagtail.models import Locale, Page, Site as WagtailSite
from wagtail.rich_text import RichText
from wagtail.test.utils.form_data import querydict_from_html

from libretto.models import Etat, Evenement, Individu, Lieu, NatureDeLieu

from .models import (
    Letter, LetterCorpus, LetterIndex, LetterRecipient, LetterSender,
)
from .wagtail_hooks import confirm_unpublished_autorites


class PublicationWarningsTestCase(TestCase):
    """A page with unpublished people, places or links is published after a
    warning, never blocked."""

    def setUp(self):
        self.super = get_user_model().objects.create_superuser(
            'super', 's@x.fr', 'pw')
        public = Etat.objects.create(nom='test public', public=True)
        Etat.objects.create(nom='test privé', public=False)
        self.lieu = Lieu.objects.create(
            nom='Lieu test', nature=NatureDeLieu.objects.create(
                nom='nature test'), etat=public)

    def _unpublished_event(self):
        return Evenement.objects.create(
            debut_date=date(2000, 1, 1), debut_lieu=self.lieu,
            etat=Etat.objects.get(nom='test privé'),
            circonstance='Non publié')

    def _draft_corpus(self):
        public = Etat.objects.get(nom='test public')
        prive = Etat.objects.get(nom='test privé')
        Locale.objects.get_or_create(
            language_code=get_supported_content_language_variant(
                settings.LANGUAGE_CODE))
        site = WagtailSite.objects.filter(is_default_site=True).first()
        if site is None:
            racine = Page.get_first_root_node() or Page.add_root(
                instance=Page(title='Racine', slug='racine'))
            site = WagtailSite.objects.create(
                hostname='testserver', is_default_site=True,
                root_page=racine.add_child(
                    instance=Page(title='Accueil', slug='accueil')))
        self.letter_index = site.root_page.add_child(
            instance=LetterIndex(title='Index test', slug='index-test'))
        self.correspondant = Individu.objects.create(
            nom='Correspondant', etat=public)
        self.unpublished_individu = Individu.objects.create(
            nom='Individu non publié', etat=prive)
        self.unpublished_lieu = Lieu.objects.create(
            nom='Lieu non publié', nature=self.lieu.nature, etat=prive)
        return self.letter_index.add_child(instance=LetterCorpus(
            title='Corpus test', slug='corpus-test', live=False,
            person=self.correspondant))

    def _draft_letter(self, corpus, slug, **fields):
        senders = fields.pop('senders', [self.correspondant])
        recipients = fields.pop('recipients', [])
        fields.setdefault('writing_lieu', self.lieu)
        letter = Letter(title=slug, slug=slug, live=False, **fields)
        letter.senders = [LetterSender(person=p) for p in senders]
        letter.recipients = [LetterRecipient(person=p) for p in recipients]
        return corpus.add_child(instance=letter)

    def _publish(self, page):
        page.save_revision().publish()

    def _link(self, autorite, link_type):
        return f'<p><a linktype="{link_type}-link" id="{autorite.pk}">x</a></p>'

    def testUnpublishedPeopleAndPlacesAreFound(self):
        corpus = self._draft_corpus()
        cas = {
            'expéditeur': {'senders': [self.unpublished_individu]},
            'destinataire': {'recipients': [self.unpublished_individu]},
            'lieu de rédaction': {'writing_lieu': self.unpublished_lieu},
            'lieu de conservation': {'storage_place': self.unpublished_lieu},
        }
        for i, (nom, fields) in enumerate(cas.items()):
            with self.subTest(nom):
                letter = self._draft_letter(corpus, f'lettre-{i}', **fields)
                found = letter.get_unpublished_autorites()
                self.assertEqual(len(found), 1)
                self.assertIn(found[0], (
                    self.unpublished_individu, self.unpublished_lieu))
                self.assertEqual(letter.get_unpublished_links(), [])
        unpublished_corpus = self.letter_index.add_child(
            instance=LetterCorpus(
                title='Autre corpus', slug='autre-corpus', live=False,
                person=self.unpublished_individu))
        self.assertEqual(
            unpublished_corpus.get_unpublished_autorites(),
            [self.unpublished_individu])

    def testAnUnpublishedAutoriteIsListedOnce(self):
        corpus = self._draft_corpus()
        letter = self._draft_letter(
            corpus, 'lettre-doublon', senders=[self.unpublished_individu],
            recipients=[self.unpublished_individu])
        self.assertEqual(
            letter.get_unpublished_autorites(), [self.unpublished_individu])

    def testUnpublishedLinksAreFound(self):
        prive = Etat.objects.get(nom='test privé')
        unpublished_event = self._unpublished_event()
        corpus = self._draft_corpus()
        corpus.body = [('text', RichText(
            self._link(self.unpublished_individu, 'individu')
            + self._link(self.correspondant, 'individu')))]
        corpus.save()
        letter = self._draft_letter(
            corpus, 'lettre-liens',
            description=self._link(unpublished_event, 'evenement'),
            transcription=self._link(self.unpublished_individu, 'individu'),
            recipients=[self.unpublished_individu])
        self.assertEqual(
            corpus.get_unpublished_links(), [self.unpublished_individu])
        self.assertEqual(
            set(letter.get_unpublished_links()),
            {self.unpublished_individu, unpublished_event})
        # The people and places of the page are not links.
        self.assertEqual(corpus.get_unpublished_autorites(), [])

    def testPublicationIsNotBlocked(self):
        corpus = self._draft_corpus()
        letter = self._draft_letter(
            corpus, 'lettre-publiee', recipients=[self.unpublished_individu],
            description=self._link(self.unpublished_individu, 'individu'))
        self._publish(corpus)
        self._publish(Letter.objects.get(pk=letter.pk))
        self.assertTrue(Letter.objects.get(pk=letter.pk).live)

    def _warnings(self, response):
        return [
            m.message for m in response.context['messages']
            if m.level_tag == 'warning'
        ]

    def _post_edit(self, page, publish):
        # The second click must keep the session of the first one.
        if self.client.session.get('_auth_user_id') != str(self.super.pk):
            self.client.force_login(self.super)
        url = reverse('wagtailadmin_pages:edit', args=(page.pk,))
        data = querydict_from_html(
            self.client.get(url).content.decode(), form_id='page-edit-form')
        # The StreamField fields are filled in by JavaScript in the browser.
        if 'body-count' not in data:
            data['body-count'] = '0'
        if publish:
            data['action-publish'] = 'action-publish'
        return self.client.post(url, data, follow=True)

    def _letter_with_unpublished_autorites(self):
        corpus = self._draft_corpus()
        self._publish(corpus)
        return self._draft_letter(
            LetterCorpus.objects.get(pk=corpus.pk), 'lettre-admin',
            recipients=[self.unpublished_individu],
            writing_lieu=self.unpublished_lieu)

    def testTheFirstPublishClickWarnsAndPublishesNothing(self):
        letter = self._letter_with_unpublished_autorites()
        response = self._post_edit(letter, publish=True)
        self.assertFalse(Letter.objects.get(pk=letter.pk).live)
        avertissement, confirmation = self._warnings(response)
        self.assertIn('Attention', avertissement)
        self.assertIn('Individu non publié', avertissement)
        self.assertIn('Lieu non publié', avertissement)
        self.assertIn('état « test privé »', avertissement)
        self.assertIn('n’a pas été publiée', confirmation)

    def testTheSecondPublishClickPublishes(self):
        letter = self._letter_with_unpublished_autorites()
        self._post_edit(letter, publish=True)
        response = self._post_edit(letter, publish=True)
        self.assertTrue(Letter.objects.get(pk=letter.pk).live)
        self.assertEqual(self._warnings(response), [])

    def testAChangeAfterTheWarningAsksAgain(self):
        letter = self._letter_with_unpublished_autorites()
        self._post_edit(letter, publish=True)
        prive = Etat.objects.get(nom='test privé')
        draft = Letter.objects.get(pk=letter.pk).get_latest_revision_as_object()
        draft.description = self._link(
            self._unpublished_event(), 'evenement')
        draft.save_revision()
        response = self._post_edit(letter, publish=True)
        self.assertFalse(Letter.objects.get(pk=letter.pk).live)
        self.assertEqual(len(self._warnings(response)), 3)

    def testPublishingDoesNotWarnWhenEverythingIsPublished(self):
        corpus = self._draft_corpus()
        self._publish(corpus)
        letter = self._draft_letter(
            LetterCorpus.objects.get(pk=corpus.pk), 'lettre-propre',
            recipients=[self.correspondant])
        response = self._post_edit(letter, publish=True)
        self.assertTrue(Letter.objects.get(pk=letter.pk).live)
        self.assertEqual(self._warnings(response), [])

    def testSavingADraftDoesNotWarn(self):
        corpus = self._draft_corpus()
        letter = self._draft_letter(
            corpus, 'lettre-draft', recipients=[self.unpublished_individu])
        response = self._post_edit(letter, publish=False)
        self.assertFalse(Letter.objects.get(pk=letter.pk).live)
        self.assertEqual(self._warnings(response), [])

    def testTheHookAsksForAConfirmation(self):
        prive = Etat.objects.get(nom='test privé')
        unpublished_event = self._unpublished_event()
        corpus = self._draft_corpus()
        letter = self._draft_letter(
            corpus, 'lettre-hook', recipients=[self.unpublished_individu],
            description=self._link(unpublished_event, 'evenement'))
        request = RequestFactory().get('/')
        request.session = {}
        request._messages = FallbackStorage(request)
        reponse = confirm_unpublished_autorites(request, letter)
        self.assertEqual(reponse.status_code, 302)
        self.assertEqual(
            reponse.url, reverse('wagtailadmin_pages:edit', args=(letter.pk,)))
        liste = [m.message for m in get_messages(request)]
        self.assertEqual(len(liste), 3)
        self.assertIn('Individu non publié', liste[0])
        self.assertIn('introuvable pour certains lecteurs', liste[1])
        self.assertIn('événement', liste[1])
        # The same warnings again: the editor read them, so it goes on.
        self.assertIsNone(confirm_unpublished_autorites(request, letter))
        # Then it asks again.
        self.assertIsNotNone(confirm_unpublished_autorites(request, letter))

    def testTheHookIgnoresPagesWithoutWarnings(self):
        corpus = self._draft_corpus()
        letter = self._draft_letter(corpus, 'lettre-propre-hook')
        request = RequestFactory().get('/')
        request.session = {}
        request._messages = FallbackStorage(request)
        self.assertIsNone(confirm_unpublished_autorites(request, letter))
        self.assertEqual(list(get_messages(request)), [])
