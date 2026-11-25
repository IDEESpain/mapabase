#!/usr/bin/env bash
# =============================================================================
# Arranque / parada / estado del servicio Tilekiln (Mapa Ciudadano)
#
#   tools/tilekiln_servicio.sh start  [dev|live]   # por defecto dev
#   tools/tilekiln_servicio.sh stop
#   tools/tilekiln_servicio.sh restart [dev|live]
#   tools/tilekiln_servicio.sh status               # proceso, puerto, TileJSON, tesela, BD
#   tools/tilekiln_servicio.sh logs                 # tail -f del log
#   tools/tilekiln_servicio.sh cache-clear          # vacía la caché de live (tras recargar capas)
#   tools/tilekiln_servicio.sh cache-reset          # recrea la caché (tras regenerar config_rapido.yaml)
#
# Modos:
#   dev   genera cada tesela al vuelo (sin caché). Lo que se usaba hasta ahora.
#   live  genera al vuelo y GUARDA la tesela en la BD (esquema tilekiln): la segunda
#         petición de la misma tesela no consulta las capas. Requiere una vez:
#         tools/tilekiln_servicio.sh cache-init
#         y cache-clear después de recargar capas (si no, sirve teselas viejas).
#
# Formatos: cada tesela se sirve como .mvt y como .pbf (mismo contenido; ver tilekiln_pbf.py)
#   /tilejson.json      → teselas .mvt      /tilejson-pbf.json → teselas .pbf
#
# Variables (o en .env): TK_CONFIG (config_rapido.yaml si existe, si no config.yaml),
#   TK_PORT (8099), TK_HOST (0.0.0.0), TK_WORKERS (4), TK_LOG (/tmp/tilekiln_serve.log),
#   TK_PUBLIC_URL: base que aparece en el TileJSON (por defecto http://<IP de la máquina>:<puerto>;
#   por túnel desde el PC: TK_PUBLIC_URL=http://127.0.0.1:9000)
# =============================================================================
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"
if [[ -f .env ]]; then set -a; source .env; set +a; fi
# PostGIS en public o en public_modelo_2025; jit=off: las consultas de tesela son cortas
export PGOPTIONS="${PGOPTIONS:--c search_path=public,public_modelo_2025 -c jit=off}"

if [[ -z "${TK_CONFIG:-}" ]]; then
	if [[ -f config_rapido.yaml ]]; then TK_CONFIG=config_rapido.yaml; else TK_CONFIG=config.yaml; fi
fi
TK_PORT="${TK_PORT:-8099}"
TK_HOST="${TK_HOST:-0.0.0.0}"
TK_WORKERS="${TK_WORKERS:-4}"
TK_LOG="${TK_LOG:-/tmp/tilekiln_serve.log}"
TK_BIN="${TK_BIN:-$DIR/.venv/bin/tilekiln}"
TK_PY="$(dirname "$TK_BIN")/python"
if [[ -z "${TK_PUBLIC_URL:-}" ]]; then
	if [[ "$TK_HOST" == "0.0.0.0" ]]; then
		TK_PUBLIC_URL="http://$(hostname -I 2>/dev/null | awk '{print $1}'):${TK_PORT}"
	else
		TK_PUBLIC_URL="http://${TK_HOST}:${TK_PORT}"
	fi
fi
URL="http://127.0.0.1:${TK_PORT}"
CURL=(curl -s --noproxy '*' --max-time 120)   # sin --noproxy el proxy del entorno da 403

pids() { pgrep -f "(tilekiln (dev|live|serve) .*--bind-port|uvicorn tilekiln_pbf:(dev|live) .*--port) ${TK_PORT}" || true; }

start() {
	local modo="${1:-dev}"
	if [[ -n "$(pids)" ]]; then echo "Ya está arrancado (PID $(pids | tr '\n' ' '))"; return 0; fi
	[[ -x "$TK_BIN" ]] || { echo "No existe $TK_BIN (crear el venv: ver COMANDOS_PG18.txt)"; exit 1; }
	"$TK_BIN" config test "$TK_CONFIG" >/dev/null
	[[ "$modo" == dev || "$modo" == live ]] || { echo "modo desconocido: $modo (dev|live)"; exit 1; }
	echo "Arrancando tilekiln $modo · config=$TK_CONFIG · ${TK_HOST}:${TK_PORT} · workers=$TK_WORKERS · BD=${PGDATABASE:-?}@${PGHOST:-?}"
	echo "URL pública en TileJSON: $TK_PUBLIC_URL"
	# Mismas apps que «tilekiln dev/live» + rutas .pbf. La BD sale de PG* (.env).
	TILEKILN_CONFIG="$TK_CONFIG" TILEKILN_URL="${TK_PUBLIC_URL}/tiles" TILEKILN_THREADS="$TK_WORKERS" \
	PYTHONPATH="$DIR/tools${PYTHONPATH:+:$PYTHONPATH}" \
		nohup "$TK_PY" -m uvicorn "tilekiln_pbf:$modo" --host "$TK_HOST" --port "$TK_PORT" \
		--workers "$TK_WORKERS" >"$TK_LOG" 2>&1 &
	for _ in $(seq 1 20); do
		sleep 1
		if "${CURL[@]}" -o /dev/null "$URL/tilejson.json"; then echo "OK: $URL/tilejson.json"; return 0; fi
	done
	echo "No responde tras 20 s. Log:"; tail -30 "$TK_LOG"; exit 1
}

stop() {
	local p; p="$(pids)"
	if [[ -z "$p" ]]; then echo "No estaba arrancado"; return 0; fi
	kill $p; sleep 2
	p="$(pids)"; [[ -n "$p" ]] && kill -9 $p || true
	echo "Parado"
}

status() {
	echo "== Proceso (puerto $TK_PORT)"
	local p; p="$(pids)"
	if [[ -n "$p" ]]; then ps -o pid,etime,rss,args -p "$(echo $p | tr ' ' ',')" | cut -c1-160; else echo "   NO ARRANCADO"; fi
	echo "== Puerto"
	(ss -ltnp 2>/dev/null || netstat -ltnp 2>/dev/null) | grep -E ":${TK_PORT}\b" || echo "   nadie escucha en :$TK_PORT"
	echo "== TileJSON"
	if "${CURL[@]}" -o /tmp/_tk_tilejson.json -w "   HTTP %{http_code} en %{time_total}s\n" "$URL/tilejson.json"; then
		python3 - <<-'EOF' 2>/dev/null || true
			import json; d = json.load(open("/tmp/_tk_tilejson.json"))
			print(f"   {d.get('name')} · z{d.get('minzoom')}-{d.get('maxzoom')} · {len(d.get('vector_layers', []))} capas")
		EOF
	fi
	"${CURL[@]}" -o /dev/null -w "   tilejson-pbf HTTP %{http_code}\n" "$URL/tilejson-pbf.json" || true
	echo "   URL en TileJSON: $("${CURL[@]}" "$URL/tilejson.json" | grep -o '"http[^"]*{z}[^"]*"' | head -1)"
	echo "== Teselas de prueba (Madrid)"
	for t in 6/31/24 10/501/386 14/8023/6177 17/64187/49422; do
		"${CURL[@]}" -o /dev/null -w "   $t.mvt  HTTP %{http_code}  %{size_download} B  %{time_total}s\n" "$URL/tiles/$t.mvt" || echo "   $t  sin respuesta"
	done
	"${CURL[@]}" -o /dev/null -w "   10/501/386.pbf  HTTP %{http_code}  %{size_download} B  %{content_type}\n" "$URL/tiles/10/501/386.pbf" || true
	echo "== BD"
	psql -X -qAt -c "SELECT 'PostgreSQL ' || current_setting('server_version') || ' · PostGIS ' || postgis_lib_version()" 2>&1 | sed 's/^/   /'
	psql -X -qAt -c "SELECT '   conexiones tilekiln activas: ' || count(*) FROM pg_stat_activity WHERE datname = current_database() AND application_name NOT IN ('psql', 'mc_pipeline') AND state = 'active'" 2>/dev/null || true
	psql -X -qAt -c "SELECT '   caché live: ' || count(*) || ' teselas, ' || pg_size_pretty(sum(length(tile))) FROM tilekiln.\"$(config_id)\"" 2>/dev/null || echo "   caché live: no inicializada"
	echo "== Últimas líneas del log ($TK_LOG)"
	tail -5 "$TK_LOG" 2>/dev/null | sed 's/^/   /' || true
}

config_id() { python3 -c "import yaml,sys; print(yaml.safe_load(open('$TK_CONFIG'))['metadata']['id'])" 2>/dev/null \
	|| "$DIR/.venv/bin/python" -c "import yaml; print(yaml.safe_load(open('$TK_CONFIG'))['metadata']['id'])"; }

case "${1:-status}" in
	start) start "${2:-dev}" ;;
	stop) stop ;;
	restart) stop; start "${2:-dev}" ;;
	status) status ;;
	logs) tail -f "$TK_LOG" ;;
	cache-init) "$TK_BIN" storage init "$TK_CONFIG" && echo "Caché creada (esquema tilekiln)" ;;
	cache-clear) "$TK_BIN" storage delete "$TK_CONFIG" && echo "Caché vaciada" ;;
	cache-destroy) "$TK_BIN" storage destroy "$TK_CONFIG" && echo "Caché eliminada" ;;
	# Tras regenerar config_rapido.yaml: la caché tiene una partición por zoom del rango
	# con que se creó; si el rango cambia, live da 500 en los zooms nuevos.
	cache-reset) "$TK_BIN" storage destroy "$TK_CONFIG" 2>/dev/null || true
		"$TK_BIN" storage init "$TK_CONFIG" && echo "Caché recreada para $TK_CONFIG" ;;
	*) sed -n '2,29p' "$0"; exit 1 ;;
esac
