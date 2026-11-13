# Prototipos adaptables a monitor vertical

Copias de `prototipo2` y `prototipo3-simple` que funcionan con el monitor **horizontal o vertical** (girado 90°, por ejemplo 1080 × 1920). Los originales no se modificaron.

| Archivo | Basado en |
|---|---|
| `prototipo2/index.html` | `frontend/prototipo2/` (cinta animada y detalle por fruta) |
| `prototipo3-simple/index.html` | `frontend/prototipo3-simple/` (versión simple) |

## Cómo funciona

- **Automático:** si la pantalla es más alta que ancha (y mide al menos 700 px de ancho), se usa el diseño vertical. Si el monitor se gira con la página abierta, el diseño cambia solo.
- **Forzado por URL:** `?orientacion=vertical` o `?orientacion=horizontal`. Sirve si la detección falla en la Raspberry Pi.
- En horizontal, cada prototipo se ve **igual que el original**.
- En el código, todo el diseño vertical está en un bloque CSS marcado con `Pantalla vertical`, al final del `<style>`. Las reglas aplican a `html.vertical`, y un pequeño script en el `<head>` pone o quita esa clase.

## Qué cambia en vertical

**prototipo2**
- Cabecera en dos líneas: la marca arriba; el lote, el turno, la cinta, la baliza y el reloj debajo.
- La línea queda en 4 columnas: E1 a E4 con la cinta animada debajo, luego el grupo en curso y abajo E5 y E6.
- El historial ocupa todo el ancho (11 filas). Las alertas y los 4 indicadores quedan lado a lado.

**prototipo3-simple**
- Cabecera en dos líneas.
- E1 a E4 en una fila y E6 (cinta) en una franja ancha debajo.
- Grupo en curso y últimos grupos (11 filas), luego alertas y, al pie, 3 indicadores con la barra de categorías a todo el ancho.

## Probar sin girar el monitor

- Chrome o Edge: F12 → modo dispositivo (Ctrl+Shift+M) → dimensiones `1080 × 1920`.
- O abrir el archivo con `?orientacion=vertical` en una ventana angosta.

## En la Raspberry Pi 5

Hay que girar la pantalla en el sistema, no en el navegador: en Raspberry Pi OS, *Preferencias → Screen Configuration → Orientation*. Desde la terminal, con Wayland: `wlr-randr --output HDMI-A-1 --transform 90`. Chromium en modo kiosko recibe entonces una ventana vertical, y el dashboard cambia de diseño solo.

## Pendiente

- Probarlo en el monitor real: distancia de lectura y tamaño de letra.
- Cuando se elija el diseño final, llevar este bloque CSS y el script del `<head>` a `frontend/index.html`.
