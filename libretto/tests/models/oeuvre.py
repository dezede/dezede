# coding: utf-8

from __future__ import unicode_literals
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_text
from ...models import *
from .utils import new, log_as_superuser, TransactionTestCase


class OeuvreTestCase(TransactionTestCase):
    model = Oeuvre

    def setUp(self):
        # Invalid
        self.invalid = new(Oeuvre, titre_secondaire='l’essai infructeux')
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
                            prefixe_titre='Le', titre='Tartuffe',
                            coordination='ou',
                            prefixe_titre_secondaire="l'",
                            titre_secondaire='Imposteur',
                            genre=comedie)
        self.tartuffe.caracteristiques.add(cinq_actes_vers)
        # Test client
        log_as_superuser(self)

    def testClean(self, excluded=()):
        with self.assertRaises(ValidationError):
            self.invalid.clean()

        super(OeuvreTestCase, self).testClean(excluded=[self.invalid])

    def testComputedNames(self):
        # Carmen
        self.assertEqual(smart_text(self.carmen), 'Carmen')
        self.assertEqual(self.carmen.calc_pupitres(),
                         'pour deux violons\xa0et\xa0quatre \xe0 huit voix')
        # Sonate
        self.assertEqual(smart_text(self.sonate), 'Sonate pour violon')
        # Symphonie n° 5
        self.assertEqual(smart_text(self.symphonie), 'Symphonie n°\u00A05')
        self.assertEqual(self.symphonie.titre_html(tags=False),
                         'Symphonie n°\u00A05')
        self.assertEqual(self.symphonie.titre_descr_html(tags=False),
                         'Symphonie n°\xa05, op.\xa0107')
        self.assertEqual(self.symphonie.description_html(tags=False),
                         'op.\xa0107')
        # Tartufe
        self.assertEqual(smart_text(self.tartuffe),
                         'Le Tartuffe, ou l’Imposteur')

    def testHTMLRenders(self):
        # Carmen
        carmen_url = self.carmen.get_absolute_url()
        carmen_titre_html = '<a href="%(url)s"><cite>Carmen</cite></a>'\
                            % {'url': carmen_url}
        self.assertEqual(self.carmen.titre_html(), carmen_titre_html)
        self.assertEqual(self.carmen.description_html(),
                         '<span title="Genre">Opéra</span>')
        self.assertEqual(self.carmen.html(),
                         '%s, %s' % (carmen_titre_html,
                                     '<span title="Genre">opéra</span>'))
        # Symphonie n° 5
        symphonie_url = self.symphonie.get_absolute_url()
        symphonie_titre_html = '<a href="%(url)s"><span title="Genre">'\
                            'Symphonie</span> <span title="Numéro">n°\u00A05'\
                            '</span></a>' % {'url': symphonie_url}
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
