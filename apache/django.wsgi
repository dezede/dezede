import os, sys

p = os.path.abspath(__file__)
for i in range(2):
    p = os.path.split(p)[0]

if p not in sys.path:
    sys.path.append(p)

os.environ['DJANGO_SETTINGS_MODULE'] = 'dezede.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
