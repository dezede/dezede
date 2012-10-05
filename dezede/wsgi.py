import os
from .solr import start_solr
from django.core.handlers.wsgi import WSGIHandler


os.environ['DJANGO_SETTINGS_MODULE'] = 'dezede.settings'


def start_application():
    start_solr()
    return WSGIHandler()


application = start_application()
