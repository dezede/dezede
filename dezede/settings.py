# Django settings for the dezede project.
# coding: utf-8
import os
ugettext = lambda s: s

DEBUG = False
TEMPLATE_DEBUG = DEBUG

SITE_ROOT = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
SITE_URL = '/'

ADMINS = (
    ('Bertrand Bordage', 'bordage.bertrand@gmail.com'),
)

SEND_BROKEN_LINK_EMAILS = True

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'musicologie',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

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
if DEBUG:
    MEDIA_ROOT = os.path.join(SITE_ROOT, 'media/')
else:
    MEDIA_ROOT = '/var/www' + SITE_URL + 'media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = SITE_URL + 'media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

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
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'dezede.urls'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'dezede/templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

if DEBUG:
    STATIC_ROOT = os.path.join(SITE_ROOT, 'static/')
else:
    STATIC_ROOT = '/var/www' + SITE_URL + 'static/'
STATIC_URL = SITE_URL + 'static/'

STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, 'dezede/static'),
)

ADMIN_MEDIA_PREFIX = STATIC_URL + "grappelli/"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'haystack',
    'catalogue',
    'tinymce',
    'grappelli.dashboard',
    'grappelli',
    'filebrowser',
    'reversion',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django_extensions',
    'rosetta-grappelli',
    'rosetta',
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
)

LOCALE_PATHS = (
    'locale',
)

TEST_RUNNER = 'catalogue.tests.SuiteRunner'

DATE_FORMAT = 'l j F Y'

TIME_FORMAT = 'H:i'

GRAPPELLI_INDEX_DASHBOARD = 'dezede.dashboard.CustomIndexDashboard'

TINYMCE_DEFAULT_CONFIG = {
    'mode' : 'textareas',
    'theme' : 'advanced',
    'plugins' : 'contextmenu,fullscreen,inlinepopups,nonbreaking,paste,preview,searchreplace,table',
    'theme_advanced_buttons1' : 'fullscreen,preview,code,|,selectall,cut,copy,paste,pasteword,|,undo,redo,|,link,unlink,|,charmap,nonbreaking,|,search',
    'theme_advanced_buttons2' : 'removeformat,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justify,|,bullist,numlist,outdent,indent,|,sub,sup',
    'theme_advanced_buttons3' : '',
    'theme_advanced_toolbar_location' : 'top',
    'theme_advanced_toolbar_align' : 'center',
    'theme_advanced_statusbar_location' : 'bottom',
    'width' : '650',
    'height' : '300',
    'theme_advanced_resizing' : 'true',
    'theme_advanced_resizing_max_width' : '650',
}

FILEBROWSER_VERSIONS = {
    'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
}

FILEBROWSER_ADMIN_VERSIONS = []

HAYSTACK_SITECONF = 'dezede.search_sites'
HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(os.path.dirname(__file__), 'whoosh_index')
HAYSTACK_CUSTOM_HIGHLIGHTER = 'catalogue.utils.CustomHighlighter'
HAYSTACK_INCLUDE_SPELLING = True
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10

CACHES = {
    'default' : {
        'BACKEND': 'johnny.backends.memcached.MemcachedCache',
        'LOCATION': ['127.0.0.1:11211'],
        'JOHNNY_CACHE': True,
    }
}
