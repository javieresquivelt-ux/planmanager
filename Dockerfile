# ===========================================================================
# Dockerfile — PlanManager (multi-stage)
# Skill: docker-cicd-deployment + easypanel-deployment
# Puerto interno de Gunicorn: 8010 (el 8000 lo usa el proyecto previo).
# ===========================================================================

# --- Stage 1: compilar Tailwind CSS (node no va a la imagen final) ---
FROM node:22-alpine AS frontend-builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY tailwind.config.js ./
COPY templates/ ./templates/
COPY static/css/input.css ./static/css/input.css
RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/dist/main.css --minify

# --- Stage 2: runtime Python de producción ---
FROM python:3.14-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=planmanager.settings.production \
    PORT=8010

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias (pyproject.toml como fuente única)
COPY pyproject.toml ./
COPY planmanager/ ./planmanager/
RUN pip install --no-cache-dir -e .

# Copiar el resto de la aplicación y el CSS compilado en el stage 1
COPY . .
COPY --from=frontend-builder /app/static/css/dist/main.css /app/static/css/dist/main.css

RUN useradd -m -u 1000 django && chown -R django:django /app
USER django

EXPOSE 8010
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
