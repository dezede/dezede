# coding: utf-8

from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_text
from ...models import *
from .utils import new, CommonTestCase


class OeuvreTestCase(CommonTestCase):
    model = Oeuvre

    def setUp(self):
        # Carmen
        opera = new(GenreDOeuvre, nom='opéra')
        violon = new(Partie, nom='violon')
        violons = new(Pupitre, partie=violon, quantite_min=2, quantite_max=2)
        voix = new(Partie, nom='voix', nom_pluriel='voix')
        choeur = new(Pupitre, partie=voix, quantite_min=4, quantite_max=8)
        self.carmen = new(Oeuvre, titre='Carmen', genre=opera)
        self.carmen.pupitres.add(violons, choeur)
        # Sonate
        sonate = new(GenreDOeuvre, nom='sonate')
        violon_solo = new(Pupitre, partie=violon, quantite_max=1)
        self.sonate = new(Oeuvre, genre=sonate)
        self.sonate.pupitres.add(violon_solo)
        # Symphonie n° 5
        symphonie = new(GenreDOeuvre, nom='symphonie')
        self.symphonie = new(Oeuvre, genre=symphonie, numero='5', opus='107')
        # Tartufe
        comedie = new(GenreDOeuvre, nom='comédie')
        self.tartuffe = new(Oeuvre,
                            prefixe_titre='Le', titre='Tartuffe',
                            coordination='ou',
                            prefixe_titre_secondaire="l'",
                            titre_secondaire='Imposteur',
                            genre=comedie, coupe='cinq actes et en vers')

    def testComputedNames(self):
        # Carmen
        with self.assertNumQueries(1):
            self.assertEqual(smart_text(self.carmen), 'Carmen')
        with self.assertNumQueries(1):
            self.assertEqual(
                self.carmen.calc_pupitres(),
                'pour deux violons et\xa0quatre à huit voix')
        # Sonate
        with self.assertNumQueries(2):
            self.assertEqual(smart_text(self.sonate), 'Sonate pour violon')
        # Symphonie n° 5
        with self.assertNumQueries(2):
            self.assertEqual(smart_text(self.symphonie), 'Symphonie n°\u00A05')
        with self.assertNumQueries(2):
            self.assertEqual(self.symphonie.titre_html(tags=False),
                             'Symphonie n°\u00A05')
        with self.assertNumQueries(2):
            self.assertEqual(self.symphonie.titre_descr(),
                             'Symphonie n°\xa05, op.\xa0107')
        with self.assertNumQueries(2):
            self.assertEqual(self.symphonie.description_html(tags=False),
                             'op.\xa0107')
        # Tartufe
        with self.assertNumQueries(1):
            self.assertEqual(smart_text(self.tartuffe),
                             'Le Tartuffe, ou l’Imposteur')

    def testHTMLRenders(self):
        # Carmen
        carmen_url = self.carmen.get_absolute_url()
        carmen_titre_html = '<a href="%(url)s"><cite>Carmen</cite></a>'\
                            % {'url': carmen_url}
        with self.assertNumQueries(1):
            self.assertHTMLEqual(self.carmen.titre_html(), carmen_titre_html)
        with self.assertNumQueries(1):
            self.assertHTMLEqual(self.carmen.description_html(),
                                 '<span title="Genre">Opéra</span>')
        with self.assertNumQueries(2):
            self.assertHTMLEqual(
                self.carmen.html(),
                '%s, %s' % (carmen_titre_html,
                            '<span title="Genre">opéra</span>'))
        # Symphonie n° 5
        symphonie_url = self.symphonie.get_absolute_url()
        symphonie_titre_html = (
            '<a href="%(url)s"><span title="Genre">'
            'Symphonie</span> n°\u00A05</a>') % {'url': symphonie_url}
        with self.assertNumQueries(2):
            self.assertHTMLEqual(self.symphonie.titre_html(),
                                 symphonie_titre_html)
        symphonie_description_html = '<span title="Opus">op.\u00A0107</span>'
        with self.assertNumQueries(2):
            self.assertHTMLEqual(self.symphonie.description_html(),
                                 symphonie_description_html)
        with self.assertNumQueries(3):
            self.assertHTMLEqual(self.symphonie.html(),
                                 '%s,&#32;%s' % (symphonie_titre_html,
                                                 symphonie_description_html))
        # Tartufe
        tartuffe_url = self.tartuffe.get_absolute_url()
        with self.assertNumQueries(1):
            self.assertHTMLEqual(self.tartuffe.titre_html(),
                                 '<a href="%(url)s"><cite>Le Tartuffe, ou '
                                 'l’Imposteur</cite></a>'
                                 % {'url': tartuffe_url})
        with self.assertNumQueries(1):
            self.assertHTMLEqual(self.tartuffe.description_html(),
                                 '<span title="Genre">Comédie</span>&#32;'
                                 '<span title="Coupe">'
                                 'en cinq actes et en vers</span>')
