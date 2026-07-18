import os
from pathlib import Path

# ================= BASE DIR =================
BASE_DIR = Path(__file__).resolve().parent.parent

# ================= SECRET KEY =================
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-7f9$#@!kdfjskdfjsdfkjsdfkjsdfkjsdf",
)

# ================= DEBUG =================
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

# ================= ALLOWED_HOSTS =================
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

# ================= INSTALLED APPS =================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "main",
    "accounts",
]

# ================= MIDDLEWARE =================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# ================= TEMPLATES =================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"

# ================= DATABASE =================
import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}

# ================= AUTH PASSWORD VALIDATORS =================
AUTH_PASSWORD_VALIDATORS = []

# ================= INTERNATIONALIZATION =================
LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

# ================= STATIC FILES =================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ================= MEDIA FILES =================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
WHITENOISE_SERVE_MEDIA = True

# ================= DEFAULT =================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ================= LOGIN/LOGOUT =================
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# ================= COOKIES =================
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = 315360000
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ================= CORS =================
RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
CORS_ALLOWED_ORIGINS = [f"https://{RAILWAY_DOMAIN}"] if RAILWAY_DOMAIN else []
CSRF_TRUSTED_ORIGINS = [f"https://{RAILWAY_DOMAIN}"] if RAILWAY_DOMAIN else []

# ================= PUSH NOTIFICATIONS (VAPID) =================
VAPID_PRIVATE_KEY = os.environ.get(
    "VAPID_PRIVATE_KEY",
    "-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg51WPYupFD1DEjcj+\nIUvH8zZGqnvxOtKoFTHKlWArwpahRANCAARF/zS3swd0rKN8RYNXn+y2XLHx+uHv\nYQCxGZWXW7ggb74Kc921hF9un8FU+oFD8pM9yWb24UTz0E8pnVtkNsqo\n-----END PRIVATE KEY-----",
)
VAPID_PUBLIC_KEY = os.environ.get(
    "VAPID_PUBLIC_KEY",
    "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAERf80t7MHdKyjfEWDV5/stlyx8frh\n72EAsRmVl1u4IG++CnPdtYRfbp/BVPqBQ/KTPclm9uFE89BPKZ1bZDbKqA==\n-----END PUBLIC KEY-----",
)
VAPID_CLAIM_EMAIL = os.environ.get("VAPID_CLAIM_EMAIL", "admin@ithouse.uz")
