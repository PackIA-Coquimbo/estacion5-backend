"""Configuración común de pytest para la API de la Estación 5."""

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
CONTRATOS = RAIZ / "docs" / "formato_datos"
ESTACIONES = ["E1", "E2", "E3", "E4", "E6"]

# Permite importar app/ y tools/ desde los tests sin instalar el proyecto
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


def leer_contrato(estacion: str) -> dict:
    """Carga el JSON de ejemplo de una estación desde docs/formato_datos."""
    with open(CONTRATOS / f"{estacion}.json", encoding="utf-8") as archivo:
        return json.load(archivo)


@pytest.fixture
def contratos() -> dict[str, dict]:
    """Todos los contratos de ejemplo, por estación: {"E1": {...}, ...}."""
    return {estacion: leer_contrato(estacion) for estacion in ESTACIONES}


@pytest.fixture
def client():
    """Cliente HTTP de prueba contra la app FastAPI (sin levantar servidor)."""
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as cliente:
        yield cliente
