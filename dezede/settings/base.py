# coding: utf-8

import re
from django.utils.safestring import mark_safe
from easy_thumbnails.conf import Settings as thumbnail_settings
from pathlib import Path

ugettext = lambda s: s


# Allows PyPy to work with Django.
try:
    import psycopg2
except ImportError:
    # Fall back to psycopg2cffi.
    from psycopg2cffi import compat
    compat.register()


BASE_DIR = Path(__file__).parent.parent.parent
SITE_URL = '/'

ADMINS = (
    ('Bertrand Bordage', 'bordage.bertrand@gmail.com'),
)
MANAGERS = ADMINS

SEND_BROKEN_LINK_EMAILS = True
EMAIL_SUBJECT_PREFIX = u'[Dezède] '
IGNORABLE_404_URLS = (
    re.compile(r'^/favicon\.ico/?$'),
)

MAINTENANCE_MODE = False
MAINTENANCE_IGNORE_URLS = (
    r'^/admin/.*$',
)

DATABASES = {
    'default': {
        'ENGINE': 'transaction_hooks.backends.postgis',
        'NAME': 'dezede',
        'USER': 'dezede',
        'CONN_MAX_AGE': None,
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Europe/Paris'
LANGUAGES = (
    ('de', ugettext('Deutsch')),
    ('en', ugettext('English')),
    ('es', ugettext('Español')),
    ('fr', ugettext('Français')),
    ('it', ugettext('Italiano')),
)
USE_I18N = True
USE_L10N = True
USE_TZ = True

SITE_ID = 1

MEDIA_ROOT = str(BASE_DIR / 'media')
MEDIA_URL = SITE_URL + 'media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'replace_this_with_some_random_string'

WSGI_APPLICATION = 'dezede.wsgi.application'

ROOT_URLCONF = 'dezede.urls'


STATIC_ROOT = str(BASE_DIR / 'static')
STATIC_URL = SITE_URL + 'static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
STATICFILES_DIRS = (
    str(BASE_DIR / 'dezede/static'),
)


INSTALLED_APPS = (
    'dezede',
    'common',
    'accounts',
    'exporter',

    'super_inlines.grappelli_integration',
    'super_inlines',
    'cachalot',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.gis',
    'django.contrib.postgres',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'haystack',
    'django_rq',
    'libretto',
    'dossiers',
    'examens',
    'afo',
    'mptt',
    'el_pagination',
    'tablature',
    'tinymce',
    'grappelli.dashboard',
    'grappelli',
    'rest_framework',
    'crispy_forms',
    'ajax_select',
    'range_slider',
    'easy_thumbnails',
    'image_cropping',
    'reversion',
    'django.contrib.admin',
    'compressor',
    'static_grouper',
)

MIDDLEWARE_CLASSES = (
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
)

LOCALE_PATHS = (
    'locale',
)

DATE_FORMAT = 'l j F Y'

TIME_FORMAT = 'H:i'

GRAPPELLI_INDEX_DASHBOARD = 'dezede.dashboard.CustomIndexDashboard'
GRAPPELLI_ADMIN_TITLE = mark_safe('<a href="/">Dezède</a>')

AUTH_USER_MODEL = 'accounts.HierarchicUser'
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
ACCOUNT_ADAPTER = 'accounts.adapter.HierarchicUserAdapter'
ACCOUNT_SIGNUP_FORM_CLASS = 'accounts.forms.HierarchicUserSignupForm'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
ACCOUNT_EMAIL_SUBJECT_PREFIX = EMAIL_SUBJECT_PREFIX
ACCOUNT_FORMS = {
    'login': 'accounts.forms.LoginForm',
}
LOGIN_URL = '/connexion'
LOGIN_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True

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
    'entity_encoding': 'raw',
    'element_format': 'html',
}

THUMBNAIL_ALIASES = {
    '': {
        'avatar': {'size': (96, 96)},
        'thumbnail': {'size': (192, 192)},
        'small': {'size': (950, 700)},
        'medium': {'size': (2000, 2000)},
    },
}
THUMBNAIL_PROCESSORS = (
    'image_cropping.thumbnail_processors.crop_corners',
) + thumbnail_settings.THUMBNAIL_PROCESSORS
IMAGE_CROPPING_THUMB_SIZE = (800, 600)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'dezede.elasticsearch_backend.ConfigurableElasticSearchEngine',
        'URL': '127.0.0.1:9200',
        'INDEX_NAME': 'dezede',
        'TIMEOUT': 60*5,  # seconds
        'INCLUDE_SPELLING': True,
    },
}
HAYSTACK_SIGNAL_PROCESSOR = 'libretto.signals.AutoInvalidatorSignalProcessor'
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10
HAYSTACK_CUSTOM_HIGHLIGHTER = 'dezede.highlighting.CustomHighlighter'
ELASTICSEARCH_INDEX_SETTINGS = {
    'settings': {
        'analysis': {
            'analyzer': {
                'default': {
                    'type': 'custom',
                    'tokenizer': 'standard',
                    'char_filter': ['html_strip'],
                    'filter': [
                        'lowercase',
                        'snowball_fr',
                        'snowball_de',
                        'asciifolding',
                        'elision',
                        'worddelimiter',
                    ],
                },
                'ngram_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'standard',
                    'char_filter': ['html_strip'],
                    'filter': [
                        'haystack_ngram',
                        'lowercase',
                        'snowball_fr',
                        'snowball_de',
                        'asciifolding',
                        'elision',
                        'worddelimiter',
                    ],
                },
                'edgengram_analyzer': {
                    'type': 'custom',
                    'tokenizer': 'standard',
                    'char_filter': ['html_strip'],
                    'filter': [
                        'haystack_edgengram',
                        'lowercase',
                        'snowball_fr',
                        'snowball_de',
                        'asciifolding',
                        'elision',
                        'worddelimiter',
                    ],
                }
            },
            'filter': {
                'snowball_fr': {
                    'type': 'snowball',
                    'language': 'French',
                },
                'snowball_de': {
                    'type': 'snowball',
                    'language': 'German2',
                },
                'elision': {
                    'type': 'elision',
                    'articles': ['l', 'm', 't', 'qu', 'n', 's', 'j', 'd'],
                },
                'worddelimiter': {
                    'type': 'word_delimiter',
                    'preserve_original': True,
                },
                'haystack_ngram': {
                    'type': 'nGram',
                    'min_gram': 2,
                    'max_gram': 15,
                },
                'haystack_edgengram': {
                    'type': 'edgeNGram',
                    'min_gram': 2,
                    'max_gram': 15,
                }
            }
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'unix:///var/run/redis/redis.sock',
        'KEY_PREFIX': '2Z',
        'TIMEOUT': None,  # seconds
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

COMPRESS_ENABLED = True
COMPRESS_OUTPUT_DIR = ''
COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
)
NPM_BINARY_PATH = BASE_DIR / 'node_modules/.bin/'
COMPRESS_PRECOMPILERS = (
    ('text/less', '%s {infile} {outfile}' % (NPM_BINARY_PATH / 'lessc')),
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

AJAX_LOOKUP_CHANNELS = {
    'lieu': ('libretto.lookups', 'LieuLookup'),
    'ensemble': ('libretto.lookups', 'EnsembleLookup'),
    'individu': ('libretto.lookups', 'IndividuLookup'),
    'individu__prenoms': ('libretto.lookups', 'IndividuPrenomsLookup'),
    'ensemble__particule_nom': ('libretto.lookups', 'EnsembleParticuleNomLookup'),
    'oeuvre': ('libretto.lookups', 'OeuvreLookup'),
    'oeuvre__prefixe_titre': ('libretto.lookups', 'OeuvrePrefixeTitreLookup'),
    'oeuvre__coordination': ('libretto.lookups', 'OeuvreCoordinationLookup'),
    'oeuvre__prefixe_titre_secondaire': ('libretto.lookups',
                                         'OeuvrePrefixeTitreSecondaireLookup'),
    'oeuvre__coupe': ('libretto.lookups', 'OeuvreCoupeLookup'),
    'oeuvre__tempo': ('libretto.lookups', 'OeuvreTempoLookup'),
    'elementdeprogramme__autre': ('libretto.lookups',
                                  'ElementDeProgrammeAutreLookup'),
    'source__titre': ('libretto.lookups', 'SourceTitreLookup'),
    'source__lieu_conservation': ('libretto.lookups',
                                  'SourceLieuConservationLookup'),
}

REST_FRAMEWORK = {
    'UNICODE_JSON': False,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': ['rest_framework.filters.DjangoFilterBackend'],
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '600/day',
    },
    'PAGE_SIZE': 10,
}

RQ_QUEUES = {
    'default': {
        'USE_REDIS_CACHE': 'default',
        'DEFAULT_TIMEOUT': 2*60*60,  # seconds
    },
}

EL_PAGINATION_PREVIOUS_LABEL = '<i class="fa fa-angle-left"></i>'
EL_PAGINATION_NEXT_LABEL = '<i class="fa fa-angle-right"></i>'

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
        },
        'elasticsearch': {
            'handlers': ['rq_console', 'mail_admins'],
            'level': 'WARNING'
        },
    }
}
