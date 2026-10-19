-- Script de Creación del Esquema de BD: PackIA Estación 5
-- Generado para PostgreSQL / SQLite

-- 1. Tabla de Lotes
CREATE TABLE IF NOT EXISTS lote (
    id_lote VARCHAR(50) PRIMARY KEY,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo' CHECK (estado IN ('activo', 'finalizado', 'pausado'))
);

-- 2. Tabla de Cajas
CREATE TABLE IF NOT EXISTS caja_item (
    id_caja VARCHAR(50) PRIMARY KEY,
    id_lote VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Datos Estación 1: Recepción y Captura
    e1_validez_imagen BOOLEAN,
    e1_estado_captura VARCHAR(30),

    -- Dato Estación 2: Análisis Visual
    e2_calidad_visual VARCHAR(30),
    e2_confianza_captura REAL,

    -- Datos Estación 3: Calibre y Consistencia Física
    e3_peso_total_kg REAL,
    e3_nivel_llenado VARCHAR(30),
    e3_consistencia_fisica VARCHAR(30),

    -- Datos Estación 4: Decisión Comercial Final
    e4_categoria_final VARCHAR(30),
    e4_probabilidad REAL,

    -- Datos Estación 6: Movimiento del Carrito
    e6_estado_carrito VARCHAR(30),
    e6_posicion_actual VARCHAR(50),

    -- Clave Foránea
    CONSTRAINT fk_caja_lote FOREIGN KEY (id_lote) REFERENCES lote (id_lote) ON DELETE CASCADE
);