# coding: utf-8

from .base import *

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        # 'django.template.loaders.eggs.Loader',
    )),
)

ALLOWED_HOSTS = ('dezede.org',)

EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = 'noreply@dezede.org'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
