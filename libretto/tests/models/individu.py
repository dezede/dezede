from ...models import *
from .utils import new, CommonTestCase


class IndividuTestCase(CommonTestCase):
    model = Oeuvre

    def setUp(self):
        self.moliere = new(Individu, nom='Poquelin', prenoms='Jean-Baptiste',
                           pseudonyme='Molière', designation='P')
        self.piaf = new(Individu, nom='Gassion', prenoms='Édith',
                        prenoms_complets='Édith Giovanna',
                        pseudonyme='La Môme Piaf', designation='S', titre='F')

    def testComputedNames(self):
        with self.assertNumQueries(0):
            self.assertEqual(str(self.moliere), 'Molière')
        with self.assertNumQueries(0):
            self.assertEqual(self.moliere.nom_complet(tags=False),
                             'Jean-Baptiste Poquelin dit\u00A0Molière')
        with self.assertNumQueries(0):
            self.assertEqual(str(self.piaf),
                             'Gassion (É.) dite\u00A0La Môme Piaf')
        with self.assertNumQueries(0):
            self.assertEqual(self.piaf.nom_complet(tags=False),
                             'Édith Giovanna Gassion dite\u00A0La Môme Piaf')

    def testHTMLRenders(self):
        moliere_url = self.moliere.get_absolute_url()
        with self.assertNumQueries(0):
            self.assertHTMLEqual(self.moliere.html(),
                                 '<a href="%(url)s">'
                                 '<span class="sc">Molière</span></a>'
                                 % {'url': moliere_url})
        with self.assertNumQueries(0):
            self.assertHTMLEqual(self.moliere.nom_complet(),
                                 '<a href="%(url)s">Jean-Baptiste '
                                 '<span class="sc">Poquelin</span> '
                                 'dit\u00A0Molière</a>'
                                 % {'url': moliere_url})
        piaf_url = self.piaf.get_absolute_url()
        with self.assertNumQueries(0):
            self.assertHTMLEqual(self.piaf.html(),
                                 '<a href="%(url)s">'
                                 '<span class="sc">Gassion</span> '
                                 '(<span title="\xc9dith">\xc9.</span>) '
                                 'dite\u00A0La Môme Piaf</a>'
                                 % {'url': piaf_url})
        with self.assertNumQueries(0):
            self.assertHTMLEqual(self.piaf.nom_complet(),
                                 '<a href="%(url)s">Édith Giovanna '
                                 '<span class="sc">Gassion</span> '
                                 'dite\u00A0La Môme Piaf</a>'
                                 % {'url': piaf_url})

    def testTemplateRenders(self):
        for individu in Individu.objects.all():
            self.assertURL(individu.get_absolute_url())
