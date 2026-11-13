# Plan individual — Rol B: Integración y calidad

**Dueño de:** contratos JSON (`docs/formato_datos/`), `tests/`, `tools/simulador.py`, Docker, coordinación con otras estaciones
**Revisa PRs de:** A · **Tus PRs los revisa:** C
**Meta del sprint de recuperación (5 días):** contratos cerrados con las otras estaciones, simulador funcionando, tests que protegen la API y una primera integración real con E4 y E6.

> Eres el **desbloqueador**: A y C dependen de que cierres los contratos el Día 1. Lo demás se hace en paralelo.

## Ruta crítica (lo que otros esperan de ti)

| Entrega | Quién la espera | Fecha límite |
|---|---|---|
| Contratos v2 cerrados (con A) | A, C | **Día 1, mediodía** |
| `tools/simulador.py` | A (para probar), C (para ver datos) | **Día 2** |
| Tests de ingesta | A | **Día 2–3** |
| Docker con PostgreSQL | todos | **Día 4** |
| Primera prueba con E4 y E6 reales | todos | **Día 5** |

## Día 1 — Cerrar contratos (prioridad máxima)
- [ ] Enviar a E1–E4 y E6 la sección 2 del plan general y pedir respuesta **hoy**. Si no responden, se avanza con la decisión por defecto y se avisa.
- [ ] Preguntas a cerrar:
  - [ ] ¿Quién asigna `id_grupo` e `id_fruta`? (por defecto: E1)
  - [ ] Rangos de diámetro de E3 para pequeño, mediano y grande.
  - [ ] Lista cerrada de `defectos_detectados` de E2.
  - [ ] Frecuencia de envío de E6 (por defecto: al cambiar + *heartbeat* cada 10 s).
  - [ ] IP o URL donde correrá la API de E5.
- [ ] Actualizar los cinco archivos de `docs/formato_datos/*.json` a v2 (ejemplo E3: `40 mm → mediano`).
- [ ] Mensaje en el chat del equipo: "contratos v2 congelados" con el commit.

## Día 2 — Simulador y base de tests
- [ ] `tools/simulador.py` (usar `httpx` o `requests`, argumento `--url` y `--velocidad`):
  - Genera grupos de 2 a 5 frutas con ids `G-0001`, `F1..Fn`.
  - Envía E1 → E2 → E3 → E4 con retardos realistas, y E6 con *heartbeat*.
  - Opciones para provocar casos: `--falla-cinta`, `--sin-e3`, `--baja-confianza`, `--duplicados`.
  - Los rangos de diámetro salen de los que informe E3 (por ahora: pequeño < 92, mediano 92–111, grande ≥ 112, como en `prototipo2`).
- [ ] `requirements-dev.txt` con `pytest` y `httpx`.
- [ ] `tests/conftest.py`: `TestClient` con SQLite en memoria (cuando A entregue la BD) y fixtures que cargan los JSON de `docs/formato_datos`.
- [ ] `tests/test_ingesta.py`: cada JSON válido → 201; falta un campo, valor fuera de rango o `estacion` incorrecta → 422.
- [ ] Rama: `feat/b-simulador` → PR a C.

## Día 3 — Tests de comportamiento
- [ ] Mensaje duplicado no crea filas nuevas (*upsert*).
- [ ] Mensajes en desorden (E3 antes que E1) crean el grupo igual.
- [ ] `tests/test_consultas.py` contra los endpoints `GET` de A.
- [ ] `tests/test_reglas.py`: un test por regla de anomalías (A deja `evaluar` como función pura).
- [ ] Revisar los PRs de A el mismo día; no dejarlos esperando.

## Día 4 — Docker y entorno
- [ ] `docker-compose.yml`: servicio `db` (PostgreSQL) + `backend` con `DATABASE_URL`; quitar `version:` obsoleto.
- [ ] Dockerfile sin `--reload` (el compose de desarrollo lo agrega con `command:`).
- [ ] Agregar `.env.example` y documentar en el README cómo levantar todo.
- [ ] Probar `docker compose up --build` desde cero **en otro computador** (el de A o C).
- [ ] Pedirle a E1, E2, E3, E4 y E6 el ejemplo real que enviarán, y compararlo con los contratos.

## Día 5 — Primera integración real
- [ ] Agendar con E4 y E6 una prueba conjunta (30 min): ellos envían a la API de E5, tú miras los logs.
- [ ] Crear `docs/integracion/semana5.md` con la tabla: campo esperado / campo recibido / acción.
- [ ] Pasar los errores encontrados a A con el payload exacto.
- [ ] Redactar `docs/trelo/semana3.md` (bitácora): qué se logró, qué falta, riesgos.

## Si vas justo de tiempo, recorta en este orden
1. Opciones extra del simulador (`--duplicados`).
2. Prueba de carga.
3. PostgreSQL en compose (SQLite alcanza para la demo si hace falta).

**No se recorta:** contratos v2, simulador básico, tests de ingesta, prueba real con E4 y E6.

## Riesgos propios
- Los otros grupos no responden → avanzar con la decisión por defecto, dejarla escrita y avisar en el chat. No bloquear a A y C.
- Los tests dependen de la BD de A → empezar por los tests de validación (422/201), que no la necesitan.
