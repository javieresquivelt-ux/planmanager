#!/bin/sh
# ===========================================================================
# entrypoint.sh — Auto-provisionamiento idempotente (Docker CI/CD)
# Skill: docker-cicd-deployment
# Puerto fijado en 8010 (EasyPanel inyecta PORT=80, que rompería Gunicorn).
# ===========================================================================
set -e

echo "==> Recolectando estáticos (WhiteNoise)..."
python manage.py collectstatic --noinput

echo "==> Aplicando migraciones..."
python manage.py migrate --noinput

if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "==> Creando superusuario inicial (idempotente)..."
    python manage.py createsuperuser --noinput || true
fi

PORT=8010
echo "==> Arrancando Gunicorn en 0.0.0.0:${PORT}..."
exec gunicorn planmanager.wsgi:application \
    --bind 0.0.0.0:${PORT} \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
