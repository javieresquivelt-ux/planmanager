# Despliegue de PlanManager en EasyPanel (VPS Hostinger)

> Enfoque según las skills `docker-cicd-deployment` y `easypanel-deployment`.
> El puerto interno de Gunicorn es **8010** (el 8000 lo usa el proyecto previo).
> Traefik (de EasyPanel) expone el dominio con SSL automático; no se usa nginx ni systemd.

## Arquitectura

```
cystec.cloud (HTTPS, Let's Encrypt)
      │
      ▼
[ Traefik (EasyPanel) ]
      │
      └──▶ Contenedor PlanManager (Gunicorn 0.0.0.0:8010)
              ├── WhiteNoise sirve /static/
              └── /media/ en un volumen persistente
            └──▶ PostgreSQL (servicio EasyPanel, red interna)
```

## Pasos en EasyPanel

### 1. Crear el servicio de la app
1. **Apps → New service → App** → tipo de build **Dockerfile**.
2. Repositorio: `https://github.com/javieresquivelt-ux/planmanager.git` (rama `main`).
3. Dockerfile: `Dockerfile` (raíz).
4. **Port**: `8010`.
5. **Domain**: `cystec.cloud` (EasyPanel emitirá el certificado Let's Encrypt).

### 2. Volumen persistente (media/uploads)
- Mount Path: `/app/media`.
- (Los estáticos no necesitan volumen: `collectstatic` los regenera en cada deploy.)

### 3. Servicio PostgreSQL
1. **Services → Database → PostgreSQL** (one-click).
2. Anotar usuario, contraseña y nombre de BD.
3. El `DATABASE_URL` usará el nombre interno del servicio (ej. `postgres`).

### 4. Variables de entorno del servicio de la app

| Variable | Valor |
|---|---|
| `SECRET_KEY` | cadena aleatoria larga (`openssl rand -base64 42`) |
| `ALLOWED_HOSTS` | `cystec.cloud` |
| `DATABASE_URL` | `postgres://<usuario>:<password>@<host-postgres>:5432/<bd>` |
| `DJANGO_SUPERUSER_EMAIL` | `admin@cystec.cloud` |
| `DJANGO_SUPERUSER_PASSWORD` | contraseña segura |

> Nota: `DEBUG` ya está en `False` en `settings/production.py`; no se expone en env.

### 5. DNS en Hostinger
- Registro `A @` → IP pública del VPS (TTL 300).
- Esperar propagación; EasyPanel emitirá el SSL automáticamente.

## Verificación

```bash
curl -I https://cystec.cloud/          # 200 (o redirect a login)
```
- Login/registro funciona.
- `/static/` y `/media/` (avatares, adjuntos) se sirven.
- La base de datos y los uploads sobreviven a un redeploy (volumen).
