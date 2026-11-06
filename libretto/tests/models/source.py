from datetime import date
from django.contrib.auth import get_user_model
from ...models import *
from .utils import new, CommonTestCase


class SourceTestCase(CommonTestCase):
    model = Source

    def setUp(self):
        type_de_source = new(TypeDeSource, nom='compte rendu',
                             nom_pluriel='comptes rendus')
        self.journal = new(Source, titre='Journal de Rouen',
                           date=date(1828, 1, 15),
                           type=type_de_source)

    def testComputedNames(self):
        self.assertEqual(str(self.journal),
                         'Journal de Rouen, mardi 15 janvier 1828')

    def testPageWithPresentationRenders(self):
        # The presentation tab reuses the dossier templates, which ask for
        # contributors.
        editeur = get_user_model().objects.create_user('editeur', 'e@x.fr')
        self.journal.etat = Etat.objects.create(nom='test public',
                                                public=True)
        self.journal.presentation = 'Texte de présentation'
        self.journal.save()
        self.journal.editeurs_scientifiques.add(editeur)
        response = self.client.get(self.journal.get_absolute_url())
        self.assertContains(response, 'Texte de présentation')
