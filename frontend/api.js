/* Capa de datos del dashboard de la Estación 5.
 *
 * Todo acceso a datos pasa por aquí: si cambia un campo o una ruta, se corrige en este archivo.
 * El dashboard usa window.E5Api; no llama a fetch directamente.
 *
 * Modos (se elige con la URL):
 *   (sin parámetros)  API real. Si la página la sirve la propia API usa su dirección;
 *                     si se abre como archivo usa http://localhost:8000.
 *   ?api=http://IP:8000  API real en otra dirección (por ejemplo la Raspberry Pi).
 *   ?mock=1           Lee los ejemplos de frontend/mock/*.json (sirve para desarrollar sin backend).
 *                     Hay que abrir la página desde un servidor, no con doble clic.
 *   ?sim=1            El dashboard usa sus datos simulados internos y no llama a la API (plan B de la demo).
 *
 * Forma de las respuestas (propuesta para el backend; los ejemplos están en frontend/mock/):
 *   getGrupos     -> { id_lote, total_grupos, total_frutas, grupos:[{ id_grupo, estado, frutas_detectadas, ingreso, salida,
 *                      diametro_medio_mm, uniformidad, frutas:[{ id_fruta, categoria_final, tamano, diametro_mm, alertas }] }] }
 *   getMetricas   -> { id_lote, desde, hasta, grupos_turno, frutas_turno, frutas_ultima_hora, grupos_ultima_hora,
 *                      rechazadas, porcentaje_rechazo, alertas_ultima_hora, por_categoria:{ <categoria>: n } }
 *   getAlertas    -> { alertas:[{ id, severidad, estacion, mensaje, id_grupo, id_fruta, creada_en, resuelta }] }
 *   getEstaciones -> { id_lote, ahora, estaciones:[{ estacion, estado, ultima_lectura, id_grupo, severidad_ultima,
 *                      (solo E6) estado_cinta, falla_mecanica_detectada }] }
 *   getGrupo      -> { id_lote, id_grupo, estado, ingreso, salida, e1:{...}, frutas:[{ id_fruta, e2:{...}, e3:{...}, e4:{...}, alertas }], alertas }
 *
 * Valores cerrados: estado de grupo = ok | anomalia | rechazo | proceso; severidad = info | alerta | falla;
 * estado de estación = ok | sin_senal | falla; tamano = pequeno | mediano | grande.
 * Las fechas son ISO 8601 con zona (UTC), tal como las envían las estaciones.
 */
(function () {
  "use strict";

  var params = new URLSearchParams(location.search);
  var TIMEOUT_MS = 5000;

  var mode = params.get("sim") === "1" ? "sim" : params.get("mock") === "1" ? "mock" : "api";
  var base = (params.get("api") ||
    (location.protocol === "file:" ? "http://localhost:8000" : location.origin)).replace(/\/+$/, "");

  function getJSON(url) {
    var ctl = new AbortController();
    var timer = setTimeout(function () { ctl.abort(); }, TIMEOUT_MS);
    return fetch(url, { signal: ctl.signal, headers: { Accept: "application/json" } })
      .then(function (res) {
        if (!res.ok) throw new Error("La API respondió " + res.status + " en " + url);
        return res.json();
      })
      .catch(function (err) {
        if (err.name === "AbortError") throw new Error("La API no respondió en " + TIMEOUT_MS / 1000 + " s (" + url + ")");
        throw err;
      })
      .finally(function () { clearTimeout(timer); });
  }

  /* En modo mock se lee frontend/mock/<archivo>.json; en modo api, la ruta real. */
  function request(mockFile, path, query) {
    if (mode === "sim") return Promise.reject(new Error("Modo ?sim=1: el dashboard usa datos simulados"));
    if (mode === "mock") return getJSON("mock/" + mockFile + ".json");
    var qs = new URLSearchParams();
    Object.keys(query || {}).forEach(function (k) {
      if (query[k] !== undefined && query[k] !== null) qs.set(k, query[k]);
    });
    var s = qs.toString();
    return getJSON(base + path + (s ? "?" + s : ""));
  }

  var enc = encodeURIComponent;

  window.E5Api = {
    mode: mode,
    sim: mode === "sim",
    base: base,

    /* Últimos grupos de un lote, del más reciente al más antiguo. */
    getGrupos: function (opts) {
      opts = opts || {};
      return request("grupos", "/api/v1/lotes/" + enc(opts.lote || "") + "/grupos", { limit: opts.limit || 20 });
    },
    /* Indicadores del turno. */
    getMetricas: function (lote) {
      return request("metricas", "/api/v1/metricas", { lote: lote });
    },
    /* Alertas; por defecto solo las activas. */
    getAlertas: function (opts) {
      opts = opts || {};
      return request("alertas", "/api/v1/alertas", { activas: opts.activas === false ? "false" : "true" });
    },
    /* Última lectura y señal de cada estación. */
    getEstaciones: function () {
      return request("estaciones", "/api/v1/estaciones/estado");
    },
    /* Trazabilidad completa de un grupo. */
    getGrupo: function (idGrupo) {
      return request("grupo", "/api/v1/grupos/" + enc(idGrupo));
    }
  };
})();
