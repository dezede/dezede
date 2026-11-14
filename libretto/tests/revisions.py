from datetime import date
from io import StringIO

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management import CommandError, call_command
from django.db.models.signals import post_save
from django.test import Client, TestCase
from django.urls import reverse
from bs4 import BeautifulSoup
from wagtail.models import ModelLogEntry, Revision

from ..api.rest.serializers import (
    EvenementSerializer, PartieSerializer, ProfessionSerializer,
    SourceSerializer,
)
from ..models import *
from ..models.base import AutoriteModel


__all__ = ('WagtailRevisionsTestCase',)


class WagtailRevisionsTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.super = User.objects.create_superuser('super', 's@x.fr', 'pw')

        self.etat = etat = Etat.objects.create(nom='test public', public=True)
        self.nature = NatureDeLieu.objects.create(nom='nature test')
        lieu = Lieu.objects.create(nom='Lieu test', etat=etat, nature=self.nature)
        self.objets = {
            Evenement: Evenement.objects.create(
                debut_date=date(2000, 1, 1), debut_lieu=lieu, etat=etat,
                circonstance='Circonstance test'),
            Individu: Individu.objects.create(nom='Individu test', etat=etat),
            Oeuvre: Oeuvre.objects.create(titre='Oeuvre test', etat=etat),
            Partie: Partie.objects.create(
                nom='Partie test', type=Partie.INSTRUMENT, etat=etat),
            Profession: Profession.objects.create(
                nom='Profession test', etat=etat),
            Source: Source.objects.create(
                type=TypeDeSource.objects.create(nom='type test'),
                titre='Source test', etat=etat),
            Lieu: lieu,
            Ensemble: Ensemble.objects.create(
                nom='Ensemble test', etat=etat,
                type=TypeDEnsemble.objects.create(nom='orchestre')),
        }

    def testEveryAutoriteModelIsCovered(self):
        # AutoriteModel gives revisions to every subclass, so a new authority
        # model fails here until its objects, serializers and API are checked.
        # Models that extend another one (Audio, Video) share its column.
        autorites = {
            model for model in apps.get_models()
            if issubclass(model, AutoriteModel)
            and not any(issubclass(parent, AutoriteModel)
                        for parent in model._meta.parents)}
        self.assertEqual(set(self.objets), autorites)

    def testSaveRevisionOnEveryAutoriteModel(self):
        # The snapshot serialises every field, so a field that cannot be
        # written to JSON or read back shows up here.
        for model, obj in self.objets.items():
            with self.subTest(model.__name__):
                revision = obj.save_revision(user=self.super)
                obj.refresh_from_db()
                self.assertEqual(obj.latest_revision, revision)
                self.assertEqual(obj.revisions.count(), 1)
                self.assertEqual(revision.as_object().pk, obj.pk)

    def testRevisionKeepsTheChildRelations(self):
        # Rows hanging off a ParentalKey are only in the snapshot if
        # ClusterableModel serialises it, which depends on the class order.
        evenement = self.objets[Evenement]
        ElementDeProgramme.objects.create(
            evenement=evenement, oeuvre=self.objets[Oeuvre], position=1)
        revision = evenement.save_revision()
        self.assertEqual(len(revision.content['programme']), 1)

    def testDistributionIsKeptUnderItsOwnParent(self):
        # ElementDeDistribution has two ParentalKeys, and a row only fills one
        # of them. Each row must appear once, under the parent that owns it.
        evenement = self.objets[Evenement]
        individu = self.objets[Individu]
        element = ElementDeProgramme.objects.create(
            evenement=evenement, oeuvre=self.objets[Oeuvre], position=1)
        ElementDeDistribution.objects.create(
            evenement=evenement, individu=individu)
        ElementDeDistribution.objects.create(
            element_de_programme=element, individu=individu)
        content = evenement.save_revision().content
        self.assertEqual(len(content['distribution']), 1)
        self.assertEqual(len(content['programme'][0]['distribution']), 1)

    def testAuteurIsKeptUnderItsOwnParent(self):
        individu = self.objets[Individu]
        oeuvre, source = self.objets[Oeuvre], self.objets[Source]
        Auteur.objects.create(oeuvre=oeuvre, individu=individu)
        Auteur.objects.create(source=source, individu=individu)
        self.assertEqual(len(oeuvre.save_revision().content['auteurs']), 1)
        self.assertEqual(len(source.save_revision().content['auteurs']), 1)

    def testParenteIsOnlyInTheRevisionOfTheChild(self):
        # ParenteDIndividus has a ParentalKey on `enfant` only, so an edit made
        # from the parent's side is not part of the parent's snapshot.
        parent = self.objets[Individu]
        enfant = Individu.objects.create(nom='Enfant test', etat=self.etat)
        type_ = TypeDeParenteDIndividus.objects.create(
            nom='père', nom_relatif='fils')
        ParenteDIndividus.objects.create(
            type=type_, parent=parent, enfant=enfant)
        self.assertEqual(len(enfant.save_revision().content['parentes']), 1)
        self.assertEqual(parent.save_revision().content['parentes'], [])

    def testRestoringARevisionRestoresTheChildren(self):
        evenement = self.objets[Evenement]
        oeuvre = self.objets[Oeuvre]
        premier = ElementDeProgramme.objects.create(
            evenement=evenement, oeuvre=oeuvre, position=1)
        second = ElementDeProgramme.objects.create(
            evenement=evenement, oeuvre=oeuvre, position=2)
        ElementDeDistribution.objects.create(
            element_de_programme=premier, individu=self.objets[Individu])
        revision = evenement.save_revision()

        second_pk = second.pk
        second.delete()
        premier.distribution.all().delete()
        ElementDeProgramme.objects.create(
            evenement=evenement, oeuvre=oeuvre, position=3)

        revision.as_object().save()
        elements = ElementDeProgramme.objects.filter(evenement=evenement)
        self.assertEqual(
            sorted(elements.values_list('pk', 'position')),
            [(premier.pk, 1), (second_pk, 2)])
        self.assertEqual(premier.distribution.count(), 1)

    def testChildEditedOnItsOwnCreatesNoRevision(self):
        # Known loss: only a save of the parent records its children.
        evenement = self.objets[Evenement]
        element = ElementDeProgramme.objects.create(
            evenement=evenement, oeuvre=self.objets[Oeuvre], position=1)
        evenement.save_revision()
        element.autre = 'modifié'
        element.save()
        self.assertEqual(evenement.revisions.count(), 1)
        self.assertEqual(
            evenement.latest_revision.content['programme'][0]['autre'], '')

    def testTreePathIsNotPartOfTheRevision(self):
        for model in (Lieu, Oeuvre):
            with self.subTest(model.__name__):
                revision = self.objets[model].save_revision()
                self.assertNotIn('path', revision.content)

    def testRestoringATreeObjectKeepsTheTreeValid(self):
        # The database computes the path, so a restored object has none until
        # it is saved, and saving fills it in again.
        siblings = {
            Lieu: lambda: Lieu.objects.create(
                nom='Autre lieu', etat=self.etat, nature=self.nature),
            Oeuvre: lambda: Oeuvre.objects.create(
                titre='Autre oeuvre', etat=self.etat),
        }
        for model, create_sibling in siblings.items():
            with self.subTest(model.__name__):
                obj = self.objets[model]
                create_sibling()
                order = list(model.objects.values_list('pk', flat=True))
                restored = obj.save_revision().as_object()
                self.assertIsNone(restored.path.value)
                restored.save()
                self.assertIsNotNone(model.objects.get(pk=obj.pk).path.value)
                self.assertEqual(
                    list(model.objects.values_list('pk', flat=True)), order)

    def testRevisionsSurviveTheDeletion(self):
        ensemble = self.objets[Ensemble]
        ensemble.save_revision()
        pk = ensemble.pk
        ensemble.delete()
        self.assertTrue(Revision.objects.filter(
            object_id=str(pk),
            content_type=ContentType.objects.get_for_model(Ensemble),
        ).exists())

    def testSaveRevisionDoesNotSaveTheObjectAgain(self):
        # A second save would reindex the object for search.
        ensemble = self.objets[Ensemble]
        sent = []

        def receiver(**kwargs):
            sent.append(kwargs)

        post_save.connect(receiver, sender=Ensemble)
        self.addCleanup(post_save.disconnect, receiver, sender=Ensemble)
        revision = ensemble.save_revision()
        self.assertEqual(sent, [])
        self.assertEqual(
            Ensemble.objects.get(pk=ensemble.pk).latest_revision_id,
            revision.pk)
        self.assertEqual(ensemble.latest_revision_id, revision.pk)

    def _form_data(self, response, action='revert'):
        soup = BeautifulSoup(response.content, 'html.parser')
        form = soup.find('form', action=lambda a: a and action in a)
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

    def testEditCannotReachTheChildOfAnotherParent(self):
        evenement = self.objets[Evenement]
        autre = Evenement.objects.create(
            debut_date=date(2001, 1, 1), debut_lieu=self.objets[Lieu],
            etat=self.etat)
        oeuvre = self.objets[Oeuvre]
        mien = ElementDeProgramme.objects.create(
            evenement=evenement, oeuvre=oeuvre, position=1, numerotation='O')
        etranger = ElementDeProgramme.objects.create(
            evenement=autre, oeuvre=oeuvre, position=7, numerotation='O')
        client = Client()
        client.force_login(self.super)
        url = reverse(
            'wagtailsnippets_libretto_evenement:edit', args=(evenement.pk,))
        # A form marked for deletion is not validated, but must not delete
        # the foreign row either.
        for delete, status in (('', 200), ('on', 302)):
            with self.subTest(delete=delete):
                data = self._form_data(client.get(url), 'edit')
                self.assertEqual(data['programme-0-id'], str(mien.pk))
                data['programme-0-id'] = str(etranger.pk)
                data['programme-0-numerotation'] = 'B'
                data['programme-0-DELETE'] = delete
                response = client.post(url, data)
                self.assertEqual(response.status_code, status)
                etranger.refresh_from_db()
                self.assertEqual(etranger.evenement_id, autre.pk)
                self.assertEqual(etranger.numerotation, 'O')
                self.assertEqual(etranger.position, 7)
        mien.refresh_from_db()
        self.assertEqual(mien.numerotation, 'O')

        data = self._form_data(client.get(url), 'edit')
        data['programme-0-numerotation'] = 'B'
        self.assertEqual(client.post(url, data).status_code, 302)
        mien.refresh_from_db()
        self.assertEqual(mien.numerotation, 'B')

    def testRevertBringsBackAChildDeletedSince(self):
        # The hidden id of the restored child is no longer in the database.
        evenement = self.objets[Evenement]
        element = ElementDeProgramme.objects.create(
            evenement=evenement, oeuvre=self.objets[Oeuvre], position=1)
        first = Evenement.objects.get(pk=evenement.pk).save_revision()
        element.delete()
        client = Client()
        client.force_login(self.super)
        url = reverse(
            'wagtailsnippets_libretto_evenement:revisions_revert',
            args=(evenement.pk, first.pk))
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        response = client.post(url, self._form_data(response))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(evenement.programme.count(), 1)

    def _restore_deleted(self, *args, **kwargs):
        out = StringIO()
        call_command('restore_deleted', *args, stdout=out, **kwargs)
        return out.getvalue()

    def testRestoreDeletedBringsBackTheObjectAndItsChildren(self):
        evenement = self.objets[Evenement]
        ElementDeProgramme.objects.create(
            evenement=evenement, oeuvre=self.objets[Oeuvre], position=1)
        evenement.save_revision()
        pk = evenement.pk
        evenement.delete()

        self.assertIn(str(pk), self._restore_deleted('libretto.Evenement'))
        self._restore_deleted('libretto.Evenement', str(pk))

        restored = Evenement.objects.get(pk=pk)
        self.assertEqual(restored.programme.count(), 1)
        self.assertEqual(restored.revisions.count(), 2)
        self.assertNotIn(
            str(pk), self._restore_deleted('libretto.Evenement'))

    def testRestoreDeletedBringsBackAMultiTableChild(self):
        audio = Audio.objects.create(
            type=self.objets[Source].type, titre='Audio test', etat=self.etat)
        # Reload: the default of `date_publication` is a datetime until then.
        audio = Audio.objects.get(pk=audio.pk)
        audio.save_revision(clean=False)
        pk = audio.pk
        audio.delete()
        self.assertTrue(Revision.objects.filter(object_id=str(pk)).exists())

        self.assertIn(str(pk), self._restore_deleted('libretto.Audio'))
        self._restore_deleted('libretto.Audio', str(pk))

        self.assertEqual(Audio.objects.get(pk=pk).titre, 'Audio test')
        self.assertEqual(Source.objects.get(pk=pk).titre, 'Audio test')

    def testRestoreDeletedLogsTheGivenUser(self):
        ensemble = self.objets[Ensemble]
        ensemble.save_revision()
        pk = ensemble.pk
        ensemble.delete()
        with self.assertRaises(CommandError):
            self._restore_deleted('libretto.Ensemble', str(pk), user='nobody')
        self.assertFalse(Ensemble.objects.filter(pk=pk).exists())
        self._restore_deleted('libretto.Ensemble', str(pk), user='super')
        entry = ModelLogEntry.objects.filter(object_id=str(pk)).latest('pk')
        self.assertEqual(entry.action, 'wagtail.revert')
        self.assertEqual(entry.user, self.super)

    def testRestoreDeletedDryRunSavesNothing(self):
        ensemble = self.objets[Ensemble]
        ensemble.save_revision()
        pk = ensemble.pk
        ensemble.delete()
        self._restore_deleted('libretto.Ensemble', str(pk), dry_run=True)
        self.assertFalse(Ensemble.objects.filter(pk=pk).exists())

    def testRestoreDeletedRefusesAnExistingObject(self):
        ensemble = self.objets[Ensemble]
        ensemble.save_revision()
        with self.assertRaises(CommandError):
            self._restore_deleted('libretto.Ensemble', str(ensemble.pk))

    def testSerializersExcludeTheLatestRevision(self):
        # These serializers list their fields with `exclude`, so any new model
        # field leaks. Their endpoints cannot be called: they reverse Django
        # admin URLs, and these models have no Django admin page.
        for serializer in (SourceSerializer, EvenementSerializer,
                           PartieSerializer, ProfessionSerializer):
            with self.subTest(serializer.__name__):
                self.assertNotIn('latest_revision', serializer().fields)
