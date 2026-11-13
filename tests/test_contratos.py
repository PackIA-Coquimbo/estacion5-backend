"""Tests de los contratos v2 (docs/formato_datos) y del simulador.

No dependen de app/schemas.py: comprueban que los ejemplos y los mensajes
del simulador cumplen lo acordado con las otras estaciones.
"""

import random
from datetime import datetime

import pytest

from conftest import ESTACIONES, leer_contrato
from tools import simulador

ESTADOS_CAPTURA = {"aceptada", "repetir", "revision"}
CALIDADES = {"alta", "media", "baja", "defectos_visibles", "revision"}
TAMANOS = {"pequeno", "mediano", "grande"}
CATEGORIAS = {"exportacion", "mercado_nacional", "proceso", "rechazo", "revision_manual"}
ESTADOS_CINTA = {"normal", "detenida", "falla_mecanica"}


def errores_contrato(m: dict) -> list[str]:
    """Devuelve la lista de incumplimientos del contrato v2 (vacía si cumple)."""
    errores = []

    def revisar(condicion: bool, mensaje: str) -> None:
        if not condicion:
            errores.append(mensaje)

    estacion = m.get("estacion")
    revisar(estacion in ESTACIONES, f"estacion inválida: {estacion}")
    revisar(isinstance(m.get("id_lote"), str) and m["id_lote"] != "", "falta id_lote")
    revisar("id_caja" not in m, "id_caja es de v1, ya no se usa")

    try:
        fecha = datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00"))
        revisar(fecha.tzinfo is not None, "timestamp sin zona horaria")
    except (KeyError, AttributeError, ValueError):
        errores.append("timestamp ausente o no es ISO 8601")

    if estacion == "E6":
        revisar("id_grupo" not in m, "E6 no lleva id_grupo")
    else:
        revisar(isinstance(m.get("id_grupo"), str) and m["id_grupo"] != "", "falta id_grupo")

    if estacion in ("E1", "E6"):
        datos = m.get("datos")
        if not isinstance(datos, dict):
            return errores + ["falta el objeto datos"]
        if estacion == "E1":
            revisar(isinstance(datos.get("validez_imagen"), bool), "validez_imagen debe ser booleano")
            revisar(datos.get("estado_captura") in ESTADOS_CAPTURA, "estado_captura inválido")
            revisar(isinstance(datos.get("posicion_correcta"), bool), "posicion_correcta debe ser booleano")
            n = datos.get("frutas_detectadas")
            revisar(isinstance(n, int) and not isinstance(n, bool) and n > 0, "frutas_detectadas debe ser entero > 0")
        else:
            revisar(datos.get("estado_cinta") in ESTADOS_CINTA, "estado_cinta inválido")
            revisar(isinstance(datos.get("falla_mecanica_detectada"), bool), "falla_mecanica_detectada debe ser booleano")
            grupo = datos.get("id_grupo_en_cinta")
            revisar(grupo is None or isinstance(grupo, str), "id_grupo_en_cinta debe ser texto u omitirse")
        return errores

    frutas = m.get("frutas")
    if not isinstance(frutas, list) or not frutas:
        return errores + ["falta la lista frutas"]
    ids = [f.get("id_fruta") for f in frutas]
    revisar(all(isinstance(i, str) and i for i in ids), "id_fruta vacío o ausente")
    revisar(len(ids) == len(set(ids)), "id_fruta repetido dentro del grupo")

    for f in frutas:
        if estacion == "E2":
            revisar(f.get("calidad_visual") in CALIDADES, f"calidad_visual inválida: {f}")
            revisar(isinstance(f.get("confianza_visual"), (int, float))
                    and 0 <= f["confianza_visual"] <= 1, f"confianza_visual fuera de 0..1: {f}")
            revisar(isinstance(f.get("defectos_detectados"), list), f"defectos_detectados debe ser lista: {f}")
        elif estacion == "E3":
            revisar(isinstance(f.get("diametro_mm"), (int, float))
                    and f["diametro_mm"] > 0, f"diametro_mm debe ser > 0: {f}")
            revisar(f.get("tamano") in TAMANOS, f"tamano inválido: {f}")
        elif estacion == "E4":
            revisar(f.get("categoria_final") in CATEGORIAS, f"categoria_final inválida: {f}")
            revisar(isinstance(f.get("probabilidad"), (int, float))
                    and 0 <= f["probabilidad"] <= 1, f"probabilidad fuera de 0..1: {f}")
            revisar(isinstance(f.get("requiere_revision_manual"), bool), f"requiere_revision_manual debe ser booleano: {f}")
    return errores


# ------------------------------------------------- contratos de ejemplo

@pytest.mark.parametrize("estacion", ESTACIONES)
def test_contrato_cumple_formato_v2(estacion):
    assert errores_contrato(leer_contrato(estacion)) == []


@pytest.mark.parametrize("estacion", ESTACIONES)
def test_estacion_coincide_con_el_archivo(estacion):
    assert leer_contrato(estacion)["estacion"] == estacion


def test_contratos_describen_el_mismo_grupo(contratos):
    lotes = {c["id_lote"] for c in contratos.values()}
    assert len(lotes) == 1
    grupos = {c["id_grupo"] for e, c in contratos.items() if e != "E6"}
    assert len(grupos) == 1
    assert contratos["E6"]["datos"].get("id_grupo_en_cinta") in grupos


def test_frutas_coinciden_entre_estaciones(contratos):
    n = contratos["E1"]["datos"]["frutas_detectadas"]
    ids = [[f["id_fruta"] for f in contratos[e]["frutas"]] for e in ("E2", "E3", "E4")]
    assert all(len(lista) == n for lista in ids)
    assert ids[0] == ids[1] == ids[2]


def test_ejemplo_e3_40mm_es_mediano(contratos):
    """Decisión confirmada en el plan: 40 mm -> mediano."""
    f1 = next(f for f in contratos["E3"]["frutas"] if f["diametro_mm"] == 40)
    assert f1["tamano"] == "mediano"


def test_validador_detecta_errores(contratos):
    """El validador debe fallar ante mensajes mal formados."""
    malo = dict(contratos["E3"], frutas=[{"id_fruta": "F1", "diametro_mm": 0, "tamano": "enorme"}])
    assert len(errores_contrato(malo)) == 2
    v1 = dict(contratos["E1"], id_caja="CAJA-0047")
    assert errores_contrato(v1) == ["id_caja es de v1, ya no se usa"]
    sin_zona = dict(contratos["E4"], timestamp="2026-11-18T10:17:10")
    assert errores_contrato(sin_zona) == ["timestamp sin zona horaria"]


# ------------------------------------------------------------ simulador

def generar_grupo(rng, numero, rangos=(35.0, 45.0), baja_confianza=False):
    id_grupo = f"G-{numero:04d}"
    n = rng.randint(2, 5)
    ids = [f"F{i}" for i in range(1, n + 1)]
    e1 = simulador.generar_e1(rng, "LOTE-TEST", id_grupo, n)
    e2 = simulador.generar_e2(rng, "LOTE-TEST", id_grupo, ids, baja_confianza)
    e3 = simulador.generar_e3(rng, "LOTE-TEST", id_grupo, ids, *rangos)
    e4 = simulador.generar_e4(rng, "LOTE-TEST", id_grupo, e2)
    return e1, e2, e3, e4


@pytest.mark.parametrize("rangos", [(35.0, 45.0), (92.0, 112.0)])
@pytest.mark.parametrize("baja_confianza", [False, True])
def test_simulador_genera_mensajes_validos(rangos, baja_confianza):
    rng = random.Random(42)
    for numero in range(1, 201):
        for mensaje in generar_grupo(rng, numero, rangos, baja_confianza):
            assert errores_contrato(mensaje) == [], mensaje


@pytest.mark.parametrize("estado", sorted(ESTADOS_CINTA))
def test_simulador_e6_valido(estado):
    mensaje = simulador.generar_e6("LOTE-TEST", estado, "G-0001")
    assert errores_contrato(mensaje) == []
    assert mensaje["datos"]["falla_mecanica_detectada"] == (estado == "falla_mecanica")
    assert errores_contrato(simulador.generar_e6("LOTE-TEST", estado, None)) == []


def test_simulador_grupo_coherente():
    rng = random.Random(1)
    e1, e2, e3, e4 = generar_grupo(rng, 1)
    ids = [f["id_fruta"] for f in e2["frutas"]]
    assert len(ids) == e1["datos"]["frutas_detectadas"]
    assert ids == [f["id_fruta"] for f in e3["frutas"]] == [f["id_fruta"] for f in e4["frutas"]]
    for f2, f4 in zip(e2["frutas"], e4["frutas"]):
        assert f4["categoria_final"] == simulador.CATEGORIA_POR_CALIDAD[f2["calidad_visual"]]


@pytest.mark.parametrize("diametro, esperado", [(34, "pequeno"), (35, "mediano"), (40, "mediano"), (45, "grande")])
def test_simulador_tamano_por_rangos(diametro, esperado):
    assert simulador.tamano_para(diametro, 35, 45) == esperado


def test_simulador_baja_confianza_produce_alertas():
    rng = random.Random(5)
    confianzas = [f["confianza_visual"] for n in range(1, 51)
                  for f in generar_grupo(rng, n, baja_confianza=True)[1]["frutas"]]
    assert any(c < 0.70 for c in confianzas)
    rng = random.Random(5)
    normales = [f["confianza_visual"] for n in range(1, 51)
                for f in generar_grupo(rng, n)[1]["frutas"]]
    assert all(c >= 0.70 for c in normales)
