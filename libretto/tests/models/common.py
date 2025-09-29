from ...models import *
from .utils import new, CommonTestCase


class EtatTestCase(CommonTestCase):
    model = Etat

    def setUp(self):
        self.brouillon = new(Etat, nom='brouillon', public=False)
        self.nouveau = new(Etat, nom='nouveau', nom_pluriel='nouveaux')

    def testComputedNames(self):
        self.assertEqual(str(self.brouillon), 'brouillon')
        self.assertEqual(self.brouillon.pluriel(),   'brouillons')
        self.assertEqual(str(self.nouveau), 'nouveau')
        self.assertEqual(self.nouveau.pluriel(),   'nouveaux')
