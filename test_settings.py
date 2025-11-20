"""
Django settings for running tests.
"""

SECRET_KEY = "test-secret-key"

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "taggit",
    "wagtail",
    "wagtail.admin",
    "wagtail.images",
    "wagtail.documents",
    "wagtail_thumbnail_choice_block",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
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

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

STATIC_URL = "/static/"
STATICFILES_DIRS = []
ROOT_URLCONF = ""

# Wagtail settings
WAGTAIL_SITE_NAME = "Test Site"
WAGTAILADMIN_BASE_URL = "http://localhost:8000"

# Use settings for django.setup()
USE_TZ = True
