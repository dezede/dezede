# coding: utf-8

from __future__ import unicode_literals
import os
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_text
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
        self.assertEqual(smart_text(programme[0]),
                         '« Avez-vous été bien sages les enfants ? »')
        self.assertEqual(smart_text(programme[1]),
                         'Le père Fouettard, ou la correction méritée, '
                         'mélodrame [première représentation]')
        self.assertEqual(smart_text(programme[2]),
                         'Distribution de tatanées')
        self.assertEqual(smart_text(programme[3]),
                         'L’arrivée du père Noël, ou Le Saint Nicolas vengeur')
        self.assertEqual(smart_text(programme[4]),
                         'Distribution de pains d’épices')
        self.assertEqual(
            smart_text(programme[5]),
            'Molière [auteur dram.], Le Tartuffe, ou l’Imposteur, '
            'comédie en cinq actes et en vers. — Gassion (É.) '
            'dite La Môme Piaf [chanteuse]')

    def testRendering(self):
        self.assertEqual(smart_text(self.nicolas),
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
