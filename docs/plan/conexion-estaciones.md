# Conexión entre estaciones y E5

**Estado:** propuesta, pendiente de aprobación del equipo · **Propuesta de:** Christian (Rol C)
**Responsable de confirmarla con las otras estaciones:** Maicol (Rol B)

> Las estaciones **no se conectan entre sí**. Todas envían sus datos a E5, que corre en la Raspberry Pi 5. El dashboard también lee de esa misma API.

## 1. Cómo se comunican (ya definido en el plan)

- Protocolo: **HTTP**, con un `POST` de JSON a la API de E5 (FastAPI).
- Rutas: `/api/v1/ingest/e1`, `/e2`, `/e3`, `/e4` y `/e6`.
- Un mensaje **por grupo y por estación**, con la lista de frutas adentro (contratos v2 en `docs/formato_datos/`).
- E5 valida con Pydantic. Si el mensaje es inválido responde error 422 y no lo guarda.

## 2. Red física (propuesta)

**Cable Ethernet a un router o switch propio del proyecto, y Wi-Fi solo como respaldo.**

| Decisión | Propuesta |
|---|---|
| Medio | Ethernet para todo equipo que tenga puerto. Wi-Fi solo para equipos que no puedan (por ejemplo un ESP32). |
| Red | Router o switch propio del proyecto, sin internet, solo para la línea. No usar la red del colegio. |
| IP de la Pi | Fija (reservada en el router), por ejemplo `192.168.10.10`. |
| Dirección que usa cada estación | `http://192.168.10.10:8000/api/v1/ingest/eX` |
| Dashboard | Corre en la misma Pi: `http://localhost:8000/`. |

**Por qué cable:** una caída de Wi-Fi haría que E5 marque "sin señal" en una estación que sí funciona, y en una demo eso se nota. Los mensajes son pequeños, así que la velocidad no es el problema; lo importante es que no se corten. La Pi 5 trae puerto Ethernet y un switch de 5 puertos es barato.

## 3. Robustez (propuesta)

- **Reintentos:** si E5 no responde, la estación guarda el mensaje y reintenta (por ejemplo cada 2 s, hasta 5 veces). No debe perder datos ni bloquear su proceso.
- **Autenticación simple:** un header `X-API-Key` con una clave compartida del equipo, para que un equipo cualquiera de la red no pueda enviar datos. Es opcional en la primera demo.
- **Señal de vida:** `GET /api/v1/estaciones/estado` marca una estación como "sin señal" si no llega un mensaje en un tiempo definido.

## 4. Pendientes y quién los resuelve

| Pendiente | Responsable |
|---|---|
| Qué equipo usa cada estación (PC, Pi, ESP32) y si tiene puerto de cable | Maicol |
| Si se puede instalar un router o switch propio en el lugar de la demo | Todo el equipo |
| Reservar la IP fija de la Pi en el router | Quien configure la red |
| Tiempo máximo sin mensajes para marcar "sin señal" | Gabriel y Maicol |
| Si la clave `X-API-Key` entra en la primera demo | Todo el equipo |
| Corregir el README: E6 aparece como "estado del carrito" y debe decir cinta transportadora (`estado_cinta`) | Quien edite el README |
