#!/usr/bin/env bash
# =============================================================================
# Despliegue de PlanManager en VPS Hostinger (aditivo y aislado, SIN nginx)
#
# REGLA DE ORO: NO TOCAR NADA EN PRODUCCIÓN.
#   - No toca el puerto 8000 (proyecto previo) ni Traefik (80/443).
#   - Gunicorn directo en 0.0.0.0:8010 + WhiteNoise (static y media).
#   - Paths propios: /opt/planmanager
#   - PostgreSQL propio: docker-compose en host 5433
#
# Uso (con shell completo en el VPS):
#   sudo bash deploy/deploy.sh <github_url>
#
# Requisitos previos del host (deben estar YA instalados):
#   python3.14, git, node/npm, docker + docker-compose-plugin.
# El script solo instala gettext.
# =============================================================================
set -euo pipefail

REPO_URL="${1:-https://github.com/javieresquivelt-ux/planmanager.git}"
APP_DIR="/opt/planmanager"
PYTHON="python3.14"
DOMAIN="cystec.cloud"

echo "==> [1/8] Verificando paquetes base (aditivo)"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
# Python 3.14, git, node/npm y Docker YA están instalados en este VPS.
# Solo se instala gettext (para `compilemessages` si hiciera falta).
apt-get install -y --no-install-recommends gettext

echo "==> [2/8] Clonando repositorio en $APP_DIR"
if [ -d "$APP_DIR/.git" ]; then
    git -C "$APP_DIR" pull --ff-only
else
    git clone "$REPO_URL" "$APP_DIR"
fi

echo "==> [3/8] Creando entorno virtual e instalando dependencias"
cd "$APP_DIR"
"$PYTHON" -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .

echo "==> [4/8] Variables de entorno (.env)"
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  !! Edita $APP_DIR/.env (SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS=$DOMAIN,<IP>) y vuelve a ejecutar."
    echo "  !! Luego reanuda desde el paso 5."
    exit 0
fi

echo "==> [5/8] Frontend (Tailwind) + estáticos"
npm ci
npm run build
.venv/bin/python manage.py collectstatic --noinput

echo "==> [6/8] Base de datos (PostgreSQL vía Docker Compose)"
docker compose up -d db
.venv/bin/python manage.py migrate
.venv/bin/python manage.py createsuperuser || true

echo "==> [7/8] Servicio systemd (Gunicorn directo en :8010)"
install -m 644 deploy/planmanager.service /etc/systemd/system/planmanager.service
systemctl daemon-reload
systemctl enable --now planmanager

echo "==> [8/8] Firewall"
ufw allow 8010/tcp || true

echo ""
echo "Despliegue completado. Acceso: http://$DOMAIN:8010/"
echo "Verificar: curl -I http://localhost:8010/"
echo "DNS (Hostinger): registro A @ -> IP pública del VPS (TTL 300)."
