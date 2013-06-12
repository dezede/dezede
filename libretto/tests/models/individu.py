# coding: utf-8

from __future__ import unicode_literals
from django.utils.encoding import smart_text
from ...models import *
from .utils import new, log_as_superuser, TransactionTestCase


class IndividuTestCase(TransactionTestCase):
    def setUp(self):
        jb = new(Prenom, prenom='Jean-Baptiste', favori=True, classement=1.0)
        self.moliere = new(Individu, nom='Poquelin', pseudonyme='Molière',
                           designation='P')
        self.moliere.prenoms.add(jb)
        edith = new(Prenom, prenom='Édith', favori=True, classement=1.0)
        giovanna = new(Prenom, prenom='Giovanna', favori=False, classement=2.0)
        self.piaf = new(Individu, nom='Gassion', pseudonyme='La Môme Piaf',
                        designation='S', titre='F')
        self.piaf.prenoms.add(edith, giovanna)
        # Test client
        log_as_superuser(self)

    def testComputedNames(self):
        self.assertEqual(smart_text(self.moliere), 'Molière')
        self.assertEqual(self.moliere.nom_complet(tags=False),
                         'Jean-Baptiste Poquelin, dit Molière')
        self.assertEqual(smart_text(self.piaf),
                         'Gassion (É.), dite La Môme Piaf')
        self.assertEqual(self.piaf.nom_complet(tags=False),
                         'Édith Giovanna Gassion, dite La Môme Piaf')

    def testHTMLRenders(self):
        moliere_url = self.moliere.get_absolute_url()
        self.assertEqual(self.moliere.html(),
                         '<a href="%(url)s">'
                         '<span class="sc">Molière</span></a>'
                         % {'url': moliere_url})
        self.assertEqual(self.moliere.nom_complet(),
                         '<a href="%(url)s">Jean-Baptiste '
                         '<span class="sc">Poquelin</span>, '
                         'dit Molière</a>'
                         % {'url': moliere_url})
        piaf_url = self.piaf.get_absolute_url()
        self.assertEqual(self.piaf.html(),
                         '<a href="%(url)s">'
                         '<span class="sc">Gassion</span> '
                         '(<span title="\xc9dith">\xc9.</span>), '
                         'dite La Môme Piaf</a>'
                         % {'url': piaf_url})
        self.assertEqual(self.piaf.nom_complet(),
                         '<a href="%(url)s">Édith Giovanna '
                         '<span class="sc">Gassion</span>, '
                         'dite La Môme Piaf</a>'
                         % {'url': piaf_url})

    def testTemplateRenders(self):
        for individu in [self.moliere, self.piaf]:
            response = self.client.get(individu.get_absolute_url())
            self.assertEqual(response.status_code, 200)
