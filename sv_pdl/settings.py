import os
import sys

import dj_database_url


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = PACKAGE_ROOT

DEBUG = bool(int(os.environ.get("DEBUG", "1")))
TRACING_ENABLED = bool(int(os.environ.get("TRACING_ENABLED", not DEBUG)))
LIBRARY_VIEW_API_VERSION = int(os.environ.get("LIBRARY_VIEW_API_VERSION", 0))

DATABASES = {
    "default": dj_database_url.config(default="postgres://localhost/scaife-viewer")
}

ALLOWED_HOSTS = [
    "localhost",
    "scaife.perseus.org",
    "scaife-dev.perseus.org",
]

if "HEROKU_APP_NAME" in os.environ:
    ALLOWED_HOSTS.append(".herokuapp.com")

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "UTC"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = int(os.environ.get("SITE_ID", 1))

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PACKAGE_ROOT, "site_media", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"

# Absolute path to the directory static files should be collected to.
# Don"t put anything in this directory yourself; store your static files
# in apps" "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PACKAGE_ROOT, "site_media", "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/site_media/static/"

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "static", "dist"),
]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

if "SECRET_KEY" in os.environ:
    SECRET_KEY = os.environ["SECRET_KEY"]
else:
    if not DEBUG:
        raise RuntimeError("missing SECRET_KEY environment variable")
    else:
        SECRET_KEY = "----dev-secret-key----"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PACKAGE_ROOT, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "account.context_processors.account",
                "pinax_theme_bootstrap.context_processors.theme",
                "sv_pdl.context_processors.google_analytics",
            ],
        },
    },
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "sv_pdl.middleware.PerRequestMiddleware",
]

PER_REQUEST_MIDDLEWARE = {
    "default": [
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.sites.middleware.CurrentSiteMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "account.middleware.LocaleMiddleware",
    ],
    "api": [],
}

# Due to PER_REQUEST_MIDDLEWARE being used to add SessionMiddleware,
# AuthenticationMiddleware and MessageMiddleware, we must silence related
# SystemCheckErrors
# refs https://code.djangoproject.com/ticket/30237#comment:10
SILENCED_SYSTEM_CHECKS = [
    "admin.E408",
    "admin.E409",
    "admin.E410"
]

ROOT_URLCONF = "sv_pdl.urls"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "sv_pdl.wsgi.application"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",

    "webpack_loader",

    # theme
    "bootstrapform",
    "pinax_theme_bootstrap",

    # external
    "account",
    "corsheaders",
    "django_extensions",
    "django_jsonfield_backport",
    "letsencrypt",
    "oidc_provider",
    "graphene_django",
    "pinax.eventlog",
    "pinax.webanalytics",
    "raven.contrib.django.raven_compat",

    # scaife-viewer
    "scaife_viewer.atlas",
    "scaife_viewer.core",

    # project
    "sv_pdl",
    "sv_pdl.atlas",
    "sv_pdl.reading",
    "sv_pdl.stats",
]

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "",
        "STATS_FILE": os.path.join(PROJECT_ROOT, "static", "stats", "webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "IGNORE": [".*.hot-update.js", ".+.map"]
    }
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        },
        "sentry": {
            "level": "WARNING",
            "class": "raven.contrib.django.raven_compat.handlers.SentryHandler",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": sys.stdout
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "scaife_viewer.cts": {
            "level": "ERROR",
        },
        "raven": {
            "level": "WARNING",
            "handlers": ["sentry"],
            "propagate": False,
        },
        "sentry.errors": {
            "level": "WARNING",
            "handlers": ["sentry"],
            "propagate": False,
        },
        "": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": True
        }
    }
}

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]
LANGUAGES = [
    ("de", "Deutsch"),
    ("en", "English"),
    ("fr", "français"),
    ("it", "italiano"),
]

SESSION_COOKIE_NAME = "sv-sessionid"

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_EMAIL_UNIQUE = True
ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True
ACCOUNT_LOGIN_REDIRECT_URL = "home"
ACCOUNT_LOGOUT_REDIRECT_URL = "home"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 2
ACCOUNT_LANGUAGES = LANGUAGES

AUTHENTICATION_BACKENDS = [
    "account.auth_backends.UsernameAuthenticationBackend",
]

LOGIN_URL = "account_login"

OIDC_USERINFO = "sv_pdl.oidc.userinfo"

DEFAULT_FROM_EMAIL = "Scaife Viewer <perseus_webmaster@tufts.edu>"
THEME_CONTACT_EMAIL = "perseus_webmaster@tufts.edu"

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = os.environ.get("EMAIL_PORT", "")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = bool(int(os.environ.get("SECURE_SSL_REDIRECT", "0")))
SECURE_REDIRECT_EXEMPT = [
    r"\.well-known/acme-challenge/.+",
]

DEFAULT_HTTP_PROTOCOL = "https" if SECURE_SSL_REDIRECT else "http"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "sv-cache",
    },
}

CTS_RESOLVER_CACHE_LOCATION = os.environ.get("CTS_RESOLVER_CACHE_LOCATION", "cts_resolver_cache")
SCAIFE_VIEWER_CORE_RESOLVER_CACHE_LABEL = "cts-resolver"

CTS_LOCAL_RESOLVER_CACHE = bool(int(os.environ.get("CTS_LOCAL_RESOLVER_CACHE", "1")))
if CTS_LOCAL_RESOLVER_CACHE:
    CTS_RESOLVER_CACHE_KWARGS = {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": CTS_RESOLVER_CACHE_LOCATION,
    }
else:
    # NOTE: This cache is disabled in production, since
    # the CTS data is loaded on boot from CTS_API_ENDPOINT
    CTS_RESOLVER_CACHE_KWARGS = {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
CACHES.update({
    SCAIFE_VIEWER_CORE_RESOLVER_CACHE_LABEL: CTS_RESOLVER_CACHE_KWARGS,
})

XSL_STYLESHEET_PATH = os.environ.get("XSL_STYLESHEET_PATH", os.path.join(PACKAGE_ROOT, "tei.xsl"))

resolver = os.environ.get("CTS_RESOLVER", "api")
if resolver == "api":
    CTS_API_ENDPOINT = os.environ.get("CTS_API_ENDPOINT", "https://scaife-cts-dev.perseus.org/api/cts")
    CTS_RESOLVER = {
        "type": "api",
        "kwargs": {
            "endpoint": CTS_API_ENDPOINT,
        },
    }
    CTS_LOCAL_TEXT_INVENTORY = "ti.xml" if DEBUG else None
elif resolver == "local":
    CTS_LOCAL_DATA_PATH = os.environ["CTS_LOCAL_DATA_PATH"]
    CTS_RESOLVER = {
        "type": "local",
        "kwargs": {
            "data_path": CTS_LOCAL_DATA_PATH,
        },
    }

if "SENTRY_DSN" in os.environ:
    RAVEN_CONFIG = {
        "dsn": os.environ["SENTRY_DSN"],
    }


FORCE_SCRIPT_NAME = os.environ.get("FORCE_SCRIPT_NAME")
if FORCE_SCRIPT_NAME:
    # prepend FORCE_SCRIPT_NAME to STATIC_URL
    STATIC_URL = f"{FORCE_SCRIPT_NAME}{STATIC_URL}"


ELASTICSEARCH_HOSTS = os.environ.get("ELASTICSEARCH_HOSTS", "localhost:9200").split(",")
ELASTICSEARCH_INDEX_NAME = os.environ.get("ELASTICSEARCH_INDEX_NAME", "scaife-viewer")
ELASTICSEARCH_SNIFF_ON_START = bool(int(os.environ.get("ELASTICSEARCH_SNIFF_ON_START", "0")))
ELASTICSEARCH_SNIFF_ON_CONNECTION_FAIL = bool(int(os.environ.get("ELASTICSEARCH_SNIFF_ON_CONNECTION_FAIL", "0")))

DEPLOYMENT_TIMESTAMP_VAR_NAME = os.environ.get("DEPLOYMENT_TIMESTAMP_VAR_NAME", "HEROKU_RELEASE_CREATED_AT")


GRAPHENE = {
    "SCHEMA": "sv_pdl.atlas.schema.schema",
    # setting RELAY_CONNECTION_MAX_LIMIT to None removes the limit; for backwards compatability with current API
    # @@@ restore the limit
    "RELAY_CONNECTION_MAX_LIMIT": None,
}

SCAIFE_VIEWER_CORE_USE_CLOUD_INDEXER = bool(int(os.environ.get("USE_CLOUD_INDEXER", "0")))


SV_ATLAS_DATA_DIR = os.getenv(
    "ATLAS_DATA_DIR",
    os.path.join(
        PROJECT_ROOT, "atlas_data"
    )
)

SV_ATLAS_HOOKSET = "sv_pdl.atlas.hooks.ATLASHookSet"

SV_ATLAS_DB_LABEL = "atlas"
SV_ATLAS_DB_PATH = os.getenv(
    "ATLAS_DB_PATH",
    os.path.join(SV_ATLAS_DATA_DIR, "atlas.sqlite")
)

SV_ATLAS_INGESTION_PIPELINE = [
    "scaife_viewer.atlas.importers.versions.import_versions",
    # TODO: Run bin/fetch_corpus_repo_metadata first
    "scaife_viewer.atlas.importers.repo_metadata.import_repo_metadata",
    # TODO: Run extract_atlas_annotations command first
    "scaife_viewer.atlas.importers.attributions.import_attributions",
]
# ATLAS uses an isolated database with a custom router that ensures
# that SV_ATLAS_DB_LABEL database only contains data from the ATLAS application.
DATABASES.update({
    SV_ATLAS_DB_LABEL: {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": SV_ATLAS_DB_PATH,
    }
})

DATABASE_ROUTERS = ["scaife_viewer.atlas.db_routers.ATLASRouter"]


def populate_cors_origin_whitelist():
    allowed = []
    for host in ALLOWED_HOSTS:
        allowed.append(f"https://{host}")
        allowed.append(f"http://{host}")
    return allowed


if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
else:
    CORS_ORIGIN_WHITELIST = populate_cors_origin_whitelist()
