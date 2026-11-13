# Contratos de datos v2 — Estación 5

Estos JSON son la **única fuente de verdad** de lo que cada estación envía a la API de E5. Si un campo cambia, se actualiza primero aquí, se avisa al equipo y recién después se cambian `app/schemas.py`, la base de datos y el frontend.

**Regla general:** un mensaje por grupo y por estación, con la lista de frutas adentro (E2, E3 y E4). E6 informa el estado de la cinta y no depende de un grupo.

## Endpoints

| Estación | Método y ruta | Ejemplo |
|---|---|---|
| E1 — Recepción y captura | `POST /api/v1/ingest/e1` | [E1.json](E1.json) |
| E2 — Calidad visual | `POST /api/v1/ingest/e2` | [E2.json](E2.json) |
| E3 — Diámetro y tamaño | `POST /api/v1/ingest/e3` | [E3.json](E3.json) |
| E4 — Decisión comercial | `POST /api/v1/ingest/e4` | [E4.json](E4.json) |
| E6 — Estado de la cinta | `POST /api/v1/ingest/e6` | [E6.json](E6.json) |

Respuesta esperada: **201** si el mensaje es válido y **422** si falta un campo, un valor está fuera de rango o `estacion` no coincide con la ruta.

## Campos comunes

| Campo | Tipo | Obligatorio | Notas |
|---|---|---|---|
| `id_lote` | texto | sí | Ejemplo: `LOTE-2026-11-A` |
| `id_grupo` | texto | sí (excepto E6) | Ejemplo: `G-0001` |
| `estacion` | `E1`, `E2`, `E3`, `E4` o `E6` | sí | Debe coincidir con la ruta |
| `timestamp` | fecha ISO 8601 **con zona horaria** | sí | La pone la estación al medir. Ejemplo: `2026-11-18T10:15:30Z` |

## Campos por estación

### E1 — `datos`
| Campo | Tipo | Valores |
|---|---|---|
| `validez_imagen` | booleano | `true` / `false` |
| `estado_captura` | texto | `aceptada`, `repetir`, `revision` |
| `posicion_correcta` | booleano | `true` / `false` |
| `frutas_detectadas` | entero | mayor que 0 |

### E2 — `frutas[]`
| Campo | Tipo | Valores |
|---|---|---|
| `id_fruta` | texto | `F1`, `F2`, … |
| `calidad_visual` | texto | `alta`, `media`, `baja`, `defectos_visibles`, `revision` |
| `confianza_visual` | decimal | entre 0 y 1 |
| `defectos_detectados` | lista de texto | puede ir vacía; lista cerrada por confirmar con E2 |

### E3 — `frutas[]`
| Campo | Tipo | Valores |
|---|---|---|
| `id_fruta` | texto | `F1`, `F2`, … |
| `diametro_mm` | número | mayor que 0 |
| `tamano` | texto | `pequeno`, `mediano`, `grande` |

E3 calcula el tamaño. E5 guarda el diámetro y el tamaño tal como llegan y **no** recalcula nada.

### E4 — `frutas[]`
| Campo | Tipo | Valores |
|---|---|---|
| `id_fruta` | texto | `F1`, `F2`, … |
| `categoria_final` | texto | `exportacion`, `mercado_nacional`, `proceso`, `rechazo`, `revision_manual` |
| `probabilidad` | decimal | entre 0 y 1 |
| `requiere_revision_manual` | booleano | `true` / `false` |

### E6 — `datos`
| Campo | Tipo | Valores |
|---|---|---|
| `estado_cinta` | texto | `normal`, `detenida`, `falla_mecanica` |
| `falla_mecanica_detectada` | booleano | `true` / `false` |
| `id_grupo_en_cinta` | texto | opcional |

## Preguntas abiertas con las otras estaciones

Si una estación no responde, se avanza con la **respuesta por defecto** y se avisa en el chat.

| Pregunta | Para | Respuesta por defecto |
|---|---|---|
| ¿Quién asigna `id_grupo` e `id_fruta`? | E1 y todas | E1 asigna `G-0001` y `F1..Fn`; las demás los reutilizan |
| Rangos de diámetro para pequeño, mediano y grande | E3 | Pendiente. El ejemplo usa 40 mm → mediano; el simulador recibe los rangos como parámetro |
| Lista cerrada de `defectos_detectados` | E2 | Texto libre en minúsculas con guion bajo (`mancha_leve`) |
| Frecuencia de envío del estado de la cinta | E6 | Cada vez que cambia, más un *heartbeat* cada 10 s |
| URL de la API de E5 | todas | `http://<IP-fija-de-la-Raspberry-Pi>:8000` (IP por definir) |

## Mensaje para enviar a las otras estaciones

> Hola, somos E5 (Supervisión y Trazabilidad). Cerramos el formato v2 de los mensajes que nos envían: un mensaje por grupo de frutas, con la lista de frutas adentro. Los ejemplos y campos están en `docs/formato_datos/` del repo de E5. Necesitamos que nos confirmen **hoy**: (1) si E1 asigna `id_grupo` y `id_fruta`, (2) los rangos de diámetro de E3, (3) la lista de defectos de E2 y (4) cada cuánto envía E6 su estado. Si no tenemos respuesta, avanzamos con los valores por defecto que dejamos en el documento.
