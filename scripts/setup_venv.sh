#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY_BIN="${PY_BIN:-python3}"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"

echo "[setup-venv] Creando entorno virtual en: $VENV_DIR"
"$PY_BIN" -m venv "$VENV_DIR"

echo "[setup-venv] Actualizando pip/setuptools/wheel..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel

echo "[setup-venv] Instalando dependencias Python del proyecto..."
"$VENV_DIR/bin/pip" install -r "$ROOT_DIR/requirements.txt"

echo "[setup-venv] Validando imports críticos del pipeline..."
"$VENV_DIR/bin/python" - <<'PY'
mods = [
    "pandas",
    "numpy",
    "networkx",
    "osmnx",
    "geopy",
    "folium",
    "sklearn",
    "pymoo",
]
for m in mods:
    __import__(m)
print("imports-ok")
PY

echo
echo "[setup-venv] OK"
echo "Para activar:"
echo "  source .venv/bin/activate"

