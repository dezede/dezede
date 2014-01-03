# coding: utf-8

from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

INTERNAL_IPS = ('127.0.0.1',)

INSTALLED_APPS += (
    'django_extensions',
    'debug_toolbar',
    'template_timings_panel',
    # Réactiver quand il sera devenu compatible debug-toolbar 1.0
    # 'haystack_panel',
    'django_nose',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
    'template_timings_panel.panels.TemplateTimings.TemplateTimings',
    # Réactiver quand il sera devenu compatible debug-toolbar 1.0
    # 'haystack_panel.panel.HaystackDebugPanel',
)

TEST_RUNNER = b'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--with-doctest']
