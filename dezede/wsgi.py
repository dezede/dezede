import os
from django.core.handlers.wsgi import WSGIHandler


os.environ['DJANGO_SETTINGS_MODULE'] = 'dezede.settings'


def start_application():
    return WSGIHandler()


application = start_application()
