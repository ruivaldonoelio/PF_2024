"""
Django settings for djangoProject project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import environ
import os
from pathlib import Path

from django.contrib import staticfiles
from django.core.management.utils import get_random_secret_key
import dj_database_url
import sys

# Set the project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

# Set the project base directory


# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# False if not in os.environ because of casting above


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,profdevhub-da9cw.ondigitalocean.app").split(",")
CSRF_TRUSTED_ORIGINS = ['https://profdevhub-da9cw.ondigitalocean.app']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True


LOGIN_URL = '/login'

LOGOUT_URL = '/logout'

LOGIN_REDIRECT_URL = '/homepage'

LOGOUT_REDIRECT_URL = '/login'




INSTALLED_APPS = [
    'profdevhub',
    'daphne',
    'channels',
    'social_django',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.instagram.InstagramOAuth2',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = 'djangoProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.joinpath('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'djangoProject.asgi.application'

# Configuração de Canal Padrão
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(env("redis"))],
        },
    },
}

WSGI_APPLICATION = 'djangoProject.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("db_name_user"),
        'USER': env("db_user"),
        'PASSWORD': env("db_pass"),
        'HOST': env("db_host"),
        'PORT': env("db_port"),
        'ATOMIC_REQUESTS': True,
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/


TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGE_CODE = 'pt'

LANGUAGES = [
    ('en', 'English'),
    ('pt', 'Português'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGE_COOKIE_NAME = 'django_language'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'

# Add these new lines
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'  # URL base para servir arquivos de mídia
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CELERY_BROKER_URL = env("redis")
CELERY_RESULT_BACKEND = env("redis")

CELERY_BEAT_SCHEDULE = {
    'check-workshop-inscricao': {
        'task': 'profdevhub.tasks.check_inscricao',
        'schedule': 60.0,  # verifica a cada hora
    },
    'check-course-vaga': {
        'task': 'profdevhub.tasks.check_vaga',
        'schedule': 300.0,  # verifica a cada hora
    },
}

SOCIAL_AUTH_GITHUB_KEY = env("github_id")
SOCIAL_AUTH_GITHUB_SECRET = env("github_secret")

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env("google_id")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env("google_secret")

SOCIAL_AUTH_INSTAGRAM_KEY = ''
SOCIAL_AUTH_INSTAGRAM_SECRET = ''

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'profdevhub.social_auth.check_user_exists_and_login',
)