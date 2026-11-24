# TASK — Plan de Trabajo

> Proyecto: **Gestor de Proyectos con Roles**
> Metodología: **HARNESS** (`ANALIZAR → PLANIFICAR → APROBAR → EJECUTAR → REGISTRAR → APRENDER`)
> Skills canónicas: `ai-skills-core` (`/home/jet/proyectos_lnx/Skills/ai-skills-core`)
> Última actualización: 2026-11-23

---

## Estado global

| Ciclo | Estado |
|---|---|
| ANALIZAR | ✅ Completado (auditoría pre-flight) |
| PLANIFICAR | ✅ Completado (este documento + spec.md + memory.md) |
| APROBAR | ⏳ Pendiente de aprobación humana antes de ejecutar |
| EJECUTAR | ⬜ No iniciado |
| REGISTRAR | 🔄 Continuo (task.md / memory.md) |
| APRENDER | ⬜ Al cierre de cada hito |

---

## Decisiones aprobadas (del ciclo ANALIZAR)

- Arquitectura: **Server-Driven** — Django Templates (DTL) + HTMX + Alpine.js.
- Base de datos: **PostgreSQL 16** (vía Docker Compose).
- Alcance: **MVP extendido** (proyectos, tareas, comentarios, adjuntos, dashboard).
- Roles: **roles por proyecto** (membresía con rol: OWNER / MANAGER / MEMBER / VIEWER).
- UI: **full responsive**, diseño moderno, **dark/light mode**, **i18n ES (default) / EN**.

---

## Fases de ejecución

### Fase 0 — APROBAR (punto de control humano)
- [ ] Visto bueno explícito del plan antes de tocar el repositorio.
- [ ] Aprobación de cambios "destructivos": `git init`, migración `db.sqlite3` → PostgreSQL, migraciones iniciales.

### Fase 1 — Fundaciones (setup + CustomUser ANTES de migrar)
- [ ] `git init`, `.gitignore` (`.venv`, `.env`, `__pycache__`, `media/`, `staticfiles/`, `db.sqlite3`).
- [ ] `agent.md` (contexto del agente) en raíz con protocolo `ai-skills-core` y ruta canónica.
- [ ] `pyproject.toml` como fuente única: dependencias (`Django`, `django-environ`, `psycopg[binary]`, `Pillow`) + tooling (ruff + mypy strict + pytest); instalar con `pip install -e ".[dev]"`.
- [ ] **Validación de compatibilidad**: `psycopg[binary]` y `mypy` sobre Python 3.14 / Django 6.1.3 antes de congelar versiones.
- [ ] Settings modulares: `planmanager/settings/{base,local,production}.py`; `DJANGO_SETTINGS_MODULE=planmanager.settings.local`.
- [ ] `.env.example` + `.env` real (`django-environ`); cero hardcoding de `SECRET_KEY`, `DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`.
- [ ] `docker-compose.yml` para PostgreSQL 16 con credenciales vía `.env` (interpolación `${...}`, nunca hardcoded) + `healthcheck`; `DATABASES` desde `DATABASE_URL`.
- [ ] Descartar `db.sqlite3` (migrado con `auth.User` nativo) → primera migración limpia en Postgres.
- [ ] App `users`: `CustomUser` (login por email) + `UserManager` propio + `AUTH_USER_MODEL = "users.User"`.
- [ ] App `core`: `SiteConfig` singleton + context processor global; templates base; assets locales (HTMX/Alpine/Tailwind).
- [ ] Config de i18n: `LANGUAGE_CODE="es"`, `LANGUAGES`, `LOCALE_PATHS`, `LocaleMiddleware`.
- [ ] Primer `migrate` (en Postgres), `createsuperuser`, `manage.py check`.

### Fase 1.5 — Frontend / Sistema de Diseño (Tailwind + Alpine)
- [ ] `package.json` + `tailwind.config.js` (`darkMode: "class"`, color primario, fuente local).
- [ ] `@layer base` con contraste explícito de inputs en light/dark.
- [ ] Layout responsive mobile-first; `overflow-x-clip` en `<body>`.
- [ ] HTMX/Alpine servidos desde `/static/js/vendor/` (zero CDN).
- [ ] Script anti-FOUC dark mode antes del `<link>` CSS + toggle persistente (localStorage).
- [ ] Toggle de idioma 1-clic vía `set_language` (pill en navbar).

### Fase 2 — Autenticación
- [ ] Registro y login por email (`UserCreationForm`, nunca `CharField password` en `ModelForm`).
- [ ] Logout y vista de perfil; señal idempotente de auto-perfil.

### Fase 3 — Dominio: Proyectos, Roles por proyecto, Tareas
- [ ] App `projects`: `Project` (nombre, descripción, owner, timestamps).
- [ ] `ProjectMembership` (M2M `through` User↔Project) con `role` + `through_fields` + `unique_together`.
- [ ] Optimización de acceso: `db_index=True` en `role`, `Meta.indexes = [Index(fields=["project", "role"])]`, helper `ProjectMembership.get_role(user, project)` cacheable por request.
- [ ] App `tasks`: `Task` (FK Project, FK assignee, status, priority, due_date, descripción).
- [ ] `Comment` (FK Task, FK author) y `Attachment` (FK Task, `FileField` → `media/`).

### Fase 4 — Autorización (RBAC por proyecto)
- [ ] Mixins guard (`UserPassesTestMixin`): `ProjectMemberRequiredMixin`, `ProjectManagerRequiredMixin`, ownership.
- [ ] Matriz de permisos por rol; toda vista de escritura verifica permiso.

### Fase 5 — Vistas Server-Driven
- [ ] CRUD de proyectos y tareas (CBV + DTL).
- [ ] Fragmentos HTMX: añadir/editar tareas, comentarios, cambio de estado sin recarga.
- [ ] Alpine para micro-estado (modales, menú móvil, toggles).

### Fase 6 — Dashboard
- [ ] Panel por usuario/proyecto: conteos, tareas por estado, prioridades, actividad reciente.
- [ ] ORM optimizado (`select_related`/`prefetch_related`) sin N+1.

### Fase 7 — Calidad y Testing
- [ ] Tests pytest: managers, señales, ownership (403), matriz de roles, comentarios/adjuntos, dashboard.
- [ ] `ruff check`, `mypy`, `pytest` en verde.
- [ ] Check-list de skills: `python-project-setup`, `django-web-patterns`, `django-server-driven-fullstack`, `frontend-tailwind-alpine`.
- [ ] Verificación visual en breakpoints móviles (360–390 px).

### Fase 8 — REGISTRAR / APRENDER
- [ ] `task.md` y `memory.md` actualizados tras cada hito.
- [ ] Lecciones aprendidas registradas en `memory.md`.

---

## Gotchas críticos (de las skills)

1. `AUTH_USER_MODEL` **antes** del primer `migrate`.
2. `CustomUser` sin `UserManager` rompe `createsuperuser`.
3. M2M `through` con `through_fields` explícitos (roles por proyecto).
4. `input` sin `@layer base` → texto invisible en dark mode.
5. `overflow-x-hidden` rompe `sticky` → usar `overflow-x-clip`.
6. Anclas puras (`#seccion`) fallan entre páginas → URL canónica.
7. Parpadeo de tema (FOUC) → script previo al CSS.
8. Django **6.1.3** vs "5.2 LTS" de las skills (verificar compatibilidad de paquetes).
