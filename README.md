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
├── docs/
│   ├── formato_datos/      # contratos JSON v2 por estación (fuente de verdad)
│   └── plan/               # plan general y planes por rol
├── frontend/               # dashboard (HTML, CSS y JS)
├── tests/                  # pytest: contratos e ingesta
├── tools/
│   └── simulador.py        # simula las estaciones E1–E4 y E6
├── Dockerfile
├── docker-compose.yml          # configuración base (Raspberry Pi)
├── docker-compose.override.yml # ajustes de desarrollo (--reload)
├── .env.example
├── requirements.txt
├── requirements-dev.txt        # pytest y httpx
├── README.md
└── .gitignore
```

### Archivos principales

- `app/main.py`: definición de la aplicación FastAPI y endpoints de ingestión.
- `app/schemas.py`: modelos Pydantic con la estructura de cada payload.
- `app/script.sql`: esquema base para tablas de lote y caja.
- `docker-compose.yml`: servicio del backend con reinicio automático, `healthcheck` y volumen persistente para la base de datos.
- `docker-compose.override.yml`: solo para desarrollo; agrega `--reload` y monta el código.
- `Dockerfile`: imagen de producción (sin `--reload`).
- `docs/formato_datos/`: contratos de datos v2; ver su [README](docs/formato_datos/README.md).
- `tools/simulador.py`: envía datos simulados de las estaciones a la API.

## Ejecución local

### Opción 1: Docker Compose (desarrollo)

```bash
docker compose up --build
```

Docker suma automáticamente `docker-compose.override.yml`, así que los cambios en `app/` y `frontend/` se recargan sin reconstruir la imagen. Para cambiar el puerto, la base de datos o la zona horaria, copiar `.env.example` como `.env` y editarlo.

La API queda disponible en:

- `http://localhost:8000/`
- `http://localhost:8000/docs` (Swagger UI)

Para detenerla: `docker compose down` (agregar `-v` borra también la base de datos).

### Opción 2: Ejecutar directamente con uvicorn

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Raspberry Pi 5 (producción)

Requiere Raspberry Pi OS de 64 bits con Docker instalado. Se usa solo el archivo base, sin el override de desarrollo:

```bash
docker compose -f docker-compose.yml up -d --build
docker compose -f docker-compose.yml ps     # debe indicar "healthy"
```

El contenedor se reinicia solo si se cae o si la Pi se reinicia (`restart: unless-stopped`), y la base SQLite queda en el volumen `e5_datos`. *Pendiente: aún no se ha probado en la Pi real.*

## Contratos de datos

Los mensajes que envía cada estación están en [`docs/formato_datos/`](docs/formato_datos/) (versión 2: un mensaje por grupo de frutas). Son la fuente de verdad: si un campo cambia, se actualiza primero el contrato y se avisa al equipo.

## Pruebas

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate            # en Linux o macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

- `tests/test_contratos.py`: valida los JSON de `docs/formato_datos/` y los mensajes del simulador.
- `tests/test_ingesta.py`: cada contrato responde 201 y los mensajes inválidos responden 422. **Se saltan** mientras `app/schemas.py` siga en v1 y se activan solos con los schemas v2.

## Simulador de estaciones

Envía grupos de 2 a 5 frutas por E1 → E2 → E3 → E4 y el estado de la cinta (E6) a la API, para probar sin depender de las otras estaciones. Requiere `requirements-dev.txt`.

```bash
python tools/simulador.py --dry-run --grupos 2            # solo imprime los JSON
python tools/simulador.py --grupos 20                     # envía a http://localhost:8000
python tools/simulador.py --url http://IP-DE-LA-PI:8000 --grupos 0   # sin fin (Ctrl+C para detener)
```

| Opción | Efecto |
|---|---|
| `--velocidad 2` | el doble de rápido |
| `--falla-cinta` | la cinta falla a mitad de la simulación y luego se recupera |
| `--sin-e3` | E3 no envía (estación caída) |
| `--baja-confianza` | parte de las frutas de E2 con confianza < 0,70 |
| `--duplicados` | cada mensaje se envía dos veces |
| `--rangos 92,112` | cortes de diámetro en mm para pequeño, mediano y grande (por defecto `35,45`) |
| `--semilla 7` | repite exactamente la misma simulación |

Al terminar muestra cuántos mensajes fueron aceptados y cuántos tuvieron error.

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
