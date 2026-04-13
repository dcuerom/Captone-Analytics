import json
import math
import re
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

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

OPTIMIZATION_STATE: Dict[str, Any] = {
    "status": "idle",
    "startedAt": None,
    "finishedAt": None,
    "error": None,
    "result": None,
    "requestedDate": None,
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
    if text in {"", "-", "—", "nan", "NaN", "None"}:
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
    if not text or text in {"-", "—", "nan", "NaN", "None"}:
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
        "Dirección": "direccion_ruteo",
        "comuna": "Comuna",
        "lat": "latitud",
        "latitude": "latitud",
        "lng": "longitud",
        "lon": "longitud",
        "longitude": "longitud",
        "delivery_date": "fecha_entrega",
        "date": "fecha_entrega",
        "time_window_start": "a_ventana",
        "time_window_end": "b_ventana",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

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
        df["latitud"] = 0.0
    if "longitud" not in df.columns:
        df["longitud"] = 0.0
    df["latitud"] = df["latitud"].map(lambda x: _safe_float(x, 0.0))
    df["longitud"] = df["longitud"].map(lambda x: _safe_float(x, 0.0))

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
    df["día"] = pd.to_datetime(df["fecha_entrega"], errors="coerce").dt.weekday.fillna(0).astype(int)

    ordered_cols = [
        "id_pedido",
        "id_cliente",
        "direccion_ruteo",
        "Comuna",
        "latitud",
        "longitud",
        "fecha_entrega",
        "día",
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


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_date_from_name(name: str) -> Optional[str]:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", name)
    return m.group(1) if m else None


def _find_files_for_date(date_str: str) -> Dict[str, Optional[Path]]:
    out: Dict[str, Optional[Path]] = {}
    for prefix in ["kpis", "resumen_camiones", "detalle_paradas", "clientes_atendidos"]:
        matches = sorted(RESULTS_DIR.glob(f"{prefix}_*_{date_str}.csv"), key=lambda p: p.stat().st_mtime)
        out[prefix] = matches[-1] if matches else None
    return out


def _list_available_dates() -> List[str]:
    dates = set()
    for p in RESULTS_DIR.glob("kpis_*.csv"):
        d = _extract_date_from_name(p.name)
        if d:
            dates.add(d)
    return sorted(dates)


def _latest_map_file() -> Optional[Path]:
    candidates = sorted(MAP_DIR.glob("mapa_flotaglobal_*.html"), key=lambda p: p.stat().st_mtime)
    if candidates:
        return candidates[-1]
    fallback = MAP_DIR / "mapa_clusters_santiago.html"
    return fallback if fallback.exists() else None


def _load_orders_base(date_str: str) -> pd.DataFrame:
    source = EDA_PATH if EDA_PATH.exists() else SIM_PATH
    df = _read_csv(source)

    if "Dirección" in df.columns and "direccion_ruteo" not in df.columns:
        df = df.rename(columns={"Dirección": "direccion_ruteo"})
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


def _build_dataset(date_str: str, include_routes: bool) -> Dict[str, Any]:
    files = _find_files_for_date(date_str)
    missing = [k for k, v in files.items() if v is None]
    if missing:
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
            if str(row.get("Atendido", "")).strip().lower() in {"sí", "si"}
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

                vol_l = _safe_float(df_d.get("Vol_L", pd.Series(dtype=float)).replace("—", 0).astype(float).sum(), 0.0)
                peso_kg = _safe_float(df_d.get("Peso_kg", pd.Series(dtype=float)).replace("—", 0).astype(float).sum(), 0.0)
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

    vehicles_used = len({r["vehicleId"] for r in routes}) if routes else int(kpi_map.get("Vehículos Utilizados", 0.0))
    vehicles_available = int(kpi_map.get("Capacidad Flota Fija", DEFAULT_VEHICLES_AVAILABLE))
    if vehicles_available <= 0:
        vehicles_available = DEFAULT_VEHICLES_AVAILABLE

    wait_total_global = kpi_map.get("Espera Total Acumulada (min)", 0.0)
    on_time_pct = kpi_map.get("% Entregas a Tiempo", 0.0)
    avg_util = kpi_map.get("% Utilización Promedio Capacidad Vehículos", 0.0)

    warnings: List[str] = []
    if split_orders > 0:
        warnings.append(f"{split_orders} pedido(s) exceden capacidad y se tratan como split interno.")
    if unassigned_orders > 0:
        warnings.append(f"{unassigned_orders} pedido(s) no fueron asignados en la corrida.")
    routes_with_wait = [r for r in routes if r["totalWaitTimeMinutes"] > 30]
    if routes_with_wait:
        warnings.append(f"{len(routes_with_wait)} ruta(s) con espera acumulada > 30 minutos.")

    run = {
        "id": f"RUN-{date_str}",
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


def _build_payload() -> Dict[str, Any]:
    dates = _list_available_dates()
    if not dates:
        raise FileNotFoundError("No se encontraron archivos de corridas en resultados/rutas.")

    latest = dates[-1]
    current = _build_dataset(latest, include_routes=True)

    history = []
    for d in reversed(dates):
        ds = _build_dataset(d, include_routes=False)
        run = ds["run"]
        run["routes"] = []
        history.append(run)

    return {
        "optimizationRun": current["run"],
        "orders": current["orders"],
        "fleet": current["fleet"],
        "historicalRuns": history,
    }


def _start_optimization_async(requested_date: Optional[str], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    with OPTIMIZATION_LOCK:
        if OPTIMIZATION_STATE["status"] == "running":
            return {"started": False, "reason": "already_running", "state": OPTIMIZATION_STATE.copy()}

        OPTIMIZATION_STATE["status"] = "running"
        OPTIMIZATION_STATE["startedAt"] = _utc_now_iso()
        OPTIMIZATION_STATE["finishedAt"] = None
        OPTIMIZATION_STATE["error"] = None
        OPTIMIZATION_STATE["result"] = None
        OPTIMIZATION_STATE["requestedDate"] = requested_date

    def _worker() -> None:
        try:
            from algoritmo.genetic_algorithm import disparar_rutina_ga

            result = disparar_rutina_ga(
                input_csv_path=str(EDA_PATH if EDA_PATH.exists() else SIM_PATH),
                fecha_target=requested_date,
                max_vehiculos_globales=None,
                config=config,
            )
            with OPTIMIZATION_LOCK:
                OPTIMIZATION_STATE["status"] = "completed"
                OPTIMIZATION_STATE["finishedAt"] = _utc_now_iso()
                OPTIMIZATION_STATE["result"] = result
                OPTIMIZATION_STATE["error"] = None
        except Exception as exc:
            with OPTIMIZATION_LOCK:
                OPTIMIZATION_STATE["status"] = "failed"
                OPTIMIZATION_STATE["finishedAt"] = _utc_now_iso()
                OPTIMIZATION_STATE["error"] = str(exc)
                OPTIMIZATION_STATE["result"] = None

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
        if self.path in {"/api/v1/health", "/api/health"}:
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "ok"}, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            return

        if self.path in {"/api/v1/data", "/api/data"}:
            try:
                payload = _build_payload()
                self._set_headers(200)
                self.wfile.write(json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            except Exception as exc:
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(exc)}, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            return

        if self.path in {"/api/v1/optimize-status", "/api/optimize-status"}:
            self._set_headers(200)
            with OPTIMIZATION_LOCK:
                state = OPTIMIZATION_STATE.copy()
            self.wfile.write(json.dumps(state, ensure_ascii=False, allow_nan=False).encode("utf-8"))
            return

        if self.path in {"/api/v1/optimize-config", "/api/optimize-config"}:
            from algoritmo.config import DEFAULT_OPTIMIZATION_CONFIG

            self._set_headers(200)
            self.wfile.write(
                json.dumps({"defaults": DEFAULT_OPTIMIZATION_CONFIG}, ensure_ascii=False, allow_nan=False).encode("utf-8")
            )
            return

        if self.path in {"/api/v1/map", "/api/map"}:
            try:
                latest = _latest_map_file()
                if latest is None:
                    self._set_headers(200, "text/html; charset=utf-8")
                    self.wfile.write(
                        (
                            "<html><body style='font-family:Arial,sans-serif;padding:24px'>"
                            "<h3>Mapa backend no disponible</h3>"
                            "<p>No se encontró un archivo HTML en <code>resultados/mapa_rutas</code>.</p>"
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
        if self.path in {"/api/v1/optimize", "/api/optimize"}:
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                payload = json.loads(body) if body.strip() else {}
                requested_date = payload.get("date")
                requested_date = str(requested_date) if requested_date else None
                config = payload.get("config") if isinstance(payload.get("config"), dict) else None

                result = _start_optimization_async(requested_date, config=config)
                if not result["started"]:
                    self._set_headers(409)
                    self.wfile.write(
                        json.dumps(
                            {"error": "Ya hay una optimización en ejecución", "state": result["state"]},
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

        if self.path not in {"/api/v1/upload-orders", "/api/upload-orders"}:
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
                    json.dumps({"error": "Payload inválido: campo 'csv' vacío"}, ensure_ascii=False, allow_nan=False).encode("utf-8")
                )
                return

            df_raw = pd.read_csv(StringIO(csv_text))
            df = _normalize_uploaded_orders(df_raw)
            if df.empty:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "El CSV no contiene filas"}, ensure_ascii=False, allow_nan=False).encode("utf-8"))
                return

            EDA_PATH.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(EDA_PATH, index=False, encoding="utf-8-sig")

            self._set_headers(200)
            self.wfile.write(
                json.dumps(
                    {
                        "status": "ok",
                        "message": "CSV cargado exitosamente",
                        "filename": filename,
                        "rows": int(len(df)),
                        "columns": list(df.columns),
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
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"[backend-api] serving on http://{host}:{port}")
    print(
        "[backend-api] endpoints: "
        "/api/v1/health, /api/v1/data, /api/v1/map, "
        "GET /api/v1/optimize-config, GET /api/v1/optimize-status, POST /api/v1/optimize, POST /api/v1/upload-orders"
    )
    server.serve_forever()


if __name__ == "__main__":
    run_server()
