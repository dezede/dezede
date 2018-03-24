# coding: utf-8

from __future__ import unicode_literals


__version__ = 3, 0, 0
get_version = lambda: '.'.join(str(i) for i in __version__)

default_app_config = 'dezede.apps.DezedeConfig'
