from pydantic import BaseModel, Field
from typing import Optional, List 
from datetime import datetime 

# Esquema base genérico para metadatos comunes
class IngestaBase(BaseModel):
    id_lote: str = Field(..., example="LOTE-2026-10-A", description="ID del lote activo")
    id_caja: str = Field(..., example="CAJA-0047", description="ID de la caja procesada")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Payload Estación 1: Recepción y Captura
class E1Data(BaseModel):
    validez_imagen: bool 
    estado_captura: str 
    posicion_correcta: bool 

class E1Payload(IngestaBase):
    estacion: str = "E1"
    datos: E1Data 

# Payload Estación 2: Análisis Visual de Calidad
class E2Data(BaseModel):
    calidad_visual: str 
    confianza_visual: float = Field(..., ge=0.0, le=1.0)
    defectos_detectados: Optional[List[str]] = []

class E2Payload(IngestaBase):
    estacion: str = "E2"
    datos: E2Data

# Payload Estación 3: Calibre y Consistencia Física
class E3Data(BaseModel):
    peso_total_kg: float
    nivel_llenado: str 
    cantidad_frutas_visibles: int 
    consistencia_fisica: str 

class E3Payload(IngestaBase):
    estacion: str = "E3"
    datos: E3Data

# Payload Estación 4: Clasificación Comercial Final
class E4Data(BaseModel):
    categoria_final: str 
    probabilidad: float = Field(..., ge=0.0, le=1.0)
    requiere_revision_manual: bool 

class E4Payload(IngestaBase):
    estacion: str = "E4"
    datos: E4Data

# Payload Estación 6: Estado del Carrito
class E6Data(BaseModel):
    estado_carrito: str 
    posicion_actual: str 
    falla_mecanica_detectada: bool 

class E6Payload(IngestaBase):
    estacion: str = "E6"
    datos: E6Data 