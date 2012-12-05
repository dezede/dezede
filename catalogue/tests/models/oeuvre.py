# coding: utf-8

from __future__ import unicode_literals
from django.utils.unittest import TestCase
from ...models import *
from .utils import new


class OeuvreTestCase(TestCase):
    def setUp(self):
        # Carmen
        opera = new(GenreDOeuvre, nom='opéra')
        self.carmen = new(Oeuvre, titre='Carmen', genre=opera)
        # Symphonie n° 5
        symphonie = new(GenreDOeuvre, nom='symphonie')
        numero = new(TypeDeCaracteristiqueDOeuvre, nom='numéro',
                     classement=1.0)
        n_5 = new(CaracteristiqueDOeuvre, valeur='n°\u00A05', type=numero)
        opus = new(TypeDeCaracteristiqueDOeuvre, nom='opus', classement=2.0)
        op_107 = new(CaracteristiqueDOeuvre, valeur='op.\u00A0107', type=opus)
        self.symphonie = new(Oeuvre, genre=symphonie)
        self.symphonie.caracteristiques.add(n_5, op_107)
        # Tartufe
        comedie = new(GenreDOeuvre, nom='comédie')
        decoupage = new(TypeDeCaracteristiqueDOeuvre, nom='découpage',
                        classement=1.0)
        cinq_actes_vers = new(CaracteristiqueDOeuvre, type=decoupage,
                              valeur='en cinq actes et en vers')
        self.tartuffe = new(Oeuvre,
                            prefixe_titre='Le ', titre='Tartuffe',
                            coordination=', ou ',
                            prefixe_titre_secondaire="l'",
                            titre_secondaire='Imposteur',
                            genre=comedie)
        self.tartuffe.caracteristiques.add(cinq_actes_vers)

    def testComputedNames(self):
        self.assertEqual(unicode(self.carmen), 'Carmen')
        self.assertEqual(unicode(self.symphonie), 'Symphonie n°\u00A05')
        self.assertEqual(unicode(self.tartuffe),
                         'Le Tartuffe, ou l’Imposteur')

    def testHTMLRenders(self):
        # Carmen
        carmen_url = self.carmen.get_absolute_url()
        self.assertEqual(self.carmen.titre_html(),
                         '<a href="%(url)s"><cite>Carmen</cite></a>'
                         % {'url': carmen_url})
        self.assertEqual(self.carmen.description_html(),
                         '<span title="Genre">Opéra</span>')
        self.assertEqual(self.carmen.html(),
                         '<a href="%(url)s"><cite>Carmen</cite></a>, '
                         '<span title="Genre">opéra</span>'
                         % {'url': carmen_url})
        # Symphonie n° 5
        symphonie_url = self.symphonie.get_absolute_url()
        symphonie_titre_html = '<a href="%(url)s"><cite><span title="Genre">'\
                            'Symphonie</span> <span title="Numéro">n°\u00A05'\
                            '</span></cite></a>' % {'url': symphonie_url}
        self.assertEqual(self.symphonie.titre_html(), symphonie_titre_html)
        symphonie_description_html = '<span title="Opus">op.\u00A0107</span>'
        self.assertEqual(self.symphonie.description_html(),
                         symphonie_description_html)
        self.assertEqual(self.symphonie.html(),
                         '%s,&#32;%s' % (symphonie_titre_html,
                                         symphonie_description_html))
        # Tartufe
        tartuffe_url = self.tartuffe.get_absolute_url()
        self.assertEqual(self.tartuffe.titre_html(),
                         '<a href="%(url)s"><cite>Le Tartuffe, ou '
                         'l’Imposteur</cite></a>'
                         % {'url': tartuffe_url})
        self.assertEqual(self.tartuffe.description_html(),
                         '<span title="Genre">Comédie</span>&#32;'
                         '<span title="Découpage">'
                         'en cinq actes et en vers</span>')
