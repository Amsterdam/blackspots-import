"""
Django settings for blackspots-import project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from distutils.util import strtobool

import sentry_sdk
from django.utils.translation import gettext_lazy as _
from sentry_sdk.integrations.django import DjangoIntegration

# always import third party strings so makemessages picks them up
from . import third_party_strings  # noqa F401

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = strtobool(os.getenv("DEBUG", "false"))
ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ("127.0.0.1", "0.0.0.0")


LANGUAGE_CODE = "nl-nl"
LANGUAGES = [
    ("nl", _("Dutch")),
]
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django_filters",
    "django_extensions",
    "datapunt_api",
    "rest_framework",
    "rest_framework_gis",
    "drf_yasg",  # Used to generate schemas
    "rest_framework_swagger",
    "datasets.blackspots",
    "import_process",
    "health",
    "api",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "authorization_django.authorization_middleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "main.urls"

STATIC_URL = "/blackspots/static/"
STATIC_ROOT = "static"


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "main.wsgi.application"


# Database

if strtobool(os.getenv("DATABASE_ENABLED", "true")):
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.postgis",
            "NAME": os.getenv("DATABASE_NAME", "dev"),
            "USER": os.getenv("DATABASE_USER", "dev"),
            "PASSWORD": os.getenv("DATABASE_PASSWORD", "dev"),
            "HOST": os.getenv("DATABASE_HOST", "database"),
            "PORT": os.getenv("DATABASE_PORT", "5432"),
            "CONN_MAX_AGE": float(os.getenv("DATABASE_CONN_MAX_AGE", 20)),
        }
    }


SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        ignore_errors=["ExpiredSignatureError"],
    )

BAG_GEO_SEARCH_API_URL = "https://api.data.amsterdam.nl/geosearch/bag/"

OBJECTSTORE_CONNECTION_CONFIG = dict(
    VERSION="2.0",
    AUTHURL="https://identity.stack.cloudvps.com/v2.0",
    TENANT_NAME=os.getenv("OBJECTSTORE_TENANT_NAME"),
    TENANT_ID=os.getenv("OBJECTSTORE_TENANT_ID"),
    USER=os.getenv("OBJECTSTORE_USER"),
    PASSWORD=os.getenv("OBJECTSTORE_PASSWORD"),
    REGION_NAME="NL",
)

REST_FRAMEWORK = dict(
    PAGE_SIZE=20,
    MAX_PAGINATE_BY=100,
    UNAUTHENTICATED_USER={},
    UNAUTHENTICATED_TOKEN={},
    DEFAULT_AUTHENTICATION_CLASSES=(
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),
    DEFAULT_PAGINATION_CLASS=("datapunt_api.pagination.HALPagination",),
    DEFAULT_RENDERER_CLASSES=(
        "rest_framework.renderers.JSONRenderer",
        "datapunt_api.renderers.PaginatedCSVRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        # must be lowest!
        "rest_framework_xml.renderers.XMLRenderer",
    ),
    DEFAULT_FILTER_BACKENDS=(
        # 'rest_framework.filters.SearchFilter',
        "rest_framework.filters.OrderingFilter",
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    COERCE_DECIMAL_TO_STRING=False,
    # DEFAULT_VERSIONING_CLASS='rest_framework.versioning.NamespaceVersioning',
    # DEFAULT_VERSION='v0',
    # ALLOWED_VERSIONS=API_VERSIONS.keys(),
)

# The following JWKS data was obtained in the authz project :
# jwkgen -create -alg ES256
# This is a test public/private key def and added for testing.
JWKS_TEST_KEY = """
    {
        "keys": [
            {
                "kty": "EC",
                "key_ops": [
                    "verify",
                    "sign"
                ],
                "kid": "2aedafba-8170-4064-b704-ce92b7c89cc6",
                "crv": "P-256",
                "x": "6r8PYwqfZbq_QzoMA4tzJJsYUIIXdeyPA27qTgEJCDw=",
                "y": "Cf2clfAfFuuCB06NMfIat9ultkMyrMQO9Hd2H7O9ZVE=",
                "d": "N1vu0UQUp0vLfaNeM0EDbl4quvvL6m_ltjoAXXzkI3U="
            }
        ]
    }
"""


SCOPE_BS_READ = 'bs_r'
SCOPE_BS_WRITE = 'bs_w'

DATAPUNT_AUTHZ = {
    "JWKS": os.getenv("PUB_JWKS", JWKS_TEST_KEY),
    "MIN_SCOPE": (),
    "FORCED_ANONYMOUS_ROUTES": (
        "/status/",
        "/blackspots/redoc/",
        "/blackspots/swagger.yaml",
        "/favicon.ico",
    ),
    "PROTECTED": [
        ("/", ["GET", "HEAD", "TRACE"], [SCOPE_BS_READ]),
        ("/", ["POST", "PUT", "DELETE", "PATCH"], [SCOPE_BS_WRITE]),
    ]
}

# drf_yasg Swagger generation settings
SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "OAuth2": {
            "type": "oauth2",
            "authorizationUrl": "/oauth2/authorize",
            "flow": "implicit",
            "scopes": {"bs_w": "Blackspots write", "bs_r": "Blackspots read"},
        }
    },
    "SECURITY_REQUIREMENTS": {},  # No global scope required, only per api
}

OBJECTSTORE_UPLOAD_CONTAINER_NAME = os.environ["OBJECTSTORE_UPLOAD_CONTAINER_NAME"]

if DEBUG:

    INSTALLED_APPS += (
        "debug_toolbar",
        "corsheaders",
    )
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

    insert_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(insert_idx, "corsheaders.middleware.CorsMiddleware")

    CORS_ORIGIN_ALLOW_ALL = True
    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ]
