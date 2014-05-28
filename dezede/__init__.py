# coding: utf-8

from __future__ import unicode_literals
from .celery import app as celery_app


__version__ = 2, 0, 1
get_version = lambda: '.'.join(str(i) for i in __version__)
__verbose_name__ = 'Dezède'
