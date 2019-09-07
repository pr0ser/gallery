"""
Django settings for gallery project.

"""

from ast import literal_eval
from os import path, environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = literal_eval(environ['DEBUG'])

ALLOWED_HOSTS = literal_eval(environ['ALLOWED_HOSTS'])

# Use secure cookies if DEBUG is False
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_BROWSER_XSS_FILTER = True

# Application definition
INSTALLED_APPS = [
    'gallery.apps.GalleryConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'django_cleanup',
    'rest_framework',
    'corsheaders',
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 30
}

if DEBUG:
    INSTALLED_APPS += ['dj_static']

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'photogallery.urls'

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

# WSGI configuration
WSGI_APPLICATION = 'photogallery.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE':       'django.db.backends.postgresql',
        'NAME':         environ['POSTGRES_DB'],
        'USER':         environ['POSTGRES_USER'],
        'PASSWORD':     environ['POSTGRES_PASSWORD'],
        'HOST':         environ['DB_HOST'],
        'PORT':         environ['DB_PORT'],
        'CONN_MAX_AGE': 600,
    }
}


# Password validation
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
LANGUAGE_CODE = 'fi'

TIME_ZONE = 'Europe/Helsinki'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

LOCALE_PATHS = (
    path.join(BASE_DIR, 'locale'),
)

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

STATIC_ROOT = path.join(BASE_DIR, 'static')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': path.join(BASE_DIR, 'logs', 'gallery.log'),
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 0,
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s',
            'datefmt': "%G-%m-%d %H:%M:%S %z"
        },
        'simple': {
            'format': '%(levelname)s|%(message)s'
        },
    },
    'loggers': {
        'gallery.request': {
            'handlers': ['console', 'logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
        'gallery.models': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'gallery.views': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'gallery.exif_reader': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'gallery.utils': {
            'handlers': ['console', 'logfile'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# Celery
CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_RESULT_BACKEND = 'django-db'

# Other
MEDIA_ROOT = path.join(BASE_DIR, 'media')

FILE_UPLOAD_PERMISSIONS = int(environ['UPLOAD_PERMISSIONS'], 8)

FILE_UPLOAD_DIRECTORY_PERMISSIONS = int(environ['DIRECTORY_PERMISSIONS'], 8)

MEDIA_URL = '/media/'

LOGIN_URL = '/login/'

LOGIN_REDIRECT_URL = '/'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Load Django debug toolbar
if DEBUG:
    INTERNAL_IPS = ('127.0.0.1', '172.18.0.1', '172.19.0.1')
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INSTALLED_APPS += ['debug_toolbar']

# CORS headers configuration

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = environ.get('CORS_ORIGIN_WHITELIST').split(',')

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)

CORS_ALLOW_CREDENTIALS = True
