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
    from psycopg2ct import compat
    compat.register()


DEBUG = False
TEMPLATE_DEBUG = DEBUG

SITE_ROOT = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
SITE_URL = '/'

ADMINS = (
    ('Bertrand Bordage', 'bordage.bertrand@gmail.com'),
)

SEND_BROKEN_LINK_EMAILS = True
IGNORABLE_404_URLS = (
    re.compile(r'^/favicon\.ico/?$'),
)

MANAGERS = ADMINS

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
    'importation': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dezede_importation',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'OPTIONS': {
            'autocommit': True,
        },
    },
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
SECRET_KEY = ''

WSGI_APPLICATION = 'dezede.wsgi.application'

INTERNAL_IPS = ('127.0.0.1',)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'johnny.middleware.LocalStoreClearMiddleware',
    'johnny.middleware.QueryCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
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
    'catalogue',
    'dossiers',
    'typography',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'mptt',
    'endless_pagination',
    'django_tables2',
    'tinymce',
    'flatpages_tinymce',
    'grappelli.dashboard',
    'grappelli',
    'registration',
    'profiles',
    'accounts',
    'crispy_forms',
    'ajax_select',
    'filebrowser',
    'reversion',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'compressor',
    'django_nose',
    'sekizai',
    'django_extensions',
    'south',
    'debug_toolbar',
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
AUTH_PROFILE_MODULE = 'accounts.StudentProfile'
LOGIN_REDIRECT_URL = '/profils/'

TINYMCE_DEFAULT_CONFIG = {
    'mode': 'textareas',
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
TINYMCE_FILEBROWSER = False

FILEBROWSER_VERSIONS = {
    'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
}

FILEBROWSER_ADMIN_VERSIONS = []

HAYSTACK_SITECONF = 'dezede.search_sites'
HAYSTACK_SEARCH_ENGINE = 'solr'
HAYSTACK_SOLR_URL = 'http://127.0.0.1:15031/solr'
HAYSTACK_INCLUDE_SPELLING = True
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10
HAYSTACK_CUSTOM_HIGHLIGHTER = 'dezede.highlighting.CustomHighlighter'

CACHES = {
    'default': {
        'BACKEND': 'johnny.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'JOHNNY_CACHE': True,
    }
}
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
CACHE_MIDDLEWARE_SECONDS = 24 * 60 * 60

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

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
    'lieu': ('catalogue.lookups', 'LieuLookup'),
    'oeuvre': ('catalogue.lookups', 'OeuvreLookup'),
    'oeuvre__prefixe_titre': ('catalogue.lookups', 'OeuvrePrefixeTitreLookup'),
    'oeuvre__coordination': ('catalogue.lookups', 'OeuvreCoordinationLookup'),
    'oeuvre__prefixe_titre_secondaire': ('catalogue.lookups',
                                         'OeuvrePrefixeTitreSecondaireLookup'),
    'source__nom': ('catalogue.lookups', 'SourceNomLookup'),
}
AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = 'inline'
