# MEMORY — Decisiones Técnicas

> Proyecto: **Gestor de Proyectos con Roles**
> Propósito: registro continuo de decisiones técnicas (HARNESS → MEMORIA CONTINUA).
> Última actualización: 2026-11-23

---

## Entorno verificado (pre-flight)

- `.venv` activo: **Python 3.14.4**.
- **Django 6.1.3** (skills referencian 5.2 LTS → vigilar compatibilidad).
- `requirements.txt`: `asgiref==3.13.0`, `Django==6.1.3`, `sqlparse==0.6.1`.
- Estructura: `startproject` estándar (`planmanager/` config, `manage.py`, `db.sqlite3`, `requirements.txt`). Sin apps de negocio.
- **No es repo git** (se debe `git init`).
- `db.sqlite3` existe (131 KB) → probablemente migrado con `auth.User` por defecto; se sustituirá por PostgreSQL.
- Node **v22.22.1**, npm **9.2.0** disponibles (build Tailwind). Docker disponible; `psql` NO instalado localmente.
- `ai-skills-core` presente en `/home/jet/proyectos_lnx/Skills/ai-skills-core`.

---

## Decisiones de arquitectura (APROBADAS)

| # | Decisión | Justificación / Razonamiento |
|---|---|---|
| 1 | **Server-Driven** (DTL + HTMX 2.x + Alpine.js 3.x) | No hay requisito de SPA; Django server-rendered + HTMX por fragmentos + Alpine solo micro-estado. Alineado con `django-web-patterns` y `django-server-driven-fullstack`. |
| 2 | **PostgreSQL 16** (Docker Compose) | Skills recomiendan Postgres para producción; `psql` no está local, pero Docker sí. Cero hardcoding vía `DATABASE_URL`. |
| 3 | **Roles por proyecto** (`ProjectMembership` M2M `through`) | Un usuario puede tener distinto rol en cada proyecto (OWNER/MANAGER/MEMBER/VIEWER). Más realista que roles globales. M2M con `through` + `through_fields` explícitos + `unique_together`. |
| 4 | **CustomUser por email** | `username = None`, `USERNAME_FIELD="email"`, `UserManager` propio (evita `TypeError` en `createsuperuser`). |
| 5 | **App `users` / `core` / `projects` / `tasks`** | Modularidad por dominio; `core` aloja `SiteConfig` singleton + context processor + templates base. |
| 6 | **Tailwind CSS (darkMode: class) + Alpine** | Diseño moderno y eficiente, dark/light toggle, responsive mobile-first. Assets servidos localmente (zero CDN). |
| 7 | **i18n ES default / EN** | `LANGUAGE_CODE="es"`, `LANGUAGES=[("es","ES"),("en","EN")]`, `LOCALE_PATHS`, `LocaleMiddleware`, `makemessages`/`compilemessages`. |
| 8 | **Cero hardcoding** | Config vía `django-environ`/`.env`: `SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`. |
| 9 | **Calidad**: ruff + mypy (strict) + pytest | Skill `python-project-setup`; `pyproject.toml` único. |
| 10 | **Services vs Selectors** | Mutaciones en `services.py`, lecturas en `selectors.py`, vistas delgadas (clean architecture). |
| 11 | **Settings modulares** | `planmanager/settings/{base,local,production}.py`; `DJANGO_SETTINGS_MODULE=planmanager.settings.local`. |
| 12 | **Dependencias en `pyproject.toml`** | Fuente única (Django, django-environ, `psycopg[binary]`, Pillow) + extras dev (ruff, mypy, pytest). `psycopg` 3 (no `psycopg2`) por mejor soporte de wheels en Python 3.14. |
| 13 | **PostgreSQL vía Docker con credenciales en `.env`** | `docker-compose.yml` usa interpolación `${...}`; nunca credenciales hardcodeadas en el YAML. |
| 14 | **Índices en `ProjectMembership`** | `db_index=True` en `role`, `Meta.indexes=[("project","role")]`, helper `get_role()` cacheable para mixins (menos queries por request). |

> **Excepción a "src layout"**: la regla de oro de `python-project-setup` (src layout) **no aplica a apps Django**; Django usa `manage.py` + apps en la raíz. Registrada para evitar confusión en ejecución.

---

## Skills canónicas cargadas

- `python-project-setup` — entorno, pyproject, ruff/mypy/pytest, src layout, `.env`.
- `django-web-patterns` — CustomUser email, forms, señales idempotentes, M2M `through`, ownership, i18n.
- `django-server-driven-fullstack` — RBAC grupos/mixins, CustomUser, singleton config, server-driven.
- `frontend-tailwind-alpine` — Tailwind + Alpine, dark mode anti-FOUC, contraste inputs, responsividad, vendor local.

---

## Gotchas / antipatrones a vigilar

1. `AUTH_USER_MODEL` debe fijarse **antes** del primer `migrate` (Postgres).
2. `CustomUser` sin `UserManager` → `createsuperuser` falla.
3. `ModelForm` con `CharField password` guarda en texto plano → usar `UserCreationForm`.
4. M2M `self` con `through` invertido → fijar `through_fields`.
5. Señales `post_save` no idempotentes duplican perfiles en `loaddata`.
6. `delete()` masivo contra BD real → prohibido sin aprobación.
7. Inputs sin `@layer base` → texto invisible en dark (Chromium/Edge).
8. `overflow-x-hidden` rompe `sticky` → `overflow-x-clip`.
9. Anclas puras fallan entre páginas → URL canónica con `{% url %}#ancla`.
10. FOUC en dark mode → script inline antes del primer `<link>` CSS.
11. CDN externo de HTMX/Alpine → servir desde `static/js/vendor/`.
12. Django 6.1.3 vs skills "5.2 LTS" → validar `django-environ`, crispy-forms (si se usa).
13. `psycopg2` puede carecer de wheels para Python 3.14 → usar `psycopg[binary]` (psycopg 3); validar `mypy`/`Pillow` sobre 3.14 antes de congelar versiones.
14. `db.sqlite3` ya migrado con `auth.User` nativo → descartar y hacer primera migración limpia en Postgres.

---

## Matriz de roles (por proyecto)

| Acción | OWNER | MANAGER | MEMBER | VIEWER |
|---|---|---|---|---|
| Ver proyecto/tareas | ✅ | ✅ | ✅ | ✅ |
| Crear/editar tareas | ✅ | ✅ | ✅ (propias) | ❌ |
| Asignar tareas | ✅ | ✅ | ❌ | ❌ |
| Comentar | ✅ | ✅ | ✅ | ❌ |
| Adjuntar archivos | ✅ | ✅ | ✅ | ❌ |
| Gestionar miembros/roles | ✅ | ❌ | ❌ | ❌ |
| Editar/eliminar proyecto | ✅ | ❌ | ❌ | ❌ |

---

## Lecciones aprendidas

_(Se irán registrando tras cada hito de ejecución.)_
