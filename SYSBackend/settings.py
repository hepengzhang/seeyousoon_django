# Django settings for SYSBackend project.

import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Hepeng', 'hepeng.zhang1@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'seeyousoon',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'root',
        'PASSWORD': '888',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    },
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

STATIC_URL = '/static/'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9+r$a=hbg$czzww2gn$7!#7d&5!cu)zdxqnd-bs0v$xkvgy0!+'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'SYSBackend.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'SYSBackend.wsgi.application'

INSTALLED_APPS = (
#     'django.contrib.auth',
    'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.sites',
#     'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'webapi',
#     'seeyousoonAPI',
    'rest_framework',
    'rest_framework_docs'
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'webapi.Utils.Authentication.SYSAPIAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'webapi.Utils.Permissions.AuthPermission',
    )
}

#Apple push notification provider
PYAPNS_CONFIG = {
  'HOST': 'http://localhost:8077/',
  'TIMEOUT': 15,                    # OPTIONAL, host timeout in seconds
  'INITIAL': [                      # OPTIONAL, see below
    ('SeeYouSoon', '/Users/Hepeng/Dropbox/AppKeys/SYSDevAPNSCertificate.pem', 'sandbox'),
  ]
}

if 'test' in sys.argv:
    try:
        from test_settings import *
    except ImportError:
        pass
