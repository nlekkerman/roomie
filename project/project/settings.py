"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
import dj_database_url
from decouple import config, Csv
from datetime import timedelta
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

if os.path.exists('env.py'):
    import env

# Define environment variables using python-decouple
SECRET_KEY = config('SECRET_KEY')
DATABASES = {
    'default': dj_database_url.parse(config('DATABASE_URL')),
    
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1').split(',')

CSRF_TRUSTED_ORIGINS = [
    'https://*.gitpod.io',
    'https://*.herokuapp.com',
    "http://localhost:5173",
    
    
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'cloudinary_storage',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'roomie_property',
    'roomie_user',
    'cash_flow',
    'corsheaders',
    'accounts_app',
    'communication',
   
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # ✅ Must be ABOVE CSRF
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'project.wsgi.application'

# Cloudinary configuration
CLOUDINARY_URL = os.getenv('CLOUDINARY_URL')
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'ERROR',  # Change INFO -> DEBUG for detailed logs
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',  # Change INFO -> DEBUG to capture everything
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),  # Save logs to debug.log
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',  # Ensure Django logs errors & authentication issues
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'rest_framework': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',  # Logs Django Rest Framework-related issues
            'propagate': False,
        },
        'roomie_user': {  # Use this instead of 'cash_flow' for your app logs
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'communication': {  # Use this instead of 'cash_flow' for your app logs
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins (for development)
CORS_ALLOW_CREDENTIALS = True  # Allow sending credentials (cookies, authentication)
CORS_ALLOW_METHODS = [  # Ensure OPTIONS is allowed
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS",
    "PATCH",
]

CORS_ALLOW_HEADERS = [
    "content-type",
    "x-csrftoken",
    "authorization",
]
REST_FRAMEWORK = {
    
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 6,  # Number of items per page
    
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}


IMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=100),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
