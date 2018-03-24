# coding: utf-8

from .base import *

TEMPLATES[0]['OPTIONS']['loaders'] = [
   ('django.template.loaders.cached.Loader', [
       'django.template.loaders.filesystem.Loader',
       'django.template.loaders.app_directories.Loader',
   ]),
]
del TEMPLATES[0]['APP_DIRS']

ALLOWED_HOSTS = ('dezede.org',)

EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = 'noreply@dezede.org'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
