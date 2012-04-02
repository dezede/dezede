# coding: utf-8
from django.utils.unittest import TestCase
from django.test.simple import DjangoTestSuiteRunner
from doctest import DocTestSuite
from musicologie.catalogue.models import *
from musicologie.settings import LANGUAGE_CODE
from musicologie.catalogue import functions
from datetime import date
from django.utils.translation import activate

def new(model, **kwargs):
    obj, created = model.objects.get_or_create(**kwargs)
    if created:
        obj.save()
    return obj

class SaisonTestCase(TestCase):
    def setUp(self):
        theatre = new(NatureDeLieu, nom=u'théâtre')
        ville = new(NatureDeLieu, nom='ville')
        rouen = new(Lieu, nom='Rouen', nature=ville)
        theatre_des_arts = new(Lieu,
            nom=u'Théâtre des Arts', nature=theatre, parent=rouen)
        self.saison = new(Saison,
            lieu=theatre_des_arts, debut=date(2011, 9, 1),
            fin=date(2012, 8, 31))
    def testComputedNames(self):
        self.assertEqual(self.saison.__unicode__(),
                    u'Rouen, Théâtre des Arts, 2011–2012')

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
        self.assertEqual(self.moliere.__unicode__(), u'Molière')
        moliere_url = self.moliere.get_absolute_url()
        self.assertEqual(self.moliere.nom_complet(tags=False),
                         u'Jean-Baptiste Poquelin, dit Molière')
        self.assertEqual(self.piaf.__unicode__(),
                         u'Gassion (É.), dite La Môme Piaf')
        self.assertEqual(self.piaf.nom_complet(tags=False),
                         u'Édith Giovanna Gassion, dite La Môme Piaf')
    def testHTMLRenders(self):
        moliere_url = self.moliere.get_absolute_url()
        self.assertEqual(self.moliere.html(),
                         u'''<a href="%(url)s">'''
                         u'''<span class="sc">Molière</span></a>'''
                           % {'url': moliere_url})
        self.assertEqual(self.moliere.nom_complet(),
                         u'''<a href="%(url)s">Jean-Baptiste '''
                         u'''<span class="sc">Poquelin</span>, '''
                         u'''dit Molière</a>'''
                           % {'url': moliere_url})
        piaf_url = self.piaf.get_absolute_url()
        self.assertEqual(self.piaf.html(),
                         u'''<a href="%(url)s">'''
                         u'''<span class="sc">Gassion</span> (É.), '''
                         u'''dite La Môme Piaf</a>'''
                           % {'url': piaf_url})
        self.assertEqual(self.piaf.nom_complet(),
                         u'''<a href="%(url)s">Édith Giovanna '''
                         u'''<span class="sc">Gassion</span>, '''
                         u'''dite La Môme Piaf</a>'''
                           % {'url': piaf_url})

class OeuvreTestCase(TestCase):
    def setUp(self):
        opera = new(GenreDOeuvre, nom=u'opéra')
        self.carmen = new(Oeuvre, titre=u'Carmen', genre=opera)
        symphonie = new(GenreDOeuvre, nom=u'symphonie')
        numero = new(TypeDeCaracteristiqueDOeuvre, nom=u'numéro', classement=1.0)
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
            prefixe_titre='Le ', titre='Tartuffe', coordination=', ou ',
            prefixe_titre_secondaire="l'", titre_secondaire='Imposteur',
            genre=comedie)
        self.tartuffe.caracteristiques.add(cinq_actes_vers)
    def testComputedNames(self):
        self.assertEqual(self.carmen.__unicode__(), u'Carmen')
        self.assertEqual(self.symphonie.__unicode__(), u'Symphonie n°\u00A05')
        self.assertEqual(self.tartuffe.__unicode__(), u'Le Tartuffe, ou l’Imposteur')
    def testHTMLRenders(self):
        carmen_url = self.carmen.get_absolute_url()
        self.assertEqual(self.carmen.titre_html(),
                         u'''<a href="%(url)s"><cite>Carmen</cite></a>'''
                             % {'url': carmen_url})
        self.assertEqual(self.carmen.description_html(),
                         u'''<span title="genre">Opéra</span>''')
        self.assertEqual(self.carmen.html(),
                         u'''<a href="%(url)s"><cite>Carmen</cite></a>, '''
                         u'''<span title="genre">opéra</span>'''
                             % {'url': carmen_url})
        symphonie_url = self.symphonie.get_absolute_url()
        self.assertEqual(self.symphonie.titre_html(),
                         u'''<a href="%(url)s"><cite><span title="genre">'''
                         u'''Symphonie</span> <span title="numéro">n°\u00A05'''
                         u'''</span></cite></a>'''
                             % {'url': symphonie_url})
        self.assertEqual(self.symphonie.description_html(),
                         u'''<span title="opus">op.\u00A0107</span>''')
        self.assertEqual(self.symphonie.html(),
                         u'''<a href="%(url)s"><cite><span title="genre">'''
                         u'''Symphonie</span> <span title="numéro">n°\u00A05'''
                         u'''</span></cite></a>,&#32;<span title="opus">'''
                         u'''op.\u00A0107</span>'''
                            % {'url': symphonie_url})
        tartuffe_url = self.tartuffe.get_absolute_url()
        self.assertEqual(self.tartuffe.titre_html(),
                         u'''<a href="%(url)s"><cite>Le Tartuffe, ou '''
                         u'''l’Imposteur</cite></a>'''
                             % {'url': tartuffe_url})
        self.assertEqual(self.tartuffe.description_html(),
                         u'''<span title="genre">Comédie</span>&#32;'''
                         u'''<span title="découpage">'''
                         u'''en cinq actes et en vers</span>''')

class SourceTestCase(TestCase):
    def setUp(self):
        type_de_source = new(TypeDeSource, nom='compte rendu',
                                           nom_pluriel='comptes rendus')
        self.journal = new(Source, nom='Journal de Rouen',
                                   date=date(1828, 1, 15),
                                   type=type_de_source)
    def testComputedNames(self):
        self.assertEqual(self.journal.__unicode__(),
                         'Journal de Rouen du mardi 15 janvier 1828')

class SuiteRunner(DjangoTestSuiteRunner):
    def __init__(self, *args, **kwargs):
        self.verbosity = 1
        self.interactive = False
        self.failfast = False
    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        test_labels = (
            'catalogue.SaisonTestCase',
            'catalogue.IndividuTestCase',
            'catalogue.OeuvreTestCase',
            'catalogue.SourceTestCase',
        )
        return super(SuiteRunner, self).build_suite(test_labels, extra_tests, **kwargs)
    def run_suite(self, suite, **kwargs):
        activate(LANGUAGE_CODE)
        suite.addTest(DocTestSuite(functions))
        return super(SuiteRunner, self).run_suite(suite, **kwargs)

