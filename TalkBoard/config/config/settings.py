"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from decouple import config
from dotenv import load_dotenv
# Build paths inside the project like this: BASE_DIR / 'subdir'.
load_dotenv() 

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')
# SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['talkboard.onrender.com', "localhost", "127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "app.apps.AppConfig"
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',  # SQLite3データベースを使用
#         'NAME': BASE_DIR / 'db.sqlite3',         # プロジェクトのルートにdb.sqlite3ファイルを作成
#     }
# }
# Import the dj-database-url package at the beginning of the file
# import dj_database_url
# DATABASES = {
#     'default': dj_database_url.config(
#         # Replace this value with your local database's connection string.
#         default='postgresql://postgres:postgres@localhost:5432/',
#         conn_max_age=600
#     )
# }
if os.getenv('SQLITE3'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

if os.getenv('RENDER'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',  # 使用するデータベースのエンジン
            # 'NAME': config('DB_NAME'),          # データベース名
            # 'USER': config('DB_USER'),          # データベースのユーザー名
            # 'PASSWORD': config('DB_PASSWORD'),  # データベースのパスワード
            # 'HOST': config('DB_HOST'),          # データベースのホスト
            # 'PORT': config('DB_PORT'),          # データベースのポート
            'NAME': os.environ.get('DB_NAME'),          # データベース名
            'USER': os.environ.get('DB_USER'),          # データベースのユーザー名
            'PASSWORD': os.environ.get('DB_PASSWORD'),  # データベースのパスワード
            'HOST': os.environ.get('DB_HOST'),          # データベースのホスト
            'PORT': os.environ.get('DB_PORT'), 
            # 'OPTIONS': {
            #     'sslmode': 'require',  # or 'verify-full' if CA certificate is provided
            # }
        }
    }


# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#         },
#     },
#     "root": {
#         "handlers": ["console"],
#         "level": "WARNING",
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["console"],
#             "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
#             "propagate": False,
#         },
#     },
# }

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

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [] #コマンド"collectstatic"を使う場合は設定

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Emailの設定

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD') #アプリパスワード

#画像ファイルの保存場所を設定
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
