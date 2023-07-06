from .base import *

TEMPLATES[0]['OPTIONS']['loaders'] = [
   ('django.template.loaders.cached.Loader', [
       'django.template.loaders.filesystem.Loader',
       'django.template.loaders.app_directories.Loader',
   ]),
]
del TEMPLATES[0]['APP_DIRS']

ALLOWED_HOSTS = ('dezede.org',)

EMAIL_HOST = 'mail.gandi.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@dezede.org'
EMAIL_HOST_PASSWORD = 'sJ8qZL6SmHU@49C'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_TIMEOUT = 5

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
