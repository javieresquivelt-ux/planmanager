# SPEC — Especificaciones

> Proyecto: **Gestor de Proyectos con Roles**
> Documento de especificación funcional y técnica (versión 1.0).
> Última actualización: 2026-11-23

---

## 1. Visión general

Aplicación web de **gestión de proyectos** con control de acceso basado en **roles por proyecto**. Permite crear proyectos, organizar tareas, comentar y adjuntar archivos, y consultar un **dashboard** de actividad. Orientada a equipos que necesitan colaboración con permisos granulares, interfaz **moderna, responsive** y soporte **bilingüe (ES/EN)** con **modo claro/oscuro**.

---

## 2. Objetivos

- Gestión completa de proyectos, tareas, comentarios y adjuntos.
- Control de acceso por **rol dentro de cada proyecto**.
- Autenticación por **email** (sin username).
- Interfaz server-driven, responsive y accesible.
- Internacionalización **ES (default)** / **EN**.
- Tema **claro/oscuro** persistente.

---

## 3. Alcance (MVP extendido)

**Incluido (v1):**
- Autenticación (registro, login, logout, perfil).
- CRUD de Proyectos con membresías y roles.
- CRUD de Tareas (estado, prioridad, fecha límite, asignación).
- Comentarios en tareas.
- Adjuntos de archivos en tareas.
- Dashboard por usuario/proyecto.
- UI responsive + dark/light + i18n ES/EN.

**Fuera de alcance (v1):**
- Notificaciones por email / push.
- Búsqueda de texto completo (full-text search).
- Tableros Kanban/calendario avanzados.
- Pagos / suscripciones.
- API REST pública (DRF).

---

## 4. Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Django 6.1.x (server-rendered, sin DRF) |
| Frontend | DTL + HTMX 2.x + Alpine.js 3.x |
| Estilos | Tailwind CSS (darkMode: class), mobile-first |
| Base de datos | PostgreSQL 16 (Docker Compose) |
| Config | `django-environ` + `.env` (cero hardcoding); settings modulares `planmanager/settings/{base,local,production}.py` |
| Dependencias | `pyproject.toml` (fuente única) + extras dev; `psycopg[binary]` (psycopg 3) |
| Calidad | ruff + mypy (strict) + pytest |
| i18n | `gettext` (ES default / EN), `LocaleMiddleware` |
| Build front | Node/npm (`npm ci`, Tailwind CLI) |
| Despliegue | gunicorn + WhiteNoise (producción, posterior) |

---

## 5. Arquitectura

- **Server-Driven por defecto**: DTL renderiza páginas; HTMX actualiza fragmentos; Alpine maneja micro-estado (modales, menú, toggles de tema/idioma).
- **Modular por dominio**: apps `users`, `core`, `projects`, `tasks`.
- **Separación de capas**: mutaciones en `services.py`, lecturas en `selectors.py`, vistas delgadas.
- **Singleton de configuración** (`SiteConfig`) inyectado por context processor.

### Estructura de apps

```
planmanager/
├── settings/               # base.py / local.py / production.py
├── core/                   # SiteConfig, base templates, context processor
├── users/                  # CustomUser, auth, perfil
├── projects/               # Project + ProjectMembership (roles)
└── tasks/                  # Task + Comment + Attachment
```

---

## 6. Modelo de datos

### `users.User` (CustomUser)
- `email` (unique, identificador), `password`, `is_active`, `is_staff`, `is_superuser`.
- `USERNAME_FIELD = "email"`, `REQUIRED_FIELDS = []`, `UserManager` propio.

### `projects.Project`
- `name`, `description`, `owner` (FK User), `created_at`, `updated_at`.

### `projects.ProjectMembership` (M2M `through`)
- `project` (FK), `user` (FK), `role` (choices), `joined_at`.
- `unique_together = ("project", "user")`.
- Optimización: `db_index=True` en `role`; `Meta.indexes = [Index(fields=["project", "role"])]`; helper `get_role(user, project)` cacheable por request.

### `tasks.Task`
- `project` (FK), `title`, `description`, `assignee` (FK User, nullable), `status`, `priority`, `due_date`, `created_by`, `created_at`, `updated_at`.

### `tasks.Comment`
- `task` (FK), `author` (FK User), `body`, `created_at`.

### `tasks.Attachment`
- `task` (FK), `uploaded_by` (FK User), `file` (FileField → `media/`), `created_at`.

### Enumeraciones
- `role`: `OWNER`, `MANAGER`, `MEMBER`, `VIEWER`.
- `status`: `TODO`, `IN_PROGRESS`, `REVIEW`, `DONE`.
- `priority`: `LOW`, `MEDIUM`, `HIGH`, `URGENT`.

---

## 7. Roles y permisos (RBAC por proyecto)

| Acción | OWNER | MANAGER | MEMBER | VIEWER |
|---|---|---|---|---|
| Ver proyecto/tareas | ✅ | ✅ | ✅ | ✅ |
| Crear tarea | ✅ | ✅ | ✅ | ❌ |
| Editar tarea | ✅ | ✅ | ✅ (propias) | ❌ |
| Asignar tarea | ✅ | ✅ | ❌ | ❌ |
| Cambiar estado/prioridad | ✅ | ✅ | ✅ (propias) | ❌ |
| Comentar | ✅ | ✅ | ✅ | ❌ |
| Adjuntar archivo | ✅ | ✅ | ✅ | ❌ |
| Gestionar miembros/roles | ✅ | ❌ | ❌ | ❌ |
| Editar/eliminar proyecto | ✅ | ❌ | ❌ | ❌ |

Enforcement vía mixins `UserPassesTestMixin` (`ProjectMemberRequiredMixin`, `ProjectManagerRequiredMixin`, ownership check).

---

## 8. Funcionalidades por módulo

### Autenticación
- Registro con email + contraseña (hasheada vía `UserCreationForm`).
- Login/logout; perfil editable.

### Proyectos
- Listado de proyectos del usuario.
- Crear proyecto (owner automático).
- Invitar/gestionar miembros y roles (OWNER).
- Editar/eliminar (OWNER).

### Tareas
- Listado y filtros por estado/prioridad/asignado.
- Crear/editar/eliminar (según rol).
- Asignación y fechas límite.

### Comentarios y adjuntos
- Hilos de comentarios por tarea (HTMX sin recarga).
- Subida de adjuntos a `media/`.

### Dashboard
- Resumen de proyectos activos, tareas por estado, prioridades y actividad reciente.

---

## 9. UI/UX

- **Full responsive**: mobile-first, sin scroll horizontal (360–390 px).
- **Diseño moderno**: Tailwind, design tokens, color primario corporativo, tipografía local (WOFF2).
- **Dark/light mode**: estrategia `class`, script anti-FOUC, persistencia en `localStorage`, respeta `prefers-color-scheme`.
- **Accesibilidad**: contraste explícito en inputs (light/dark), foco visible.
- **Cero CDN**: HTMX/Alpine/fuentes servidos desde `static/`.

---

## 10. Internacionalización

- `LANGUAGE_CODE = "es"`, `LANGUAGES = [("es","ES"),("en","EN")]`, `LOCALE_PATHS = [BASE_DIR/"locale"]`.
- Cadenas de modelo con `gettext_lazy`; plantillas con `{% trans %}`/`{% blocktrans %}`.
- Toggle de idioma 1-clic (`set_language`) en navbar.
- `makemessages -l en -l es` + `compilemessages`.

---

## 11. Seguridad

- Contraseñas siempre hasheadas (nunca texto plano).
- `AUTH_USER_MODEL` definido antes de la primera migración.
- Autorización backend en cada vista de escritura (nunca confiar en UI).
- Secrets via `.env` (`.env` en `.gitignore`; `.env.example` commiteado).
- `DEBUG=False`, `ALLOWED_HOSTS` correctos en producción.
- CSRF en formularios y peticiones HTMX/AJAX.

---

## 12. Calidad y testing

- `pyproject.toml` único (ruff + mypy strict + pytest).
- Type hints en funciones públicas.
- Tests: managers (`create_user`/`create_superuser`), señales, ownership (403), matriz de roles, comentarios/adjuntos, dashboard.
- Criterio de aceptación: `ruff check`, `mypy`, `pytest` en verde + checklist de skills.

---

## 13. Criterios de aceptación (Definition of Done)

- [ ] `manage.py check` sin errores; migraciones aplicadas en Postgres.
- [ ] `createsuperuser` funciona (CustomUser + UserManager).
- [ ] CRUD de proyectos/tareas respeta la matriz de roles.
- [ ] Comentarios y adjuntos operativos.
- [ ] Dashboard sin queries N+1.
- [ ] Dark/light mode sin parpadeo (anti-FOUC) y persistente.
- [ ] i18n ES/EN funcional (toggle + traducciones).
- [ ] Responsive verificado en breakpoints móviles.
- [ ] `ruff`, `mypy`, `pytest` en verde.
