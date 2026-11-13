# Plan de trabajo — Conexiones de la línea

**Objetivo:** que las estaciones E1, E2, E3, E4 y E6 envíen sus mensajes a E5 (Raspberry Pi 5) por la red del proyecto, de forma estable y lista para la demo.
**Jornada de conexiones:** miércoles 18 de noviembre de 2026, con **todo el equipo** (Gabriel, Maicol y Christian). Todas las fases se hacen en conjunto.
**Base técnica:** [`conexion-estaciones.md`](conexion-estaciones.md) (cómo se comunican y por qué cable) · maqueta: [`conexion-estaciones.html`](conexion-estaciones.html) · contratos: [`../formato_datos/`](../formato_datos/).

---

## 0. Cómo usar este documento

- Las fases van **en orden**. Cada una termina con una prueba **"Listo cuando"**. No se pasa a la siguiente hasta que esa prueba funcione.
- Marca cada casilla `[x]` al terminar y sube el cambio, así todos ven en qué paso va la red.
- Los nombres de menús del router pueden variar un poco según la versión de su firmware. Si un menú no aparece donde dice el plan, búscalo dentro de **Advanced** (Avanzado) con un nombre parecido.
- **Nunca** se escriben contraseñas en este repo. Se guardan donde el equipo acuerde (por ejemplo, un mensaje fijado en el grupo del equipo).
- Si algo falla, revisa primero la **sección 11 (Problemas comunes)**.

### Palabras que se usan

| Palabra | Qué significa aquí |
|---|---|
| **Router** | El TP-Link Archer AX1800. Crea la red de la línea y entrega las direcciones IP. |
| **Switch** | Caja con muchos puertos de red. Se conecta al router para tener más puertos. No se configura. |
| **Puerto LAN** | Puerto del router para los equipos de la línea (Pi, estaciones, switch). |
| **Puerto WAN / Internet** | Puerto del router que recibe internet desde otra red (por ejemplo, la del colegio). |
| **IP** | Dirección de un equipo en la red, por ejemplo `192.168.0.10`. |
| **MAC** | Identificador fijo de la tarjeta de red de un equipo, por ejemplo `D8:3A:DD:12:34:56`. Sirve para reservarle una IP. |
| **Reserva de IP** | Regla en el router: "a esta MAC dale siempre esta IP". |
| **SSH** | Forma de manejar la Pi desde un notebook escribiendo comandos, sin teclado ni pantalla en la Pi. |
| **API** | El programa de E5 que recibe los mensajes de las estaciones (puerto `8000`). |

---

## 1. Material

| Material | Estado |
|---|---|
| Raspberry Pi 5 | ✅ Disponible |
| Fuente oficial USB-C de 27 W para la Pi | ⏳ Por confirmar |
| Tarjeta microSD de 32 GB | ✅ Disponible |
| Router TP-Link Archer AX1800 (Wi-Fi 6, doble banda) con su fuente | ✅ Disponible |
| Monitor | ✅ Disponible |
| Cable micro-HDMI a HDMI | ✅ Disponible |
| Teclado y mouse (solo para la instalación) | ⏳ Por confirmar |
| Notebook con Windows o Linux para configurar y probar | ✅ Los del equipo |
| Tubos PVC con abrazaderas y tees | ✅ Disponibles · falta medir si alcanzan (Fase 6) |
| Codos y uniones PVC | ⏳ Por confirmar según el recorrido |
| Cables de red (uno por equipo cableado, más 2 de repuesto) | ⏳ Por confirmar cuántos hay |
| Switch de 8 puertos | ⏳ Por conseguir |

**Límite actual:** el router trae 4 puertos LAN. Uno es para la Pi, así que **solo 3 estaciones pueden ir por cable** hasta que llegue el switch. Las otras van por Wi-Fi mientras tanto.

---

## 2. Plan de direcciones

Todas las IP de equipos de la línea se **reservan en el router** (paso 2.5), así cada equipo recibe siempre la misma.

| Equipo | IP | Conexión ahora | Conexión con switch |
|---|---|---|---|
| Router | `192.168.0.1` | — | — |
| Raspberry Pi 5 (E5) | `192.168.0.10` | Cable, LAN 1 | Cable |
| E1 | `192.168.0.11` | Por definir | Cable |
| E2 | `192.168.0.12` | Por definir | Cable |
| E3 | `192.168.0.13` | Por definir | Cable |
| E4 | `192.168.0.14` | Por definir | Cable |
| E6 | `192.168.0.16` | Por definir | Cable |
| Notebooks del equipo | Automática (`.100` en adelante) | Wi-Fi | Wi-Fi |

**Dirección a la que envía cada estación:** `http://192.168.0.10:8000/api/v1/ingest/eX` (cambiando `eX` por `e1`, `e2`, `e3`, `e4` o `e6`).

> Si en el paso 1.6 el router muestra otra red (por ejemplo `192.168.1.1`), se usa esa misma numeración (`192.168.1.10`, `192.168.1.11`, …) y se corrige esta tabla en el repo.

---

## 3. Fase 1 — Configurar el router · Responsables: todos

### 1.1 Conocer el router

Revisa la parte trasera y frontal antes de conectar nada.

| Parte | Dónde | Para qué |
|---|---|---|
| Entrada de corriente | Atrás | Fuente del router. |
| Botón **Power** | Atrás | Enciende y apaga. |
| Puerto **Internet / WAN** | Atrás, separado de los otros (a veces de otro color) | Solo para traer internet. **Nunca** se conecta ahí la Pi ni una estación. |
| Puertos **LAN 1 a 4** | Atrás, juntos | Pi, estaciones y, más adelante, el switch. |
| Botón **Reset** | Atrás, hundido (se presiona con un clip) | Volver a la configuración de fábrica (ver 1.9). |
| Etiqueta | Abajo | Nombre y clave del Wi-Fi de fábrica, y dirección de configuración. |
| Luces | Adelante | Encendido, Wi-Fi 2,4 GHz, Wi-Fi 5 GHz, Internet y puertos LAN. |

📷 Saca una foto de la etiqueta de abajo y guárdala junto a las contraseñas del equipo.

### 1.2 Conectar físicamente

1. Pon el router en un lugar cercano a la Pi y al centro de la línea, a la vista y con ventilación.
2. Conecta la fuente y presiona **Power**. Espera **2 minutos** hasta que las luces se estabilicen.
3. **Internet (opcional, recomendado al principio):** conecta un cable desde la red del colegio (o de casa) al puerto **Internet/WAN**. Sirve para instalar programas en la Pi en la Fase 2. Si no hay red disponible, sigue sin él y revisa el riesgo correspondiente en la sección 12.
4. Conecta un notebook al router:
   - **Por Wi-Fi:** usa el nombre y la clave de la etiqueta de abajo, **o**
   - **Por cable:** del notebook a cualquier puerto **LAN**.

### 1.3 Primer ingreso

1. En el notebook, abre el navegador y entra a **`http://tplinkwifi.net`**. Si no carga, usa **`http://192.168.0.1`**.
2. La primera vez, el router pide **crear la contraseña de administrador**. Escríbela dos veces y guárdala en el lugar acordado por el equipo.
   - Esta clave sirve para **configurar** el router. No es la clave del Wi-Fi.
3. Si aparece una invitación a iniciar sesión con **TP-Link ID** (cuenta en la nube), elige **omitir / más tarde**. No es necesaria.

### 1.4 Asistente rápido (Quick Setup)

Después del primer ingreso se abre el asistente. Si no aparece, búscalo como **Quick Setup** en el menú superior.

1. **Región y zona horaria:** Chile, `(UTC-04:00) Santiago` (o la que ofrezca para Santiago).
2. **Tipo de conexión a internet:**
   - Si conectaste el cable al puerto WAN: elige **Auto Detect** o **Dynamic IP**.
   - Si no hay cable en WAN: el asistente avisará que no hay internet. Elige **omitir / skip** y continúa.
3. **Wi-Fi:** desactiva **Smart Connect** si aparece, para configurar cada banda por separado:

   | Banda | Nombre (SSID) | Seguridad | Clave |
   |---|---|---|---|
   | 2,4 GHz | `PackIA-Linea` | WPA2-Personal (o WPA2/WPA3) | La que acuerde el equipo, mínimo 12 caracteres |
   | 5 GHz | `PackIA-Linea-5G` | WPA2-Personal (o WPA2/WPA3) | La misma clave |

   - **Por qué dos nombres:** un ESP32 o un Arduino con Wi-Fi solo se conecta a **2,4 GHz**. Con dos nombres se sabe en qué banda queda cada equipo. Los notebooks pueden usar la de 5 GHz, que es más rápida.
   - No uses **solo WPA3**: algunos equipos antiguos o un ESP32 no se conectan.
4. Revisa el resumen y guarda. El router se reinicia el Wi-Fi: **vuelve a conectar el notebook a `PackIA-Linea`** con la clave nueva y entra otra vez a `http://tplinkwifi.net`.

### 1.5 Revisar el Wi-Fi

En **Advanced → Wireless → Wireless Settings**:

- [ ] Las dos bandas están activas, con los nombres de la tabla anterior.
- [ ] **Hide SSID** (ocultar red) está **desactivado**.
- [ ] Si el lugar tiene muchas redes, deja el canal en **Auto** por ahora. Si en las pruebas hay cortes, se cambia (ver sección 11).

### 1.6 Revisar la red interna (LAN y DHCP)

1. En **Advanced → Network → LAN**, anota la **IP del router** (normalmente `192.168.0.1`) y la máscara (`255.255.255.0`). **No la cambies.**
2. En **Advanced → Network → DHCP Server**:
   - [ ] **DHCP Server** está **activado**.
   - [ ] Anota el rango de direcciones automáticas (**IP Address Pool**), por ejemplo `192.168.0.100 – 192.168.0.249`.
   - Las IP fijas del plan (`.10` a `.16`) quedan **fuera** de ese rango a propósito, para que nunca se las entregue a otro equipo.
3. Si el router usa otra red, corrige la tabla de la sección 2 antes de seguir.

### 1.7 Evitar reinicios sorpresa

1. En **Advanced → System → Firmware Update**, revisa si hay una opción de **actualización automática**. Si existe, **desactívala**.
2. En **Advanced → System → Reboot Schedule** (o "Reinicio programado"), confirma que esté **desactivado**.
3. Si el router ofrece funciones de **Parental Controls**, **QoS** o **HomeShield**, déjalas desactivadas. No se usan en la línea.

### 1.8 Respaldar la configuración

1. En **Advanced → System → Backup & Restore**, presiona **Backup**. Se descarga un archivo de configuración.
2. Guárdalo junto a las contraseñas del equipo (**no** en el repo). Si alguien resetea el router, se recupera todo con **Restore** en segundos.
3. Repite el respaldo cada vez que cambies algo importante (por ejemplo, al agregar reservas de IP).

### 1.9 Si hay que volver a fábrica

Úsalo solo si nadie recuerda la clave de administrador o la configuración quedó mal.

1. Con el router **encendido**, presiona el botón **Reset** con un clip durante unos **10 segundos**, hasta que las luces parpadeen.
2. Suelta y espera **2 minutos**.
3. El router vuelve a la configuración de la etiqueta. Entra de nuevo (1.3) y usa **Restore** con el respaldo (1.8), o repite los pasos 1.3 a 1.8.

### ✅ Listo cuando

- [ ] Un notebook conectado a `PackIA-Linea` abre `http://tplinkwifi.net` con la clave de administrador nueva.
- [ ] El respaldo de configuración está guardado.
- [ ] La red real del router quedó anotada en la sección 2.

---

## 4. Fase 2 — Pi en la red con la API · Responsables: todos

### 2.1 Preparar la tarjeta microSD (en un notebook)

1. Descarga e instala **Raspberry Pi Imager** desde `raspberrypi.com/software`.
2. Inserta la microSD en el notebook y abre el Imager.
3. Elige:
   - **Dispositivo:** Raspberry Pi 5.
   - **Sistema operativo:** **Raspberry Pi OS (64-bit)**. Tiene que ser la versión de 64 bits.
   - **Almacenamiento:** la microSD. ⚠️ Revisa que sea la microSD y no otro disco: se borra completa.
4. Cuando pregunte si quieres **personalizar el sistema** (OS customisation), elige **editar ajustes**. En versiones nuevas del Imager esto aparece como un asistente, pero las opciones son las mismas:

   | Opción | Valor |
   |---|---|
   | Nombre del equipo (hostname) | `e5-pi` |
   | Usuario | `packia` |
   | Contraseña | La que acuerde el equipo (guardarla con las demás) |
   | Wi-Fi | **No configurar** (la Pi va por cable) |
   | Zona horaria | `America/Santiago` |
   | Teclado | `latam` o `es`, según el teclado que usen |
   | **SSH** (pestaña Servicios) | **Activado**, con usuario y contraseña |

5. Guarda, acepta y espera a que termine de **escribir y verificar**. Saca la microSD.

### 2.2 Primer arranque

1. Inserta la microSD en la Pi (ranura por debajo de la placa).
2. Conecta un **cable de red** desde la Pi al puerto **LAN 1** del router.
3. Opcional para este primer arranque: monitor por **micro-HDMI** (el puerto más cercano a la entrada de corriente), teclado y mouse.
4. Conecta la fuente USB-C. La Pi enciende sola. El **primer arranque tarda unos 3 a 5 minutos**: no la desconectes.

### 2.3 Encontrar la Pi en la red

1. En el notebook, entra a `http://tplinkwifi.net` → **Network Map → Clients** (o "Clientes").
2. Busca el equipo llamado **`e5-pi`** y anota:
   - Su **IP actual** (algo como `192.168.0.1xx`).
   - Su **MAC** (algo como `D8:3A:DD:xx:xx:xx`).
3. Si no aparece, revisa que la luz del puerto LAN del router y la del puerto de red de la Pi estén encendidas. Espera un minuto y recarga.

### 2.4 Probar el acceso por SSH

Desde el notebook, abre una terminal (en Windows: **PowerShell**) y escribe, con la IP del paso anterior:

```bash
ssh packia@192.168.0.1xx
```

- La primera vez pregunta si confías en el equipo: escribe `yes`.
- Escribe la contraseña de la Pi (no se ve mientras escribes; es normal).
- Si entras, verás algo como `packia@e5-pi:~ $`. Para salir: `exit`.

### 2.5 Reservar la IP fija de la Pi

1. En el router: **Advanced → Network → DHCP Server → Address Reservation → Add**.
2. Completa:
   - **MAC Address:** la MAC de la Pi (paso 2.3).
   - **Reserved IP Address:** `192.168.0.10`.
   - **Description:** `E5 Raspberry Pi`.
   - Marca **Enable** (activar).
3. Guarda.
4. Reinicia la Pi para que tome la IP nueva. Desde la sesión SSH: `sudo reboot`. Espera 1 minuto.
5. Conéctate de nuevo, ahora con la IP fija: `ssh packia@192.168.0.10`.
6. Haz un nuevo respaldo del router (paso 1.8).

> Si el router no acepta una IP fuera del rango automático, reserva la primera del rango (por ejemplo `192.168.0.100`), anótala en la sección 2 y úsala en todos los pasos siguientes en vez de `192.168.0.10`.

### 2.6 Actualizar la Pi e instalar Docker y git

Requiere internet en el router (paso 1.2.3). Todo se escribe en la sesión SSH:

```bash
sudo apt update && sudo apt full-upgrade -y     # actualiza el sistema (puede tardar 10-20 min)
sudo apt install -y git                          # git para clonar el repo
curl -fsSL https://get.docker.com | sh           # instala Docker y Docker Compose
sudo usermod -aG docker $USER                    # permite usar Docker sin sudo
exit                                             # salir y volver a entrar para aplicar el permiso
```

Vuelve a entrar con `ssh packia@192.168.0.10` y comprueba:

```bash
docker --version
docker compose version
```

Ambos comandos deben mostrar un número de versión.

### 2.7 Descargar el proyecto y levantar la API

```bash
cd ~
git clone https://github.com/PackIA-Coquimbo/estacion5-backend.git
cd estacion5-backend
docker compose -f docker-compose.yml up -d --build
```

- La **primera vez tarda varios minutos**, porque descarga la imagen de Python para ARM64 e instala dependencias.
- Se usa `-f docker-compose.yml` para tomar **solo la configuración de la Pi** (sin el modo de desarrollo).

### 2.8 Comprobar que funciona

En la Pi:

```bash
docker compose ps                          # el servicio "backend" debe decir "running" o "healthy"
curl http://localhost:8000/                # debe responder {"status":"online", ...}
```

En el notebook (conectado a `PackIA-Linea`), abre en el navegador:

- `http://192.168.0.10:8000/` → mensaje `"status": "online"`.
- `http://192.168.0.10:8000/docs` → página de documentación de la API con las rutas de ingesta.

### 2.9 Prueba de reinicio

1. En la Pi: `sudo reboot`.
2. Espera 2 minutos **sin hacer nada más**.
3. En el notebook, recarga `http://192.168.0.10:8000/docs`. Debe volver a abrir sola, porque Docker usa `restart: unless-stopped`.

### 2.10 Comandos útiles de la Pi

Todos se escriben dentro de `~/estacion5-backend`:

| Para qué | Comando |
|---|---|
| Ver si la API está corriendo | `docker compose ps` |
| Ver los mensajes de la API en vivo (salir con `Ctrl+C`) | `docker compose logs -f` |
| Detener la API | `docker compose -f docker-compose.yml down` |
| Actualizar a lo último de `main` | `git pull && docker compose -f docker-compose.yml up -d --build` |
| Ver la temperatura de la Pi | `vcgencmd measure_temp` |
| Ver la IP de la Pi | `hostname -I` |
| **Apagar la Pi correctamente** | `sudo shutdown -h now` (esperar a que se apague la luz verde antes de desenchufar) |

⚠️ No desenchufes la Pi sin apagarla: puede dañar la microSD o la base de datos.

### ✅ Listo cuando

- [ ] `http://192.168.0.10:8000/docs` abre desde un notebook en el Wi-Fi.
- [ ] Sigue abriendo después de reiniciar la Pi, sin tocar nada.

---

## 5. Fase 3 — Prueba de red con el simulador · Responsables: todos

El simulador hace el mismo recorrido que harán las estaciones reales, sin necesitarlas.

> ⚠️ **Importante:** hoy la API de `main` todavía valida con los **contratos v1**, y el simulador envía **contratos v2**. Por eso la API responderá **422** a los mensajes del simulador hasta que Gabriel actualice `app/schemas.py`. **Para probar la red esto no importa:** recibir un 422 demuestra que el mensaje llegó a la Pi y que la API respondió. Lo que indica un problema de red es un error de conexión o de tiempo de espera.

### 3.1 Preparar el notebook (una sola vez)

En la carpeta del repo, en el notebook:

**Windows (PowerShell):**
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

**Linux o Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 3.2 Comprobar la conexión básica

```bash
ping 192.168.0.10
```

Debe responder con tiempos de pocos milisegundos. Detener con `Ctrl+C` (en Windows se detiene solo).

```bash
curl http://192.168.0.10:8000/
```

En Windows PowerShell usa `curl.exe` en lugar de `curl`.

### 3.3 Correr el simulador

```bash
python tools/simulador.py --url http://192.168.0.10:8000 --grupos 50
```

Anota cuántos mensajes llegaron y cuántos fallaron por conexión.

### 3.4 Pruebas a realizar

| # | Prueba | Cómo | Resultado esperado |
|---|---|---|---|
| 1 | Notebook por Wi-Fi 5 GHz | Conectado a `PackIA-Linea-5G`, 50 grupos | Sin errores de conexión |
| 2 | Notebook por Wi-Fi 2,4 GHz | Conectado a `PackIA-Linea`, 50 grupos | Sin errores de conexión |
| 3 | Notebook por cable | Cable a un puerto LAN libre, 50 grupos | Sin errores de conexión |
| 4 | Fallas simuladas | Agregar `--falla-cinta`, `--sin-e3`, `--baja-confianza`, `--duplicados` | La API responde a todos |
| 5 | Corte de red | Desconectar el cable de la Pi 10 s durante una corrida con `--grupos 0` | Anotar qué mensajes se pierden y si se recupera al reconectar |
| 6 | Carga | `--grupos 200 --velocidad 5` | Anotar tiempos y temperatura de la Pi |

### 3.5 Correr los tests en la Pi

En la sesión SSH, dentro de `~/estacion5-backend`:

```bash
sudo apt install -y python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

Debe dar el mismo resultado que en los notebooks (hoy: 27 pasan y 46 se omiten hasta que existan los schemas v2).

### ✅ Listo cuando

- [ ] Las pruebas 1 a 3 llegan sin errores de conexión.
- [ ] El resultado de las pruebas 4 a 6 quedó anotado en `docs/avance/`.

---

## 6. Fase 4 — Conectar las estaciones reales · Responsables: todos

### 4.1 Levantar información de cada estación

Completa esta tabla con cada equipo de estación:

| Estación | Equipo (PC, Pi, ESP32, Arduino) | ¿Tiene puerto de red? | Distancia aprox. al router | Conexión asignada |
|---|---|---|---|---|
| E1 | | | | |
| E2 | | | | |
| E3 | | | | |
| E4 | | | | |
| E6 | | | | |

### 4.2 Repartir las conexiones mientras no hay switch

- Los **3 puertos LAN libres** (LAN 2, 3 y 4) van para las estaciones que **tienen puerto de red** y envían más mensajes. La prioridad es **E2 y E3**, que envían datos de cada fruta.
- Las demás se conectan por Wi-Fi: `PackIA-Linea` (2,4 GHz) si es ESP32 o Arduino con Wi-Fi, y `PackIA-Linea-5G` si es un PC o una Pi.
- Una estación con **Arduino Uno** no tiene red propia. Necesita un Ethernet Shield o un equipo intermedio por USB (ver `conexion-estaciones.md`).

### 4.3 Conectar y reservar la IP de cada estación

Repite esto con cada estación:

1. Conecta el equipo por cable al puerto LAN asignado, o al Wi-Fi que le corresponda.
2. En el router, busca el equipo en **Network Map → Clients** y anota su **MAC**.
3. Resérvale su IP de la sección 2 (como en el paso 2.5), con la descripción `E1`, `E2`, etc.
4. Reinicia la conexión de red del equipo (o el equipo) para que tome la IP nueva.
5. Comprueba desde el equipo de la estación: `ping 192.168.0.10`.
6. Respalda la configuración del router (paso 1.8).

### 4.4 Lo que se entrega a cada estación

Envíale a cada estación este mensaje (cambiando `eX` y `EX`):

> **Conexión a E5**
> - Red Wi-Fi: `PackIA-Linea` (2,4 GHz) o `PackIA-Linea-5G` (5 GHz). La clave se entrega en persona.
> - Tu IP fija: `192.168.0.1X`.
> - Envía cada mensaje con `POST` a: `http://192.168.0.10:8000/api/v1/ingest/eX`
> - Encabezado: `Content-Type: application/json`
> - Formato: el contrato v2 de `docs/formato_datos/EX.json`.
> - Respuestas: `201` es aceptado; `422` es un mensaje con formato incorrecto (el texto de la respuesta dice qué campo falla); un error de conexión significa que no llegó.
> - Si no llega o no hay respuesta en 5 s, guarda el mensaje y reintenta cada 2 s, hasta 5 veces.

### 4.5 Prueba de cada estación

Desde el equipo de la estación, o desde un notebook en la red, con el repo descargado:

**Linux, Mac o Pi:**
```bash
curl -X POST http://192.168.0.10:8000/api/v1/ingest/e6 \
     -H "Content-Type: application/json" \
     --data-binary @docs/formato_datos/E6.json
```

**Windows PowerShell:**
```powershell
curl.exe -X POST http://192.168.0.10:8000/api/v1/ingest/e6 -H "Content-Type: application/json" --data-binary "@docs/formato_datos/E6.json"
```

- Se sugiere empezar por **E6**, porque su mensaje es el más simple.
- Con la API actual (v1) la respuesta será 422 hasta que estén los schemas v2. Mientras tanto, la prueba confirma la conexión. Cuando los schemas v2 estén en `main`, hay que actualizar la Pi (`git pull` y reconstruir, ver 2.10), y la respuesta debe ser `201`.
- En la Pi, `docker compose logs -f` muestra cada mensaje que llega.

### ✅ Listo cuando

- [ ] La tabla 4.1 está completa.
- [ ] Cada estación hace `ping` a la Pi desde su equipo real.
- [ ] Cada estación envía al menos un mensaje que la API responde (`201` cuando existan los schemas v2).

---

## 7. Fase 5 — Llega el switch: todo por cable · Responsables: todos

Un switch común (no administrable) **no se configura**: se enchufa y funciona.

1. Conecta la fuente del switch y enciéndelo.
2. Conecta un cable desde **cualquier puerto LAN del router** (por ejemplo LAN 4) a **cualquier puerto del switch**. Nunca al puerto Internet/WAN del router.
3. Revisa que se encienda la luz de ese puerto en el router y en el switch.
4. Pasa al switch las estaciones que estaban por Wi-Fi y que tienen puerto de red. Las que ya estaban en el router pueden quedarse ahí.
5. **No hay que cambiar ninguna reserva de IP:** la reserva va con la MAC del equipo, no con el puerto.
6. Repite las pruebas 1 a 3 de la Fase 3 y la prueba 4.5 de cada estación.
7. Etiqueta cada cable **en ambos extremos** (`E1`, `E2`, …, `E5-Pi`, `Router-Switch`).

⚠️ No conectes un cable desde un puerto del switch a otro puerto del mismo switch: se forma un bucle y la red completa deja de funcionar.

### ✅ Listo cuando

- [ ] Todas las estaciones con puerto de red envían por cable.
- [ ] El Wi-Fi solo queda para notebooks y equipos sin puerto (ESP32).

---

## 8. Fase 6 — Canalización con tubos PVC · Responsables: todos

Recorrido por detrás de la línea, como en la maqueta [`conexion-estaciones.html`](conexion-estaciones.html).

1. **Medir:** la distancia de cada estación al router o switch, siguiendo el recorrido real por detrás (no en línea recta). Anótala en la tabla 4.1.
2. **Revisar si el material alcanza:** ya hay tubos, abrazaderas y tees. Compara lo disponible con lo necesario: largo total de los tramos más un 10 %, una tee por estación, abrazaderas cada 50 cm aprox., y codos y uniones según el recorrido (estos aún no se han confirmado).
3. **Probar los cables antes de pasarlos:** con cada cable, conecta una estación y haz `ping 192.168.0.10`.
4. **Pasar los cables por el tubo antes de cerrar las uniones.** No dobles el cable en ángulo cerrado ni lo tires con fuerza.
5. **Probar de nuevo** cada estación con el cable ya dentro del tubo.
6. **Fijar** los tubos con abrazaderas.
7. Deja el **router y el switch accesibles**, fuera del tubo, para poder revisar luces y cables.

### ✅ Listo cuando

- [ ] Ningún cable queda a la vista entre estaciones.
- [ ] Todas las estaciones responden al `ping` y a la prueba 4.5 después de cerrar los tubos.

---

## 9. Fase 7 — Ensayo general · Responsables: todos

### 9.1 Orden de encendido

1. Router (esperar 2 minutos).
2. Switch.
3. Raspberry Pi (esperar 2 minutos; la API arranca sola).
4. Monitor de E5.
5. Equipos de las estaciones.

### 9.2 Abrir el dashboard en el monitor

Mientras la API no sirva la página del dashboard, se abre el archivo directamente en el navegador de la Pi, en pantalla completa:

```bash
chromium-browser --kiosk "file:///home/packia/estacion5-backend/frontend/prototipo3-simple/index.html?sim=1"
```

- En versiones nuevas de Raspberry Pi OS el comando puede llamarse `chromium` en vez de `chromium-browser`.
- Cambia la ruta por la versión del dashboard que se use (por ejemplo, las de `frontend/vertical/` si el monitor queda vertical).
- Para salir del modo kiosko: `Alt+F4`.
- Cuando el dashboard lea datos reales, la dirección pasará a ser `http://localhost:8000/`.

### 9.3 Corrida completa

- [ ] Enviar datos con las estaciones reales, o con el simulador para las que falten.
- [ ] Desconectar el cable de una estación y confirmar que E5 la marca como "sin señal" (cuando exista `/api/v1/estaciones/estado`).
- [ ] Revisar la temperatura de la Pi después de 30 minutos (`vcgencmd measure_temp`; sobre 80 °C es demasiado).
- [ ] Anotar los tiempos y problemas en `docs/avance/`.

### 9.4 Orden de apagado

1. Equipos de las estaciones.
2. Pi: `sudo shutdown -h now` por SSH, o desde su menú. Esperar a que se apague la luz verde.
3. Monitor, switch y router.

### ✅ Listo cuando

- [ ] El ensayo completo, desde el encendido hasta el apagado, funciona **dos veces seguidas** sin intervención.

---

## 10. Orden y dependencias

```
Fase 1 router ──► Fase 2 Pi + API ──► Fase 3 simulador ──► Fase 4 estaciones reales ──► Fase 7 ensayo
                                                              ▲
                                     Fase 5 switch ───────────┤  (cuando llegue)
                                     Fase 6 tubos PVC ────────┘  (cuando haya material)
```

No hace falta esperar al switch: las fases 1 a 4 se pueden hacer solo con el router.

---

## 11. Problemas comunes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `tplinkwifi.net` no abre | El notebook no está conectado al router, o usa datos móviles | Conectarse a `PackIA-Linea` o por cable, desactivar la VPN y probar `http://192.168.0.1` |
| Nadie recuerda la clave de administrador | — | Reset de fábrica (1.9) y restaurar el respaldo (1.8) |
| La Pi no aparece en **Clients** | Cable mal conectado, o la Pi aún arrancando | Revisar las luces del puerto, esperar 3 min, probar otro cable |
| `ssh` dice *Connection refused* | SSH no se activó en el Imager | Conectar monitor y teclado a la Pi y ejecutar `sudo raspi-config` → Interface Options → SSH → Enable |
| `ssh` dice *Connection timed out* | IP equivocada | Revisar la IP en **Clients** o con `hostname -I` en la Pi |
| `ssh` avisa *REMOTE HOST IDENTIFICATION HAS CHANGED* | Se reinstaló la Pi con la misma IP | En el notebook: `ssh-keygen -R 192.168.0.10` y volver a entrar |
| `apt update` o `get.docker.com` fallan | El router no tiene internet | Revisar el cable WAN o usar el plan B de la sección 12 |
| `docker: permission denied` | Falta aplicar el permiso de Docker | Salir con `exit` y volver a entrar por SSH |
| `/docs` abre en la Pi pero no desde el notebook | El notebook está en otra red | Confirmar que el notebook esté en `PackIA-Linea` y no en la red del colegio |
| La API responde **422** | El mensaje no cumple el contrato (o la API sigue en v1) | Leer el detalle de la respuesta: dice qué campo falla. Ver la nota de la Fase 3 |
| Un ESP32 no encuentra la red | Está buscando 5 GHz o la red usa solo WPA3 | Conectarlo a `PackIA-Linea` (2,4 GHz) con WPA2 |
| Cortes intermitentes por Wi-Fi | Interferencia de otras redes | Pasar ese equipo a cable o fijar un canal en 1.5 (en 2,4 GHz: 1, 6 u 11) |
| Toda la red se cae al conectar el switch | Bucle de cable en el switch | Revisar que ningún cable vaya de un puerto del switch a otro del mismo switch |
| La Pi se reinicia o se pone lenta | Fuente débil o temperatura alta | Usar la fuente oficial de 27 W y revisar `vcgencmd measure_temp` |

---

## 12. Riesgos

| Riesgo | Qué hacer |
|---|---|
| El switch no llega a tiempo | Seguir con 3 estaciones por cable y el resto por Wi-Fi. Priorizar el cable para E2 y E3. |
| La red del colegio no permite conectar el router al WAN | Plan B: compartir internet desde un celular por cable USB o Wi-Fi a la Pi solo durante la instalación (Fase 2.6). Después la línea funciona sin internet. |
| Una estación no tiene puerto de red (por ejemplo un Arduino Uno) | Ethernet Shield, equipo intermedio por USB o ESP32 por Wi-Fi (ver `conexion-estaciones.md`). |
| La IP de la Pi cambia | Reservarla en el router (2.5) y no depender de la IP automática. |
| Alguien cambia la configuración del router | La clave de administrador la conoce solo el equipo, y hay respaldo (1.8). |
| La microSD se daña | Apagar siempre con `sudo shutdown -h now`. Tener una microSD de respaldo con la instalación hecha. |

---

## 13. Registro de configuración

Completar al terminar cada fase. **Sin contraseñas.**

| Dato | Valor |
|---|---|
| Red del router (IP / máscara) | |
| Rango DHCP automático | |
| Nombre Wi-Fi 2,4 GHz / 5 GHz | `PackIA-Linea` / `PackIA-Linea-5G` |
| Dónde están guardadas las contraseñas | |
| Dónde está el respaldo del router (fecha) | |
| Versión del firmware del router | |
| MAC de la Pi | |
| IP de la Pi | |
| Usuario de la Pi | `packia` |
| MAC e IP de cada estación | Ver tabla 4.1 |

---

## 14. Decisiones pendientes

| Decisión | Quién |
|---|---|
| Qué equipo usa cada estación y si tiene puerto de red | Todos, con cada estación |
| Qué estaciones ocupan los 3 puertos LAN libres mientras no hay switch | Todos, después de completar la tabla 4.1 |
| Si el router se conecta a internet durante la demo | Todos |
| Dónde se guardan las contraseñas y el respaldo del router | Todos |
| Si se usa la clave `X-API-Key` en la primera demo | Todos |
