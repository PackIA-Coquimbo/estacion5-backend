# Registro de avance — Dashboard (Rol C)

**Responsable:** Christian · **Área:** `frontend/` · **Rama:** `feat/c-prototipo-v2-contratos`
**Última actualización:** 2026-11-13

> **Para qué sirve este documento:** dejar por escrito qué se hizo en el dashboard, por qué, para qué sirve y qué falta, de modo que Gabriel (backend) y Maicol (integración) puedan entender el estado sin preguntar, y que cualquiera retome el trabajo con contexto. Se actualiza agregando entradas nuevas al final de la sección 4.

---

## 1. Resumen en 30 segundos

- El dashboard es la pantalla de supervisión de la **Estación 5**, que se mostrará en un **monitor conectado a una Raspberry Pi 5**.
- Hoy funciona **solo con datos simulados** dentro del navegador. Todavía no está conectado a la API.
- Esta etapa dejó listo: una versión **simplificada** del dashboard para comparar con la anterior, el **nombre de campo `tamano`** alineado al contrato v2, la **capa de datos (`api.js`)** con ejemplos de lo que el dashboard espera recibir del backend, y **copias de ambos diseños que se adaptan a un monitor vertical** (`frontend/vertical/`).
- Lo que sigue depende de otras personas: Gabriel debe construir los endpoints, y el equipo debe decidir cuál de los dos diseños usar.

## 2. Contexto del proyecto (decisiones del equipo)

Estas decisiones están confirmadas y el dashboard se construye sobre ellas. El detalle completo está en `docs/plan/plan-avance-e5.md`.

| Tema | Decisión |
|---|---|
| Transporte | Cinta transportadora (no carrito). E6 informa `estado_cinta`. |
| Unidad de seguimiento | Grupo de frutas (`id_grupo`), con datos por fruta (`id_fruta`). |
| Estación 3 | Informa `diametro_mm` y `tamano` (`pequeno`, `mediano` o `grande`) por fruta. Ejemplo: 40 mm, mediano. |
| Equipo | Raspberry Pi 5 con monitor (modo kiosko) y base de datos SQLite. |
| Contratos | Los JSON de `docs/formato_datos/` son la fuente de verdad. |

**Roles:** Gabriel (A) backend y datos · Maicol (B) integración y calidad · Christian (C) dashboard.

## 3. Mapa de archivos del frontend

| Archivo | Qué es | Estado |
|---|---|---|
| `frontend/prototipo2/index.html` | Dashboard completo, con animación de cinta, listas por fruta y panel de la Pi. Es la referencia original. | Usa datos simulados. Campo `calibre` renombrado a `tamano`. |
| `frontend/prototipo3-simple/index.html` | Versión simplificada del mismo dashboard, para comparar y elegir. | Usa datos simulados. |
| `frontend/index.html` | Copia de `prototipo1`. | **Desactualizado.** Se reemplazará cuando se decida qué diseño usar. |
| `frontend/api.js` | Capa de datos: todas las llamadas a la API pasan por aquí. | Listo, sin uso todavía. |
| `frontend/mock/*.json` | Ejemplos de lo que devolverá la API. | Propuesta para Gabriel. |
| `frontend/vertical/` | Copias de `prototipo2` y `prototipo3-simple` que funcionan con el monitor horizontal o vertical. Incluye un README. | Usan datos simulados. Vistas en navegador; falta probarlas en el monitor real. |

## 4. Registro de lo realizado

### 4.1 Versión simplificada del dashboard (`prototipo3-simple`)

- **Qué es:** una segunda versión del dashboard, más simple, en una carpeta aparte. `prototipo2` no se modificó en este paso.
- **Por qué:** el dashboard original muestra mucha información y es pesado (285 KB, con una tipografía incrustada y una animación continua de la cinta). Se pidió una versión simple para tenerla como referencia y **validar en equipo cuál se usa**.
- **Para qué:** que la persona de planta vea de un vistazo si todo marcha bien, y que la Raspberry Pi lo dibuje con poco esfuerzo.
- **Qué hace:**
  - Cabecera con lote, estado de la cinta y reloj; barra roja con botón "Reanudar cinta" si hay falla.
  - Cinco tarjetas (E1, E2, E3, E4 y E6) con estado y un dato principal por estación. Ejemplo de E3: "102 mm de diámetro medio, 2 mediano, 1 grande".
  - Grupo en curso con su avance E1 a E5, tabla de los últimos 8 grupos y las últimas 6 alertas.
  - Cuatro indicadores: frutas en la última hora, % de rechazo, alertas en la última hora y categoría final por fruta.
  - Tres botones de simulación para la demo: falla de cinta, corte de señal de E3 y baja confianza de E2.

**Comparación:**

| | `prototipo2` | `prototipo3-simple` |
|---|---|---|
| Tamaño del archivo | 285 KB | 28 KB |
| Tipografía | Incrustada (240 KB) | Del sistema |
| Cinta animada con frutas | Sí | No |
| Detalle por fruta en cada estación | Sí (lista) | No (resumen por grupo) |
| Panel de la Raspberry Pi, tiempos por etapa, gráfico y anomalías por estación | Sí | No |
| Tarjeta de E5 | Sí | No (la pantalla ya corre en ese equipo) |
| Alertas, historial de grupos y botón de reanudar | Sí | Sí |

### 4.2 Renombrar `calibre` a `tamano` en `prototipo2`

- **Qué:** se cambió el nombre del campo en 5 puntos del código (generador de E3, regla de categoría, texto de la alerta, filtro de la alerta y tabla de E3).
- **Por qué:** el contrato v2 define `tamano`. Así el dashboard usa los mismos nombres que usarán las estaciones y el backend.
- **Nota:** el texto de la alerta pasó de "bajo calibre mínimo" a "bajo el tamaño mínimo".

### 4.3 Capa de datos (`frontend/api.js`) y ejemplos (`frontend/mock/`)

- **Qué es:** un archivo que concentra todas las llamadas a la API. El dashboard no debe usar `fetch` directamente.
- **Por qué:** si el backend cambia un campo o una ruta, se corrige en un solo archivo y no en toda la pantalla. Además, permite trabajar antes de que exista el backend.
- **Para qué:** que el dashboard pueda pasar de datos simulados a datos reales sin reescribirlo, y que Gabriel tenga una especificación concreta de lo que necesita la pantalla.

**Funciones:**

| Función | Ruta de la API | Devuelve |
|---|---|---|
| `getGrupos({lote, limit})` | `GET /api/v1/lotes/{lote}/grupos` | Últimos grupos con sus frutas, estado y hora de salida |
| `getMetricas(lote)` | `GET /api/v1/metricas` | Frutas de la última hora, % de rechazo, conteo por categoría |
| `getAlertas({activas})` | `GET /api/v1/alertas` | Alertas con severidad, estación, mensaje, grupo y hora |
| `getEstaciones()` | `GET /api/v1/estaciones/estado` | Última lectura y señal de E1 a E4 y E6 |
| `getGrupo(id)` | `GET /api/v1/grupos/{id}` | Trazabilidad completa de un grupo |

**Modos de uso (parámetro en la URL):**

| URL | Qué hace |
|---|---|
| (sin parámetros) | Usa la API real. Si la sirve la propia API, usa su dirección; si se abre como archivo, usa `localhost:8000`. |
| `?api=http://IP:8000` | Usa la API en otra dirección, por ejemplo la Raspberry Pi. |
| `?mock=1` | Lee los ejemplos de `frontend/mock/`. Requiere abrir la página desde un servidor. |
| `?sim=1` | El dashboard usa sus datos simulados internos. Es el plan B de la demo si falla algo. |

Si la API no responde en 5 segundos o devuelve error, `api.js` entrega un mensaje claro para mostrarlo en pantalla.

### 4.4 Versiones adaptables a monitor vertical (`frontend/vertical/`)

- **Qué es:** copias de `prototipo2` y `prototipo3-simple` que cambian de diseño según la orientación del monitor. Los originales no se modificaron.
- **Por qué:** es probable que en la presentación el monitor de la Raspberry Pi esté **vertical** (por ejemplo, 1080 × 1920). Los prototipos originales están pensados para una pantalla horizontal; en vertical, sus columnas quedan demasiado angostas y la letra demasiado chica.
- **Para qué:** tener la pantalla lista para cualquiera de las dos orientaciones, sin mantener dos versiones distintas de cada diseño.
- **Cómo funciona:**
  - **Automático:** si la pantalla es más alta que ancha (y mide al menos 700 px de ancho), se usa el diseño vertical. Si se gira el monitor con la página abierta, el diseño cambia solo. Los celulares mantienen el diseño que ya tenían.
  - **Forzado:** `?orientacion=vertical` o `?orientacion=horizontal` en la URL, por si la detección falla en la Pi.
  - En horizontal, cada copia se ve **igual que su original**.
  - Todo el diseño vertical está en un solo bloque CSS (reglas sobre `html.vertical`), más un script corto en el `<head>` que pone o quita esa clase. Se puede llevar tal cual al `frontend/index.html` final.
- **Qué cambia en vertical:**

| | `prototipo2` | `prototipo3-simple` |
|---|---|---|
| Cabecera | Dos líneas: marca arriba; lote, turno, cinta, baliza y reloj debajo | Dos líneas: marca arriba; lote, cinta y reloj debajo |
| Estaciones | E1 a E4 en 4 columnas con la cinta animada debajo; luego el grupo en curso; abajo E5 y E6 | E1 a E4 en una fila; E6 en una franja ancha debajo |
| Historial | A todo el ancho, 11 grupos (12 en horizontal) | 11 grupos (8 en horizontal) |
| Alertas e indicadores | Lado a lado: alertas a la izquierda, 4 indicadores a la derecha | Alertas debajo de los grupos; 3 indicadores y la barra de categorías al pie |

- **En la Raspberry Pi:** la pantalla se gira en el sistema operativo, no en el navegador (*Preferencias → Screen Configuration → Orientation*, o `wlr-randr --output HDMI-A-1 --transform 90`). Chromium en modo kiosko recibe entonces una ventana vertical. Ese comando no se ha probado todavía.

## 5. Qué se verificó y qué no

**Verificado:**
- La sintaxis del JavaScript de `prototipo2`, `prototipo3-simple` y `api.js`.
- `prototipo3-simple`: se ejecutó el código en Node con un documento simulado, durante 400 pasos de reloj acelerado. Recorre E1 a E4, el registro y el grupo siguiente; también la falla de cinta, el corte de E3 y la baja de confianza. Esa prueba encontró y corrigió un error que habría roto la página al iniciar.
- `api.js`: se probaron sus tres modos con un `fetch` simulado y se comprobó que arma bien cada dirección.
- Los JSON de ejemplo: se revisó que los números sean coherentes entre sí (tamaños según diámetro, categorías que suman el total, detalle igual al primer grupo de la lista).
- `frontend/vertical/`: se tomaron capturas de ambas copias con Edge en modo sin ventana, a 1080 × 1920 (vertical) y 1920 × 1080 (horizontal). En vertical se corrigieron textos cortados en la tarjeta E1, filas cortadas en el historial y la altura de las tarjetas con 4 o 5 frutas. En horizontal se ven igual que los originales.

**No verificado:**
- Los originales (`prototipo2` y `prototipo3-simple`) no se han revisado en un navegador: falta revisar aspecto, ajuste al monitor y rendimiento. Las capturas de `frontend/vertical/` en horizontal sirven de referencia, porque en esa orientación son iguales.
- El diseño vertical solo se vio en capturas a 1080 × 1920; falta verlo en el monitor real (distancia de lectura y tamaño de letra).
- Nada se ha probado en la Raspberry Pi.
- `api.js` no se ha probado contra una API real, porque los endpoints aún no existen.
- Ninguna pantalla usa todavía `api.js`.

## 6. Qué necesita cada persona

| Persona | Qué se necesita | Referencia |
|---|---|---|
| **Gabriel** | Revisar la forma de las respuestas (`frontend/api.js`, comentario del encabezado, y `frontend/mock/`) y construir los endpoints con esa forma. Confirmar un punto: en `estaciones.json`, la entrada de E6 incluye `estado_cinta` y `falla_mecanica_detectada`. | `docs/plan/rol-a-backend.md`, días 3 y 4 |
| **Maicol** | Confirmar los contratos v2 con las otras estaciones y pedir a E3 los **rangos reales de diámetro** para pequeño, mediano y grande. | `docs/plan/rol-b-integracion.md`, día 1 |
| **Todos** | Decidir entre `prototipo2` y `prototipo3-simple` (o una mezcla), y confirmar si el monitor de la demo estará vertical. | Sección 3, comparación de 4.1 y sección 4.4 |

## 7. Decisiones abiertas

1. **Qué diseño usar.** Hasta decidirlo no se reemplaza `frontend/index.html` ni se separa el código en archivos.
2. **Rangos de tamaño de E3.** Los dos prototipos usan cortes provisorios: pequeño por debajo de 92 mm, mediano de 92 a 111 mm y grande desde 112 mm. El ejemplo del equipo (40 mm, mediano) no calza con ellos; hay que usar los valores reales que informe E3.
3. **Quién calcula las anomalías.** En los prototipos el navegador las calcula; en el plan, las calcula el backend. Al conectar la API, el dashboard solo debe mostrar lo que entregue el servidor.
4. **Orientación del monitor.** Es probable que sea vertical. Las copias de `frontend/vertical/` sirven para ambas orientaciones; cuando se elija el diseño, el bloque vertical se lleva a `frontend/index.html`.

## 8. Próximos pasos del dashboard

Según `docs/plan/rol-c-dashboard.md`:

1. Decidir el diseño y dejar `frontend/index.html` igual al elegido, partiendo de su copia en `frontend/vertical/` para conservar el modo vertical.
2. Separar el código de la pantalla en archivos (`app.js` y `sim.js`), usando `api.js` para los datos.
3. Conectar tabla de grupos, indicadores y tarjetas de estación a la API (consulta cada 3 a 5 segundos), cuando Gabriel entregue los endpoints.
4. Panel de alertas, estado de cada estación y vista de trazabilidad de un grupo.
5. Script de kiosko y pruebas en el monitor y en la Raspberry Pi.

## 9. Historial de commits de esta rama

| Commit | Mensaje |
|---|---|
| `2573f10` | agrega prototipo 3 simple del dashboard como referencia |
| `3215f74` | renombra calibre a tamano en prototipo 2 según contrato v2 |
| `72e20a8` | agrega capa de datos api.js y ejemplos de respuesta del dashboard |
| `34e0c09` | agrega registro de avance del dashboard |
| `726ab14` | agrega versiones de prototipo 2 y 3 adaptables a monitor vertical |
| `8ff6908` | actualiza registro de avance con las versiones para monitor vertical |

La rama está subida a GitHub y lista para el PR a `main`.
