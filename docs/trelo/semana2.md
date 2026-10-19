# Resumen de Actividades y Checklist - Semana 2
**Proyecto:** PackIA  
**Módulo / Estación:** Estación 5 (Supervisión y Trazabilidad)  
**Grupo:** Grupo 5 (3 integrantes)  

---

## 1. Checklist de Entregables - Semana 2

- [x] **Ficha de Interfaz V2 Formalizada**
  - [x] Definición de Entradas, Procesamiento, Salidas y Manejo de Errores.
  - [x] Corrección conceptual: Establecer la unidad de proceso como **caja completa de papayas por lote** (no unidades individuales).
- [x] **Propuesta Técnica de Formato JSON (Payloads / Contratos de API)**
  - [x] Definición de esquemas JSON para Estación 1 (`E1_Payload`).
  - [x] Definición de esquemas JSON para Estación 2 (`E2_Payload`).
  - [x] Definición de esquemas JSON para Estación 3 (`E3_Payload`).
  - [x] Definición de esquemas JSON para Estación 4 (`E4_Payload`).
  - [x] Definición de esquemas JSON para Estación 6 (`E6_Payload`).
- [x] **Base de Datos y Modelo de Persistencia**
  - [x] Diseño del Modelo Entidad-Relación (E-R) relacional (`lote` 1:N `caja_item`).
  - [x] Definición DDL de tablas en PostgreSQL/SQLite.
  - [x] Creación de índice `idx_caja_lote` para optimización de consultas en el Dashboard.
  - [x] Definición de regla `ON DELETE CASCADE` para integridad referencial.
- [x] **Backend e Infraestructura de Ingesta Dockerizada**
  - [x] Configuración del repositorio y estructura de carpetas (`estacion5-backend`).
  - [x] Implementación de modelos de validación con **Pydantic v2**.
  - [x] Creación del servidor de ingesta asíncrono con **FastAPI** (`app/main.py`).
  - [x] Configuración del entorno en contenedores con **Dockerfile** y **Docker Compose**.
  - [x] Generación y validación de la especificación interactiva **OpenAPI / Swagger UI**.
- [x] **Consenso e Interoperabilidad**
  - [x] Redacción de propuesta técnica para comunicación inter-estaciones.
  - [x] Publicación de la especificación técnica en el canal común del proyecto.

---

## 2. Desarrollo de Actividades Realizadas

### Actividad 2.1: Formalización de la Ficha de Interfaz V2
Se definió la especificación técnica de entrada y salida para la Estación 5, asegurando que el flujo de datos corresponda a la inspección consolidada de la caja completa de papayas.

| Campo | Especificación Técnicamente Estandarizada |
| :--- | :--- |
| **Nombre de la estación** | Estación 5: Supervisión y Trazabilidad |
| **Grupo responsable** | Grupo 5 (3 estudiantes) |
| **Función de la estación** | Centralizar, almacenar, analizar y visualizar métricas de rendimiento por caja/lote y detectar anomalías en tiempo real. |
| **Entradas** | Datos de ingestión JSON recibidos vía HTTP/REST o WebSockets desde E1, E2, E3, E4 y E6. |
| **Procesamiento** | Validación de esquema JSON (Pydantic), persistencia transaccional en BD (PostgreSQL/SQLite), cálculo de métricas acumuladas por lote y reglas de detección de anomalías. |
| **Salidas** | Endpoints API REST, transmisión de eventos por WebSockets/SSE al Dashboard y reportes de trazabilidad por lote. |
| **Estación receptora** | Estación 6 (alertas) y Administrador/Jefe de Planta (Dashboard UI). |
| **Posibles errores** | Desconexión de red/API, payload JSON corrupto, lote sin identificador activo o inconsistencia de secuencia. |
| **Acción ante error** | Búfer local de reintentos, log de auditoría, alerta visual en Dashboard y reintento con *exponential backoff*. |

---

### Actividad 2.2: Diseño del Modelo de Datos y Esquema E-R
Se diseñó un modelo relacional centrado en la entidad `lote` y la trazabilidad de cada `caja_item` procesada por las distintas estaciones.

#### Estructura de Tablas (DDL en SQL)
```sql
-- Tabla de Lotes
CREATE TABLE IF NOT EXISTS lote (
    id_lote VARCHAR(50) PRIMARY KEY,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo', 'finalizado', 'pausado'))
);

-- Tabla de Cajas (Historial Multiorigen por Estación)
CREATE TABLE IF NOT EXISTS caja_item (
    id_caja VARCHAR(50) PRIMARY KEY,
    id_lote VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Estación 1: Recepción y Captura
    e1_validez_imagen BOOLEAN,
    e1_estado_captura VARCHAR(30),
    
    -- Estación 2: Análisis Visual
    e2_calidad_visual VARCHAR(30),
    e2_confianza_visual REAL,
    e2_defectos_json TEXT,
    
    -- Estación 3: Calibre y Consistencia Física
    e3_peso_total_kg REAL,
    e3_nivel_llenado VARCHAR(30),
    e3_consistencia_fisica VARCHAR(30),
    
    -- Estación 4: Clasificación Comercial Final
    e4_categoria_final VARCHAR(30),
    e4_probabilidad REAL,
    
    -- Estación 6: Movimiento del Carrito
    e6_estado_carrito VARCHAR(30),
    e6_posicion_actual VARCHAR(50),

    CONSTRAINT fk_caja_lote FOREIGN KEY (id_lote) REFERENCES lote (id_lote) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_caja_lote ON caja_item(id_lote);
```

---

### Actividad 2.3: Implementación del Backend de Ingesta (FastAPI + Pydantic)
Se implementó el servidor de ingesta asíncrono para recibir y validar las lecturas de las estaciones E1, E2, E3, E4 y E6.

#### Implementación de Modelos de Ingesta (`app/schemas.py`)
```python
from pydantic import BaseModel, Field
from typing import Optional, List

#--- Estación 1: Recepción y Captura
class E1Data(BaseModel):
    validez_imagen: bool
    estado_captura: str
    posicion_correcta: Optional[bool] = True

class E1Payload(BaseModel):
    id_lote: str = Field(..., example="LOTE-2026-10-A")
    id_caja: str = Field(..., example="CAJA-0047")
    timestamp: str = Field(..., example="2026-10-18T10:15:30Z")
    estacion: str = Field("E1", example="E1")
    datos: E1Data

#--- Estación 2: Calidad Visual
class E2Data(BaseModel):
    calidad_visual: str = Field(..., example="alta")
    confianza_visual: float = Field(..., ge=0.0, le=1.0, example=0.92)
    defectos_detectados: List[str] = Field(default_factory=list, example=["mancha_leve"])

class E2Payload(BaseModel):
    id_lote: str = Field(..., example="LOTE-2026-10-A")
    id_caja: str = Field(..., example="CAJA-0047")
    timestamp: str = Field(..., example="2026-10-18T10:16:05Z")
    estacion: str = Field("E2", example="E2")
    datos: E2Data

#--- Estación 3: Calibre y Consistencia Física
class E3Data(BaseModel):
    peso_total_kg: float = Field(..., gt=0.0, example=4.85)
    nivel_llenado: str = Field(..., example="adecuado")
    cantidad_frutas_visibles: int = Field(..., ge=0, example=8)
    consistencia_fisica: str = Field(..., example="consistente")

class E3Payload(BaseModel):
    id_lote: str = Field(..., example="LOTE-2026-10-A")
    id_caja: str = Field(..., example="CAJA-0047")
    timestamp: str = Field(..., example="2026-10-18T10:16:40Z")
    estacion: str = Field("E3", example="E3")
    datos: E3Data

#--- Estación 4: Clasificación Comercial Final
class E4Data(BaseModel):
    categoria_final: str = Field(..., example="exportacion")
    probabilidad: float = Field(..., ge=0.0, le=1.0, example=0.88)
    requiere_revision_manual: bool = Field(False)

class E4Payload(BaseModel):
    id_lote: str = Field(..., example="LOTE-2026-10-A")
    id_caja: str = Field(..., example="CAJA-0047")
    timestamp: str = Field(..., example="2026-10-18T10:17:10Z")
    estacion: str = Field("E4", example="E4")
    datos: E4Data

#--- Estación 6: Estado del Carrito
class E6Data(BaseModel):
    estado_carrito: str = Field(..., example="normal")
    posicion_actual: str = Field(..., example="estacion_5")
    falla_mecanica_detectada: bool = Field(False)

class E6Payload(BaseModel):
    id_lote: str = Field(..., example="LOTE-2026-10-A")
    id_caja: str = Field(..., example="CAJA-0047")
    timestamp: str = Field(..., example="2026-10-18T10:17:15Z")
    estacion: str = Field("E6", example="E6")
    datos: E6Data
```

#### Servidor de Ingesta (`app/main.py`)
```python
from fastapi import FastAPI, status
from app.schemas import (
    E1Payload, E2Payload, E3Payload, E4Payload, E6Payload
)

app = FastAPI(
    title="API de Ingesta Estación 5 (Supervisión y Trazabilidad)",
    description="Servicio centralizado para la recepción de lecturas de cajas de papayas en el proyecto PackIA.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "online", "mensaje": "Servidor de Ingesta Estación 5 Operativo"}

@app.post("/api/v1/ingest/e1", status_code=status.HTTP_201_CREATED, tags=["Ingesta"])
async def ingest_e1(payload: E1Payload):
    return {"status": "success", "estacion": payload.estacion, "caja_id": payload.id_caja}

@app.post("/api/v1/ingest/e2", status_code=status.HTTP_201_CREATED, tags=["Ingesta"])
async def ingest_e2(payload: E2Payload):
    return {"status": "success", "estacion": payload.estacion, "caja_id": payload.id_caja}

@app.post("/api/v1/ingest/e3", status_code=status.HTTP_201_CREATED, tags=["Ingesta"])
async def ingest_e3(payload: E3Payload):
    return {"status": "success", "estacion": payload.estacion, "caja_id": payload.id_caja}

@app.post("/api/v1/ingest/e4", status_code=status.HTTP_201_CREATED, tags=["Ingesta"])
async def ingest_e4(payload: E4Payload):
    return {"status": "success", "estacion": payload.estacion, "caja_id": payload.id_caja}

@app.post("/api/v1/ingest/e6", status_code=status.HTTP_201_CREATED, tags=["Ingesta"])
async def ingest_e6(payload: E6Payload):
    return {"status": "success", "estacion": payload.estacion, "caja_id": payload.id_caja}
```

---

### Actividad 2.4: Infraestructura de Contenedores con Docker

#### `Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

#### `docker-compose.yml`
```yaml
version: '3.8'

services:
  backend:
    build: .
    container_name: packia_estacion5_api
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app/app
    environment:
      - PYTHONUNBUFFERED=1
```