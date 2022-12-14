from os import getenv

from config.secrets import get_secret
from config.settings.base import *

DEBUG = True

ALLOWED_HOSTS += ["*"]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASE_SECRET = get_secret(f"{PROJECT_NAME}-rds")
# DATABASE_SECRET = get_secret(f"wecooptest-rds")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": getenv("NAME"),
        "USER": getenv("USER"),
        "PASSWORD": getenv("PASSWORD"),
        "HOST": getenv("HOST"),
        "PORT": getenv("PORT"),
    },
    "reader": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": getenv("NAME"),
        "USER": getenv("USER"),
        "PASSWORD": getenv("PASSWORD"),
        "HOST": getenv("HOST"),
        "PORT": getenv("PORT"),
    },
}

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": DATABASE_SECRET["NAME"],
#         "USER": DATABASE_SECRET["USER"],
#         "PASSWORD": DATABASE_SECRET["PASSWORD"],
#         "HOST": DATABASE_SECRET["WRITER_HOST"],
#         "PORT": DATABASE_SECRET["PORT"],
#     },
#     "reader": {
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": DATABASE_SECRET["NAME"],
#         "USER": DATABASE_SECRET["USER"],
#         "PASSWORD": DATABASE_SECRET["PASSWORD"],
#         "HOST": DATABASE_SECRET["WRITER_HOST"],
#         "PORT": DATABASE_SECRET["PORT"],
#     },
# }

# REDIS
REDIS_HOST = "localhost"

# CHANNELS
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# CELERY
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:6379/0"

# # LOGGING
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'formatters': {
#         'app_formatter': {
#             'format': '[{levelname}] [{name}:{lineno} {funcName}] {message}',
#             'style': '{',
#         },
#         'simple_formatter': {
#             'format': '{message}',
#             'style': '{',
#         }
#     },
#     'handlers': {
#         'app_console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'app_formatter',
#         },
#         'simple_console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple_formatter',
#         },
#     },
#     'loggers': {
#         'app': {
#             'handlers': ['app_console'],
#             'level': 'DEBUG',
#         },
#         'request': {
#             'handlers': ['simple_console'],
#             'level': 'INFO',
#         },
#         'django.request': {
#             'level': 'ERROR',
#         },
#         'django.db.backends': {
#             'handlers': ['simple_console'],
#             'level': 'DEBUG',
#         },
#     },
# }
