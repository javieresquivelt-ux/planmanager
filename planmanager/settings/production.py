"""
Settings de producción.

Usar con: DJANGO_SETTINGS_MODULE=planmanager.settings.production
Completar endurecimiento (WhiteNoise, HSTS, etc.) en la fase de despliegue.
"""

from .base import *  # noqa: F403
from .base import env

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True
