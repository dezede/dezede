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
    obj = model(**kwargs)
    obj.save()
    return obj

class IndividuTestCase(TestCase):
    def setUp(self):
        jb = new(Prenom, prenom='Jean-Baptiste', favori=True, classement=1.0)
        self.moliere = new(Individu, nom='Poquelin', pseudonyme=u'Molière',
            designation='P')
        self.moliere.prenoms.add(jb)
    def testComputedName(self):
        self.assertEqual(self.moliere.__unicode__(), u'Molière')
        moliere_url = self.moliere.get_absolute_url()
        self.assertEqual(self.moliere.html(),
                         u'<a href="%(url)s"><span class="sc">Molière</span></a>'
                           % {'url': moliere_url})

class OeuvreTestCase(TestCase):
    def setUp(self):
        opera = new(GenreDOeuvre, nom=u'opéra')
        self.carmen = new(Oeuvre, titre='Carmen', genre=opera)
        symphonie = new(GenreDOeuvre, nom='symphonie')
        numero = new(TypeDeCaracteristiqueDOeuvre, nom='numéro')
        n_5 = new(CaracteristiqueDOeuvre, valeur=u'n°\u00A05', type=numero,
            classement=1.0)
        opus = new(TypeDeCaracteristiqueDOeuvre, nom='opus')
        op_107 = new(CaracteristiqueDOeuvre, valeur=u'op.\u00A0107', type=opus,
            classement=2.0)
        self.symphonie = new(Oeuvre, genre=symphonie)
        self.symphonie.caracteristiques.add(n_5, op_107)
    def testComputedName(self):
        activate(LANGUAGE_CODE)
        self.assertEqual(self.carmen.__unicode__(), 'Carmen')
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
        self.assertEqual(self.symphonie.__unicode__(), u'Symphonie n°\u00A05')
        symphonie_url = self.symphonie.get_absolute_url()
        self.assertEqual(self.symphonie.html(),
                         u'''<a href="%(url)s"><cite><span title="genre">'''
                         u'''Symphonie</span> <span title="numéro">n°\u00A05'''
                         u'''</span></cite></a>,&#32;<span title="opus">'''
                         u'''op.\u00A0107</span>'''
                            % {'url': symphonie_url})

class SourceTestCase(TestCase):
    def setUp(self):
        type_de_source = new(TypeDeSource, nom='compte rendu',
                                           nom_pluriel='comptes rendus')
        self.journal = new(Source, nom='Journal de Rouen',
                                   date=date(1828, 1, 15),
                                   type=type_de_source)
    def testComputedName(self):
        self.assertEqual(self.journal.__unicode__(),
                         'Journal de Rouen du mardi 15 janvier 1828')

FunctionsSuite = DocTestSuite(functions)

class SuiteRunner(DjangoTestSuiteRunner):
    verbosity = 1
    interactive = True
    failfast = True
    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        test_labels = ['catalogue.IndividuTestCase', 'catalogue.OeuvreTestCase',
                       'catalogue.SourceTestCase']
        return super(SuiteRunner, self).build_suite(test_labels, extra_tests, **kwargs)
    def run_suite(self, suite, **kwargs):
        activate(LANGUAGE_CODE)
        suite.addTest(FunctionsSuite)
        return super(SuiteRunner, self).run_suite(suite, **kwargs)

