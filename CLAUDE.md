# CLAUDE.md — Estación 5 PackIA (Supervisión y Trazabilidad)

## Reglas de trabajo (prioridad máxima)

1. **No hacer cambios sin autorización explícita.** Analizar, proponer y explicar es libre; crear, editar, borrar archivos, instalar dependencias o ejecutar comandos que modifiquen algo requiere que el usuario lo apruebe antes. Si hay duda, preguntar.
2. **Commits sin co-autor de Claude.** Nunca agregar `Co-Authored-By` ni líneas de atribución a Claude en commits ni en descripciones de PR.
3. **No hacer commit, push ni abrir PR sin que se pida.** Proponer el mensaje y esperar la orden.
4. **Nunca trabajar directo en `main`.** Una rama por tarea (`feat/a-...`, `feat/b-...`, `feat/c-...`, `docs/...`, `fix/...`).
5. Idioma: español en documentación, mensajes de commit y respuestas. Commits cortos, en minúsculas, entendibles y sin descripción larga.

## Documentación que hay que conocer antes de actuar

Leer lo que corresponda a la tarea:

| Archivo | Contenido |
|---|---|
| `README.md` | Estado, endpoints y ejecución local (parte puede estar desactualizada) |
| `docs/plan/plan-avance-e5.md` | **Plan general**: decisiones, contratos v2, modelo de BD, API objetivo, reglas de anomalías, plan por semana, despliegue en Raspberry Pi 5 |
| `docs/plan/rol-a-backend.md` | Plan individual de Gabriel (backend y datos) |
| `docs/plan/rol-b-integracion.md` | Plan individual de Maicol (integración y calidad) |
| `docs/plan/rol-c-dashboard.md` | Plan individual de Christian (dashboard) |
| `docs/trelo/semana2.md` | Bitácora de la semana 2 |
| `docs/formato_datos/*.json` | Contratos de datos por estación |

Si el código y la documentación se contradicen, avisar al usuario antes de decidir cuál manda.

## Equipo

| Rol | Persona | Área |
|---|---|---|
| A — Backend y datos | Gabriel | `app/` |
| B — Integración y calidad | Maicol | contratos, `tests/`, `tools/`, Docker |
| C — Dashboard | Christian | `frontend/` |

El usuario de esta sesión es normalmente **Christian (rol C)**; confirmar si no queda claro. No tocar el área de otro rol sin avisar.

## Decisiones confirmadas

- Transporte con **cinta transportadora** (no carrito); E6 informa `estado_cinta`.
- Seguimiento por **grupo de frutas**; E2, E3 y E4 informan **por fruta** (`id_grupo`, `id_fruta`).
- **E3** informa `diametro_mm` y `tamano` (`pequeno | mediano | grande`), por ejemplo 40 mm → mediano. E5 guarda lo que llega y no recalcula el tamaño.
- Equipo de E5: **Raspberry Pi 5** (ARM64, OS de 64 bits) con monitor en modo kiosko.
- Base de datos: **SQLite en modo WAL** (PostgreSQL solo como opción vía `DATABASE_URL`).
- Frontend sin framework (HTML/CSS/JS), servido por la misma API; *polling* y luego SSE si hay tiempo.

**Contratos:** los JSON de `docs/formato_datos/` son la fuente de verdad. Un cambio de campos se actualiza primero en el contrato y se avisa al equipo; después `schemas.py`, la BD y el frontend.

## Stack

Python 3.11, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0, SQLite, Docker/Compose, pytest. Frontend en HTML, CSS y JavaScript.

## Estado del código (verificar antes de asumir)

- `app/main.py`: endpoints `POST /api/v1/ingest/e1|e2|e3|e4|e6` que validan pero **no guardan**.
- `app/schemas.py` y `docs/formato_datos/`: todavía en formato v1 (por caja); falta migrar a v2.
- `app/script.sql`: esquema v1, no coincide con los schemas.
- `frontend/prototipo2/`: último prototipo, con datos simulados. `frontend/index.html` es una copia de `prototipo1`.

## Cómo ejecutar

```bash
docker compose up --build        # API en http://localhost:8000 (docs en /docs)
# o, sin Docker:
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Al proponer o hacer cambios

- Explicar qué se va a cambiar y en qué archivos **antes** de hacerlo, y esperar el visto bueno.
- Cambios pequeños y enfocados en la tarea; sin refactors ni mejoras no pedidas.
- Mantener sincronizados contrato, `schemas.py`, BD y frontend.
- Reportar con honestidad lo que se probó y lo que no (por ejemplo, nada se ha probado aún en la Raspberry Pi).
