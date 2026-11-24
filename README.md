# Gestor de Proyectos con Roles

Aplicación web de **gestión de proyectos** con control de acceso basado en **roles por proyecto**. Permite crear proyectos, organizar tareas, comentar y adjuntar archivos, y consultar un **dashboard** de actividad. Orientada a equipos que necesitan colaboración con permisos granulares, interfaz **moderna y responsive**, soporte **bilingüe (ES/EN)** y **modo claro/oscuro**.

---

## Características (MVP extendido)

- **Autenticación** por email (registro, login, logout, perfil).
- **Proyectos**: CRUD completo con membresías y roles.
- **Tareas**: estado, prioridad, fecha límite y asignación.
- **Comentarios** en tareas (sin recarga, vía HTMX).
- **Adjuntos** de archivos en tareas.
- **Dashboard** por usuario/proyecto.
- **Roles por proyecto**: `OWNER`, `MANAGER`, `MEMBER`, `VIEWER`.
- **UI responsive** (mobile-first) con **dark/light mode**.
- **Internacionalización**: español (default) e inglés.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Django 6.1.x (server-rendered, sin DRF) |
| Frontend | DTL + HTMX 2.x + Alpine.js 3.x |
| Estilos | Tailwind CSS (`darkMode: "class"`), mobile-first |
| Base de datos | PostgreSQL 16 (Docker Compose) |
| Config | `django-environ` + `.env` (cero hardcoding) |
| Calidad | ruff + mypy (strict) + pytest |
| i18n | `gettext` (ES default / EN) |
| Build front | Node/npm (Tailwind CLI) |

---

## Matriz de roles (por proyecto)

| Acción | OWNER | MANAGER | MEMBER | VIEWER |
|---|---|---|---|---|
| Ver proyecto/tareas | ✅ | ✅ | ✅ | ✅ |
| Crear tarea | ✅ | ✅ | ✅ | ❌ |
| Editar tarea | ✅ | ✅ | ✅ (propias) | ❌ |
| Asignar tarea | ✅ | ✅ | ❌ | ❌ |
| Comentar | ✅ | ✅ | ✅ | ❌ |
| Adjuntar archivo | ✅ | ✅ | ✅ | ❌ |
| Gestionar miembros/roles | ✅ | ❌ | ❌ | ❌ |
| Editar/eliminar proyecto | ✅ | ❌ | ❌ | ❌ |

---

## Estructura del proyecto

```
planmanager/
├── settings/               # base.py / local.py / production.py
├── core/                   # SiteConfig, templates base, context processor
├── users/                  # CustomUser, auth, perfil
├── projects/               # Project + ProjectMembership (roles)
└── tasks/                  # Task + Comment + Attachment
```

---

## Modelo de datos

- `users.User` — CustomUser con email como identificador (sin username).
- `projects.Project` — nombre, descripción, owner.
- `projects.ProjectMembership` — M2M `through` con `role`.
- `tasks.Task` — project, assignee, status, priority, due_date.
- `tasks.Comment` — task, author, body.
- `tasks.Attachment` — task, uploaded_by, file.

Enumeraciones: `role` (`OWNER`/`MANAGER`/`MEMBER`/`VIEWER`), `status` (`TODO`/`IN_PROGRESS`/`REVIEW`/`DONE`), `priority` (`LOW`/`MEDIUM`/`HIGH`/`URGENT`).

---

## Configuración local

```bash
# 1. Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 2. Configurar variables de entorno
cp .env.example .env   # y editar los valores

# 3. Levantar PostgreSQL
docker compose up -d db

# 4. Migrar y crear superusuario
python manage.py migrate
python manage.py createsuperuser
```

---

## Gobernanza

El desarrollo sigue la metodología **HARNESS** (`ANALIZAR → PLANIFICAR → APROBAR → EJECUTAR → REGISTRAR → APRENDER`) y el catálogo de skills **`ai-skills-core`**.

Documentos de proyecto:

- [`task.md`](task.md) — plan de trabajo y progreso.
- [`spec.md`](spec.md) — especificación funcional y técnica.
- [`memory.md`](memory.md) — decisiones técnicas y lecciones aprendidas.
- [`agent.md`](agent.md) — reglas de ingeniería del agente.
