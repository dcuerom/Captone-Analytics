"""
Local preflight para el runtime SaaS.

Uso:
  python scripts/preflight_check.py
  python scripts/preflight_check.py --json
  python scripts/preflight_check.py --strict-env
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT_DIR = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT_DIR / "backend" / "api_server.py",
    ROOT_DIR / "algoritmo" / "config.py",
    ROOT_DIR / "algoritmo" / "savings.py",
    ROOT_DIR / "algoritmo" / "genetic_algorithm.py",
    ROOT_DIR / "grafo" / "main.py",
    ROOT_DIR / "grafo" / "network_builder.py",
    ROOT_DIR / "gestion_flota" / "gestor.py",
]

REQUIRED_IMPORTS = [
    "backend.api_server",
    "algoritmo.config",
    "algoritmo.savings",
    "algoritmo.genetic_algorithm",
    "grafo.main",
    "grafo.network_builder",
]

REQUIRED_PACKAGES = [
    "pandas",
    "numpy",
    "networkx",
    "osmnx",
    "pymoo",
]

OPTIONAL_ENV = [
    "SUPABASE_URL",
    "SUPABASE_KEY",
]


def _check_file(path: Path) -> Dict[str, Any]:
    exists = path.exists()
    return {
        "name": f"file:{path.relative_to(ROOT_DIR)}",
        "ok": exists,
        "detail": "ok" if exists else "missing",
    }


def _check_import(module_name: str) -> Dict[str, Any]:
    try:
        importlib.import_module(module_name)
        return {"name": f"import:{module_name}", "ok": True, "detail": "ok"}
    except Exception as exc:
        return {"name": f"import:{module_name}", "ok": False, "detail": str(exc)}


def _check_package(package_name: str) -> Dict[str, Any]:
    try:
        importlib.import_module(package_name)
        return {"name": f"package:{package_name}", "ok": True, "detail": "ok"}
    except Exception as exc:
        return {"name": f"package:{package_name}", "ok": False, "detail": str(exc)}


def _check_env(var_name: str, strict: bool) -> Dict[str, Any]:
    present = bool(os.getenv(var_name))
    return {
        "name": f"env:{var_name}",
        "ok": present or (not strict),
        "detail": "set" if present else ("missing (warning)" if not strict else "missing"),
    }


def run_preflight(strict_env: bool = False) -> Dict[str, Any]:
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))

    checks: List[Dict[str, Any]] = []
    checks.extend(_check_file(path) for path in REQUIRED_FILES)
    checks.extend(_check_package(name) for name in REQUIRED_PACKAGES)
    checks.extend(_check_import(name) for name in REQUIRED_IMPORTS)
    checks.extend(_check_env(name, strict=strict_env) for name in OPTIONAL_ENV)

    failed = [c for c in checks if not c["ok"]]
    return {
        "status": "ok" if not failed else "failed",
        "failedCount": len(failed),
        "checks": checks,
    }


def _print_human(report: Dict[str, Any]) -> None:
    print(f"Preflight status: {report['status']} (failed={report['failedCount']})")
    for check in report["checks"]:
        state = "OK " if check["ok"] else "ERR"
        print(f" - [{state}] {check['name']}: {check['detail']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight local del runtime SaaS")
    parser.add_argument("--json", action="store_true", help="Salida en JSON")
    parser.add_argument(
        "--strict-env",
        action="store_true",
        help="Tratar variables de entorno opcionales como requeridas",
    )
    args = parser.parse_args()

    report = run_preflight(strict_env=bool(args.strict_env))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_human(report)
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())

