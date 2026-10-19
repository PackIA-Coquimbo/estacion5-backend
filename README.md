# Estación 5 - Backend PackIA

Backend desarrollado en FastAPI para la ingestión de datos de la Estación 5 del proyecto PackIA. El servicio centraliza la recepción de eventos de las cajas de papayas y valida el formato de cada payload mediante modelos Pydantic antes de aceptar la petición.

## Estado actual del proyecto

La implementación actual incluye:

- API REST con FastAPI
- Endpoint de salud para verificar que el servicio está operativo
- Endpoints de ingestión para las estaciones E1, E2, E3, E4 y E6
- Modelos de validación para cada payload usando Pydantic
- Configuración Docker para levantar la API localmente
- Esquema SQL base para persistencia relacional de lotes y cajas

## Alcance implementado

### Endpoints disponibles

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Verifica que el backend está activo |
| POST | `/api/v1/ingest/e1` | Ingesta datos de recepción y captura |
| POST | `/api/v1/ingest/e2` | Ingesta datos de análisis visual de calidad |
| POST | `/api/v1/ingest/e3` | Ingesta datos de calibre y consistencia física |
| POST | `/api/v1/ingest/e4` | Ingesta datos de clasificación comercial final |
| POST | `/api/v1/ingest/e6` | Ingesta datos del estado del carrito |

### Validaciones implementadas

Se define un modelo base con los siguientes campos comunes:

- `id_lote`
- `id_caja`
- `timestamp`

Cada estación tiene un payload específico con datos propios, por ejemplo:

- `E1`: validez de imagen, estado de captura y posición correcta
- `E2`: calidad visual, confianza visual y defectos detectados
- `E3`: peso total, nivel de llenado, cantidad de frutas visibles y consistencia física
- `E4`: categoría final, probabilidad y revisión manual
- `E6`: estado del carrito, posición actual y falla mecánica

## Estructura del proyecto

```text
estacion5-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   └── script.sql
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .gitignore
```

### Archivos principales

- `app/main.py`: definición de la aplicación FastAPI y endpoints de ingestión.
- `app/schemas.py`: modelos Pydantic con la estructura de cada payload.
- `app/script.sql`: esquema base para tablas de lote y caja.
- `docker-compose.yml`: definición del servicio del backend para ejecución local.
- `Dockerfile`: imagen base y comando de inicio del servicio.

## Ejecución local

### Opción 1: Docker Compose

```bash
docker compose up --build
```

La API queda disponible en:

- `http://localhost:8000/`
- `http://localhost:8000/docs` (Swagger UI)

### Opción 2: Ejecutar directamente con uvicorn

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Observaciones de diseño

El backend ya ofrece la capa de API y validación de entrada requerida para la ingestión de datos de la Estación 5. En la implementación actual, la lógica de persistencia en base de datos aún está preparada como base estructural a nivel de esquema (`script.sql`), pero no se ha conectado todavía a una BD real ni se han implementado operaciones de almacenamiento persistente dentro del servicio.

Esto significa que, por ahora, el sistema funciona como API de recepción y validación de payloads, con la base para integrar la persistencia en fases posteriores.

## Tecnologías utilizadas

- Python 3.11
- FastAPI
- Pydantic
- Uvicorn
- Docker / Docker Compose

## Próximo alcance sugerido

- Conexión real con base de datos relacional
- Persistencia de eventos por estación y caja
- Registro de lotes/cajas con trazabilidad
- Validaciones de negocio más específicas por estación
- Endpoints de consulta y consulta histórica
- Mecanismo de autenticación y seguridad para exposición externa
