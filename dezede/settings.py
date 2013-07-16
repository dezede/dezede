# coding: utf-8

import os
from os import environ
import re


ugettext = lambda s: s


# Permet l'utilisation de pypy.
try:
    import psycopg2
except ImportError:
    # Fall back to psycopg2-ctypes
    from psycopg2cffi import compat
    compat.register()


DEBUG = False
TEMPLATE_DEBUG = DEBUG

SITE_ROOT = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
SITE_URL = '/'

ADMINS = (
    ('Bertrand Bordage', 'bordage.bertrand@gmail.com'),
)
MANAGERS = ADMINS

SEND_BROKEN_LINK_EMAILS = True
IGNORABLE_404_URLS = (
    re.compile(r'^/favicon\.ico/?$'),
)

MAINTENANCE_MODE = False
MAINTENANCE_IGNORE_URLS = (
    r'^(?!/admin/).*$',
)

DATABASES = {
    'postgresql': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dezede',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
            'autocommit': True,
        },
    },
    # 'importation': {
    #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #     'NAME': 'dezede_importation',
    #     'USER': '',
    #     'PASSWORD': '',
    #     'HOST': '',
    #     'PORT': '',
    #     'OPTIONS': {
    #         'autocommit': True,
    #     },
    # },
}

default_database = environ.get('DJANGO_DATABASE', 'postgresql')
DATABASES['default'] = DATABASES[default_database]
del DATABASES[default_database]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr'

LANGUAGES = (
    ('fr', ugettext(u'Français')),
    ('en', ugettext('English')),
    ('de', ugettext('Deutsch')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = SITE_URL + 'media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'replace_this_with_some_random_string'

WSGI_APPLICATION = 'dezede.wsgi.application'

INTERNAL_IPS = ('127.0.0.1',)
ALLOWED_HOSTS = ('dezede.org',)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
        # 'django.template.loaders.eggs.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
    'johnny.middleware.LocalStoreClearMiddleware',
    'johnny.middleware.QueryCacheMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'dezede.middlewares.MaintenanceModeMiddleware',
)

ROOT_URLCONF = 'dezede.urls'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'dezede/templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)


FLATPAGES_TEMPLATE_DIR = 'dezede/templates/flatpages'


STATIC_ROOT = os.path.join(SITE_ROOT, 'static/')
STATIC_URL = SITE_URL + 'static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, 'dezede/static'),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'dezede',
    'haystack',
    'libretto',
    'dossiers',
    'typography',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'polymorphic_tree',
    'polymorphic',
    'mptt',
    'endless_pagination',
    'django_tables2',
    'tinymce',
    'flatpages_tinymce',
    'grappelli.dashboard',
    'grappelli',
    'registration',
    'accounts',
    'rest_framework',
    'crispy_forms',
    'ajax_select',
    'filebrowser',
    'reversion',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'compressor',
    'sekizai',
    'django_extensions',
    'south',
    'django_nose',
    'debug_toolbar',
    'template_timings_panel',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'sekizai.context_processors.sekizai',
    'dezede.context_processors.site',
)

LOCALE_PATHS = (
    'locale',
)

TEST_RUNNER = b'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = ['--with-doctest']

DATE_FORMAT = 'l j F Y'

TIME_FORMAT = 'H:i'

GRAPPELLI_INDEX_DASHBOARD = 'dezede.dashboard.CustomIndexDashboard'
GRAPPELLI_ADMIN_TITLE = u'<a href="/evenements/">Dezède</a>'

ACCOUNT_ACTIVATION_DAYS = 7
AUTH_USER_MODEL = 'accounts.HierarchicUser'
LOGIN_REDIRECT_URL = '/'

TINYMCE_FILEBROWSER = True
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'plugins': 'contextmenu,fullscreen,inlinepopups,nonbreaking,paste,preview,searchreplace,table,smallcaps',
    'theme_advanced_buttons1': 'fullscreen,preview,code,|,selectall,cut,copy,paste,pasteword,|,undo,redo,|,link,unlink,|,charmap,nonbreaking,|,search',
    'theme_advanced_buttons2': 'removeformat,formatselect,|,smallcaps,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justify,|,bullist,numlist,outdent,indent,|,sub,sup',
    'theme_advanced_buttons3': 'tablecontrols',
    'theme_advanced_toolbar_location': 'top',
    'theme_advanced_toolbar_align': 'center',
    'theme_advanced_statusbar_location': 'bottom',
    'width': '650',
    'height': '350',
    'theme_advanced_resizing': 'true',
    'theme_advanced_resizing_max_width': '1024',

    'content_css': STATIC_URL + 'css/styles.css',
}

FILEBROWSER_VERSIONS = {
    'avatar': {'verbose_name': ugettext('Avatar'),
               'width': 150, 'height': 150, 'opts': ''},
    'thumbnail': {'verbose_name': ugettext('Standard thumbnail'),
                  'width': 60, 'height': 60, 'opts': ''}
}
FILEBROWSER_ADMIN_THUMBNAIL = 'thumbnail'
FILEBROWSER_ADMIN_VERSIONS = ['avatar']
FILEBROWSER_MAX_UPLOAD_SIZE = 50 * (1024 ** 2)  # octets

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:15031/solr',
        'INCLUDE_SPELLING': True,
        'BATCH_SIZE': 100,
    },
}
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10
HAYSTACK_CUSTOM_HIGHLIGHTER = 'dezede.highlighting.CustomHighlighter'

CACHES = {
    'default': {
        'BACKEND': 'johnny.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': '2Z',
        'JOHNNY_CACHE': True,
    }
}
JOHNNY_MIDDLEWARE_KEY_PREFIX = '2Z'
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_SECONDS = 24 * 60 * 60
CACHE_MIDDLEWARE_KEY_PREFIX = '2Z'

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    # 'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    # 'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    # 'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    # 'debug_toolbar.panels.logger.LoggingPanel',
    # 'debug_toolbar.panels.profiling.ProfilingDebugPanel',
    'template_timings_panel.panels.TemplateTimings.TemplateTimings',
)

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.webfaction.com'
EMAIL_HOST_USER = 'dezede'
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'noreply@dezede.org'
SERVER_EMAIL = 'noreply@dezede.org'

CRISPY_TEMPLATE_PACK = 'bootstrap'

COMPRESS_OUTPUT_DIR = 'assets'

AJAX_LOOKUP_CHANNELS = {
    'lieu': ('libretto.lookups', 'LieuLookup'),
    'individu': ('libretto.lookups', 'IndividuLookup'),
    'oeuvre': ('libretto.lookups', 'OeuvreLookup'),
    'oeuvre__prefixe_titre': ('libretto.lookups', 'OeuvrePrefixeTitreLookup'),
    'oeuvre__coordination': ('libretto.lookups', 'OeuvreCoordinationLookup'),
    'oeuvre__prefixe_titre_secondaire': ('libretto.lookups',
                                         'OeuvrePrefixeTitreSecondaireLookup'),
    'elementdeprogramme__autre': ('libretto.lookups',
                                  'ElementDeProgrammeAutreLookup'),
    'source__nom': ('libretto.lookups', 'SourceNomLookup'),
}
AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = 'inline'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.JSONPRenderer',
        'rest_framework.renderers.YAMLRenderer',
        'rest_framework.renderers.XMLRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': ['rest_framework.filters.DjangoFilterBackend'],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser'
    ],
    'PAGINATE_BY': 10,
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
