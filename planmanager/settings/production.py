"""
Settings de producción.

Usar con: DJANGO_SETTINGS_MODULE=planmanager.settings.production
Despliegue: Gunicorn + nginx (reverse proxy) servido por HTTP en el puerto 8010.
"""

from .base import *  # noqa: F403
from .base import env

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# WhiteNoise sirve los estáticos en producción (tras `collectstatic`).
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Cookies: False porque el sitio se sirve por HTTP (sin TLS) en el puerto 8010.
# Si se monta HTTPS (nginx + Let's Encrypt), restaurar a True y añadir
# SECURE_PROXY_SSL_HEADER y CSRF_TRUSTED_ORIGINS.
SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False
