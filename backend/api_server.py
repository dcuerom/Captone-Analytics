import json
import importlib
import math
import os
import re
import sys
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
RESULTS_DIR = BASE_DIR / "resultados" / "rutas"
MAP_DIR = BASE_DIR / "resultados" / "mapa_rutas"
EDA_PATH = BASE_DIR / "EDA" / "df_despacho.csv"
SIM_PATH = BASE_DIR / "DatosSimulados" / "df_despacho.csv"

DEFAULT_CAP_VOL_M3 = 3.75
DEFAULT_CAP_PESO_KG = 803.333
DEFAULT_VEHICLES_AVAILABLE = 20
API_SCHEMA_VERSION = "2.1.0"

RUNTIME_REQUIRED_FILES = [
    BASE_DIR / "algoritmo" / "config.py",
    BASE_DIR / "algoritmo" / "savings.py",
    BASE_DIR / "algoritmo" / "genetic_algorithm.py",
    BASE_DIR / "grafo" / "main.py",
    BASE_DIR / "gestion_flota" / "gestor.py",
]
RUNTIME_REQUIRED_IMPORTS = [
    "algoritmo.config",
    "algoritmo.savings",
    "algoritmo.genetic_algorithm",
]
RUNTIME_ENV_OPTIONAL = [
    "SUPABASE_URL",
    "SUPABASE_KEY",
]

OPTIMIZATION_STATE: Dict[str, Any] = {
    "runId": None,
    "status": "idle",
    "startedAt": None,
    "finishedAt": None,
    "error": None,
    "result": None,
    "requestedDate": None,
    "depotAddress": None,
    "requestedConfig": None,
    "progressPct": 0.0,
    "stage": "idle",
    "stageMessage": "Sin optimizaciÃ³n en curso.",
    "currentStep": 0,
    "totalSteps": 0,
    "updatedAt": None,
}
OPTIMIZATION_LOCK = threading.Lock()


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        out = float(value)
        if math.isnan(out) or math.isinf(out):
            return default
        return out

    text = str(value).strip().replace(",", ".")
    if text in {"", "-", "â€”", "nan", "NaN", "None"}:
        return default

    try:
        out = float(text)
        if math.isnan(out) or math.isinf(out):
            return default
        return out
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    return int(round(_safe_float(value, float(default))))


def _to_hhmm(minutes: float) -> str:
    minutes_int = int(round(minutes))
    h = minutes_int // 60
    m = minutes_int % 60
    return f"{h:02d}:{m:02d}"


def _parse_hhmm(value: Any) -> Optional[int]:
    text = str(value).strip()
    if not text or text in {"-", "â€”", "nan", "NaN", "None"}:
        return None
    m = re.match(r"^(\d{1,2}):(\d{2})$", text)
    if not m:
        return None
    h = int(m.group(1))
    mm = int(m.group(2))
    if h < 0 or h > 47 or mm < 0 or mm > 59:
        return None
    return h * 60 + mm


def _add_minutes_to_hhmm(hhmm: Any, delta: float) -> str:
    base = _parse_hhmm(hhmm)
    if base is None:
        return str(hhmm)
    return _to_hhmm(base + _safe_float(delta, 0.0))


def _clean_rut_like(value: Any) -> str:
    text = str(value).strip().upper()
    if not text or text in {"N/A", "NONE", "NAN"}:
        return ""
    return re.sub(r"[^0-9K]", "", text)


def _to_minutes(value: Any, default: int) -> int:
    parsed = _parse_hhmm(value)
    if parsed is not None:
        return parsed
    return _safe_int(value, default)


def _normalize_uploaded_orders(df_in: pd.DataFrame) -> pd.DataFrame:
    df = df_in.copy()
    df.columns = [str(c).strip() for c in df.columns]

    rename_map = {
        "order_id": "id_pedido",
        "pedido_id": "id_pedido",
        "id": "id_pedido",
        "customer_id": "id_cliente",
        "customer": "id_cliente",
        "rut": "id_cliente",
        "RUT": "id_cliente",
        "address": "direccion_ruteo",
        "direccion": "direccion_ruteo",
        "Direccion": "direccion_ruteo",
        "DIRECCION": "direccion_ruteo",
        "dirección": "direccion_ruteo",
        "Dirección": "direccion_ruteo",
        "DirecciÃ³n": "direccion_ruteo",
        "direccion_ruteo": "direccion_ruteo",
        "comuna": "Comuna",
        "Comuna": "Comuna",
        "lat": "latitud",
        "Latitud": "latitud",
        "LATITUD": "latitud",
        "latitud": "latitud",
        "latitude": "latitud",
        "lng": "longitud",
        "lon": "longitud",
        "Longitud": "longitud",
        "LONGITUD": "longitud",
        "longitud": "longitud",
        "longitude": "longitud",
        "delivery_date": "fecha_entrega",
        "Fecha_entrega": "fecha_entrega",
        "fecha entrega": "fecha_entrega",
        "date": "fecha_entrega",
        "time_window_start": "a_ventana",
        "time_window_end": "b_ventana",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Fallback defensivo para encabezados con codificacion inconsistente.
    if "direccion_ruteo" not in df.columns:
        for c in list(df.columns):
            c_low = str(c).strip().lower()
            if "direcci" in c_low or "direccion" in c_low:
                df = df.rename(columns={c: "direccion_ruteo"})
                break
    if "latitud" not in df.columns:
        for c in list(df.columns):
            c_low = str(c).strip().lower()
            if c_low.startswith("lat") or "latitud" in c_low:
                df = df.rename(columns={c: "latitud"})
                break
    if "longitud" not in df.columns:
        for c in list(df.columns):
            c_low = str(c).strip().lower()
            if c_low.startswith("lon") or "longitud" in c_low:
                df = df.rename(columns={c: "longitud"})
                break

    now_date = pd.Timestamp.now().strftime("%Y-%m-%d")

    if "id_pedido" not in df.columns:
        df["id_pedido"] = [f"ORD-UPLOAD-{i:06d}" for i in range(1, len(df) + 1)]
    df["id_pedido"] = df["id_pedido"].astype(str).str.strip()
    empty_ids = df["id_pedido"].eq("") | df["id_pedido"].str.lower().isin({"nan", "none"})
    if empty_ids.any():
        df.loc[empty_ids, "id_pedido"] = [f"ORD-UPLOAD-{i:06d}" for i in range(1, int(empty_ids.sum()) + 1)]

    if "id_cliente" not in df.columns:
        df["id_cliente"] = "N/A"
    df["id_cliente"] = df["id_cliente"].astype(str).str.strip()

    if "direccion_ruteo" not in df.columns:
        df["direccion_ruteo"] = ""
    df["direccion_ruteo"] = df["direccion_ruteo"].astype(str).fillna("")

    if "Comuna" not in df.columns:
        df["Comuna"] = "N/A"
    df["Comuna"] = df["Comuna"].astype(str).fillna("N/A")

    if "latitud" not in df.columns:
        df["latitud"] = None
    if "longitud" not in df.columns:
        df["longitud"] = None
    df["latitud"] = pd.to_numeric(df["latitud"], errors="coerce")
    df["longitud"] = pd.to_numeric(df["longitud"], errors="coerce")
    invalid_lat_mask = df["latitud"].notna() & ((df["latitud"] < -90) | (df["latitud"] > 90))
    invalid_lng_mask = df["longitud"].notna() & ((df["longitud"] < -180) | (df["longitud"] > 180))
    if invalid_lat_mask.any():
        df.loc[invalid_lat_mask, "latitud"] = pd.NA
    if invalid_lng_mask.any():
        df.loc[invalid_lng_mask, "longitud"] = pd.NA

    if "fecha_entrega" not in df.columns:
        df["fecha_entrega"] = now_date
    df["fecha_entrega"] = df["fecha_entrega"].astype(str).replace({"": now_date, "nan": now_date, "None": now_date})

    if "a_ventana" not in df.columns:
        df["a_ventana"] = 540
    if "b_ventana" not in df.columns:
        df["b_ventana"] = 1260
    df["a_ventana"] = df["a_ventana"].map(lambda x: _to_minutes(x, 540))
    df["b_ventana"] = df["b_ventana"].map(lambda x: _to_minutes(x, 1260))

    if "peso_pedido" not in df.columns:
        if "weight_kg" in df.columns:
            df["peso_pedido"] = df["weight_kg"].map(lambda x: _safe_float(x, 0.0) * 1000.0)
        elif "peso_kg" in df.columns:
            df["peso_pedido"] = df["peso_kg"].map(lambda x: _safe_float(x, 0.0) * 1000.0)
        elif "weight_g" in df.columns:
            df["peso_pedido"] = df["weight_g"].map(lambda x: _safe_float(x, 0.0))
        elif "peso_pedido_g" in df.columns:
            df["peso_pedido"] = df["peso_pedido_g"].map(lambda x: _safe_float(x, 0.0))
        else:
            df["peso_pedido"] = 0.0
    else:
        df["peso_pedido"] = df["peso_pedido"].map(lambda x: _safe_float(x, 0.0))

    if "volumen_pedido" not in df.columns:
        if "volume_m3" in df.columns:
            df["volumen_pedido"] = df["volume_m3"].map(lambda x: _safe_float(x, 0.0) * 1_000_000.0)
        elif "volumen_m3" in df.columns:
            df["volumen_pedido"] = df["volumen_m3"].map(lambda x: _safe_float(x, 0.0) * 1_000_000.0)
        elif "volume_l" in df.columns:
            df["volumen_pedido"] = df["volume_l"].map(lambda x: _safe_float(x, 0.0) * 1000.0)
        elif "volumen_l" in df.columns:
            df["volumen_pedido"] = df["volumen_l"].map(lambda x: _safe_float(x, 0.0) * 1000.0)
        elif "volume_cm3" in df.columns:
            df["volumen_pedido"] = df["volume_cm3"].map(lambda x: _safe_float(x, 0.0))
        elif "volumen_pedido_cm3" in df.columns:
            df["volumen_pedido"] = df["volumen_pedido_cm3"].map(lambda x: _safe_float(x, 0.0))
        else:
            df["volumen_pedido"] = 0.0
    else:
        df["volumen_pedido"] = df["volumen_pedido"].map(lambda x: _safe_float(x, 0.0))

    df["rut_clean"] = df["id_cliente"].map(_clean_rut_like)
    df["id_nodo"] = df["id_pedido"].astype(str).str.strip() + "_" + df["rut_clean"].astype(str)
    df["dÃ­a"] = pd.to_datetime(df["fecha_entrega"], errors="coerce").dt.weekday.fillna(0).astype(int)

    ordered_cols = [
        "id_pedido",
        "id_cliente",
        "direccion_ruteo",
        "Comuna",
        "latitud",
        "longitud",
        "fecha_entrega",
        "dÃ­a",
        "a_ventana",
        "b_ventana",
        "peso_pedido",
        "volumen_pedido",
        "rut_clean",
        "id_nodo",
    ]
    for col in ordered_cols:
        if col not in df.columns:
            df[col] = ""
    return df[ordered_cols]


def _validate_normalized_orders(df: pd.DataFrame) -> List[Dict[str, Any]]:
    errors: List[Dict[str, Any]] = []
    required_cols = [
        "id_pedido",
        "id_cliente",
        "direccion_ruteo",
        "Comuna",
        "latitud",
        "longitud",
        "fecha_entrega",
        "a_ventana",
        "b_ventana",
        "peso_pedido",
        "volumen_pedido",
        "id_nodo",
    ]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        return [{"row": None, "errors": [f"Faltan columnas requeridas: {', '.join(missing_cols)}"]}]

    for idx, row in df.iterrows():
        row_errors: List[str] = []
        row_num = int(idx) + 2  # +1 por header y +1 por index base 0

        order_id = str(row.get("id_pedido", "")).strip()
        customer_id = str(row.get("id_cliente", "")).strip()
        address = str(row.get("direccion_ruteo", "")).strip()
        lat = row.get("latitud")
        lng = row.get("longitud")
        a_window = _safe_float(row.get("a_ventana"), -1.0)
        b_window = _safe_float(row.get("b_ventana"), -1.0)
        peso = _safe_float(row.get("peso_pedido"), -1.0)
        volumen = _safe_float(row.get("volumen_pedido"), -1.0)

        if not order_id:
            row_errors.append("id_pedido vacio")
        if not customer_id or customer_id.upper() in {"N/A", "NONE", "NAN"}:
            row_errors.append("id_cliente vacio")
        if not address:
            row_errors.append("direccion_ruteo vacia")
        if pd.isna(lat) or pd.isna(lng):
            row_errors.append("latitud/longitud faltantes")
        else:
            lat_f = _safe_float(lat, 999.0)
            lng_f = _safe_float(lng, 999.0)
            if lat_f < -90 or lat_f > 90:
                row_errors.append("latitud fuera de rango [-90,90]")
            if lng_f < -180 or lng_f > 180:
                row_errors.append("longitud fuera de rango [-180,180]")

        if a_window < 0 or b_window < 0:
            row_errors.append("ventanas horarias invalidas")
        elif b_window < a_window:
            row_errors.append("b_ventana debe ser >= a_ventana")

        if peso < 0:
            row_errors.append("peso_pedido negativo")
        if volumen < 0:
            row_errors.append("volumen_pedido negativo")

        if row_errors:
            errors.append({"row": row_num, "id_pedido": order_id or None, "errors": row_errors})

    return errors


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sorted_delivery_dates(df: pd.DataFrame) -> List[str]:
    if "fecha_entrega" not in df.columns:
        return []
    parsed = pd.to_datetime(df["fecha_entrega"], errors="coerce").dropna()
    if parsed.empty:
        return []
    return sorted({value.strftime("%Y-%m-%d") for value in parsed})


def _new_run_id() -> str:
    return f"run-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"


def _preflight_check() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    for path in RUNTIME_REQUIRED_FILES:
        exists = path.exists()
        checks.append(
            {
                "name": f"file:{path.relative_to(BASE_DIR)}",
                "ok": exists,
                "detail": "ok" if exists else "missing",
            }
        )

    for module_name in RUNTIME_REQUIRED_IMPORTS:
        try:
            importlib.import_module(module_name)
            checks.append({"name": f"import:{module_name}", "ok": True, "detail": "ok"})
        except Exception as exc:
            checks.append({"name": f"import:{module_name}", "ok": False, "detail": str(exc)})

    source_exists = EDA_PATH.exists() or SIM_PATH.exists()
    checks.append(
        {
            "name": "data_source",
            "ok": source_exists,
            "detail": str(EDA_PATH if EDA_PATH.exists() else SIM_PATH if SIM_PATH.exists() else "missing"),
        }
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MAP_DIR.mkdir(parents=True, exist_ok=True)
    checks.append({"name": "artifacts_dir", "ok": True, "detail": f"{RESULTS_DIR} | {MAP_DIR}"})
    for env_name in RUNTIME_ENV_OPTIONAL:
        present = bool(os.getenv(env_name))
        checks.append(
            {
                "name": f"env:{env_name}",
                "ok": True,
                "detail": "set" if present else "missing (fallback_local_osm)",
            }
        )

    failed = [c for c in checks if not c["ok"]]
    status = "ok" if not failed else "failed"
    return {
        "status": status,
        "generatedAt": _utc_now_iso(),
        "failedCount": len(failed),
        "checks": checks,
    }


def _extract_date_from_name(name: str) -> Optional[str]:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", name)
    return m.group(1) if m else None


def _read_run_metadata(run_id: str) -> Optional[Dict[str, Any]]:
    path = RESULTS_DIR / f"run_{run_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _list_run_metadata() -> List[Dict[str, Any]]:
    runs: List[Dict[str, Any]] = []
    for p in RESULTS_DIR.glob("run_*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            data["_metaPath"] = str(p)
            data["_mtime"] = p.stat().st_mtime
            runs.append(data)
        except Exception:
            continue
    runs.sort(key=lambda r: (str(r.get("createdAt") or ""), float(r.get("_mtime", 0))), reverse=True)
    return runs


def _find_files_for_date(date_str: str, run_id: Optional[str] = None) -> Dict[str, Optional[Path]]:
    out: Dict[str, Optional[Path]] = {}
    for prefix in ["kpis", "resumen_camiones", "detalle_paradas", "clientes_atendidos"]:
        matches = sorted(RESULTS_DIR.glob(f"{prefix}_*_{date_str}*.csv"), key=lambda p: p.stat().st_mtime)
        if run_id:
            matches = [p for p in matches if run_id in p.stem]
        out[prefix] = matches[-1] if matches else None
    return out


def _list_available_dates() -> List[str]:
    dates = set()
    for p in RESULTS_DIR.glob("kpis_*.csv"):
        d = _extract_date_from_name(p.name)
        if d:
            dates.add(d)
    return sorted(dates)


def _latest_map_file(run_id: Optional[str] = None) -> Optional[Path]:
    candidates = sorted(MAP_DIR.glob("mapa_flotaglobal_*.html"), key=lambda p: p.stat().st_mtime)
    if run_id:
        candidates = [p for p in candidates if run_id in p.stem]
    if candidates:
        return candidates[-1]
    fallback = MAP_DIR / "mapa_clusters_santiago.html"
    return fallback if fallback.exists() else None


def _load_orders_base(date_str: str) -> pd.DataFrame:
    source = EDA_PATH if EDA_PATH.exists() else SIM_PATH
    df = _read_csv(source)

    if "DirecciÃ³n" in df.columns and "direccion_ruteo" not in df.columns:
        df = df.rename(columns={"DirecciÃ³n": "direccion_ruteo"})
    if "Latitud" in df.columns and "latitud" not in df.columns:
        df = df.rename(columns={"Latitud": "latitud"})
    if "Longitud" in df.columns and "longitud" not in df.columns:
        df = df.rename(columns={"Longitud": "longitud"})

    if "rut_clean" not in df.columns:
        if "id_cliente" in df.columns:
            df["rut_clean"] = df["id_cliente"].astype(str).str.replace(r"[^0-9kK]", "", regex=True).str.upper()
        else:
            df["rut_clean"] = ""

    if "id_nodo" not in df.columns:
        if "id_pedido" in df.columns:
            df["id_nodo"] = df["id_pedido"].astype(str).str.strip() + "_" + df["rut_clean"].astype(str)
        else:
            df["id_nodo"] = df.index.astype(str)

    if "fecha_entrega" in df.columns:
        filtered = df[df["fecha_entrega"].astype(str) == date_str].copy()
        if not filtered.empty:
            df = filtered

    return df


def _build_dataset(date_str: str, include_routes: bool, run_id: Optional[str] = None) -> Dict[str, Any]:
    files = _find_files_for_date(date_str, run_id=run_id)
    missing = [k for k, v in files.items() if v is None]
    if missing:
        if run_id:
            raise FileNotFoundError(f"Faltan archivos para run_id {run_id}: {', '.join(missing)}")
        raise FileNotFoundError(f"Faltan archivos para fecha {date_str}: {', '.join(missing)}")

    df_kpi = _read_csv(files["kpis"])  # type: ignore[arg-type]
    df_resumen = _read_csv(files["resumen_camiones"])  # type: ignore[arg-type]
    df_detalle = _read_csv(files["detalle_paradas"])  # type: ignore[arg-type]
    df_clientes = _read_csv(files["clientes_atendidos"])  # type: ignore[arg-type]
    df_orders = _load_orders_base(date_str)

    kpi_map = {
        str(row["KPI"]).strip(): _safe_float(row["Valor"], 0.0)
        for _, row in df_kpi.iterrows()
        if "KPI" in df_kpi.columns and "Valor" in df_kpi.columns
    }

    cluster_map = {}
    if {"id_nodo", "Cluster"}.issubset(df_clientes.columns):
        cluster_map = {str(row["id_nodo"]): row.get("Cluster", "Sin Cluster") for _, row in df_clientes.iterrows()}

    attended_set = set()
    if {"id_nodo", "Atendido"}.issubset(df_clientes.columns):
        attended_set = {
            str(row["id_nodo"])
            for _, row in df_clientes.iterrows()
            if str(row.get("Atendido", "")).strip().lower() in {"sÃ­", "si"}
        }

    orders: List[Dict[str, Any]] = []
    for _, row in df_orders.iterrows():
        oid = str(row.get("id_nodo", "")).strip()
        if not oid:
            continue

        vol_cm3 = _safe_float(row.get("volumen_pedido", row.get("volumen_pedido_cm3", 0.0)), 0.0)
        peso_g = _safe_float(row.get("peso_pedido", row.get("peso_pedido_g", 0.0)), 0.0)
        vol_m3 = vol_cm3 / 1_000_000.0
        peso_kg = peso_g / 1000.0

        is_oversized = vol_m3 > DEFAULT_CAP_VOL_M3 or peso_kg > DEFAULT_CAP_PESO_KG
        attended = oid in attended_set

        status = "assigned" if attended else "unassigned"
        if is_oversized:
            status = "split"

        a_window = _safe_float(row.get("a_ventana", 540.0), 540.0)
        b_window = _safe_float(row.get("b_ventana", 1260.0), 1260.0)

        orders.append(
            {
                "id": oid,
                "customerId": str(row.get("id_cliente", "N/A")),
                "customerName": f"Cliente {row.get('id_cliente', 'N/A')}",
                "address": str(row.get("direccion_ruteo", "Sin direccion")),
                "comuna": str(row.get("Comuna", "N/A")),
                "lat": _safe_float(row.get("latitud", 0.0), 0.0),
                "lng": _safe_float(row.get("longitud", 0.0), 0.0),
                "volumeM3": round(vol_m3, 4),
                "weightKg": round(peso_kg, 2),
                "timeWindowStart": _to_hhmm(a_window),
                "timeWindowEnd": _to_hhmm(b_window),
                "deliveryDate": str(row.get("fecha_entrega", date_str)),
                "cluster": cluster_map.get(oid),
                "status": status,
                "serviceTimeMinutes": 5,
            }
        )

    orders_by_id = {o["id"]: o for o in orders}

    total_distance_km = kpi_map.get(
        "Distancia Total Recorrida (km)",
        _safe_float(df_resumen.get("Distancia_km", pd.Series(dtype=float)).sum(), 0.0),
    )
    total_cost = kpi_map.get("Costo de Ruta (F.O. componente transporte)", 0.0)
    cost_per_km = (total_cost / total_distance_km) if total_distance_km > 0 else 0.0

    routes: List[Dict[str, Any]] = []

    if include_routes and not df_resumen.empty and not df_detalle.empty:
        veh_col = "Vehiculo_Fisico" if "Vehiculo_Fisico" in df_resumen.columns else None
        if veh_col is not None:
            vehicle_ids = sorted(df_resumen[veh_col].dropna().astype(int).unique().tolist())

            for vid in vehicle_ids:
                df_r = df_resumen[df_resumen[veh_col].astype(int) == vid].copy()
                df_d = df_detalle[df_detalle[veh_col].astype(int) == vid].copy()

                if df_d.empty:
                    continue

                if "Nodo" in df_d.columns:
                    df_d = df_d[df_d["Nodo"].astype(str) != "DEPOT_01_BASE"].copy()

                if df_d.empty:
                    continue

                if "Secuencia" in df_d.columns:
                    df_d = df_d.sort_values("Secuencia")

                stops: List[Dict[str, Any]] = []
                on_time_count = 0

                for idx, (_, stop_row) in enumerate(df_d.iterrows(), start=1):
                    order_id = str(stop_row.get("Nodo", ""))
                    wait_min = _safe_float(stop_row.get("Tiempo_Espera_min", 0.0), 0.0)
                    viol_min = _safe_float(stop_row.get("Violacion_Ventana_min", 0.0), 0.0)
                    is_on_time = viol_min <= 0.0
                    if is_on_time:
                        on_time_count += 1

                    arrival = str(stop_row.get("Hora_Llegada", "00:00"))
                    service = _safe_float(stop_row.get("Tiempo_Servicio_min", 0.0), 0.0)

                    stops.append(
                        {
                            "orderId": order_id,
                            "sequence": idx,
                            "arrivalTime": arrival,
                            "departureTime": _add_minutes_to_hhmm(arrival, service),
                            "waitTimeMinutes": round(wait_min, 1),
                            "distanceFromPreviousKm": round(_safe_float(stop_row.get("Distancia_Recorrida_km", 0.0), 0.0), 3),
                            "travelTimeMinutes": round(_safe_float(stop_row.get("Tiempo_Viaje_min", 0.0), 0.0), 2),
                            "isOnTime": is_on_time,
                            "timeWindowViolationMinutes": round(viol_min, 2),
                        }
                    )

                    if order_id in orders_by_id and not orders_by_id[order_id].get("cluster"):
                        orders_by_id[order_id]["cluster"] = stop_row.get("Cluster_Visitado")

                dist_km = _safe_float(df_r.get("Distancia_km", pd.Series(dtype=float)).sum(), 0.0)
                wait_total = _safe_float(df_r.get("Espera_min", pd.Series(dtype=float)).sum(), 0.0)
                travel_total = _safe_float(df_r.get("Viaje_Efectivo_min", pd.Series(dtype=float)).sum(), 0.0)
                service_total = _safe_float(df_r.get("Servicio_min", pd.Series(dtype=float)).sum(), 0.0)

                vol_l = _safe_float(df_d.get("Vol_L", pd.Series(dtype=float)).replace("â€”", 0).astype(float).sum(), 0.0)
                peso_kg = _safe_float(df_d.get("Peso_kg", pd.Series(dtype=float)).replace("â€”", 0).astype(float).sum(), 0.0)
                vol_m3 = vol_l / 1000.0

                cluster_value = df_r["Cluster"].iloc[0] if "Cluster" in df_r.columns and not df_r.empty else 0
                try:
                    cluster_num = int(cluster_value)
                except Exception:
                    cluster_num = 0

                utilization_vol = (vol_m3 / DEFAULT_CAP_VOL_M3 * 100.0) if DEFAULT_CAP_VOL_M3 > 0 else 0.0
                utilization_peso = (peso_kg / DEFAULT_CAP_PESO_KG * 100.0) if DEFAULT_CAP_PESO_KG > 0 else 0.0

                vehicle_id = f"V{vid:03d}"
                route_cost = dist_km * cost_per_km

                routes.append(
                    {
                        "vehicleId": vehicle_id,
                        "vehicleName": f"Camion {vid:03d}",
                        "stops": stops,
                        "totalDistanceKm": round(dist_km, 3),
                        "totalTimeMinutes": round(travel_total + service_total + wait_total, 2),
                        "totalWaitTimeMinutes": round(wait_total, 2),
                        "loadVolumeM3": round(vol_m3, 4),
                        "loadWeightKg": round(peso_kg, 2),
                        "utilizationVolume": round(utilization_vol, 2),
                        "utilizationWeight": round(utilization_peso, 2),
                        "ordersDelivered": len(stops),
                        "onTimeDeliveries": on_time_count,
                        "totalCost": round(route_cost, 2),
                        "cluster": cluster_num,
                    }
                )

    assigned_orders = sum(1 for o in orders if o["status"] != "unassigned")
    split_orders = sum(1 for o in orders if o["status"] == "split")
    total_orders = len(orders)
    unassigned_orders = max(total_orders - assigned_orders, 0)

    vehicles_used = len({r["vehicleId"] for r in routes}) if routes else int(kpi_map.get("VehÃ­culos Utilizados", 0.0))
    vehicles_available = int(kpi_map.get("Capacidad Flota Fija", DEFAULT_VEHICLES_AVAILABLE))
    if vehicles_available <= 0:
        vehicles_available = DEFAULT_VEHICLES_AVAILABLE

    wait_total_global = kpi_map.get("Espera Total Acumulada (min)", 0.0)
    on_time_pct = kpi_map.get("% Entregas a Tiempo", 0.0)
    avg_util = kpi_map.get("% UtilizaciÃ³n Promedio Capacidad VehÃ­culos", 0.0)

    warnings: List[str] = []
    if split_orders > 0:
        warnings.append(f"{split_orders} pedido(s) exceden capacidad y se tratan como split interno.")
    if unassigned_orders > 0:
        warnings.append(f"{unassigned_orders} pedido(s) no fueron asignados en la corrida.")
    routes_with_wait = [r for r in routes if r["totalWaitTimeMinutes"] > 30]
    if routes_with_wait:
        warnings.append(f"{len(routes_with_wait)} ruta(s) con espera acumulada > 30 minutos.")

    run = {
        "id": run_id or f"RUN-{date_str}",
        "name": f"Optimizacion despacho {date_str}",
        "date": date_str,
        "status": "completed",
        "totalOrders": total_orders,
        "assignedOrders": assigned_orders,
        "unassignedOrders": unassigned_orders,
        "splitOrders": split_orders,
        "totalVehiclesUsed": vehicles_used,
        "totalVehiclesAvailable": vehicles_available,
        "totalDistanceKm": round(kpi_map.get("Distancia Total Recorrida (km)", total_distance_km), 3),
        "totalCost": round(total_cost, 3),
        "totalWaitTimeMinutes": round(wait_total_global, 2),
        "onTimePercentage": round(on_time_pct, 2),
        "averageUtilization": round(avg_util, 2),
        "executionTimeSeconds": 0.0,
        "warnings": warnings,
        "routes": routes,
    }

    fleet = []
    for idx in range(1, vehicles_available + 1):
        vehicle_id = f"V{idx:03d}"
        fleet.append(
            {
                "id": vehicle_id,
                "name": f"Camion {idx:03d}",
                "capacityM3": DEFAULT_CAP_VOL_M3,
                "capacityKg": DEFAULT_CAP_PESO_KG,
                "costPerKm": round(cost_per_km, 4),
                "costPerHour": 0.0,
                "shift": "morning" if idx % 2 else "afternoon",
                "available": True,
            }
        )

    return {"run": run, "orders": orders, "fleet": fleet}


def _build_payload(run_id: Optional[str] = None, date_str: Optional[str] = None) -> Dict[str, Any]:
    runs = _list_run_metadata()
    if run_id:
        run_meta = _read_run_metadata(run_id)
        if run_meta:
            target_date = str(run_meta.get("date") or date_str or "")
            if not target_date:
                target_date = datetime.now().strftime("%Y-%m-%d")
            current = _build_dataset(target_date, include_routes=True, run_id=run_id)
        else:
            if not date_str:
                raise FileNotFoundError(f"No existe metadata para run_id {run_id}")
            current = _build_dataset(date_str, include_routes=True, run_id=run_id)
    else:
        if runs:
            latest_meta = runs[0]
            run_id = str(latest_meta.get("runId", "")).strip() or None
            target_date = str(latest_meta.get("date") or date_str or "")
            if not target_date:
                target_date = datetime.now().strftime("%Y-%m-%d")
            current = _build_dataset(target_date, include_routes=True, run_id=run_id)
        else:
            dates = _list_available_dates()
            if not dates:
                raise FileNotFoundError("No se encontraron corridas en resultados/rutas.")
            latest = date_str or dates[-1]
            current = _build_dataset(latest, include_routes=True)

    history: List[Dict[str, Any]] = []
    if runs:
        for meta in runs:
            rid = str(meta.get("runId", "")).strip()
            d = str(meta.get("date", "")).strip()
            if not rid or not d:
                continue
            try:
                ds = _build_dataset(d, include_routes=False, run_id=rid)
                run = ds["run"]
                run["routes"] = []
                history.append(run)
            except Exception:
                continue
    else:
        for d in reversed(_list_available_dates()):
            try:
                ds = _build_dataset(d, include_routes=False)
                run = ds["run"]
                run["routes"] = []
                history.append(run)
            except Exception:
                continue

    return {
        "schemaVersion": API_SCHEMA_VERSION,
        "generatedAt": _utc_now_iso(),
        "optimizationRun": current["run"],
        "orders": current["orders"],
        "fleet": current["fleet"],
        "historicalRuns": history,
    }


def _start_optimization_async(
    requested_date: Optional[str],
    config: Optional[Dict[str, Any]] = None,
    run_id: Optional[str] = None,
    depot_address: Optional[str] = None,
) -> Dict[str, Any]:
    if not run_id:
        run_id = _new_run_id()
    preflight = _preflight_check()
    if preflight.get("status") != "ok":
        return {
            "started": False,
            "reason": "preflight_failed",
            "preflight": preflight,
            "state": OPTIMIZATION_STATE.copy(),
        }

    def _report_progress(
        stage: str,
        message: str,
        progress_pct: float,
        current_step: Optional[int] = None,
        total_steps: Optional[int] = None,
    ) -> None:
        with OPTIMIZATION_LOCK:
            OPTIMIZATION_STATE["stage"] = str(stage)
            OPTIMIZATION_STATE["stageMessage"] = str(message)
            OPTIMIZATION_STATE["progressPct"] = max(0.0, min(100.0, float(progress_pct)))
            OPTIMIZATION_STATE["updatedAt"] = _utc_now_iso()
            if current_step is not None:
                OPTIMIZATION_STATE["currentStep"] = int(current_step)
            if total_steps is not None:
                OPTIMIZATION_STATE["totalSteps"] = int(total_steps)

    with OPTIMIZATION_LOCK:
        if OPTIMIZATION_STATE["status"] == "running":
            return {"started": False, "reason": "already_running", "state": OPTIMIZATION_STATE.copy()}

        OPTIMIZATION_STATE["status"] = "running"
        OPTIMIZATION_STATE["startedAt"] = _utc_now_iso()
        OPTIMIZATION_STATE["finishedAt"] = None
        OPTIMIZATION_STATE["error"] = None
        OPTIMIZATION_STATE["result"] = None
        OPTIMIZATION_STATE["requestedDate"] = requested_date
        OPTIMIZATION_STATE["runId"] = run_id
        OPTIMIZATION_STATE["depotAddress"] = depot_address
        OPTIMIZATION_STATE["requestedConfig"] = config or {}
        OPTIMIZATION_STATE["progressPct"] = 0.0
        OPTIMIZATION_STATE["stage"] = "preparing"
        OPTIMIZATION_STATE["stageMessage"] = "Preparando optimizaciÃ³n..."
        OPTIMIZATION_STATE["currentStep"] = 0
        OPTIMIZATION_STATE["totalSteps"] = 0
        OPTIMIZATION_STATE["updatedAt"] = _utc_now_iso()

    def _worker() -> None:
        try:
            from algoritmo.genetic_algorithm import disparar_rutina_ga

            _report_progress("preparing", "Iniciando flujo de optimizaciÃ³n...", 3.0)
            result = disparar_rutina_ga(
                input_csv_path=str(EDA_PATH if EDA_PATH.exists() else SIM_PATH),
                fecha_target=requested_date,
                max_vehiculos_globales=None,
                config=config,
                run_id=run_id,
                depot_address=depot_address,
                progress_callback=_report_progress,
            )
            with OPTIMIZATION_LOCK:
                OPTIMIZATION_STATE["status"] = "completed"
                OPTIMIZATION_STATE["finishedAt"] = _utc_now_iso()
                OPTIMIZATION_STATE["result"] = result
                OPTIMIZATION_STATE["error"] = None
                OPTIMIZATION_STATE["progressPct"] = 100.0
                OPTIMIZATION_STATE["stage"] = "completed"
                OPTIMIZATION_STATE["stageMessage"] = "OptimizaciÃ³n finalizada correctamente."
                OPTIMIZATION_STATE["updatedAt"] = _utc_now_iso()
        except Exception as exc:
            with OPTIMIZATION_LOCK:
                OPTIMIZATION_STATE["status"] = "failed"
                OPTIMIZATION_STATE["finishedAt"] = _utc_now_iso()
                OPTIMIZATION_STATE["error"] = str(exc)
                OPTIMIZATION_STATE["result"] = None
                OPTIMIZATION_STATE["stage"] = "failed"
                OPTIMIZATION_STATE["stageMessage"] = f"OptimizaciÃ³n fallida: {exc}"
                OPTIMIZATION_STATE["updatedAt"] = _utc_now_iso()

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return {"started": True, "reason": "started", "state": OPTIMIZATION_STATE.copy()}


class Handler(BaseHTTPRequestHandler):
    server_version = "CapstoneBackendAdapter/1.0"

    def _set_headers(self, status: int = 200, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._set_headers(204)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path in {"/api/v1/health", "/api/health"}:
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "ok"}, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            return

        if path in {"/api/v1/preflight", "/api/preflight"}:
            report = _preflight_check()
            self._set_headers(200 if report.get("status") == "ok" else 503)
            self.wfile.write(json.dumps(report, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            return

        if path in {"/api/v1/data", "/api/data"}:
            try:
                run_id = query.get("runId", [None])[0]
                requested_date = query.get("date", [None])[0]
                payload = _build_payload(run_id=run_id, date_str=requested_date)
                self._set_headers(200)
                self.wfile.write(json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            except Exception as exc:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(exc)}, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            return

        if path in {"/api/v1/optimize-status", "/api/optimize-status"}:
            self._set_headers(200)
            with OPTIMIZATION_LOCK:
                state = OPTIMIZATION_STATE.copy()
            self.wfile.write(json.dumps(state, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            return

        if path in {"/api/v1/optimize-config", "/api/optimize-config"}:
            from algoritmo.config import DEFAULT_OPTIMIZATION_CONFIG

            self._set_headers(200)
            self.wfile.write(
                json.dumps(
                    {"schemaVersion": API_SCHEMA_VERSION, "defaults": DEFAULT_OPTIMIZATION_CONFIG},
                    ensure_ascii=False,
                    allow_nan=False,
                ).encode("utf-8")
            )
            return

        if path in {"/api/v1/routes-geometry", "/api/routes-geometry"}:
            run_id = query.get("runId", [None])[0]
            if not run_id:
                with OPTIMIZATION_LOCK:
                    run_id = OPTIMIZATION_STATE.get("runId")
            if not run_id:
                metas = _list_run_metadata()
                run_id = metas[0].get("runId") if metas else None
            if not run_id:
                self._set_headers(404)
                self.wfile.write(
                    json.dumps({"error": "No hay run_id disponible para geometria"}, ensure_ascii=False, allow_nan=False).encode("utf-8")
                )
                return
            geometry_path = RESULTS_DIR / f"route_geometry_{run_id}.json"
            if not geometry_path.exists():
                self._set_headers(404)
                self.wfile.write(
                    json.dumps(
                        {"error": f"No existe geometria para run_id {run_id}", "path": str(geometry_path)},
                        ensure_ascii=False,
                        allow_nan=False,
                    ).encode("utf-8")
                )
                return
            self._set_headers(200)
            self.wfile.write(geometry_path.read_text(encoding="utf-8").encode("utf-8"))
            return

        if path in {"/api/v1/map", "/api/map"}:
            try:
                run_id = query.get("runId", [None])[0]
                latest = _latest_map_file(run_id=run_id)
                if latest is None:
                    self._set_headers(200, "text/html; charset=utf-8")
                    self.wfile.write(
                        (
                            "<html><body style='font-family:Arial,sans-serif;padding:24px'>"
                            "<h3>Mapa backend no disponible</h3>"
                            "<p>No se encontro un archivo HTML en <code>resultados/mapa_rutas</code>.</p>"
                            "<p>Genera una corrida que exporte <code>mapa_flotaglobal_*.html</code> para ver calles reales.</p>"
                            "</body></html>"
                        ).encode("utf-8")
                    )
                    return
                html = latest.read_text(encoding="utf-8", errors="replace")
                self._set_headers(200, "text/html; charset=utf-8")
                self.wfile.write(html.encode("utf-8"))
            except Exception as exc:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(exc)}, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Not found"}, ensure_ascii=False, allow_nan=False).encode("utf-8"))

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path

        if path in {"/api/v1/optimize", "/api/optimize"}:
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                payload = json.loads(body) if body.strip() else {}
                requested_date = payload.get("date")
                requested_date = str(requested_date) if requested_date else None
                config = payload.get("config") if isinstance(payload.get("config"), dict) else None
                depot_address = payload.get("depotAddress")
                depot_address = str(depot_address).strip() if depot_address else None
                requested_run_id = payload.get("runId")
                requested_run_id = str(requested_run_id).strip() if requested_run_id else _new_run_id()

                result = _start_optimization_async(
                    requested_date,
                    config=config,
                    run_id=requested_run_id,
                    depot_address=depot_address,
                )
                if not result["started"]:
                    status_code = 503 if result.get("reason") == "preflight_failed" else 409
                    self._set_headers(status_code)
                    self.wfile.write(
                        json.dumps(
                            {
                                "error": "Preflight fallido antes de optimizar"
                                if result.get("reason") == "preflight_failed"
                                else "Ya hay una optimizacion en ejecucion",
                                "reason": result.get("reason"),
                                "state": result.get("state"),
                                "preflight": result.get("preflight"),
                            },
                            ensure_ascii=False,
                            allow_nan=False,
                        ).encode("utf-8")
                    )
                    return

                self._set_headers(202)
                self.wfile.write(json.dumps(result["state"], ensure_ascii=False, allow_nan=False).encode("utf-8"))
            except Exception as exc:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(exc)}, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            return

        if path not in {"/api/v1/upload-orders", "/api/upload-orders"}:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body)

            csv_text = payload.get("csv", "")
            filename = str(payload.get("filename", "uploaded_orders.csv"))
            if not csv_text.strip():
                self._set_headers(400)
                self.wfile.write(
                    json.dumps({"error": "Payload invalido: campo 'csv' vacio"}, ensure_ascii=False, allow_nan=False).encode("utf-8")
                )
                return

            df_raw = pd.read_csv(StringIO(csv_text))
            df = _normalize_uploaded_orders(df_raw)
            if df.empty:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "El CSV no contiene filas"}, ensure_ascii=False, allow_nan=False).encode("utf-8"))
                return

            validation_errors = _validate_normalized_orders(df)
            if validation_errors:
                invalid_coords = [
                    err
                    for err in validation_errors
                    if any(
                        coord_msg in str(msg)
                        for msg in err.get("errors", [])
                        for coord_msg in (
                            "latitud/longitud faltantes",
                            "latitud fuera de rango [-90,90]",
                            "longitud fuera de rango [-180,180]",
                        )
                    )
                ]

                geocode_attempted = False
                geocode_filled = 0
                if invalid_coords and "direccion_ruteo" in df.columns:
                    non_empty_addr = df["direccion_ruteo"].astype(str).str.strip().ne("").sum()
                    if non_empty_addr > 0:
                        try:
                            from grafo.geocoder import geocode_orders

                            geocode_attempted = True
                            before_missing = int(df["latitud"].isna().sum() + df["longitud"].isna().sum())
                            df_geo = geocode_orders(df, address_col="direccion_ruteo")
                            df_geo["latitud"] = pd.to_numeric(df_geo["latitud"], errors="coerce")
                            df_geo["longitud"] = pd.to_numeric(df_geo["longitud"], errors="coerce")
                            after_missing = int(df_geo["latitud"].isna().sum() + df_geo["longitud"].isna().sum())
                            geocode_filled = max(0, before_missing - after_missing)
                            df = df_geo
                            validation_errors = _validate_normalized_orders(df)
                        except Exception:
                            # Si falla geocodificacion, se mantiene validacion original.
                            pass

            if validation_errors:
                self._set_headers(400)
                self.wfile.write(
                    json.dumps(
                        {
                            "error": "CSV invalido: corrige los campos requeridos del contrato canonico.",
                            "schemaVersion": API_SCHEMA_VERSION,
                            "invalidRows": len(validation_errors),
                            "errors": validation_errors[:25],
                            "geocodeAttempted": geocode_attempted if 'geocode_attempted' in locals() else False,
                            "geocodeFilled": geocode_filled if 'geocode_filled' in locals() else 0,
                        },
                        ensure_ascii=False,
                        allow_nan=False,
                    ).encode("utf-8")
                )
                return

            EDA_PATH.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(EDA_PATH, index=False, encoding="utf-8-sig")
            detected_dates = _sorted_delivery_dates(df)

            self._set_headers(200)
            self.wfile.write(
                json.dumps(
                    {
                        "status": "ok",
                        "message": "CSV cargado exitosamente",
                        "filename": filename,
                        "rows": int(len(df)),
                        "columns": list(df.columns),
                        "detectedDeliveryDates": detected_dates,
                        "defaultDeliveryDate": detected_dates[0] if detected_dates else None,
                        "schemaVersion": API_SCHEMA_VERSION,
                        "saved_to": str(EDA_PATH),
                    },
                    ensure_ascii=False,
                    allow_nan=False,
                ).encode("utf-8")
            )
        except Exception as exc:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": str(exc)}, ensure_ascii=False, allow_nan=False).encode("utf-8"))

def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    preflight = _preflight_check()
    print(f"[backend-api] preflight status: {preflight.get('status')} (failed={preflight.get('failedCount')})")
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"[backend-api] serving on http://{host}:{port}")
    print(
        "[backend-api] endpoints: "
        "/api/v1/health, /api/v1/preflight, /api/v1/data, /api/v1/map, /api/v1/routes-geometry, "
        "GET /api/v1/optimize-config, GET /api/v1/optimize-status, POST /api/v1/optimize, POST /api/v1/upload-orders"
    )
    server.serve_forever()


if __name__ == "__main__":
    run_server()
