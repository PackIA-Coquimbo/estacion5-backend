"""Tests de ingesta v2: POST /api/v1/ingest/{e1,e2,e3,e4,e6}.

Cada JSON de docs/formato_datos debe responder 201; un mensaje con un campo
faltante, un valor fuera de rango o una estación equivocada debe responder 422.

Se saltan mientras app/schemas.py siga en v1 (por caja). Se activan solos
cuando entren los schemas v2 de A.
"""

import copy

import pytest

from app import schemas
from conftest import ESTACIONES

SCHEMAS_V2 = "id_grupo" in schemas.E1Payload.model_fields

pytestmark = pytest.mark.skipif(
    not SCHEMAS_V2,
    reason="app/schemas.py sigue en v1; esperando schemas v2 de A (feat/a-contratos-v2)",
)


def ruta(estacion: str) -> str:
    return f"/api/v1/ingest/{estacion.lower()}"


def con_cambio(mensaje: dict, camino: list, valor) -> dict:
    """Copia el mensaje y reemplaza el valor en `camino` (lista de claves/índices)."""
    nuevo = copy.deepcopy(mensaje)
    destino = nuevo
    for paso in camino[:-1]:
        destino = destino[paso]
    destino[camino[-1]] = valor
    return nuevo


def sin_campo(mensaje: dict, camino: list) -> dict:
    """Copia el mensaje y borra el campo indicado por `camino`."""
    nuevo = copy.deepcopy(mensaje)
    destino = nuevo
    for paso in camino[:-1]:
        destino = destino[paso]
    del destino[camino[-1]]
    return nuevo


# ------------------------------------------------------------ casos válidos

@pytest.mark.parametrize("estacion", ESTACIONES)
def test_contrato_valido_responde_201(client, contratos, estacion):
    respuesta = client.post(ruta(estacion), json=contratos[estacion])
    assert respuesta.status_code == 201, respuesta.text


def test_e6_sin_id_grupo_en_cinta_es_valido(client, contratos):
    mensaje = sin_campo(contratos["E6"], ["datos", "id_grupo_en_cinta"])
    assert client.post(ruta("E6"), json=mensaje).status_code == 201


def test_e2_sin_defectos_es_valido(client, contratos):
    mensaje = con_cambio(contratos["E2"], ["frutas", 0, "defectos_detectados"], [])
    assert client.post(ruta("E2"), json=mensaje).status_code == 201


# ----------------------------------------------------------- campo faltante

CAMPOS_OBLIGATORIOS = [
    ("E1", ["id_lote"]),
    ("E1", ["id_grupo"]),
    ("E1", ["timestamp"]),
    ("E1", ["datos"]),
    ("E1", ["datos", "estado_captura"]),
    ("E1", ["datos", "frutas_detectadas"]),
    ("E2", ["id_grupo"]),
    ("E2", ["frutas"]),
    ("E2", ["frutas", 0, "id_fruta"]),
    ("E2", ["frutas", 0, "confianza_visual"]),
    ("E3", ["frutas", 0, "diametro_mm"]),
    ("E3", ["frutas", 0, "tamano"]),
    ("E4", ["frutas", 0, "categoria_final"]),
    ("E4", ["frutas", 0, "requiere_revision_manual"]),
    ("E6", ["id_lote"]),
    ("E6", ["datos", "estado_cinta"]),
    ("E6", ["datos", "falla_mecanica_detectada"]),
]


@pytest.mark.parametrize("estacion, camino", CAMPOS_OBLIGATORIOS,
                         ids=[f"{e}-{'.'.join(map(str, c))}" for e, c in CAMPOS_OBLIGATORIOS])
def test_campo_faltante_responde_422(client, contratos, estacion, camino):
    mensaje = sin_campo(contratos[estacion], camino)
    assert client.post(ruta(estacion), json=mensaje).status_code == 422


# ------------------------------------------------- valor fuera de rango

VALORES_INVALIDOS = [
    ("E1", ["datos", "estado_captura"], "rechazada"),
    ("E1", ["datos", "frutas_detectadas"], "tres"),
    ("E2", ["frutas", 0, "calidad_visual"], "excelente"),
    ("E2", ["frutas", 0, "confianza_visual"], 1.5),
    ("E2", ["frutas", 0, "confianza_visual"], -0.1),
    ("E3", ["frutas", 0, "diametro_mm"], 0),
    ("E3", ["frutas", 0, "diametro_mm"], -40),
    ("E3", ["frutas", 0, "tamano"], "enorme"),
    ("E4", ["frutas", 0, "categoria_final"], "basura"),
    ("E4", ["frutas", 0, "probabilidad"], 1.01),
    ("E6", ["datos", "estado_cinta"], "rapida"),
    ("E1", ["timestamp"], "2026-11-18T10:15:30"),
    ("E1", ["timestamp"], "ayer"),
]


@pytest.mark.parametrize("estacion, camino, valor", VALORES_INVALIDOS,
                         ids=[f"{e}-{c[-1]}={v}" for e, c, v in VALORES_INVALIDOS])
def test_valor_invalido_responde_422(client, contratos, estacion, camino, valor):
    mensaje = con_cambio(contratos[estacion], camino, valor)
    assert client.post(ruta(estacion), json=mensaje).status_code == 422


# ---------------------------------------------------- estación equivocada

@pytest.mark.parametrize("estacion", ESTACIONES)
def test_estacion_distinta_a_la_ruta_responde_422(client, contratos, estacion):
    otra = "E2" if estacion != "E2" else "E1"
    mensaje = con_cambio(contratos[estacion], ["estacion"], otra)
    assert client.post(ruta(estacion), json=mensaje).status_code == 422


@pytest.mark.parametrize("origen, destino", [("E1", "E2"), ("E3", "E4"), ("E6", "E1")])
def test_mensaje_enviado_a_otra_ruta_responde_422(client, contratos, origen, destino):
    assert client.post(ruta(destino), json=contratos[origen]).status_code == 422


def test_mensaje_v1_con_id_caja_responde_422(client, contratos):
    v1 = sin_campo(contratos["E1"], ["id_grupo"])
    v1["id_caja"] = "CAJA-0047"
    assert client.post(ruta("E1"), json=v1).status_code == 422
