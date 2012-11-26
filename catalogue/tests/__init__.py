# coding: utf-8

from django.test.simple import DjangoTestSuiteRunner
from doctest import DocTestSuite
from django.conf import settings
from django.utils.translation import activate
from ..models import functions
from .models import *


class SuiteRunner(DjangoTestSuiteRunner):
    def __init__(self, *args, **kwargs):
        self.verbosity = 1
        self.interactive = False
        self.failfast = False

    def run_suite(self, suite, **kwargs):
        activate(settings.LANGUAGE_CODE)
        suite.addTest(DocTestSuite(functions))
        return super(SuiteRunner, self).run_suite(suite, **kwargs)
