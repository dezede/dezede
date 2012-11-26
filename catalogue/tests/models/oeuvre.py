# coding: utf-8

from django.utils.unittest import TestCase
from ...models import *
from .utils import new


class OeuvreTestCase(TestCase):
    def setUp(self):
        opera = new(GenreDOeuvre, nom=u'opéra')
        self.carmen = new(Oeuvre, titre=u'Carmen', genre=opera)
        symphonie = new(GenreDOeuvre, nom=u'symphonie')
        numero = new(TypeDeCaracteristiqueDOeuvre, nom=u'numéro',
                     classement=1.0)
        n_5 = new(CaracteristiqueDOeuvre, valeur=u'n°\u00A05', type=numero)
        opus = new(TypeDeCaracteristiqueDOeuvre, nom=u'opus', classement=2.0)
        op_107 = new(CaracteristiqueDOeuvre, valeur=u'op.\u00A0107', type=opus)
        self.symphonie = new(Oeuvre, genre=symphonie)
        self.symphonie.caracteristiques.add(n_5, op_107)
        comedie = new(GenreDOeuvre, nom=u'comédie')
        decoupage = new(TypeDeCaracteristiqueDOeuvre, nom=u'découpage',
                        classement=1.0)
        cinq_actes_vers = new(CaracteristiqueDOeuvre, type=decoupage,
                              valeur=u'en cinq actes et en vers')
        self.tartuffe = new(Oeuvre,
                            prefixe_titre='Le ', titre='Tartuffe',
                            coordination=', ou ',
                            prefixe_titre_secondaire="l'",
                            titre_secondaire='Imposteur',
                            genre=comedie)
        self.tartuffe.caracteristiques.add(cinq_actes_vers)

    def testComputedNames(self):
        self.assertEqual(self.carmen.__unicode__(), u'Carmen')
        self.assertEqual(self.symphonie.__unicode__(), u'Symphonie n°\u00A05')
        self.assertEqual(self.tartuffe.__unicode__(),
                         u'Le Tartuffe, ou l’Imposteur')

    def testHTMLRenders(self):
        carmen_url = self.carmen.get_absolute_url()
        self.assertEqual(self.carmen.titre_html(),
                         u'<a href="%(url)s"><cite>Carmen</cite></a>'
                         % {'url': carmen_url})
        self.assertEqual(self.carmen.description_html(),
                         u'<span title="Genre">Opéra</span>')
        self.assertEqual(self.carmen.html(),
                         u'<a href="%(url)s"><cite>Carmen</cite></a>, '
                         u'<span title="Genre">opéra</span>'
                         % {'url': carmen_url})
        symphonie_url = self.symphonie.get_absolute_url()
        self.assertEqual(self.symphonie.titre_html(),
                         u'<a href="%(url)s"><cite><span title="genre">'
                         u'Symphonie</span> <span title="numéro">n°\u00A05'
                         u'</span></cite></a>'
                         % {'url': symphonie_url})
        self.assertEqual(self.symphonie.description_html(),
                         u'<span title="opus">op.\u00A0107</span>')
        self.assertEqual(self.symphonie.html(),
                         u'<a href="%(url)s"><cite><span title="genre">'
                         u'Symphonie</span> <span title="numéro">n°\u00A05'
                         u'</span></cite></a>,&#32;<span title="opus">'
                         u'op.\u00A0107</span>'
                         % {'url': symphonie_url})
        tartuffe_url = self.tartuffe.get_absolute_url()
        self.assertEqual(self.tartuffe.titre_html(),
                         u'<a href="%(url)s"><cite>Le Tartuffe, ou '
                         u'l’Imposteur</cite></a>'
                         % {'url': tartuffe_url})
        self.assertEqual(self.tartuffe.description_html(),
                         u'<span title="genre">Comédie</span>&#32;'
                         u'<span title="découpage">'
                         u'en cinq actes et en vers</span>')
