from datetime import date
from django.utils.encoding import smart_text
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
        self.assertEqual(smart_text(self.journal),
                         'Journal de Rouen, mardi 15 janvier 1828')
