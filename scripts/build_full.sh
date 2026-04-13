#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONT_DIR="$ROOT_DIR/Logistics Route Optimization Platform"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

echo "[1/3] Compilando backend (Python)..."
"$PYTHON_BIN" -m compileall -q "$ROOT_DIR/backend"
echo "[OK] Backend compilado."

echo "[2/3] Instalando dependencias frontend..."
cd "$FRONT_DIR"
npm i

echo "[3/3] Build frontend..."
npm run build

echo "[OK] Build completo (backend + frontend)."
