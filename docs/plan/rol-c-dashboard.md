# Plan individual — Rol C: Dashboard

**Dueño: Christian**

**Dueño de:** `frontend/`
**Revisa PRs de:** B · **Tus PRs los revisa:** A
**Meta del sprint de recuperación (5 días):** el dashboard deja de usar datos simulados internos y muestra los de la API real (alimentada por el simulador de B), con alertas, estado de estaciones y trazabilidad de un grupo.

> Tu prototipo ya está avanzado: el trabajo es **cambiar la fuente de datos**, no rediseñar. No empieces cambios visuales grandes hasta tener la conexión funcionando.

## Ruta crítica

| Qué necesitas | De quién | Cuándo |
|---|---|---|
| Contratos v2 cerrados | A y B | Día 1, mediodía (mientras, avanzas en la limpieza) |
| Ingesta guardando en BD y simulador | A y B | Día 2 |
| Endpoints `GET` de grupos y métricas | A | Día 3 |
| Alertas y estado de estaciones | A | Día 4 |

## Día 1 — Ordenar el frontend
- [ ] Dejar `frontend/index.html` = última versión (`prototipo2`); hoy es una copia de `prototipo1`. Mantener `prototipo1/` y `prototipo2/` como historial o borrarlos si el equipo está de acuerdo.
- [ ] Separar el código del prototipo en archivos: `frontend/app.js`, `frontend/sim.js` (generadores simulados) y `frontend/api.js` (llamadas `fetch`).
- [ ] Adaptar los nombres al contrato v2:
  - E3: `diametro_mm` + `tamano` (`pequeno | mediano | grande`); mostrar "40 mm · Mediano".
  - E6: `estado_cinta` (`normal | detenida | falla_mecanica`).
  - `id_grupo` en vez de `id_caja`.
- [ ] Revisar que los rangos simulados de E3 sean los que informe B (ver su plan).
- [ ] Rama: `feat/c-prototipo-v2-contratos` → PR a B.

## Día 2 — Capa de datos
- [ ] En `api.js`: `const API = new URLSearchParams(location.search).get("api") || "http://localhost:8000"` (así se prueba con otra IP sin editar código).
- [ ] Una función por endpoint que A entregue (`getGrupos`, `getMetricas`, `getAlertas`, `getEstaciones`, `getGrupo`), con `try/catch` y un estado visible "sin conexión con la API".
- [ ] Interruptor `?sim=1`: usa los datos simulados internos; sin el parámetro, usa la API. **Así la demo tiene plan B.**
- [ ] Levantar la API con el simulador de B y verificar en el navegador que las llamadas funcionan (CORS lo activa A).

## Día 3 — Conectar la pantalla
- [ ] Tabla "Últimos grupos" y KPIs (frutas por hora, % de rechazo, categoría final, anomalías por estación) desde la API con *polling* cada 3–5 s.
- [ ] Tarjetas de E1–E4 y E6 con la última lectura real de cada estación.
- [ ] Mostrar la hora de la lectura (la que envía la estación) y no la hora local del navegador.
- [ ] Manejar vacíos y errores: sin datos todavía, API caída, respuesta lenta.

## Día 4 — Alertas, estado y trazabilidad
- [ ] Panel de alertas desde `/api/v1/alertas?activas=true`.
- [ ] Estado online o sin señal por estación desde `/api/v1/estaciones/estado`.
- [ ] Banner "Cinta detenida" cuando E6 informe `falla_mecanica` o `detenida`.
- [ ] **Vista de trazabilidad:** clic en un grupo → detalle por fruta (E2, E3 con diámetro y tamaño, E4) con la hora de cada estación, desde `/api/v1/grupos/{id}`.
- [ ] Quitar los botones de simulación del modo real (dejarlos solo con `?sim=1`).

## Día 5 — Pulido y demo
- [ ] Probar en la pantalla real de planta o en la Raspberry Pi: tamaños de letra, contraste, modo pantalla completa.
- [ ] Probar con el simulador de B en modo falla: `--falla-cinta`, `--sin-e3`, `--baja-confianza`.
- [ ] Apuntar a la API real de E4 y E6 si B ya logró la prueba conjunta.
- [ ] Escribir en el README del frontend cómo abrirlo y qué parámetros acepta (`?api=`, `?sim=1`).
- [ ] Si sobra tiempo: pasar de *polling* a `EventSource` cuando A tenga el endpoint SSE.

## Si vas justo de tiempo, recorta en este orden
1. SSE (el *polling* basta).
2. Pulido visual y modo pantalla completa.
3. Anomalías por estación en los KPIs.

**No se recorta:** tabla de grupos y KPIs desde la API, alertas, banner de falla de cinta, modo `?sim=1` como respaldo.

## Riesgos propios
- La API de A llega tarde → trabajar contra los JSON de ejemplo en `docs/formato_datos/` y el modo `?sim=1`.
- Un cambio de campo rompe la pantalla → todo acceso a datos pasa por `api.js`, así el cambio se hace en un solo lugar.
- Rendimiento en la Raspberry Pi → evitar redibujar toda la tabla en cada *polling*; actualizar solo lo que cambió.

## Añadido: monitor y kiosko en la Raspberry Pi 5
- [ ] Script de arranque: `chromium-browser --kiosk --noerrdialogs --disable-infobars http://localhost:8000/`, ejecutado automáticamente al encender la Pi.
- [ ] Panel de la Pi con datos reales de `/api/v1/sistema` (reemplaza los simulados).
- [ ] Probar en el monitor real: resolución, tamaños de letra, contraste y distancia de lectura.
