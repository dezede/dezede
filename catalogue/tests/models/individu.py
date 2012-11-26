# coding: utf-8

from django.utils.unittest import TestCase
from ...models import *
from .utils import new


class IndividuTestCase(TestCase):
    def setUp(self):
        jb = new(Prenom, prenom='Jean-Baptiste', favori=True, classement=1.0)
        self.moliere = new(Individu, nom='Poquelin', pseudonyme=u'Molière',
                           designation='P')
        self.moliere.prenoms.add(jb)
        edith = new(Prenom, prenom=u'Édith', favori=True, classement=1.0)
        giovanna = new(Prenom, prenom='Giovanna', favori=False, classement=2.0)
        self.piaf = new(Individu, nom='Gassion', pseudonyme=u'La Môme Piaf',
                        designation='S', titre='F')
        self.piaf.prenoms.add(edith, giovanna)

    def testComputedNames(self):
        self.assertEqual(unicode(self.moliere), u'Molière')
        self.assertEqual(self.moliere.nom_complet(tags=False),
                         u'Jean-Baptiste Poquelin, dit Molière')
        self.assertEqual(unicode(self.piaf),
                         u'Gassion (É.), dite La Môme Piaf')
        self.assertEqual(self.piaf.nom_complet(tags=False),
                         u'Édith Giovanna Gassion, dite La Môme Piaf')

    def testHTMLRenders(self):
        moliere_url = self.moliere.get_absolute_url()
        self.assertEqual(self.moliere.html(),
                         u'<a href="%(url)s">'
                         u'<span class="sc">Molière</span></a>'
                         % {'url': moliere_url})
        self.assertEqual(self.moliere.nom_complet(),
                         u'<a href="%(url)s">Jean-Baptiste '
                         u'<span class="sc">Poquelin</span>, '
                         u'dit Molière</a>'
                         % {'url': moliere_url})
        piaf_url = self.piaf.get_absolute_url()
        self.assertEqual(self.piaf.html(),
                         u'<a href="%(url)s">'
                         u'<span class="sc">Gassion</span> '
                         u'(<span title="\xc9dith">\xc9.</span>), '
                         u'dite La Môme Piaf</a>'
                         % {'url': piaf_url})
        self.assertEqual(self.piaf.nom_complet(),
                         u'<a href="%(url)s">Édith Giovanna '
                         u'<span class="sc">Gassion</span>, '
                         u'dite La Môme Piaf</a>'
                         % {'url': piaf_url})
