import os
from django.urls import reverse
from ...models import *
from .utils import CommonTestCase


PATH = os.path.abspath(os.path.dirname(__file__))


class EvenementTestCase(CommonTestCase):
    model = Evenement
    fixtures = [
        os.path.join(PATH, 'fixtures/accounts.hierarchicuser.json'),
        os.path.join(PATH, 'fixtures/evenement.json'),
    ]

    def setUp(self):
        self.nicolas = Evenement.objects.all()[0]

    def testProgrammeRendering(self):
        programme = self.nicolas.programme.all()
        self.assertEqual(str(programme[0]),
                         '« Avez-vous été bien sages les enfants ? »')
        self.assertEqual(str(programme[1]),
                         'Le père Fouettard, ou la correction méritée, '
                         'mélodrame [première représentation]')
        self.assertEqual(str(programme[2]),
                         'Distribution de tatanées')
        self.assertEqual(str(programme[3]),
                         'L’arrivée du père Noël, ou Le Saint Nicolas vengeur')
        self.assertEqual(str(programme[4]),
                         'Distribution de pains d’épices')
        self.assertEqual(
            str(programme[5]),
            'Molière [auteur dram.], Le Tartuffe, ou l’Imposteur, '
            'comédie en cinq actes et en vers. — Gassion (É.) '
            'dite\u00A0La Môme Piaf [chanteuse]')

    def testRendering(self):
        self.assertEqual(str(self.nicolas),
                         'Jeudi 6 décembre 2012 > '
                         'Rouen, Théâtre des Arts, Saint-Nicolas')

    def testTemplateRenders(self):
        # ListView
        self.assertURL(reverse('evenements'))
        self.assertURL(
            reverse('evenements'),
            {'q': 'Rouen', 'dates_0': 1771, 'dates_1': 2012, 'lieu': '|1|',
             'oeuvre': '||', 'page': 1})
        # DetailView
        for evenement in Evenement.objects.all():
            self.assertURL(evenement.get_absolute_url())
