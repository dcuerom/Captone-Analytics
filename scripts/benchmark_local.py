"""
Benchmark local reproducible para comparar calidad de configuraciones del optimizador.

Uso ejemplo:
  python scripts/benchmark_local.py --dataset EDA/df_despacho.csv --date 2026-04-08 --profile all
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT_DIR / "resultados" / "rutas"


CONFIG_PROFILES: Dict[str, Dict[str, Any]] = {
    "baseline": {
        "ga_seed": 42,
        "ga_n_gen": 200,
        "ga_pop_size": 100,
        "clustering_eps": 0.30,
        "clustering_min_samples": 3,
    },
    "tuned_precision": {
        "ga_seed": 42,
        "ga_n_gen": 300,
        "ga_pop_size": 180,
        "clustering_eps": 0.24,
        "clustering_min_samples": 4,
        "alpha_espera": 70_000.0,
    },
}


def _load_kpis_csv(path: Path) -> Dict[str, float]:
    out: Dict[str, float] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kpi_name = str(row.get("KPI", "")).strip()
            if not kpi_name:
                continue
            try:
                out[kpi_name] = float(str(row.get("Valor", "")).replace(",", "."))
            except Exception:
                continue
    return out


def _pick_kpi(kpi_map: Dict[str, float], candidates: List[str], default: float = 0.0) -> float:
    for key in candidates:
        if key in kpi_map:
            return float(kpi_map[key])
    return default


def _extract_metrics(meta: Dict[str, Any]) -> Dict[str, float]:
    artifacts = meta.get("artifacts") or {}
    kpis_path = Path(str(artifacts.get("kpisCsv", "")))
    if not kpis_path.is_absolute():
        kpis_path = ROOT_DIR / kpis_path
    kpi_map = _load_kpis_csv(kpis_path)

    summary = meta.get("summary") or {}
    distance_km = _pick_kpi(kpi_map, ["Distancia Total Recorrida (km)"], float(summary.get("distanciaTotalKm", 0.0)))
    on_time_pct = _pick_kpi(kpi_map, ["% Entregas a Tiempo"], float(summary.get("onTimePct", 0.0)))
    backlog_pct = _pick_kpi(kpi_map, ["% Pedidos No Atendidos (Backlog)"], 0.0)
    backlog_qty = _pick_kpi(kpi_map, ["Pedidos No Atendidos (qty)"], float(summary.get("pedidosNoAtendidos", 0.0)))
    wait_min = _pick_kpi(kpi_map, ["Espera Total Acumulada (min)"], float(summary.get("esperaTotalMin", 0.0)))
    fo_total = _pick_kpi(
        kpi_map,
        [
            "Funcion Objetivo Total ($)",
            "Función Objetivo Total ($)",
            "FunciÃ³n Objetivo Total ($)",
        ],
        float(summary.get("objetivoTotal", 0.0)),
    )

    return {
        "distanceKm": float(distance_km),
        "onTimePct": float(on_time_pct),
        "backlogPct": float(backlog_pct),
        "backlogQty": float(backlog_qty),
        "waitMinutes": float(wait_min),
        "objectiveTotal": float(fo_total),
    }


def _run_once(
    profile_name: str,
    profile_cfg: Dict[str, Any],
    dataset_path: Path,
    target_date: str,
    run_idx: int,
) -> Dict[str, Any]:
    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))

    from algoritmo.genetic_algorithm import disparar_rutina_ga

    run_id = f"bench-{profile_name}-{target_date.replace('-', '')}-{run_idx:02d}-{int(time.time())}"
    t0 = time.time()

    result = disparar_rutina_ga(
        input_csv_path=str(dataset_path),
        fecha_target=target_date,
        config=profile_cfg,
        run_id=run_id,
    )

    elapsed_sec = time.time() - t0
    meta_path = RESULTS_DIR / f"run_{run_id}.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    metrics = _extract_metrics(meta) if meta else {}

    return {
        "profile": profile_name,
        "runId": run_id,
        "targetDate": target_date,
        "dataset": str(dataset_path),
        "configApplied": result.get("config_applied", profile_cfg),
        "elapsedSeconds": round(elapsed_sec, 3),
        "metrics": metrics,
        "metaPath": str(meta_path),
    }


def _aggregate(runs: List[Dict[str, Any]]) -> Dict[str, float]:
    if not runs:
        return {}
    keys = ["distanceKm", "onTimePct", "backlogPct", "backlogQty", "waitMinutes", "objectiveTotal"]
    acc: Dict[str, List[float]] = {k: [] for k in keys}
    for run in runs:
        metrics = run.get("metrics") or {}
        for key in keys:
            val = metrics.get(key)
            if isinstance(val, (int, float)):
                acc[key].append(float(val))
    return {f"{key}Avg": (sum(vals) / len(vals) if vals else 0.0) for key, vals in acc.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark local de calidad del optimizador")
    parser.add_argument("--dataset", required=True, help="CSV de pedidos")
    parser.add_argument("--date", required=True, help="Fecha objetivo YYYY-MM-DD")
    parser.add_argument(
        "--profile",
        default="all",
        choices=["all", "baseline", "tuned_precision"],
        help="Perfil de configuracion a ejecutar",
    )
    parser.add_argument("--repeat", type=int, default=1, help="Repeticiones por perfil")
    parser.add_argument(
        "--output",
        default=str(RESULTS_DIR / "benchmark_results.json"),
        help="Ruta JSON de salida",
    )
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.is_absolute():
        dataset_path = ROOT_DIR / dataset_path
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset no encontrado: {dataset_path}")

    selected = CONFIG_PROFILES
    if args.profile != "all":
        selected = {args.profile: CONFIG_PROFILES[args.profile]}

    all_runs: List[Dict[str, Any]] = []
    summary: Dict[str, Any] = {}

    for profile_name, profile_cfg in selected.items():
        profile_runs: List[Dict[str, Any]] = []
        for i in range(1, int(args.repeat) + 1):
            run_result = _run_once(profile_name, profile_cfg, dataset_path, args.date, i)
            profile_runs.append(run_result)
            all_runs.append(run_result)
            print(
                f"[benchmark] {profile_name} run={i} "
                f"on_time={run_result.get('metrics', {}).get('onTimePct', 0):.2f}% "
                f"distance={run_result.get('metrics', {}).get('distanceKm', 0):.2f}km"
            )
        summary[profile_name] = _aggregate(profile_runs)

    comparison: Dict[str, Any] = {}
    if "baseline" in summary and "tuned_precision" in summary:
        comparison = {
            "onTimePctDelta": summary["tuned_precision"]["onTimePctAvg"] - summary["baseline"]["onTimePctAvg"],
            "distanceKmDelta": summary["tuned_precision"]["distanceKmAvg"] - summary["baseline"]["distanceKmAvg"],
            "backlogPctDelta": summary["tuned_precision"]["backlogPctAvg"] - summary["baseline"]["backlogPctAvg"],
            "objectiveTotalDelta": summary["tuned_precision"]["objectiveTotalAvg"] - summary["baseline"]["objectiveTotalAvg"],
        }

    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "dataset": str(dataset_path),
        "targetDate": args.date,
        "repeat": int(args.repeat),
        "profiles": list(selected.keys()),
        "summary": summary,
        "comparison": comparison,
        "runs": all_runs,
    }

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT_DIR / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[benchmark] reporte guardado en {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
