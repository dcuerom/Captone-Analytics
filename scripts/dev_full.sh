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

cleanup() {
  if [[ -n "${BACK_PID:-}" ]] && kill -0 "$BACK_PID" 2>/dev/null; then
    kill "$BACK_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

free_port_if_needed "$BACK_PORT" "backend"
free_port_if_needed "$FRONT_PORT" "frontend"

echo "[dev] Levantando backend en http://${BACK_HOST}:${BACK_PORT} ..."
"$PYTHON_BIN" "$ROOT_DIR/backend/api_server.py" &
BACK_PID=$!

# Esperar health del backend para evitar fallback mock por carrera de arranque
for _ in {1..40}; do
  if curl -fsS "http://${BACK_HOST}:${BACK_PORT}/api/v1/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done

if ! curl -fsS "http://${BACK_HOST}:${BACK_PORT}/api/v1/health" >/dev/null 2>&1; then
  echo "[ERROR] Backend no respondió en /api/v1/health"
  exit 1
fi

echo "[dev] Backend OK. Levantando frontend en http://${FRONT_HOST}:${FRONT_PORT} ..."
cd "$FRONT_DIR"
if [[ ! -d node_modules ]]; then
  npm i
fi
npm run dev -- --host "$FRONT_HOST" --port "$FRONT_PORT" --strictPort
