# coding: utf-8

import re
from easy_thumbnails.conf import Settings as thumbnail_settings
from unipath import Path

ugettext = lambda s: s


# Allows PyPy to work with Django.
try:
    import psycopg2
except ImportError:
    # Fall back to psycopg2cffi.
    from psycopg2cffi import compat
    compat.register()


SITE_ROOT = Path(__file__).ancestor(3)
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
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'dezede',
        'USER': 'dezede',
        'OPTIONS': {
            'autocommit': True,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Europe/Paris'
LANGUAGES = (
    ('fr', ugettext(u'Français')),
    # ('en', ugettext('English')),
    # ('de', ugettext('Deutsch')),
)
USE_I18N = True
USE_L10N = True
USE_TZ = True

SITE_ID = 1

MEDIA_ROOT = SITE_ROOT.child('media')
MEDIA_URL = SITE_URL + 'media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'replace_this_with_some_random_string'

WSGI_APPLICATION = 'dezede.wsgi.application'

ROOT_URLCONF = 'dezede.urls'


STATIC_ROOT = SITE_ROOT.child('static')
STATIC_URL = SITE_URL + 'static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
STATICFILES_DIRS = (
    SITE_ROOT.child('dezede', 'static'),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.gis',
    'accounts',
    'dezede',
    'haystack',
    'django_rq',
    'libretto',
    'dossiers',
    'polymorphic_tree',
    'polymorphic',
    'mptt',
    'endless_pagination',
    'eztables',
    'tinymce',
    'grappelli.dashboard',
    'grappelli',
    'registration',
    'rest_framework',
    'crispy_forms',
    'ajax_select',
    'filebrowser',
    'easy_thumbnails',
    'image_cropping',
    'reversion',
    'django.contrib.admin',
    'compressor',
    'sekizai',
    'south',
)

MIDDLEWARE_CLASSES = (
    'johnny.middleware.LocalStoreClearMiddleware',
    'johnny.middleware.QueryCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'dezede.middlewares.MaintenanceModeMiddleware',
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

DATE_FORMAT = 'l j F Y'

TIME_FORMAT = 'H:i'

GRAPPELLI_INDEX_DASHBOARD = 'dezede.dashboard.CustomIndexDashboard'
GRAPPELLI_ADMIN_TITLE = u'<a href="/">Dezède</a>'

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

    # FIXME : Trouver un moyen d'appliquer le style de Dezède à TinyMCE.
    # 'content_css': STATIC_URL + 'css/styles.css',
}

FILEBROWSER_VERSIONS = {
    'avatar': {'verbose_name': ugettext('Avatar'),
               'width': 96, 'height': 96, 'opts': ''},
    'thumbnail': {'verbose_name': ugettext('Standard thumbnail'),
                  'width': 192, 'height': 192, 'opts': ''}
}
FILEBROWSER_ADMIN_THUMBNAIL = 'thumbnail'
FILEBROWSER_ADMIN_VERSIONS = ['avatar']
FILEBROWSER_MAX_UPLOAD_SIZE = 50 * (1024 ** 2)  # octets

THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + thumbnail_settings.THUMBNAIL_PROCESSORS
IMAGE_CROPPING_THUMB_SIZE = (800, 600)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'dezede',
        'INCLUDE_SPELLING': True,
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'libretto.signals.AutoInvalidatorSignalProcessor'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10
HAYSTACK_CUSTOM_HIGHLIGHTER = 'dezede.highlighting.CustomHighlighter'

CACHES = {
    'default': {
        'BACKEND': 'johnny.backends.redis.RedisCache',
        'LOCATION': 'unix:/var/run/redis/redis.sock:1',
        'KEY_PREFIX': '2Z',
        'TIMEOUT': 24 * 60 * 60,  # seconds
        'JOHNNY_CACHE': True,
    }
}
JOHNNY_MIDDLEWARE_KEY_PREFIX = '2Z'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

COMPRESS_ENABLED = True
COMPRESS_OUTPUT_DIR = ''
COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
)
COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
)

AJAX_LOOKUP_CHANNELS = {
    'lieu': ('libretto.lookups', 'LieuLookup'),
    'individu': ('libretto.lookups', 'IndividuLookup'),
    'individu__prenoms': ('libretto.lookups', 'IndividuPrenomsLookup'),
    'ensemble__particule_nom': ('libretto.lookups', 'EnsembleParticuleNomLookup'),
    'oeuvre': ('libretto.lookups', 'OeuvreLookup'),
    'oeuvre__prefixe_titre': ('libretto.lookups', 'OeuvrePrefixeTitreLookup'),
    'oeuvre__coordination': ('libretto.lookups', 'OeuvreCoordinationLookup'),
    'oeuvre__prefixe_titre_secondaire': ('libretto.lookups',
                                         'OeuvrePrefixeTitreSecondaireLookup'),
    'elementdeprogramme__autre': ('libretto.lookups',
                                  'ElementDeProgrammeAutreLookup'),
    'source__nom': ('libretto.lookups', 'SourceNomLookup'),
}

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

RQ_QUEUES = {
    'default': {
        'USE_REDIS_CACHE': 'default',
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'rq_console': {
            'format': '%(asctime)s %(message)s',
            'datefmt': '%H:%M:%S',
        },
    },
    'handlers': {
        'rq_console': {
            'level': 'DEBUG',
            'class': 'rq.utils.ColorizingStreamHandler',
            'formatter': 'rq_console',
            'exclude': ['%(asctime)s'],
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'rq.worker': {
            'handlers': ['rq_console', 'mail_admins'],
            'level': 'DEBUG'
        }
    }
}

SOUTH_MIGRATION_MODULES = {
    'easy_thumbnails': 'easy_thumbnails.south_migrations',
}
