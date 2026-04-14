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
BACK_LOG="/tmp/capstone_backend_dev.log"
FRONT_LOG="/tmp/capstone_frontend_dev.log"

free_port_if_needed() {
  local port="$1"
  local name="$2"
  local pids
  pids="$(lsof -ti tcp:"$port" 2>/dev/null || true)"
  if [[ -n "$pids" ]]; then
    echo "[dev] Puerto $port ocupado ($name). Cerrando proceso(s): $pids"
    kill $pids 2>/dev/null || true
    sleep 0.4
  fi
}

wait_http_ok() {
  local url="$1"
  local label="$2"
  local attempts="${3:-80}"
  local sleep_s="${4:-0.25}"
  for _ in $(seq 1 "$attempts"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "[dev] OK: $label"
      return 0
    fi
    sleep "$sleep_s"
  done
  echo "[dev] ERROR: timeout esperando $label ($url)"
  return 1
}

cleanup() {
  if [[ -n "${FRONT_PID:-}" ]] && kill -0 "$FRONT_PID" 2>/dev/null; then
    kill "$FRONT_PID" 2>/dev/null || true
  fi
  if [[ -n "${BACK_PID:-}" ]] && kill -0 "$BACK_PID" 2>/dev/null; then
    kill "$BACK_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

free_port_if_needed "$BACK_PORT" "backend"
free_port_if_needed "$FRONT_PORT" "frontend"

echo "[dev] Levantando backend en http://${BACK_HOST}:${BACK_PORT} ..."
"$PYTHON_BIN" "$ROOT_DIR/backend/api_server.py" >"$BACK_LOG" 2>&1 &
BACK_PID=$!

if ! wait_http_ok "http://${BACK_HOST}:${BACK_PORT}/api/v1/health" "backend health"; then
  echo "[dev] Backend no respondió. Revisa $BACK_LOG"
  exit 1
fi

echo "[dev] Backend OK. Levantando frontend en http://${FRONT_HOST}:${FRONT_PORT} ..."
cd "$FRONT_DIR"
if [[ ! -d node_modules ]]; then
  npm i
fi
npm run dev -- --host "$FRONT_HOST" --port "$FRONT_PORT" --strictPort >"$FRONT_LOG" 2>&1 &
FRONT_PID=$!

if ! wait_http_ok "http://${FRONT_HOST}:${FRONT_PORT}" "frontend"; then
  echo "[dev] Frontend no respondió. Revisa $FRONT_LOG"
  exit 1
fi

if ! wait_http_ok "http://${FRONT_HOST}:${FRONT_PORT}/api/v1/data" "proxy frontend -> backend"; then
  echo "[dev] El proxy del frontend no pudo cargar /api/v1/data. Revisa $FRONT_LOG y $BACK_LOG"
  exit 1
fi

echo "[dev] Servicios listos:"
echo "[dev] Frontend: http://${FRONT_HOST}:${FRONT_PORT}"
echo "[dev] Backend:  http://${BACK_HOST}:${BACK_PORT}/api/v1/health"
echo "[dev] Logs:"
echo "[dev]   $BACK_LOG"
echo "[dev]   $FRONT_LOG"
echo "[dev] Presiona Ctrl+C para detener ambos servicios."

wait "$FRONT_PID"
