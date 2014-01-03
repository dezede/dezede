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

EMAIL_HOST = 'mail.gandi.net'
EMAIL_HOST_USER = 'noreply@dezede.org'
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'noreply@dezede.org'
SERVER_EMAIL = 'noreply@dezede.org'

COMPRESS_ENABLED = True
