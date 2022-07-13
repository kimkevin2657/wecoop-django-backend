import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'pj%2ze09(g)i^joilp-f8gvs)6ou_m036u3ejs^ky&9nse5k92'

ALLOWED_HOSTS = []

LOCAL_APPS = [
    'app.staticfile',
    'app.common.apps.CommonConfig',
    'app.conference.apps.ConferenceConfig',
    'app.chat.apps.ChatConfig',
    'app.device.apps.DeviceConfig',
    'app.logger.apps.LoggerConfig',
    'app.user.apps.UserConfig',
    'app.verifier.apps.VerifierConfig',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'channels',
    'corsheaders',
    'django_filters',
    'django_hosts',
    'drf_spectacular',
    'storages',
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

INSTALLED_APPS = LOCAL_APPS + THIRD_PARTY_APPS + DJANGO_APPS


MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'config.middleware.RequestLogMiddleware',
    # 'config.middleware.DoobucMiddleWare',  # DOOBUC Middleware
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'ko'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

SITE_NAME = '위쿱'
SITE_LOGO = 'img/logo.png'  # static/img/logo.png 변경
SITE_URL = 'https://wecoop.link'

PROJECT_NAME = 'wecoop'

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_ROOT = BASE_DIR / 'media'

# APPEND_SLASH
APPEND_SLASH = False

# AUTH_USER_MODEL
AUTH_USER_MODEL = 'user.User'


# APPLICATION
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.routing.application'


# HOST
DEFAULT_HOST = 'api'
ROOT_HOSTCONF = 'config.hosts'
ROOT_URLCONF = 'config.urls.api'


# MODEL ID
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# DATABASE ROUTER
DATABASE_ROUTERS = ['config.router.Router']


# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}


# DJANGO REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'config.authentication.Authentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    # "DEFAULT_PAGINATION_CLASS": "api.common.paginations.CursorPagination",
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# SPECTACULAR
SPECTACULAR_SETTINGS = {
    'TITLE': f'{SITE_NAME} API',
    'DESCRIPTION': f'{SITE_NAME}의 API입니다.',
    'VERSION': '1.0.0',
    'SCHEMA_PATH_PREFIX': r'/v[0-9]',
    'DISABLE_ERRORS_AND_WARNINGS': True,
    'SORT_OPERATIONS': False,
    'SWAGGER_UI_SETTINGS': {
        'docExpansion': 'none',
        'defaultModelRendering': 'example',  # example, model
        'defaultModelsExpandDepth': 0,
        'deepLinking': True,
        'displayRequestDuration': True,
        'persistAuthorization': True,
        'syntaxHighlight.activate': True,
        'syntaxHighlight.theme': 'agate',
        # 'preauthorizeApiKey': False,
    },
    'PREPROCESSING_HOOKS': [],  # pre hook 추가
    'SERVE_INCLUDE_SCHEMA': False,
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'Bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization'
            }
        }
    },
    'SECURITY': [{'Bearer': [], }],
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields',
    ],
}

# COOLSMS
COOLSMS_API_KEY = 'NCSDSDSIS1BCYGXIJ'
COOLSMS_API_SECRET = '94ZEDSDS4IFCFGPO3KRVF3OQFMGY7NSSW'
COOLSMS_FROM_PHONE = '0313069114'


# MAILGUN
MAILGUM_API_KEY = "1232322f6ba7f35c9bc89d2ba5157c861-2416cf28-f88159a0"
MAILGUM_DOMAIN = "mg.1232323.io"
MAILGUM_FROM_EMAIL = 'Jangwon jangwon@jangwon.io'


# ALARMTALK
ALARMTALK_ID = 'ncp:kkobizmsg:kr:**:**'
ALARMTALK_CLIENT_ID = 'ptear2P22222QEyF8UvqZ'
ALARMTALK_CLIENT_SECRET = 'JQVuDgHb3333331LIRGGHYeSfYeYGnBzWEHamUT'


# S3
AWS_REGION = 'ap-northeast-2'
AWS_STORAGE_BUCKET_NAME = 'project_name-s3-bucket'  # project_name 은 cloudformation에서 사용한 프로젝트명
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=864000'}
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = 'public-read'
AWS_LOCATION = 'media'
AWS_S3_SECURE_URLS = True

# MEDIA
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIAFILES_LOCATION = 'media'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIAFILES_LOCATION}/'

# STATIC
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_LOCATION = 'static'
# STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATICFILES_LOCATION}/'

# CELERY
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = 'Asia/Seoul'
CELERYD_SOFT_TIME_LIMIT = 300
CELERYD_TIME_LIMIT = CELERYD_SOFT_TIME_LIMIT + 60
CELERY_TASK_IGNORE_RESULT = True


# KAKAO
KAKAO_CLIENT_ID = '29bebceec427c5cb9e5a35627b29036e'
KAKAO_CLIENT_SECRET = 'C3JcbuqA5IdvkjdBmPfP0R56WFD2x59O'
'''
KAKAO LOGIN URL
https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=${KAKAO_CLIENT_ID}&redirect_uri=${SOCIAL_REDIRECT_URL}&state=kakao
https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=29bebceec427c5cb9e5a35627b29036e&redirect_uri=http://localhost:3000/login/social/callback&state=kakao
'''

# NAVER
NAVER_CLIENT_ID = 'uGdhMg5sF0l_syyYTL4a'
NAVER_CLIENT_SECRET = 'hEG6AHEIJs'
'''
NAVER LOGIN URL
https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=${NAVER_CLIENT_ID}&redirect_uri=${SOCIAL_REDIRECT_URL}&state=naver
https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=uGdhMg5sF0l_syyYTL4a&redirect_uri=http://localhost:3000/login/social/callback&state=naver
'''

# FACEBOOK
FACEBOOK_CLIENT_ID = '390225185553512'
FACEBOOK_CLIENT_SECRET = '300c5460a4a64973bae345711599c7c4'
'''
FACEBOOK LOGIN URL
https://www.facebook.com/v9.0/dialog/oauth?response_type=code&client_id=${FACEBOOK_CLIENT_ID}&redirect_uri=${SOCIAL_REDIRECT_URL}&state=facebook
https://www.facebook.com/v9.0/dialog/oauth?response_type=code&client_id=390225185553512&redirect_uri=http://localhost:3000/login/social/callback&state=facebook
'''

# GOOGLE
GOOGLE_CLIENT_ID = '150905530006-61l7dmaai5ih8href866erlm80cf6q5i.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'FQV6EpdvGdZ1ILsCe2Al-Ym_'
'''
GOOGLE LOGIN URL
https://accounts.google.com/o/oauth2/auth/oauthchooseaccount?response_type=code&client_id=${GOOGLE_CLIENT_ID}&redirect_uri=${SOCIAL_REDIRECT_URL}&state=google&scope=openid
https://accounts.google.com/o/oauth2/auth/oauthchooseaccount?response_type=code&client_id=150905530006-61l7dmaai5ih8href866erlm80cf6q5i.apps.googleusercontent.com&redirect_uri=http://localhost:3000/login/social/callback&state=google&scope=openid
'''

# APPLE
APPLE_CLIENT_ID = 'dev.toktokhan.service.dsswsd'
APPLE_CLIENT_SECRET = """-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgYjhuYgorXIi4dBrb
gjihmQprFrpyroS6LBk3fVzDsMigCgsdsdsdzj0DAQehRANCAARVlzic8TnC65T9
YlbzYrx0zcdg78Fh38mTRCA1RxL2Vj4xWt+fvP6FTYeLeoaoOhH5uyO0RK/eFRya
kAurDWBV
-----END PRIVATE KEY-----"""
APPLE_KEY_ID = "RFDQYGNMS9"
APPLE_TEAM_ID = "T6WWD8NJA6"
'''
APPLE LOGIN URL
https://appleid.apple.com/auth/authorize?response_type=code&client_id=${APPLE_CLIENT_ID}&redirect_uri={SOCIAL_REDIRECT_URL}&state=apple
https://appleid.apple.com/auth/authorize?response_type=code&client_id=123&redirect_uri=http://localhost:3000/login/social/callback&state=apple
'''
