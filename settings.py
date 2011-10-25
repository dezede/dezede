# Django settings for musicologie project.
# coding: utf-8
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SITE_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    ('Bertrand Bordage', 'bordage.bertrand@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
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
    ('fr', 'Francais'),
    ('en', 'English'),
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
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'musicologie.urls'

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    'templates/static',
)

ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tinymce',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'musicologie.catalogue',
)

LOCALE_PATHS = (
    'locale',
)

DATE_FORMAT = 'l j F Y'

TIME_FORMAT = 'H:i'

TINYMCE_DEFAULT_CONFIG = {
    'mode' : 'textareas',
    'theme' : 'advanced',
    'plugins' : 'advhr,advimage,autosave,contextmenu,fullscreen,inlinepopups,insertdatetime,media,nonbreaking,paste,preview,save,searchreplace,style,table',
    'theme_advanced_buttons1' : 'newdocument,cancel,pasteword,|,fullscreen,preview,code,|,selectall,cut,copy,paste,|,undo,redo,|,link,unlink,image,media,|,table,delete_table,row_after,delete_row,col_after,delete_col,split_cells,merge_cells,|,sub,sup,|,charmap,nonbreaking,|,search',
    'theme_advanced_buttons2' : 'styleprops,removeformat,formatselect,fontselect,fontsizeselect,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,outdent,indent,|,forecolor,backcolor,|,insertdate,inserttime,advhr',
    'theme_advanced_buttons3' : '',
    'theme_advanced_toolbar_location' : 'top',
    'theme_advanced_toolbar_align' : 'center',
    'theme_advanced_statusbar_location' : 'bottom',
    'width' : '768',
    'height' : '300',
    'theme_advanced_resizing' : 'true',
    'theme_advanced_resizing_min_width' : '768',
    'theme_advanced_resizing_max_width' : '768',
    'plugin_insertdate_dateFormat' : '%A %d %B %Y',
    'plugin_insertdate_timeFormat' : '%H:%M',
    'save_enablewhendirty' : 'true',
}

