from .base import *

TEMPLATES[0]['OPTIONS']['loaders'] = [
   ('django.template.loaders.cached.Loader', [
       'django.template.loaders.filesystem.Loader',
       'django.template.loaders.app_directories.Loader',
   ]),
]
del TEMPLATES[0]['APP_DIRS']

ALLOWED_HOSTS = ('dezede.org',)

EMAIL_HOST = 'ssl0.ovh.net'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'noreply@dezede.org'
EMAIL_HOST_PASSWORD = 'pDVE8UyzQkf$dgf'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_TIMEOUT = 5

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
