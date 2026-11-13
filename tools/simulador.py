"""Simulador de estaciones para la API de la Estación 5 (contratos v2).

Genera grupos de 2 a 5 frutas y envía, por cada grupo, los mensajes de
E1 -> E2 -> E3 -> E4 con retardos entre estaciones. En paralelo envía el
estado de la cinta (E6) cada vez que cambia y como heartbeat cada 10 s.

Ejemplos:
    python tools/simulador.py --dry-run --grupos 2
    python tools/simulador.py --url http://localhost:8000 --grupos 20
    python tools/simulador.py --velocidad 2 --falla-cinta --baja-confianza
    python tools/simulador.py --grupos 0          # sin fin, se detiene con Ctrl+C
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone

import httpx

# Valores permitidos según docs/formato_datos (contratos v2)
ESTADOS_CAPTURA = ["aceptada", "repetir", "revision"]
CALIDADES = ["alta", "media", "baja", "defectos_visibles", "revision"]
TAMANOS = ["pequeno", "mediano", "grande"]
CATEGORIAS = ["exportacion", "mercado_nacional", "proceso", "rechazo", "revision_manual"]
ESTADOS_CINTA = ["normal", "detenida", "falla_mecanica"]
DEFECTOS = ["mancha_leve", "mancha_grave", "golpe", "deformacion", "herida_piel"]

# Calidad visual -> categoría comercial más probable
CATEGORIA_POR_CALIDAD = {
    "alta": "exportacion",
    "media": "mercado_nacional",
    "baja": "proceso",
    "defectos_visibles": "rechazo",
    "revision": "revision_manual",
}

# Segundos entre estaciones a velocidad 1
RETARDO_ENTRE_ESTACIONES = 2.0
RETARDO_ENTRE_GRUPOS = 3.0
HEARTBEAT_E6 = 10.0

RUTAS = {"E1": "e1", "E2": "e2", "E3": "e3", "E4": "e4", "E6": "e6"}


def ahora_iso() -> str:
    """Fecha y hora actual en UTC, ISO 8601 con zona (termina en Z)."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def tamano_para(diametro_mm: float, corte_mediano: float, corte_grande: float) -> str:
    """Lo calcula E3 en la línea real; aquí se imita con los rangos dados."""
    if diametro_mm >= corte_grande:
        return "grande"
    if diametro_mm >= corte_mediano:
        return "mediano"
    return "pequeno"


# ---------------------------------------------------------------- generadores
# Funciones puras: reciben un random.Random para que los tests sean repetibles.

def generar_e1(rng: random.Random, id_lote: str, id_grupo: str, n_frutas: int) -> dict:
    validez = rng.random() > 0.03
    estado = rng.choices(ESTADOS_CAPTURA, weights=[92, 5, 3])[0] if validez else "repetir"
    return {
        "id_lote": id_lote,
        "id_grupo": id_grupo,
        "estacion": "E1",
        "timestamp": ahora_iso(),
        "datos": {
            "validez_imagen": validez,
            "estado_captura": estado,
            "posicion_correcta": rng.random() > 0.05,
            "frutas_detectadas": n_frutas,
        },
    }


def generar_e2(rng: random.Random, id_lote: str, id_grupo: str, ids_fruta: list[str],
               baja_confianza: bool = False) -> dict:
    frutas = []
    for id_fruta in ids_fruta:
        calidad = rng.choices(CALIDADES, weights=[45, 30, 12, 8, 5])[0]
        if baja_confianza and rng.random() < 0.4:
            confianza = rng.uniform(0.40, 0.69)
        else:
            confianza = rng.uniform(0.72, 0.99)
        if calidad in ("alta",):
            defectos = []
        elif calidad == "defectos_visibles":
            defectos = rng.sample(DEFECTOS, k=rng.randint(1, 2))
        else:
            defectos = rng.sample(DEFECTOS[:1], k=rng.randint(0, 1))
        frutas.append({
            "id_fruta": id_fruta,
            "calidad_visual": calidad,
            "confianza_visual": round(confianza, 2),
            "defectos_detectados": defectos,
        })
    return {
        "id_lote": id_lote,
        "id_grupo": id_grupo,
        "estacion": "E2",
        "timestamp": ahora_iso(),
        "frutas": frutas,
    }


def generar_e3(rng: random.Random, id_lote: str, id_grupo: str, ids_fruta: list[str],
               corte_mediano: float, corte_grande: float) -> dict:
    centro = (corte_mediano + corte_grande) / 2
    dispersion = (corte_grande - corte_mediano) * 0.6
    frutas = []
    for id_fruta in ids_fruta:
        diametro = max(1, round(rng.gauss(centro, dispersion)))
        frutas.append({
            "id_fruta": id_fruta,
            "diametro_mm": diametro,
            "tamano": tamano_para(diametro, corte_mediano, corte_grande),
        })
    return {
        "id_lote": id_lote,
        "id_grupo": id_grupo,
        "estacion": "E3",
        "timestamp": ahora_iso(),
        "frutas": frutas,
    }


def generar_e4(rng: random.Random, id_lote: str, id_grupo: str, e2: dict) -> dict:
    frutas = []
    for fruta in e2["frutas"]:
        categoria = CATEGORIA_POR_CALIDAD[fruta["calidad_visual"]]
        probabilidad = round(rng.uniform(0.60, 0.98), 2)
        revision = categoria == "revision_manual" or probabilidad < 0.70
        frutas.append({
            "id_fruta": fruta["id_fruta"],
            "categoria_final": categoria,
            "probabilidad": probabilidad,
            "requiere_revision_manual": revision,
        })
    return {
        "id_lote": id_lote,
        "id_grupo": id_grupo,
        "estacion": "E4",
        "timestamp": ahora_iso(),
        "frutas": frutas,
    }


def generar_e6(id_lote: str, estado_cinta: str, id_grupo_en_cinta: str | None) -> dict:
    datos = {
        "estado_cinta": estado_cinta,
        "falla_mecanica_detectada": estado_cinta == "falla_mecanica",
    }
    if id_grupo_en_cinta:
        datos["id_grupo_en_cinta"] = id_grupo_en_cinta
    return {
        "id_lote": id_lote,
        "estacion": "E6",
        "timestamp": ahora_iso(),
        "datos": datos,
    }


# ------------------------------------------------------------------- envío

class Simulador:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.rng = random.Random(args.semilla)
        self.cliente = None if args.dry_run else httpx.Client(base_url=args.url, timeout=5.0)
        self.estado_cinta = "normal"
        self.grupo_en_cinta: str | None = None
        self.ultimo_e6 = 0.0
        self.enviados = 0
        self.errores = 0

    def enviar(self, mensaje: dict) -> None:
        repeticiones = 2 if self.args.duplicados else 1
        for _ in range(repeticiones):
            self._enviar_una_vez(mensaje)

    def _enviar_una_vez(self, mensaje: dict) -> None:
        estacion = mensaje["estacion"]
        etiqueta = f"{estacion} {mensaje.get('id_grupo', self.estado_cinta)}"
        if self.cliente is None:
            print(json.dumps(mensaje, ensure_ascii=False))
            self.enviados += 1
            return
        ruta = f"/api/v1/ingest/{RUTAS[estacion]}"
        try:
            respuesta = self.cliente.post(ruta, json=mensaje)
        except httpx.HTTPError as error:
            self.errores += 1
            print(f"[ERROR] {etiqueta}: no se pudo conectar ({error})", file=sys.stderr)
            return
        if respuesta.status_code in (200, 201):
            self.enviados += 1
            print(f"[{respuesta.status_code}] {etiqueta}")
        else:
            self.errores += 1
            print(f"[{respuesta.status_code}] {etiqueta}: {respuesta.text[:300]}", file=sys.stderr)

    def enviar_e6(self) -> None:
        self.enviar(generar_e6(self.args.lote, self.estado_cinta, self.grupo_en_cinta))
        self.ultimo_e6 = time.monotonic()

    def cambiar_cinta(self, estado: str) -> None:
        if estado != self.estado_cinta:
            self.estado_cinta = estado
            self.enviar_e6()

    def esperar(self, segundos: float) -> None:
        """Espera respetando --velocidad y manda el heartbeat de E6 cuando toca."""
        if self.args.dry_run:
            return
        fin = time.monotonic() + segundos / self.args.velocidad
        while True:
            restante = fin - time.monotonic()
            if time.monotonic() - self.ultimo_e6 >= HEARTBEAT_E6 / self.args.velocidad:
                self.enviar_e6()
            if restante <= 0:
                return
            time.sleep(min(restante, 0.5))

    def procesar_grupo(self, numero: int) -> None:
        a = self.args
        id_grupo = f"G-{numero:04d}"
        n_frutas = self.rng.randint(2, 5)
        ids_fruta = [f"F{i}" for i in range(1, n_frutas + 1)]
        self.grupo_en_cinta = id_grupo

        self.enviar(generar_e1(self.rng, a.lote, id_grupo, n_frutas))
        self.esperar(RETARDO_ENTRE_ESTACIONES)
        e2 = generar_e2(self.rng, a.lote, id_grupo, ids_fruta, a.baja_confianza)
        self.enviar(e2)
        self.esperar(RETARDO_ENTRE_ESTACIONES)
        if not a.sin_e3:
            self.enviar(generar_e3(self.rng, a.lote, id_grupo, ids_fruta, a.rangos[0], a.rangos[1]))
            self.esperar(RETARDO_ENTRE_ESTACIONES)
        self.enviar(generar_e4(self.rng, a.lote, id_grupo, e2))

    def correr(self) -> None:
        a = self.args
        grupo_con_falla = max(2, a.grupos // 2) if a.grupos else 5
        self.enviar_e6()
        numero = a.inicio
        procesados = 0
        while a.grupos == 0 or procesados < a.grupos:
            if a.falla_cinta and procesados + 1 == grupo_con_falla:
                print("--- simulando falla mecánica de la cinta ---", file=sys.stderr)
                self.cambiar_cinta("falla_mecanica")
                self.esperar(RETARDO_ENTRE_GRUPOS * 2)
                self.cambiar_cinta("detenida")
                self.esperar(RETARDO_ENTRE_GRUPOS)
                self.cambiar_cinta("normal")
            self.procesar_grupo(numero)
            numero += 1
            procesados += 1
            if a.grupos == 0 or procesados < a.grupos:
                self.esperar(RETARDO_ENTRE_GRUPOS)
        self.grupo_en_cinta = None
        self.enviar_e6()

    def cerrar(self) -> None:
        if self.cliente is not None:
            self.cliente.close()


def leer_rangos(texto: str) -> tuple[float, float]:
    try:
        mediano, grande = (float(x) for x in texto.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError("usa el formato MEDIANO,GRANDE, por ejemplo 35,45")
    if not 0 < mediano < grande:
        raise argparse.ArgumentTypeError("debe cumplirse 0 < MEDIANO < GRANDE")
    return mediano, grande


def leer_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simulador de estaciones E1-E4 y E6 para la API de E5 (contratos v2).")
    p.add_argument("--url", default="http://localhost:8000", help="URL base de la API (por defecto %(default)s)")
    p.add_argument("--lote", default="LOTE-2026-11-A", help="id_lote a usar (por defecto %(default)s)")
    p.add_argument("--grupos", type=int, default=10, help="cantidad de grupos; 0 = sin fin (por defecto %(default)s)")
    p.add_argument("--inicio", type=int, default=1, help="número del primer grupo, G-0001 por defecto")
    p.add_argument("--velocidad", type=float, default=1.0, help="multiplicador de velocidad; 2 = el doble de rápido")
    p.add_argument("--semilla", type=int, default=None, help="semilla aleatoria para repetir una simulación")
    p.add_argument("--rangos", type=leer_rangos, default=(35.0, 45.0), metavar="MEDIANO,GRANDE",
                   help="cortes de diámetro en mm: < MEDIANO pequeño, >= GRANDE grande (por defecto 35,45)")
    p.add_argument("--falla-cinta", action="store_true", help="la cinta falla a mitad de la simulación y luego se recupera")
    p.add_argument("--sin-e3", action="store_true", help="no envía mensajes de E3 (estación caída)")
    p.add_argument("--baja-confianza", action="store_true", help="E2 informa ~40%% de frutas con confianza < 0.70")
    p.add_argument("--duplicados", action="store_true", help="envía cada mensaje dos veces")
    p.add_argument("--dry-run", action="store_true", help="imprime los JSON sin enviarlos ni esperar")
    args = p.parse_args(argv)
    if args.velocidad <= 0:
        p.error("--velocidad debe ser mayor que 0")
    if args.grupos < 0:
        p.error("--grupos no puede ser negativo")
    if args.grupos == 0 and args.dry_run:
        p.error("--dry-run necesita una cantidad de grupos mayor que 0")
    return args


def main(argv: list[str] | None = None) -> int:
    # En Windows la consola puede no usar UTF-8 y romper tildes y símbolos
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")
    args = leer_args(argv)
    sim = Simulador(args)
    try:
        sim.correr()
    except KeyboardInterrupt:
        print("\nSimulación detenida por el usuario.", file=sys.stderr)
    finally:
        sim.cerrar()
    print(f"Mensajes aceptados: {sim.enviados} · con error: {sim.errores}", file=sys.stderr)
    return 1 if sim.errores else 0


if __name__ == "__main__":
    sys.exit(main())
