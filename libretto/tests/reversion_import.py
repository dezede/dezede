import json
from datetime import date, datetime, timezone
from io import StringIO

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.management import CommandError, call_command
from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from reversion.models import Revision as OldRevision, Version as OldVersion
from wagtail.models import ModelLogEntry, Revision

from ..models import *
from ..models.individu import Occupation
from ..reversion_import import (
    ACTION_CREATE, ACTION_EDIT, ACTION_TODAY, canonical, doubtful_entry,
    readable_comment,
)


__all__ = ('ReversionImportTestCase',)


def snapshot(model, pk, **fields):
    return json.dumps([{
        'model': 'libretto.' + model, 'pk': pk, 'fields': fields}])


class ReversionImportTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser('super', 's@x.fr', 'pw')
        self.etat = Etat.objects.create(nom='test public', public=True)
        self.lieu = Lieu.objects.create(
            nom='Lieu test', etat=self.etat,
            nature=NatureDeLieu.objects.create(nom='nature test'))
        self.oeuvre = Oeuvre.objects.create(titre='Oeuvre test', etat=self.etat)
        self.evenement = Evenement.objects.create(
            debut_date=date(2000, 1, 1), debut_lieu=self.lieu, etat=self.etat,
            circonstance='live')
        self.when = datetime(2016, 5, 4, 12, 0, tzinfo=timezone.utc)

    # --- helpers ----------------------------------------------------------

    def old_revision(self, versions, when=None, comment='Ajout.', user=True):
        """versions: (model name, pk, snapshot text) triples."""
        revision = OldRevision.objects.create(
            date_created=when or self.when, comment=comment,
            user=self.user if user else None)
        for model, pk, text in versions:
            OldVersion.objects.create(
                revision=revision, object_id=str(pk), format='json',
                content_type=ContentType.objects.get(
                    app_label='libretto', model=model),
                serialized_data=text, object_repr='repr %s %s' % (model, pk),
                db='default')
        return revision

    def evenement_fields(self, **extra):
        return {
            'owner': self.user.pk, 'etat': self.etat.pk,
            'circonstance': 'old', 'debut_date': '1800-01-01',
            'debut_lieu': self.lieu.pk, 'caracteristiques': [], **extra}

    def old_event(self, pk=None, programme=(), **extra):
        pk = pk or self.evenement.pk
        versions = [('evenement', pk, snapshot(
            'evenement', pk, **self.evenement_fields(**extra)))]
        for ppk, position in programme:
            versions.append(('elementdeprogramme', ppk, snapshot(
                'elementdeprogramme', ppk, owner=self.user.pk, evenement=pk,
                oeuvre=self.oeuvre.pk, autre='', numerotation='O',
                position=position, part_d_auteur=None, caracteristiques=[])))
        return versions

    def run_import(self, *args, **kwargs):
        out = StringIO()
        call_command('import_reversion_history', *args, stdout=out, **kwargs)
        return out.getvalue()

    def revisions_of(self, obj):
        """The revisions made from old versions, not today's copy."""
        return Revision.objects.filter(
            object_id=str(obj.pk),
            pk__in=ModelLogEntry.objects.filter(
                object_id=str(obj.pk), data__has_key='reversion_revision_id',
            ).values('revision_id'),
        ).order_by('created_at', 'pk')

    def log_of(self, obj):
        return ModelLogEntry.objects.filter(
            object_id=str(obj.pk), data__has_key='reversion_revision_id',
        ).order_by('timestamp', 'pk')

    def today_of(self, obj):
        return Revision.objects.filter(
            pk__in=ModelLogEntry.objects.filter(
                object_id=str(obj.pk), action=ACTION_TODAY,
            ).values('revision_id'))

    def form_data(self, response):
        soup = BeautifulSoup(response.content, 'html.parser')
        form = soup.find('form', action=lambda a: a and 'revert' in a)
        data = {}
        for el in form.find_all(['input', 'select', 'textarea']):
            name = el.get('name')
            if not name or '__prefix__' in name:
                continue
            if el.name == 'select':
                option = el.find('option', selected=True) or el.find('option')
                data[name] = option.get('value', '') if option else ''
            elif el.name == 'textarea':
                data[name] = el.text.lstrip('\n')
            elif el.get('type') in ('checkbox', 'radio'):
                if el.has_attr('checked'):
                    data[name] = el.get('value', 'on')
            elif el.get('type') != 'submit':
                data[name] = el.get('value', '')
        return data

    # --- tests ------------------------------------------------------------

    def testImportsARevisionWithItsChildRows(self):
        programme = ElementDeProgramme.objects.create(
            evenement=self.evenement, oeuvre=self.oeuvre, position=0)
        ElementDeDistribution.objects.create(
            evenement=self.evenement, individu=Individu.objects.create(
                nom='Un', etat=self.etat))
        old = self.old_event(
            circonstance='live', programme=[(programme.pk, 0)])
        old[0] = ('evenement', self.evenement.pk, snapshot(
            'evenement', self.evenement.pk, **self.evenement_fields(
                circonstance='live', debut_date='2000-01-01')))
        self.old_revision(old)
        self.run_import()

        revision = self.revisions_of(self.evenement).get()
        self.assertEqual(revision.created_at, self.when)
        self.assertEqual(revision.user, self.user)
        self.assertEqual(
            revision.content_type, ContentType.objects.get_for_model(Evenement))
        self.assertEqual(
            revision.base_content_type,
            ContentType.objects.get_for_model(Evenement))
        self.assertEqual(
            revision.object_str, 'repr evenement %s' % self.evenement.pk)
        self.assertEqual(
            [row['pk'] for row in revision.content['programme']],
            [programme.pk])
        # Same format as the revisions Wagtail saves itself.
        live = self.evenement.serializable_data()
        for key in ('circonstance', 'debut_date', 'debut_lieu', 'etat'):
            self.assertEqual(revision.content[key], json.loads(
                json.dumps(live[key], default=str)))
        self.assertEqual(
            sorted(revision.content['programme'][0]),
            sorted(live['programme'][0]))

        entry = self.log_of(self.evenement).get()
        self.assertEqual(entry.action, ACTION_CREATE)
        self.assertEqual(entry.timestamp, self.when)
        self.assertEqual(entry.revision, revision)
        self.assertTrue(entry.content_changed)
        self.assertEqual(
            entry.data['reversion_revision_id'], OldRevision.objects.get().pk)
        self.assertEqual(entry.data['comment'], 'Ajout.')
        self.assertFalse(entry.data['doubtful'])
        # Today differs (a cast row is not in the old revision): one more
        # revision holds today's data, and it is the newest.
        self.evenement.refresh_from_db()
        self.assertEqual(
            self.evenement.latest_revision, self.today_of(self.evenement).get())

    def testOldSnapshotsAreMappedToTodaysFields(self):
        individu = Individu.objects.create(nom='Un', etat=self.etat)
        programme_pk, old_distribution_pk = 9001, 9002
        versions = [
            ('evenement', self.evenement.pk, snapshot(
                'evenement', self.evenement.pk, owner=self.user.pk,
                etat=self.etat.pk, notes='anciennes notes',
                ancrage_debut=582, ancrage_fin=None, documents=[],
                illustrations=[], jauge=3, circonstance='old',
                caracteristiques=[], relache=False,
                search_vector='', autocomplete_vector='')),
            ('elementdeprogramme', programme_pk, snapshot(
                'elementdeprogramme', programme_pk, owner=self.user.pk,
                evenement=self.evenement.pk, oeuvre=self.oeuvre.pk, autre='',
                numerotation='O', position=0, etat=1, notes='', personnels=[],
                distribution=[old_distribution_pk], caracteristiques=[])),
            ('elementdedistribution', old_distribution_pk, snapshot(
                'elementdedistribution', old_distribution_pk,
                owner=self.user.pk, content_type=ContentType.objects.get_for_model(
                    ElementDeProgramme).pk, object_id=programme_pk,
                individus=[individu.pk, individu.pk + 1], ensembles=[],
                pupitre=None)),
        ]
        # Before 2015-05-13 the cast is a list of ids on the programme line.
        self.old_revision(
            versions, datetime(2014, 3, 1, tzinfo=timezone.utc),
            comment='Ajout.')
        self.run_import()

        revision = self.revisions_of(self.evenement).get()
        content = revision.content
        self.assertEqual(content['notes_publiques'], 'anciennes notes')
        self.assertNotIn('notes', content)
        self.assertNotIn('ancrage_debut', content)
        self.assertNotIn('jauge', content)
        # The anchor is lost: the date is absent, not made up.
        self.assertNotIn('debut_date', content)
        distribution = content['programme'][0]['distribution']
        # One row per person, the old row keeps its id.
        self.assertEqual(
            [(row['pk'], row['individu'], row['element_de_programme'])
             for row in distribution],
            [(old_distribution_pk, individu.pk, programme_pk),
             (None, individu.pk + 1, programme_pk)])
        self.assertTrue(all(row['evenement'] is None for row in distribution))
        # The anchor table is gone: the date is lost, so the revision is
        # doubtful.
        entry = self.log_of(self.evenement).get()
        self.assertTrue(entry.data['doubtful'])
        self.assertIn('lost:ancrage', entry.data['doubtful_reasons'])

    def testRenamedFieldsOfOtherModels(self):
        source = Source.objects.create(
            type=TypeDeSource.objects.create(nom='type'), titre='live',
            etat=self.etat)
        # Before 2014-11-10 the events are a list of ids on the source.
        self.old_revision([('source', source.pk, snapshot(
            'source', source.pk, owner=self.user.pk, etat=self.etat.pk,
            type=source.type_id, nom='ancien titre', contenu='<p>texte</p>',
            notes='n', evenements=[self.evenement.pk], documents=[]))],
            datetime(2013, 5, 4, 12, 0, tzinfo=timezone.utc))
        self.run_import()
        content = self.revisions_of(source).get().content
        self.assertEqual(content['titre'], 'ancien titre')
        self.assertEqual(content['transcription'], '<p>texte</p>')
        self.assertEqual(content['notes_publiques'], 'n')
        self.assertEqual(
            [row['evenement'] for row in content['sourceevenement_set']],
            [self.evenement.pk])
        # A field that did not exist yet has no key: a revert leaves it be.
        self.assertNotIn('date_publication', content)

    def testAnUnreadableSnapshotStaysInTheHistory(self):
        self.old_revision(self.old_event())
        self.old_revision(
            [('evenement', self.evenement.pk, '[{"model": "libretto.evene')],
            when=datetime(2017, 1, 1, tzinfo=timezone.utc), comment='cassé')
        self.run_import()

        self.assertEqual(self.revisions_of(self.evenement).count(), 1)
        first, second = self.log_of(self.evenement)
        self.assertEqual(second.data['comment'], 'cassé')
        self.assertTrue(second.data['snapshot_unreadable'])
        self.assertEqual(second.data['reason'], 'invalid_json')
        self.assertIsNone(second.revision)
        self.assertEqual(second.timestamp.year, 2017)
        self.assertEqual(second.user, self.user)

    def testASnapshotWithALostBackslashIsRepaired(self):
        fields = self.evenement_fields(
            notes_publiques='<p><span style="">x</span></p>')
        text = snapshot('evenement', self.evenement.pk, **fields).replace(
            'style=\\"\\"', 'style=""')
        self.assertNotEqual(text, snapshot(
            'evenement', self.evenement.pk, **fields))
        self.old_revision([('evenement', self.evenement.pk, text)])
        self.run_import()
        revision = self.revisions_of(self.evenement).get()
        self.assertEqual(
            revision.content['notes_publiques'], '<p><span style="">x</span></p>')
        entry = self.log_of(self.evenement).get()
        self.assertIn('repaired_json', entry.data['flags'])
        self.assertFalse(entry.data['doubtful'])

    def testItIsIdempotentAndResumable(self):
        self.old_revision(self.old_event())
        self.run_import()
        self.run_import()
        self.assertEqual(self.revisions_of(self.evenement).count(), 1)
        self.assertEqual(self.log_of(self.evenement).count(), 1)
        # A newer old revision is picked up by a second run.
        self.old_revision(
            self.old_event(), datetime(2017, 1, 1, tzinfo=timezone.utc))
        self.run_import()
        self.assertEqual(self.revisions_of(self.evenement).count(), 2)

    def testDryRunAndOptions(self):
        self.old_revision(self.old_event())
        self.run_import(dry_run=True)
        self.assertEqual(self.revisions_of(self.evenement).count(), 0)
        self.assertEqual(self.log_of(self.evenement).count(), 0)
        self.run_import(model=['individu'], sample=5)
        self.assertEqual(self.revisions_of(self.evenement).count(), 0)
        self.run_import(model=['evenement'], sample=5)
        self.assertEqual(self.revisions_of(self.evenement).count(), 1)

    def testARowIdOfAnotherParentIsNotReused(self):
        other = Evenement.objects.create(
            debut_date=date(2000, 1, 1), debut_lieu=self.lieu, etat=self.etat)
        stolen = ElementDeProgramme.objects.create(
            evenement=other, oeuvre=self.oeuvre, position=0)
        self.old_revision(self.old_event(programme=[(stolen.pk, 0)]))
        self.run_import()
        content = self.revisions_of(self.evenement).get().content
        self.assertIsNone(content['programme'][0]['pk'])

    def testAMultiTableChildTakesItsFieldsFromBothVersions(self):
        audio = Audio.objects.create(
            type=TypeDeSource.objects.create(nom='type'), titre='live',
            etat=self.etat)
        self.old_revision([
            ('source', audio.pk, snapshot(
                'source', audio.pk, owner=self.user.pk, etat=self.etat.pk,
                type=audio.type_id, titre='titre audio')),
            ('audio', audio.pk, snapshot(
                'audio', audio.pk, format='mp3', duree='00:01:00')),
        ])
        self.run_import(model=['source'])
        revision = self.revisions_of(audio).get()
        self.assertEqual(
            revision.content_type, ContentType.objects.get_for_model(Audio))
        self.assertEqual(
            revision.base_content_type,
            ContentType.objects.get_for_model(Source))
        self.assertEqual(revision.content['titre'], 'titre audio')
        self.assertEqual(revision.content['format'], 'mp3')
        self.assertEqual(len(self.log_of(audio)), 1)
        # Today differs, so the copy is the newest, also for a child table.
        audio.refresh_from_db()
        self.assertEqual(
            audio.latest_revision_id, self.today_of(audio).get().pk)

    # --- reverting --------------------------------------------------------

    def revert_url(self, obj, revision):
        return reverse(
            'wagtailsnippets_libretto_evenement:revisions_revert',
            args=(obj.pk, revision.pk))

    def testRevertingAnImportedRevisionBringsBackItsChildRows(self):
        programme = ElementDeProgramme.objects.create(
            evenement=self.evenement, oeuvre=self.oeuvre, position=0)
        self.old_revision(self.old_event(
            circonstance='avant', programme=[(programme.pk, 0)]))
        self.run_import()
        # The row was deleted after the old revision was taken.
        programme.delete()
        revision = self.revisions_of(self.evenement).get()
        client = Client()
        client.force_login(self.user)
        url = self.revert_url(self.evenement, revision)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        response = client.post(url, self.form_data(response))
        self.assertEqual(response.status_code, 302)
        self.evenement.refresh_from_db()
        self.assertEqual(self.evenement.circonstance, 'avant')
        self.assertEqual(self.evenement.programme.count(), 1)

    def testRevertingADoubtfulRevisionIsRefused(self):
        self.old_revision(self.old_event(
            circonstance='douteux', ancrage_debut=5))
        self.run_import()
        revision = self.revisions_of(self.evenement).get()
        client = Client()
        client.force_login(self.user)
        url = self.revert_url(self.evenement, revision)

        # Viewing is allowed, with a message and without a save button.
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'pas la restaurer')
        content = response.content.decode()
        # Below Wagtail's own warning, out of the way of the menu button.
        self.assertGreater(
            content.index('pas la restaurer'), content.index('Vous passez'))
        self.assertNotContains(response, 'action-save')
        compare = client.get(reverse(
            'wagtailsnippets_libretto_evenement:revisions_compare',
            args=(self.evenement.pk, revision.pk, 'latest')))
        self.assertEqual(compare.status_code, 200)

        data = self.form_data(response)
        response = client.post(url, data)
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, 'pas la restaurer', status_code=403)
        self.evenement.refresh_from_db()
        self.assertEqual(self.evenement.circonstance, 'live')
        self.assertEqual(self.revisions_of(self.evenement).count(), 1)

    def testRestoreDeletedRefusesADoubtfulRevision(self):
        evenement = Evenement.objects.create(
            debut_date=date(2000, 1, 1), debut_lieu=self.lieu, etat=self.etat)
        pk = evenement.pk
        self.old_revision(
            self.old_event(pk=pk, ancrage_debut=5),
            datetime(2013, 12, 1, tzinfo=timezone.utc))
        self.old_revision(
            self.old_event(pk=pk), datetime(2016, 1, 1, tzinfo=timezone.utc))
        self.run_import()
        evenement.delete()
        # The last revision is clean: it is the one that is restored.
        doubtful = Revision.objects.filter(
            object_id=str(pk)).order_by('created_at').first()
        self.assertTrue(doubtful_entry(doubtful.pk))
        with self.assertRaises(CommandError):
            call_command(
                'restore_deleted', 'libretto.Evenement', str(pk),
                revision=doubtful.pk, stdout=StringIO())
        self.assertFalse(Evenement.objects.filter(pk=pk).exists())
        call_command(
            'restore_deleted', 'libretto.Evenement', str(pk),
            stdout=StringIO())
        self.assertTrue(Evenement.objects.filter(pk=pk).exists())

    # --- readable comments ------------------------------------------------

    def testReadableComments(self):
        self.assertEqual(readable_comment('[{"added": {}}]'), 'Ajout')
        self.assertEqual(readable_comment('[]'), 'Aucun champ modifié')
        self.assertEqual(
            readable_comment('[{"changed": {"fields": ["notes_publiques", '
                             '"etat"]}}]'),
            'Modification (notes publiques, etat)')
        self.assertEqual(
            readable_comment(
                '[{"added": {}}, {"added": {"name": "source evenement", '
                '"object": "SourceEvenement object"}}]'),
            'Ajout. Ajout de source evenement')
        self.assertEqual(
            readable_comment('Ajout. Ajout de source evenement « '
                             'SourceEvenement object (12) ».'),
            'Ajout. Ajout de source evenement')
        self.assertEqual(readable_comment('Modification de Notes.'),
                         'Modification de Notes')
        self.assertTrue(readable_comment('x' * 500).endswith('…'))

    def testOldCommentsAreWorded(self):
        cases = [
            # (what the old admin wrote, what the History shows)
            ('Ajout. Ajout de élément de programme « Mussard (M.) dit '
             'Naâman [poète], Mon amour, chanson ».',
             'Ajout. Ajout d’élément de programme « Mussard (M.) dit Naâman '
             '[poète], Mon amour, chanson »'),
            ('Modification de Notes publiques. Modification de  pour l’objet '
             'élément de programme « Chaminade (C.), Duos ».',
             'Modification de Notes publiques. Modification d’élément de '
             'programme « Chaminade (C.), Duos »'),
            ('Modification de  pour l’objet élément de distribution « Un ».',
             'Modification d’élément de distribution « Un »'),
            ('Modification de Œuvre pour l’objet élément de programme « X ».',
             'Modification d’Œuvre pour l’objet élément de programme « X »'),
            ('Modification de État.', 'Modification d’État'),
            ('Modification de Individu pour l’objet auteur « Un ».',
             'Modification d’Individu pour l’objet auteur « Un »'),
            ('Ajout de auteur « Un ». Ajout de pupitre « Concerto de Amour ».',
             'Ajout d’auteur « Un ». Ajout de pupitre « Concerto de Amour »'),
            ('Suppression de élément de programme « Un ».',
             'Suppression d’élément de programme « Un »'),
            ('Ajout de source evenement « SourceEvenement object (12) ».',
             'Ajout de source evenement'),
            ('Modification de Notes publiques et Notes privées.',
             'Modification de Notes publiques et Notes privées'),
            ('Modification de Heure.', 'Modification d’Heure'),
            ('oeuvre modifié pour élément de programme « X ».',
             'oeuvre modifié pour élément de programme « X »'),
            ('Modifié etat.', 'Modifié etat'),
            ('[{"added": {"name": "élément de programme", "object": "X"}}]',
             'Ajout d’élément de programme'),
            ('[{"changed": {"name": "élément de programme", "object": "X", '
             '"fields": []}}]', 'Modification d’élément de programme'),
            ('[{"changed": {"fields": ["etat"]}}, {"deleted": {"name": '
             '"auteur", "object": "X"}}]',
             'Modification (etat). Suppression d’auteur'),
        ]
        for old, shown in cases:
            with self.subTest(old):
                self.assertEqual(readable_comment(old), shown)

    def history_page(self, obj):
        client = Client()
        client.force_login(self.user)
        return client.get(reverse(
            'wagtailsnippets_libretto_evenement:history', args=(obj.pk,)))

    def testHistoryMarksTheOldEntries(self):
        self.old_revision(
            self.old_event(), datetime(2013, 1, 1, tzinfo=timezone.utc),
            comment='[{"added": {}}]')
        self.old_revision(
            self.old_event(ancrage_debut=5),
            datetime(2016, 3, 1, tzinfo=timezone.utc),
            comment='Modification de Notes.')
        self.old_revision(
            [('evenement', self.evenement.pk, '[{"model": "libretto.eve')],
            datetime(2017, 1, 1, tzinfo=timezone.utc), comment='cassé')
        self.run_import()
        page = self.history_page(self.evenement)
        self.assertContains(page, 'Créé (ancien historique)')
        self.assertContains(
            page, 'Modifié (ancien historique, douteuse)')
        self.assertContains(page, 'Modifié (ancien historique, version illisible)')
        self.assertContains(page, 'données perdues')
        self.assertContains(page, 'Modification de Notes')
        self.assertNotContains(page, '&quot;added&quot;')
        self.assertNotContains(page, '{&quot;')

    def testHistoryDoesNotQueryPerEntry(self):
        self.history_page(self.evenement)  # warms the registries up

        def queries(count):
            evenement = Evenement.objects.create(
                debut_date=date(2000, 1, 1), debut_lieu=self.lieu,
                etat=self.etat)
            for n in range(count):
                self.old_revision(
                    self.old_event(pk=evenement.pk), datetime(
                        2016, 1, 1 + n, tzinfo=timezone.utc),
                    comment='[{"added": {}}]')
            self.run_import(model=['evenement'], pk=[evenement.pk])
            with CaptureQueriesContext(connection) as captured:
                self.history_page(evenement)
            return len(captured)
        self.assertEqual(queries(2), queries(12))

    # --- deleted objects --------------------------------------------------

    def deleted_evenement(self, when=None, **kwargs):
        self.lieu2 = Lieu.objects.create(
            nom='Autre lieu', etat=self.etat, nature=self.lieu.nature)
        kwargs.setdefault('debut_lieu', self.lieu2.pk)
        evenement = Evenement.objects.create(
            debut_date=date(2000, 1, 1), debut_lieu=self.lieu2, etat=self.etat)
        pk = evenement.pk
        programme = ElementDeProgramme.objects.create(
            evenement=evenement, oeuvre=self.oeuvre, position=0)
        self.old_revision(
            self.old_event(pk=pk, programme=[(programme.pk, 0)], **kwargs),
            when)
        programme_pk = programme.pk
        evenement.delete()
        return pk, programme_pk

    def restore(self, *args, **kwargs):
        out = StringIO()
        call_command('restore_deleted', *args, stdout=out, **kwargs)
        return out.getvalue()

    def testDeletedObjectsAreImportedAndListed(self):
        pk, _ = self.deleted_evenement()
        self.run_import()
        self.assertEqual(
            Revision.objects.filter(object_id=str(pk)).count(), 1)
        self.assertEqual(
            ModelLogEntry.objects.filter(object_id=str(pk)).count(), 1)
        listing = self.restore('libretto.Evenement')
        self.assertIn(str(pk), listing)
        self.assertNotIn('douteuse', listing)

    def testARestoredImportedSnapshotComesBackWithItsRows(self):
        pk, programme_pk = self.deleted_evenement(circonstance='ancienne')
        self.run_import()
        self.restore('libretto.Evenement', str(pk))
        evenement = Evenement.objects.get(pk=pk)
        self.assertEqual(evenement.circonstance, 'ancienne')
        self.assertEqual(
            list(evenement.programme.values_list('pk', flat=True)),
            [programme_pk])

    def testADoubtfulDeletedObjectIsListedAsSuchAndRefused(self):
        pk, _ = self.deleted_evenement(ancrage_debut=5)
        self.run_import()
        self.assertIn('(douteuse)', self.restore('libretto.Evenement'))
        with self.assertRaises(CommandError):
            self.restore('libretto.Evenement', str(pk))
        self.assertFalse(Evenement.objects.filter(pk=pk).exists())

    def testRestoringFailsCleanlyWhenALinkedObjectIsGone(self):
        pk, _ = self.deleted_evenement()
        self.run_import()
        self.lieu2.delete()
        with self.assertRaisesMessage(CommandError, 'libretto.Lieu'):
            self.restore('libretto.Evenement', str(pk))
        self.assertFalse(Evenement.objects.filter(pk=pk).exists())
        # Also for a row of the programme.
        pk, _ = self.deleted_evenement()
        self.run_import()
        self.oeuvre.delete()
        with self.assertRaisesMessage(CommandError, 'libretto.Oeuvre'):
            self.restore('libretto.Evenement', str(pk))

    def testRestoringFailsCleanlyWhenARequiredLinkIsEmpty(self):
        # Snapshots from before the field existed have no value for it.
        pk, _ = self.deleted_evenement(etat=None)
        self.run_import()
        with self.assertRaisesMessage(CommandError, 'etat is empty'):
            self.restore('libretto.Evenement', str(pk))
        self.assertFalse(Evenement.objects.filter(pk=pk).exists())

    def testRestoringKeepsTheRowsOfAnotherParent(self):
        pk, programme_pk = self.deleted_evenement()
        self.run_import()
        # The id of the old row is somebody else's now.
        other = Evenement.objects.create(
            debut_date=date(2000, 1, 1), debut_lieu=self.lieu, etat=self.etat)
        ElementDeProgramme.objects.create(
            pk=programme_pk, evenement=other, oeuvre=self.oeuvre, position=5)
        self.restore('libretto.Evenement', str(pk))
        self.assertEqual(
            ElementDeProgramme.objects.get(pk=programme_pk).evenement_id,
            other.pk)
        restored = Evenement.objects.get(pk=pk)
        self.assertEqual(restored.programme.count(), 1)
        self.assertNotEqual(restored.programme.get().pk, programme_pk)

    # --- the rows of a revision, by period --------------------------------

    def cast_snapshot(self, pk, line, individu):
        return ('elementdedistribution', pk, snapshot(
            'elementdedistribution', pk, owner=self.user.pk, evenement=None,
            element_de_programme=line.pk, individu=individu.pk, ensemble=None,
            partie=None, profession=None))

    def line_with_cast(self):
        individu = Individu.objects.create(nom='Un', etat=self.etat)
        line = ElementDeProgramme.objects.create(
            evenement=self.evenement, oeuvre=self.oeuvre, position=0)
        cast = ElementDeDistribution.objects.create(
            element_de_programme=line, individu=individu)
        return individu, line, cast

    def testANestedCastIsCarriedForward(self):
        # The old admin did not follow the cast of a programme line: a save
        # that only edits the notes holds the line, not its cast.
        individu, line, cast = self.line_with_cast()
        base = self.old_event(programme=[(line.pk, 0)])
        self.old_revision(
            base + [self.cast_snapshot(cast.pk, line, individu)],
            datetime(2016, 1, 1, tzinfo=timezone.utc))
        self.old_revision(
            base, datetime(2016, 2, 1, tzinfo=timezone.utc),
            comment='Modification de Notes publiques.')
        self.run_import()
        for revision in self.revisions_of(self.evenement):
            self.assertEqual(
                [row['pk'] for row in
                 revision.content['programme'][0]['distribution']], [cast.pk])
        self.assertEqual(
            [e.data['doubtful'] for e in self.log_of(self.evenement)],
            [False, False])

    def testANestedCastRowDeletedLaterMakesTheRevisionsUncertain(self):
        individu = Individu.objects.create(nom='Un', etat=self.etat)
        line = ElementDeProgramme.objects.create(
            evenement=self.evenement, oeuvre=self.oeuvre, position=0,
            owner=self.user)
        gone = 990001  # a cast row that no longer exists
        base = self.old_event(
            programme=[(line.pk, 0)], circonstance='live',
            debut_date='2000-01-01', owner=None)
        for month, extra in ((1, [self.cast_snapshot(gone, line, individu)]),
                             (2, []), (3, [])):
            self.old_revision(
                base + extra, datetime(2016, month, 1, tzinfo=timezone.utc))
        self.run_import()
        revisions = list(self.revisions_of(self.evenement))
        logs = list(self.log_of(self.evenement))
        # Not doubtful: a revert is allowed. Uncertain after the last version.
        self.assertEqual([e.data['doubtful'] for e in logs], [False] * 3)
        self.assertEqual(
            [e.data['uncertain_reasons'] for e in logs],
            [[], ['deleted_unknown:programme.distribution'],
             ['deleted_unknown:programme.distribution']])
        # The row is carried to the newest revision, so today differs and a
        # copy records the deletion.
        self.assertEqual(
            [len(r.content['programme'][0]['distribution'])
             for r in revisions], [1, 1, 1])
        self.evenement.refresh_from_db()
        self.assertEqual(
            self.evenement.latest_revision, self.today_of(self.evenement).get())
        self.assertEqual(
            self.today_of(self.evenement).get().content['programme'][0][
                'distribution'], [])

    def testHistoryShowsAnUncertainEntryAndItCanBeReverted(self):
        individu = Individu.objects.create(nom='Un', etat=self.etat)
        line = ElementDeProgramme.objects.create(
            evenement=self.evenement, oeuvre=self.oeuvre, position=0)
        base = self.old_event(programme=[(line.pk, 0)])
        for month, extra in ((1, [self.cast_snapshot(990003, line, individu)]),
                             (2, [])):
            self.old_revision(
                base + extra, datetime(2016, month, 1, tzinfo=timezone.utc))
        self.run_import()
        page = self.history_page(self.evenement).content.decode()
        self.assertIn('Modifié (ancien historique, incertaine)', page)
        self.assertIn('incertaine : lignes supprimées à une date inconnue', page)
        uncertain = self.revisions_of(self.evenement).last()
        client = Client()
        client.force_login(self.user)
        url = self.revert_url(self.evenement, uncertain)
        response = client.post(url, self.form_data(client.get(url)))
        self.assertEqual(response.status_code, 302)

    def testTheInitialVersionIsACreationWithAFrenchComment(self):
        self.old_revision(
            self.old_event(), datetime(2016, 1, 1, tzinfo=timezone.utc),
            comment='Initial version')
        self.old_revision(
            self.old_event(), datetime(2016, 2, 1, tzinfo=timezone.utc),
            comment='Modification de Notes.')
        self.old_revision(
            self.old_event(), datetime(2016, 3, 1, tzinfo=timezone.utc),
            comment='Initial version.')
        self.run_import()
        self.assertEqual(
            [e.action for e in self.log_of(self.evenement)],
            [ACTION_CREATE, ACTION_EDIT, ACTION_CREATE])
        page = self.history_page(self.evenement).content.decode()
        self.assertIn('Créé (ancien historique)', page)
        self.assertIn('Version initiale', page)
        self.assertNotIn('Initial version', page)
        self.assertEqual(readable_comment('Version initiale.'), 'Version initiale')

    def testFieldsAbsentFromTheNewestRevisionDoNotMakeATodayCopy(self):
        # An old snapshot lacks the fields that came later. What it has
        # equals today, so it is the current state.
        individu = Individu.objects.create(nom='Un', etat=self.etat)
        self.old_revision([('individu', individu.pk, snapshot(
            'individu', individu.pk, owner=None, etat=self.etat.pk, nom='Un',
            professions=[]))])
        self.run_import()
        content = self.revisions_of(individu).get().content
        self.assertNotIn('biographie', content)
        individu.refresh_from_db()
        self.assertEqual(
            individu.latest_revision, self.revisions_of(individu).get())
        self.assertFalse(self.today_of(individu).exists())

    def pupitre_snapshot(self, pk, maximum):
        return ('pupitre', pk, snapshot(
            'pupitre', pk, owner=self.user.pk, partie=self.partie.pk,
            quantite_min=1, quantite_max=maximum))

    def testRowsOfAnIdListComeFromVersionsInOtherRevisions(self):
        self.partie = Partie.objects.create(
            nom='Partie', type=Partie.INSTRUMENT, etat=self.etat)
        first = Pupitre.objects.create(
            oeuvre=self.oeuvre, partie=self.partie, quantite_max=5)
        live_only = Pupitre.objects.create(
            oeuvre=self.oeuvre, partie=self.partie, quantite_max=9)
        nowhere = 990002
        # Before 2015-03-30 the oeuvre lists the ids; each pupitre was saved
        # on its own page, in revisions of its own.
        self.old_revision([self.pupitre_snapshot(first.pk, 1)],
                          datetime(2013, 6, 1, tzinfo=timezone.utc))
        self.old_revision([self.pupitre_snapshot(first.pk, 2)],
                          datetime(2014, 6, 1, tzinfo=timezone.utc))
        listing = [first.pk, live_only.pk, nowhere]
        for when in (datetime(2014, 1, 1, tzinfo=timezone.utc),
                     datetime(2014, 9, 1, tzinfo=timezone.utc)):
            self.old_revision([('oeuvre', self.oeuvre.pk, snapshot(
                'oeuvre', self.oeuvre.pk, owner=self.user.pk,
                etat=self.etat.pk, titre='x', pupitres=listing))], when)
        self.run_import(model=['oeuvre'], pk=[self.oeuvre.pk])

        before, after = [
            {row['pk']: row['quantite_max'] for row in r.content['pupitres']}
            for r in self.revisions_of(self.oeuvre)]
        # The version at the date of the revision, not the latest one.
        self.assertEqual(before[first.pk], 1)
        self.assertEqual(after[first.pk], 2)
        # No version at all: the live row stands in.
        self.assertEqual(before[live_only.pk], 9)
        self.assertNotIn(nowhere, before)
        first_log, _ = self.log_of(self.oeuvre)
        self.assertIn('content_from_live', first_log.data['flags'])
        self.assertEqual(
            first_log.data['doubtful_reasons'], ['unknown_row:pupitres'])

    def testAnEmptyFollowedRelationIsNotDoubtful(self):
        line = ElementDeProgramme.objects.create(
            evenement=self.evenement, oeuvre=self.oeuvre, position=0)
        self.old_revision(
            self.old_event(programme=[(line.pk, 0)]),
            datetime(2016, 1, 1, tzinfo=timezone.utc))
        self.old_revision(
            self.old_event(), datetime(2016, 2, 1, tzinfo=timezone.utc))
        self.run_import()
        first, second = self.revisions_of(self.evenement)
        self.assertEqual(len(first.content['programme']), 1)
        self.assertEqual(second.content['programme'], [])
        self.assertEqual(
            [e.data['doubtful'] for e in self.log_of(self.evenement)],
            [False, False])

    def testLinkIdsAreKeptInEveryRevision(self):
        individu = Individu.objects.create(nom='Un', etat=self.etat)
        profession = Profession.objects.create(nom='p', etat=self.etat)
        occupation = Occupation.objects.create(
            individu=individu, profession=profession)
        for month in (1, 2, 3):
            self.old_revision([('individu', individu.pk, snapshot(
                'individu', individu.pk, owner=self.user.pk,
                etat=self.etat.pk, nom='Un', professions=[profession.pk]))],
                datetime(2016, month, 1, tzinfo=timezone.utc))
        self.run_import()
        for revision in self.revisions_of(individu):
            self.assertEqual(
                [row['pk'] for row in revision.content['occupations']],
                [occupation.pk])

    # --- the newest revision is today -------------------------------------

    def snapshot_of(self, obj, **extra):
        data = json.loads(serializers.serialize('json', [obj]))[0]
        data['fields'].update(extra)
        return json.dumps([data])

    def testTheLatestRevisionIsTheNewestWhenItEqualsTheLiveObject(self):
        individu = Individu.objects.create(nom='Un', etat=self.etat)
        self.old_revision([(
            'individu', individu.pk, self.snapshot_of(individu, professions=[]),
        )])
        self.run_import()
        individu.refresh_from_db()
        self.assertEqual(
            individu.latest_revision, self.revisions_of(individu).get())
        self.assertFalse(self.today_of(individu).exists())

    def testATodayCopyIsMadeWhenTheNewestDiffers(self):
        self.old_revision(self.old_event())  # circonstance 'old', live: 'live'
        self.run_import()
        copy = self.today_of(self.evenement).get()
        self.assertEqual(copy.content['circonstance'], 'live')
        self.assertIsNone(copy.user)
        self.assertGreater(copy.created_at, self.when)
        self.evenement.refresh_from_db()
        self.assertEqual(self.evenement.latest_revision, copy)
        entry = ModelLogEntry.objects.get(revision=copy)
        self.assertEqual(entry.action, ACTION_TODAY)
        self.assertFalse(entry.data['doubtful'])
        self.assertIn('circonstance', entry.data['differs'])
        content = self.history_page(self.evenement).content.decode()
        self.assertLess(
            content.index('État au moment du passage à Wagtail'),
            content.index('Créé (ancien historique'))

    def testAnObjectWithARevisionFromWagtailIsLeftAlone(self):
        native = self.evenement.save_revision(clean=False)
        self.old_revision(
            self.old_event(), datetime(2013, 1, 1, tzinfo=timezone.utc))
        self.run_import()
        self.evenement.refresh_from_db()
        self.assertEqual(self.evenement.latest_revision, native)
        self.assertFalse(self.today_of(self.evenement).exists())
        self.assertEqual(self.revisions_of(self.evenement).count(), 1)

    def testRevertingToAnImportedRevisionAndBackRestoresToday(self):
        individu, line, cast = self.line_with_cast()
        self.evenement.refresh_from_db()
        today = canonical(self.evenement.serializable_data())
        self.old_revision(self.old_event(
            programme=[(line.pk, 0)], circonstance='avant'))
        self.run_import()
        old = self.revisions_of(self.evenement).get()
        copy = self.today_of(self.evenement).get()
        client = Client()
        client.force_login(self.user)

        def revert(revision):
            url = self.revert_url(self.evenement, revision)
            response = client.post(url, self.form_data(client.get(url)))
            self.assertEqual(response.status_code, 302)
        revert(old)
        evenement = Evenement.objects.get(pk=self.evenement.pk)
        self.assertEqual(evenement.circonstance, 'avant')
        self.assertFalse(
            ElementDeDistribution.objects.filter(pk=cast.pk).exists())
        revert(copy)
        evenement = Evenement.objects.get(pk=self.evenement.pk)
        self.assertEqual(canonical(evenement.serializable_data()), today)

    def testResetDeletesWhatTheImportMadeAndKeepsWagtailRevisions(self):
        native = self.evenement.save_revision(clean=False)
        other = Evenement.objects.create(
            debut_date=date(2000, 1, 1), debut_lieu=self.lieu, etat=self.etat)
        self.old_revision(self.old_event(pk=other.pk))
        self.run_import()
        self.assertTrue(self.today_of(other).exists())
        out = StringIO()
        call_command('import_reversion_history', reset=True, stdout=out)
        self.assertFalse(Revision.objects.filter(
            object_id=str(other.pk)).exists())
        self.assertFalse(ModelLogEntry.objects.filter(
            action__startswith='libretto.reversion.').exists())
        self.assertTrue(Revision.objects.filter(pk=native.pk).exists())
        other.refresh_from_db()
        self.assertIsNone(other.latest_revision)
        self.assertIn('wagtail_revisions_kept: 1', out.getvalue())
