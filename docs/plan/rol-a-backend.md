# Plan individual — Rol A: Backend y datos

**Dueño de:** `app/` (schemas, BD, endpoints, reglas)
**Revisa PRs de:** C · **Tus PRs los revisa:** B
**Meta del sprint de recuperación (5 días):** la API guarda en BD con contratos v2 y expone consultas, métricas y alertas para que C conecte el dashboard.

> Estamos atrasados: **nada de pulir**. Primero lo que desbloquea a B y C. Si una tarea se complica más de medio día, se avisa en el chat y se recorta el alcance.

## Ruta crítica (lo que otros esperan de ti)

| Entrega | Quién la espera | Fecha límite |
|---|---|---|
| Contratos v2 cerrados (con B) | B, C | **Día 1, mediodía** |
| `schemas.py` v2 + ingesta que guarda en BD | B (simulador), C | **Día 2** |
| Endpoints `GET` de grupos y métricas | C | **Día 3** |
| Alertas y estado de estaciones | C | **Día 4** |

## Día 1 — Contratos y schemas
- [ ] Con B, cerrar los JSON v2 (sección 2 del plan general). Decisión por defecto si no hay respuesta de otros grupos: **E1 asigna `id_grupo` e `id_fruta`**.
- [ ] Reescribir `app/schemas.py`:
  - `estacion: Literal["E1"]` (etc.), distinto por modelo.
  - Valores cerrados como `Literal`/`Enum` (`estado_captura`, `calidad_visual`, `tamano`, `categoria_final`, `estado_cinta`).
  - `id_grupo`, lista `frutas` en E2, E3 y E4; E6 con `estado_cinta`.
  - `timestamp: AwareDatetime` (con zona horaria). Reemplazar `Field(example=...)` por `json_schema_extra`.
- [ ] Validar `diametro_mm > 0` y `confianza`/`probabilidad` entre 0 y 1.
- [ ] Rama: `feat/a-contratos-v2` → PR a B.

## Día 2 — Persistencia
- [ ] Agregar `sqlalchemy==2.0.*` a `requirements.txt`.
- [ ] `app/db.py`: engine desde `DATABASE_URL` (por defecto `sqlite:///./e5.db`), `SessionLocal`, `get_db`.
- [ ] `app/models.py`: `Lote`, `Grupo`, `Fruta` (único `(id_grupo, id_fruta)`), `Lectura`, `Alerta`, `EventoCinta`.
- [ ] `Base.metadata.create_all` al iniciar la app (sin Alembic por ahora).
- [ ] Rutas de ingesta: guardar `Lectura` con el JSON crudo, crear lote/grupo si no existen y hacer *upsert* de frutas.
- [ ] Reemplazar `app/script.sql` por el esquema nuevo (o borrarlo si `create_all` lo cubre) y actualizar el README.
- [ ] Rama: `feat/a-persistencia` → PR a B.

**Terminado cuando:** enviar el mismo mensaje dos veces no duplica filas, y B puede correr el simulador contra tu API.

## Día 3 — Consultas y métricas
- [ ] `GET /api/v1/lotes`, `GET /api/v1/lotes/{id}/grupos?limit=20`, `GET /api/v1/grupos/{id}` (trazabilidad con frutas y lecturas).
- [ ] `GET /api/v1/metricas?lote=`: frutas por hora, % de rechazo, conteo por categoría y por tamaño, anomalías por estación.
- [ ] Activar `CORSMiddleware` (en desarrollo, `allow_origins=["*"]`).
- [ ] Avisar a C con la URL y un ejemplo de respuesta de cada endpoint (pegarlo en el PR).

## Día 4 — Reglas, alertas y estado
- [ ] `app/config.py` con los umbrales (confianza mínima 0,70, tendencia 3 de 12, diferencia máxima de diámetro, segundos sin señal).
- [ ] `app/reglas.py`: función `evaluar(lectura) -> list[Alerta]` según la tabla de anomalías del plan general. Se llama desde cada ruta de ingesta.
- [ ] `GET /api/v1/alertas?activas=true`, `PATCH /api/v1/alertas/{id}`, `GET /api/v1/estaciones/estado` (online o sin señal por estación).
- [ ] B escribirá los tests de las reglas: dejar `evaluar` como función pura, sin depender de la BD.

## Día 5 — Cierre del sprint
- [ ] Corregir lo que encuentren B y C al integrar.
- [ ] Quitar `--reload` del `CMD` del Dockerfile y dejarlo solo en `docker-compose` (con B).
- [ ] Arreglar detalles: título "Supervición", `datetime.utcnow` obsoleto.
- [ ] Actualizar README (estado actual, endpoints, cómo correr).
- [ ] Si sobra tiempo: endpoint SSE `/api/v1/stream`.

## Si vas justo de tiempo, recorta en este orden
1. SSE (C usa *polling* cada 2–5 s).
2. Endpoint `PATCH` de alertas.
3. Alembic (nunca entró en el sprint).

**No se recorta:** contratos v2, persistencia con *upsert*, trazabilidad de un grupo, métricas.

## Riesgos propios
- Los otros grupos cambian campos → todo cambio entra primero al contrato JSON y se avisa.
- Mensajes de E2–E4 llegan antes que E1 → el *upsert* debe crear el grupo si no existe.
