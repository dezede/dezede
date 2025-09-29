from datetime import date
from ...models import *
from .utils import new, CommonTestCase


class LieuTestCase(CommonTestCase):
    model = Lieu

    def setUp(self):
        theatre = new(NatureDeLieu, nom='théâtre')
        ville = new(NatureDeLieu, nom='ville')
        self.rouen = Lieu.objects.create(nom='Rouen', nature=ville)
        self.theatre_des_arts = Lieu.objects.create(
            nom='Théâtre des Arts', parent=self.rouen,
            nature=theatre, is_institution=True)

    def testComputedNames(self):
        self.assertEqual(str(self.rouen), 'Rouen')
        self.assertEqual(str(self.theatre_des_arts),
                         'Rouen, Théâtre des Arts')


class SaisonTestCase(CommonTestCase):
    model = Saison

    def setUp(self):
        theatre = new(NatureDeLieu, nom='théâtre')
        ville = new(NatureDeLieu, nom='ville')
        rouen = new(Lieu, nom='Rouen', nature=ville)
        theatre_des_arts = new(
            Lieu, nom='Théâtre des Arts', nature=theatre, parent=rouen)
        self.saison = new(
            Saison, lieu=theatre_des_arts, debut=date(2011, 9, 1),
            fin=date(2012, 8, 31))

    def testComputedNames(self):
        self.assertEqual(str(self.saison),
                         'Rouen, Théâtre des Arts, 2011–2012')
