# -*- coding: utf-8 -*-
import os
PROJECT_DIR = os.path.dirname(__file__)

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/current/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

USE_I18N = True

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'uploads/')

#MEDIA_URL = '/uploads/'

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, 'media'),
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'ordercoops.middleware.SubdomainMiddleware',
)

ROOT_URLCONF = 'ordercoops.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates/'),
)

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ordercoops.catalogue",
    "ordercoops.userprofile",
)

TEMPLATE_CONTEXT_PROCESSORS = ( "django.contrib.auth.context_processors.auth",
                                "django.contrib.messages.context_processors.messages",
                                "django.core.context_processors.debug",
                                "django.core.context_processors.i18n",
                                "django.core.context_processors.media",
                                "django.core.context_processors.static",
                                "ordercoops.context_processors.coop_subdomain",
)

LOGIN_URL = "/user/login/"
SMTP_USERNAME=None
SMTP_PASSWORD=None

META_TITLE = 'Suma ordering website'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
META_DESC = 'Co-operatively order wholefoods and stuff'
META_KEYWORDS = 'wholefoods, co-operative, ordering'

AUTH_PROFILE_MODULE='userprofile.UserProfile'

# Put DATABASES, SECRET_KEY, ADMINS etc in localsettings.py, and don't commit it
from localsettings import *
