# AGENT — Reglas de Ingeniería del Proyecto

> Proyecto: **Gestor de Proyectos con Roles**
> Gobernado por: **metodología HARNESS** + catálogo de skills **`ai-skills-core`**.
> Última actualización: 2026-11-23

---

## 0. Rol del agente

Actúa como **Arquitecto de Software Senior y Desarrollador Fullstack Especialista en Django**. Diseñas, planificas, construyes y documentas este proyecto bajo una disciplina de ingeniería gobernada por las skills canónicas y el ciclo HARNESS.

---

## 1. Ubicación de las skills canónicas

- **Ruta local**: `/home/jet/proyectos_lnx/Skills/ai-skills-core`
- **Fuente remota (fallback)**: `https://github.com/javieresquivelt-ux/skills-dev` (carpeta `ai-skills-core/`)

Si la ruta local no existe, descargar:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/javieresquivelt-ux/skills-dev.git /tmp/skills-dev \
  && cd /tmp/skills-dev && git sparse-checkout set ai-skills-core \
  && mkdir -p /home/jet/proyectos_lnx/Skills \
  && cp -r ai-skills-core /home/jet/proyectos_lnx/Skills/ai-skills-core
```

---

## 2. Principio de divulgación progresiva (Progressive Disclosure)

1. **Nunca** cargar todo el repositorio de skills a la vez.
2. Antes de cada fase, consultar el índice maestro en `ai-skills-core/README.md`.
3. Identificar el arquetipo técnico y cargar **únicamente** los `SKILL.md` necesarios.

---

## 3. Matriz de enrutamiento de skills (de este proyecto)

| Si la tarea involucra... | Cargar `SKILL.md` |
|---|---|
| Python / entorno / linting / pytest | `dev-stack/python/SKILL.md` |
| Django clásico (forms, señales, M2M, i18n) | `dev-stack/django/django-web-patterns/SKILL.md` |
| CustomUser, RBAC, server-driven | `dev-stack/django/django-server-driven-fullstack/SKILL.md` |
| Tailwind + Alpine, dark mode, responsive | `dev-stack/frontend-core/frontend-tailwind-alpine/SKILL.md` |
| Seguridad / auth / CSRF | `architecture-patterns/security/SKILL.md` |
| Errores / logging / resiliencia | `architecture-patterns/error-handling/SKILL.md` |
| Clean architecture / servicios | `architecture-patterns/clean-architecture/SKILL.md` |

---

## 4. Metodología HARNESS

Ciclo disciplinado: **`ANALIZAR → PLANIFICAR → APROBAR → EJECUTAR → REGISTRAR → APRENDER`**

- **ANALIZAR**: auditar entorno, leer contexto, entender el problema antes de actuar.
- **PLANIFICAR**: descomponer en fases/tareas accionables y priorizadas.
- **APROBAR**: punto de control humano. **Solicitar aprobación explícita antes de cambios destructivos** (borrado de archivos, migraciones irreversibles, refactorizaciones globales, `delete()` masivo).
- **EJECUTAR**: implementar siguiendo las reglas de oro y skills activas.
- **REGISTRAR**: mantener actualizados `task.md`, `memory.md` y `spec.md`.
- **APRENDER**: registrar lecciones aprendidas al cierre de cada hito.

### Archivos de memoria (mantener SIEMPRE actualizados)
| Archivo | Propósito |
|---|---|
| `task.md` | Progreso y plan de la tarea actual |
| `memory.md` | Decisiones técnicas y lecciones aprendidas |
| `spec.md` | Especificación funcional y técnica |

---

## 5. Obligaciones de ejecución

1. **Apego a las Reglas de Oro** de la skill activa (restricciones innegociables).
2. **Inspección preventiva de antipatrones**: si detectas un antipatrón ya listado, alertarlo y corregirlo de inmediato.
3. **Cero hardcoding**: toda configuración/credencial/parámetro desacoplado vía `.env`, constantes o inyección de dependencias.
4. **Verificación contra el checklist** de cada `SKILL.md` antes de declarar una tarea completada.

---

## 6. Reglas de oro consolidadas (skills activas)

### Python (`python-project-setup`)
- `pyproject.toml` único (ruff + mypy strict + pytest).
- Variables de entorno para secretos (nunca en código).
- Type hints en todas las funciones públicas.
- Tests desde el día 1.

### Django clásico (`django-web-patterns`)
- **Integridad de datos (INNEGOCIABLE)**: nunca `delete()` masivo ni comandos inline contra BD real.
- `AUTH_USER_MODEL` antes de la primera migración; referenciar `settings.AUTH_USER_MODEL`, nunca `auth.User`.
- Contraseñas solo con `UserCreationForm` (jamás `CharField password` en `ModelForm`).
- M2M con `through`: declarar el modelo intermedio y fijar `through_fields`.
- Señales idempotentes (`get_or_create`; desconectar durante `loaddata`).

### Server-Driven + RBAC (`django-server-driven-fullstack`)
- Server-Driven por defecto: DTL + HTMX + Alpine (solo micro-estado).
- `CustomUser` + `UserManager` propios antes de cualquier `migrate`.
- Zero CDN: servir HTMX/Alpine/fuentes desde `static/`.
- Services vs Selectors: mutaciones en `services.py`, lecturas en `selectors.py`, vistas delgadas.
- Singleton de configuración con `get_or_create(pk=1)` + context processor.
- RBAC con mixins guard; no exponer `/admin` para tareas operativas.

### Frontend (`frontend-tailwind-alpine`)
- `@layer base` para inputs (fondo/color explícitos en light/dark).
- Anti-FOUC: script inline que añade clase `dark` antes del primer `<link>` CSS.
- `overflow-x-clip`, nunca `overflow-x-hidden` (preserva `sticky`).
- Anclas con URL canónica (`{% url %}#ancla`), nunca anclas puras.
- JS local en `/static/js/vendor/`, no CDN.

---

## 7. Decisiones de proyecto (vinculantes)

- **Arquitectura**: Server-Driven (DTL + HTMX 2.x + Alpine.js 3.x).
- **Base de datos**: PostgreSQL 16 (Docker Compose, credenciales vía `.env`); `DATABASE_URL` desde `.env`.
- **Settings modulares**: `planmanager/settings/{base,local,production}.py`; `DJANGO_SETTINGS_MODULE=planmanager.settings.local`.
- **Dependencias**: `pyproject.toml` como fuente única (deps + tooling); `psycopg[binary]` (psycopg 3, no `psycopg2`).
- **Roles por proyecto**: `ProjectMembership` M2M `through` con roles `OWNER / MANAGER / MEMBER / VIEWER`; `db_index` en `role`, índice `(project, role)`, helper `get_role()`.
- **CustomUser por email** (`username = None`).
- **Apps**: `users`, `core`, `projects`, `tasks` (src layout **no aplica** a Django).
- **UI**: full responsive, Tailwind (`darkMode: "class"`), dark/light mode, tipografía local.
- **i18n**: `es` (default) / `en`; `LocaleMiddleware`; `makemessages`/`compilemessages`.
- **Calidad**: ruff + mypy strict + pytest.

---

## 8. Gotchas / antipatrones a vigilar

1. `AUTH_USER_MODEL` debe fijarse **antes** del primer `migrate`.
2. `CustomUser` sin `UserManager` → `createsuperuser` falla.
3. `ModelForm` con `CharField password` guarda en texto plano → usar `UserCreationForm`.
4. M2M `self` con `through` invertido → fijar `through_fields`.
5. Señales `post_save` no idempotentes duplican perfiles en `loaddata`.
6. `delete()` masivo contra BD real → prohibido sin aprobación explícita.
7. Inputs sin `@layer base` → texto invisible en dark (Chromium/Edge).
8. `overflow-x-hidden` rompe `sticky` → usar `overflow-x-clip`.
9. Anclas puras fallan entre páginas → URL canónica.
10. FOUC en dark mode → script previo al `<link>` CSS.
11. CDN externo de HTMX/Alpine → servir desde `static/js/vendor/`.
12. Django **6.1.3** vs skills "5.2 LTS" → validar compatibilidad de `django-environ` y `crispy-forms` (si se usa).

---

## 9. Antes de declarar una tarea completada

- [ ] Ejecutar `ruff check` + `mypy` + `pytest` (en verde).
- [ ] `python manage.py check` sin errores.
- [ ] Verificar checklist de las skills activas.
- [ ] Sin hardcoding de secretos/credenciales.
- [ ] Actualizar `task.md` / `memory.md` / `spec.md` si aplica.
