#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONT_DIR="$ROOT_DIR/Logistics Route Optimization Platform"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi
BACK_HOST="127.0.0.1"
BACK_PORT="8000"
FRONT_HOST="127.0.0.1"
FRONT_PORT="5173"
EDA_PATH="$ROOT_DIR/EDA/df_despacho.csv"
RUN_UPLOAD_SMOKE="${RUN_UPLOAD_SMOKE:-0}"

BACK_PID=""
FRONT_PID=""
CSV_BACKUP=""

free_port_if_needed() {
  local port="$1"
  local name="$2"
  local pids
  pids="$(lsof -ti tcp:"$port" 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    echo "[dev-verify] Puerto $port ocupado ($name). Cerrando proceso(s): $pids"
    kill $pids 2>/dev/null || true
    sleep 0.4
  fi
}

wait_http_ok() {
  local url="$1"
  local label="$2"
  local attempts="${3:-60}"
  local sleep_s="${4:-0.25}"
  for _ in $(seq 1 "$attempts"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "[OK] $label"
      return 0
    fi
    sleep "$sleep_s"
  done
  echo "[ERROR] Timeout esperando $label ($url)"
  return 1
}

restore_csv_if_needed() {
  if [[ -n "$CSV_BACKUP" && -f "$CSV_BACKUP" ]]; then
    cp "$CSV_BACKUP" "$EDA_PATH"
    rm -f "$CSV_BACKUP"
    CSV_BACKUP=""
  fi
}

cleanup() {
  restore_csv_if_needed
  if [[ -n "$FRONT_PID" ]] && kill -0 "$FRONT_PID" 2>/dev/null; then
    kill "$FRONT_PID" 2>/dev/null || true
  fi
  if [[ -n "$BACK_PID" ]] && kill -0 "$BACK_PID" 2>/dev/null; then
    kill "$BACK_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

free_port_if_needed "$BACK_PORT" "backend"
free_port_if_needed "$FRONT_PORT" "frontend"

echo "[1/7] Levantando backend..."
"$PYTHON_BIN" "$ROOT_DIR/backend/api_server.py" >/tmp/capstone_backend.log 2>&1 &
BACK_PID=$!
wait_http_ok "http://${BACK_HOST}:${BACK_PORT}/api/v1/health" "Backend health"

echo "[2/7] Levantando frontend..."
cd "$FRONT_DIR"
if [[ ! -d node_modules ]]; then
  npm i
fi
npm run dev -- --host "$FRONT_HOST" --port "$FRONT_PORT" --strictPort >/tmp/capstone_frontend.log 2>&1 &
FRONT_PID=$!
wait_http_ok "http://${FRONT_HOST}:${FRONT_PORT}" "Frontend up" 120 0.25

echo "[3/7] Verificando endpoints backend directos..."
wait_http_ok "http://${BACK_HOST}:${BACK_PORT}/api/v1/data" "Backend data"
wait_http_ok "http://${BACK_HOST}:${BACK_PORT}/api/v1/map" "Backend map"

echo "[4/7] Verificando proxy del frontend..."
wait_http_ok "http://${FRONT_HOST}:${FRONT_PORT}/api/v1/health" "Proxy health"
wait_http_ok "http://${FRONT_HOST}:${FRONT_PORT}/api/v1/data" "Proxy data"
wait_http_ok "http://${FRONT_HOST}:${FRONT_PORT}/api/v1/map" "Proxy map"

echo "[5/7] Carga CSV automática: desactivada (modo manual)."
if [[ "$RUN_UPLOAD_SMOKE" == "1" ]]; then
  echo "[dev-verify] Ejecutando smoke upload por RUN_UPLOAD_SMOKE=1..."
  if [[ -f "$EDA_PATH" ]]; then
    CSV_BACKUP="$(mktemp)"
    cp "$EDA_PATH" "$CSV_BACKUP"
  fi

  cat > /tmp/capstone_smoke_orders.csv <<'CSV'
order_id,customer,address,comuna,volume_m3,weight_kg,time_window_start,time_window_end,delivery_date
ORD-SMOKE-0001,12.345.678-9,Av Siempre Viva 123,Santiago,1.25,210,09:30,12:30,2026-12-05
CSV

  CSV_JSON_PAYLOAD="$(python - <<'PY'
import json, pathlib
csv_txt = pathlib.Path("/tmp/capstone_smoke_orders.csv").read_text(encoding="utf-8")
print(json.dumps({"filename": "capstone_smoke_orders.csv", "csv": csv_txt}, ensure_ascii=False))
PY
)"

  UPLOAD_RESPONSE="$(curl -fsS -X POST "http://${FRONT_HOST}:${FRONT_PORT}/api/v1/upload-orders" \
    -H "Content-Type: application/json" \
    -d "$CSV_JSON_PAYLOAD")"
  echo "[OK] Upload response: $UPLOAD_RESPONSE"
  wait_http_ok "http://${FRONT_HOST}:${FRONT_PORT}/api/v1/data" "Data tras upload"
  restore_csv_if_needed
  wait_http_ok "http://${FRONT_HOST}:${FRONT_PORT}/api/v1/data" "Data tras restore"
fi

echo "[6/7] Resumen rápido de datos..."
python - <<PY
import json, urllib.request
with urllib.request.urlopen("http://${FRONT_HOST}:${FRONT_PORT}/api/v1/data") as r:
    data = json.loads(r.read().decode("utf-8"))
print(f"run_id={data['optimizationRun']['id']}")
print(f"orders={len(data['orders'])}")
print(f"routes={len(data['optimizationRun']['routes'])}")
PY

echo "[7/7] Estado final"
echo "Frontend: http://${FRONT_HOST}:${FRONT_PORT}"
echo "Backend:  http://${BACK_HOST}:${BACK_PORT}/api/v1/health"
echo "Carga manual de CSV: UI -> Planning -> Archivo de Pedidos (CSV) -> Cargar"
echo "Logs:"
echo "  /tmp/capstone_backend.log"
echo "  /tmp/capstone_frontend.log"

if ls "$ROOT_DIR"/resultados/mapa_rutas/mapa_flotaglobal_*.html >/dev/null 2>&1; then
  echo "[OK] Hay mapas de calles reales en resultados/mapa_rutas."
else
  echo "[AVISO] No hay mapa_flotaglobal_*.html aún. El Mapa Backend mostrará aviso hasta generar una corrida real."
fi

echo
echo "Servicios activos. Presiona Ctrl+C para detener."
wait
