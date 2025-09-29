import os
import re

from django.utils.safestring import mark_safe
from easy_thumbnails.conf import Settings as thumbnail_settings

os.environ['USE_COMPRESSOR'] = 'True'

from noridjango.settings import *

gettext = lambda s: s


SITE_URL = '/'

ADMINS = (
    ('Bertrand Bordage', 'bordage.bertrand@gmail.com'),
    ('Cécile Hauchemaille', 'cecile@noripyt.com'),
)
MANAGERS = ADMINS

SEND_BROKEN_LINK_EMAILS = True
IGNORABLE_404_URLS = (
    re.compile(r'^/favicon\.ico/?$'),
)

MAINTENANCE_MODE = False
MAINTENANCE_IGNORE_URLS = (
    r'^/admin/.*$',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'dezede',
        'USER': 'dezede',
        'CONN_MAX_AGE': None,
        'CONN_HEALTH_CHECKS': True,
    },
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

SITE_ID = 1

DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000

STATICFILES_STORAGE = 'dezede.storage.NonStrictManifestStaticFilesStorage'
STATICFILES_DIRS = (
    str(BASE_DIR / 'dezede/static'),
    str(BASE_DIR / 'public/static'),
)


INSTALLED_APPS = [
    'db_search',
    'dezede',
    'noridjango',
    'common',
    'accounts',
    'exporter',

    'wagtail_notes',
    'wagtailfontawesomesvg',
    'wagtail.api.v2',
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.admin',
    'wagtail',
    'wagtail.contrib.settings',
    'modelcluster',
    'taggit',

    'super_inlines.grappelli_integration',
    'super_inlines',
    *INSTALLED_APPS[3:],
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.gis',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'haystack',
    # Below haystack so we do not overwrite its `update_index`,
    # but we can still call `wagtail_update_index`.
    'wagtail.search',
    'django_rq',
    'correspondence',
    'libretto',
    'dossiers',
    'examens',
    'afo',
    'tree',
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
    'static_grouper',
]

MIDDLEWARE = [
    *MIDDLEWARE,
    'django.middleware.locale.LocaleMiddleware',
    'dezede.middlewares.MaintenanceModeMiddleware',
    'dezede.middlewares.CorsHeadersMiddleware',
    'dezede.middlewares.MaxFieldsMiddleware',
    'dezede.middlewares.CountryBlockMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

TEMPLATES = TEMPLATES[1:]  # We have Jinja2, but we don’t want to use it for frontend templates.
TEMPLATES[0]['OPTIONS']['context_processors'] = [
    'dezede.context_processors.site',
    'django.template.context_processors.i18n',
    'django.template.context_processors.media',
    'django.template.context_processors.static',
    *TEMPLATES[0]['OPTIONS']['context_processors'],
]

LOCALE_PATHS = ['locale']

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

EMAIL_HOST = 'ssl0.ovh.net'
EMAIL_PORT = 587
EMAIL_TIMEOUT = 30

TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'plugins': 'contextmenu,fullscreen,inlinepopups,nonbreaking,paste,preview,searchreplace,table,smallcaps',
    'theme_advanced_buttons1': 'fullscreen,preview,code,|,selectall,cut,copy,paste,pasteword,|,undo,redo,|,link,unlink,|,charmap,nonbreaking,|,search',
    'theme_advanced_buttons2': 'removeformat,formatselect,|,smallcaps,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justify,|,bullist,numlist,outdent,indent,blockquote,|,sub,sup',
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
        'small': {'size': (1140, 840)},
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
        'URL': f'elasticsearch:9200',
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
            'tokenizer': {
                'haystack_ngram_tokenizer': {
                    'type': 'nGram',
                    'min_gram': 3,
                    'max_gram': 15,
                },
                'haystack_edgengram_tokenizer': {
                    'type': 'edgeNGram',
                    'min_gram': 2,
                    'max_gram': 15,
                    'side': 'front'
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
                    'min_gram': 3,
                    'max_gram': 15,
                },
                'haystack_edgengram': {
                    'type': 'edgeNGram',
                    'min_gram': 2,
                    'max_gram': 15,
                }
            }
        },
        'index': {
            'max_result_window': 1000000,
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'unix:///var/run/redis/redis-server.sock',
        'KEY_PREFIX': '2Z',
        'TIMEOUT': None,  # seconds
    },
    'renditions': {
        # TODO: Cache renditions using Memcached.
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'

COMPRESS_PRECOMPILERS = (
    ('text/less', f"{NPM_BINARY_PATH / 'lessc'} --math=always {{infile}} {{outfile}}"),
)
COMPRESS_PARSER = 'compressor.parser.LxmlParser'

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
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

RQ_QUEUES = {
    'default': {
        'USE_REDIS_CACHE': 'default',
        'DEFAULT_TIMEOUT': 8*60*60,  # seconds
    },
}

EL_PAGINATION_PREVIOUS_LABEL = '<i class="fa fa-angle-left"></i>'
EL_PAGINATION_NEXT_LABEL = '<i class="fa fa-angle-right"></i>'

LOGGING = {
    **LOGGING,
    'formatters': {
        **LOGGING['formatters'],
        'rq_console': {
            'format': '%(asctime)s %(message)s',
            'datefmt': '%H:%M:%S',
        },
    },
    'handlers': {
        **LOGGING['handlers'],
        'rq_console': {
            'level': 'DEBUG',
            'class': 'rq.utils.ColorizingStreamHandler',
            'formatter': 'rq_console',
            'exclude': ['%(asctime)s'],
        },
    },
    'loggers': {
        **LOGGING['loggers'],
        'rq.worker': {
            'handlers': ['rq_console', 'mail_admins'],
            'level': 'DEBUG',
        },
        'elasticsearch': {
            'handlers': ['rq_console', 'mail_admins'],
            'level': 'WARNING',
        },
    }
}

if DEBUG:
    INSTALLED_APPS = INSTALLED_APPS + [
        'django_extensions',
        'template_timings_panel',
        'django_nose',
        'wagtail.contrib.styleguide',
    ]
    # FIXME: remove setting when we remove Haystack, HaystackDebugPanel and TemplateTimings.
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
        # These third-party panels cannot be deactivated by default on the debug toolbar.
        # 'template_timings_panel.panels.TemplateTimings.TemplateTimings',
    ]
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    NOSE_ARGS = ['--with-doctest']
else:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

#
# Wagtail settings
#

WAGTAIL_SITE_NAME = constants.PROJECT_VERBOSE
WAGTAILEMBEDS_RESPONSIVE_HTML = True
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAILIMAGES_MAX_UPLOAD_SIZE = constants.CLIENT_MAX_BODY_SIZE * 1024 * 1024
WAGTAILADMIN_BASE_URL = f'http://{constants.DOMAIN}' if DEBUG else f'https://{constants.DOMAIN}'
WAGTAILADMIN_PERMITTED_LANGUAGES = LANGUAGES

WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'dezede.search_backend.FixedPostgresSearchBackend',
        'SEARCH_CONFIG': 'french_unaccent_including_stopwords',
    },
}

WAGTAILADMIN_RICH_TEXT_EDITORS = {
    "default": {
        "WIDGET": "wagtail.admin.rich_text.DraftailRichTextArea",
        'OPTIONS': {
            'features': [
                'h2', 'h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'superscript', 'small-caps',
                'hr', 'link', 'document-link', 'image', 'embed',
                'blockquote', 'note-anchor', 'note-reference',
            ],
        },
    },
    'transcription': {
        'WIDGET': 'wagtail.admin.rich_text.DraftailRichTextArea',
        'OPTIONS': {
            'features': [
                'h2', 'h3', 'h4', 'bold', 'italic', 'ol', 'ul', 'superscript', 'small-caps',
                'hr', 'blockquote', 'note-anchor', 'note-reference',
                'align-center', 'align-right',
            ],
        },
    },
}

# Custom settings

AUTOCOMPLETE_CONFIG = 'simple_unaccent'

BLOCKED_COUNTRIES = [
    # Sorted by biggest offenders first.
    'SG', 'BR', 'HK', 'VN', 'IN', 'IQ', 'BD', 'CN', 'AR', 'SA',
    'ZA', 'TR', 'PK', 'VE', 'UZ', 'KE', 'EC', 'CO', 'UA', 'RU',
    'JO', 'UY', 'PY', 'NP', 'CL', 'JM', 'EG', 'ET', 'AE', 'KZ',
    'PH', 'HN', 'TT', 'CR', 'AZ', 'PA', 'OM', 'PE', 'BO', 'IR',
    'BB', 'AL', 'ID',
]
