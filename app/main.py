# app/main.py
from fastapi import FastAPI, HTTPException, status
from app.schemas import (
    E1Payload, E2Payload, E3Payload, E4Payload, E6Payload
)

app = FastAPI(
    title="API de Ingesta - Estación 5 (Supervición y Trazabilidad)",
    description="Servicio centralizado para la recepción de lecturas de la caja de papayas de PackIA.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "online", "mensaje": "Servidor de Ingesta Estación 5 Operativo"}

# Endpoint para Ingesta de Estación 1
@app.post("/api/v1/ingest/e1", status_code=status.HTTP_201_CREATED, tags=["Ingesta"])
async def ingest_e1(payload: E1Payload):
    # Aquí irá la lógica para guardar en la BD relacional (Semana 3)
    return {"status": "success", "estacion": payload.estacion, "caja_id": payload.id_caja}

# Endpoint para Ingesta de Estación 2
@app.post("/api/v1/ingest/e2", status_code=status.HTTP_201_CREATED, tags=["Ingesta"])
async def ingest_e2(payload: E2Payload):
    return {"status": "success", "estacion": payload.estacion, "caja_id": payload.id_caja}

# Endpoint para Ingesta de Estación 3
@app.post("/api/v1/ingest/e3", status_code=status.HTTP_201_CREATED, tags=["Ingesta"])
async def ingest_e3(payload: E3Payload):
    return {"status": "success", "estacion": payload.estacion, "caja_id": payload.id_caja}

# Endpoint para Ingesta de Estación 4
@app.post("/api/v1/ingest/e4", status_code=status.HTTP_201_CREATED, tags=["Ingesta"])
async def ingest_e4(payload: E4Payload):
    return {"status":"success", "estacion":payload.estacion, "caja_id":payload.id_caja}

@app.post("/api/v1/ingest/e4", status_code=status.HTTP_201_CREATED, tags=["Ingesta"])
async def ingest_e6(payload: E6Payload):
    return {"status":"success", "estacion":payload.estacion, "caja_id":payload.id_caja}