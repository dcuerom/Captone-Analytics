from __future__ import annotations

import argparse
import csv
import math
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import folium
import pandas as pd

# Permite importar modulos del repo al ejecutar este script de forma directa.
SCRIPT_PATH = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_PATH.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from grafo.geocoder import geocode_depot


# =============================================================================
# Configuracion base de rutas del proyecto
# =============================================================================
DEFAULT_ORDERS_XLSX = PROJECT_ROOT / "EDA" / "vrp_orders.xlsx"
DEFAULT_DISPATCH_CSV = PROJECT_ROOT / "DatosSimulados" / "df_despacho.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "casoBase_res"
DEFAULT_GRAPH_PATH = PROJECT_ROOT / "grafo" / "santiago_routing_graph.graphml"


@dataclass
class DepotResolution:
    """Estructura de salida para explicar como se obtuvo el depot final."""

    geocoded_lat: Optional[float]
    geocoded_lon: Optional[float]
    final_lat: float
    final_lon: float
    method: str
    num_clusters_dbscan: int


@dataclass
class RouteStop:
    """Representa una parada dentro de una ruta."""

    stop_number: int
    order_id: str
    node_id: str
    address: str
    comuna: str
    lat: float
    lon: float
    demand_g: float
    demand_cm3: float
    distance_from_previous_km: float
    arrival_min: float
    service_start_min: float
    service_end_min: float
    status: str


@dataclass
class TruckRoute:
    """Representa una ruta/tour de un camion."""

    truck_id: int
    route_id: int
    start_min: float
    end_min: float
    distance_km: float
    load_used_g: float
    load_used_cm3: float
    stops: List[RouteStop]


def parse_args() -> argparse.Namespace:
    """Argumentos CLI para configurar hiperparametros del caso base."""
    parser = argparse.ArgumentParser(
        description=(
            "Heuristica TSP/VRP caso base (sin ventanas de tiempo y sin "
            "clusterizacion de clientes), con depot configurable por direccion exacta."
        )
    )
    parser.add_argument(
        "--orders-xlsx",
        type=Path,
        default=DEFAULT_ORDERS_XLSX,
        help="Ruta al archivo vrp_orders.xlsx",
    )
    parser.add_argument(
        "--dispatch-csv",
        type=Path,
        default=DEFAULT_DISPATCH_CSV,
        help="Ruta al archivo df_despacho.csv",
    )
    parser.add_argument(
        "--depot-address",
        type=str,
        default="SANTA ELENA 840 SANTIAGO",
        help="Direccion exacta del depot a geocodificar",
    )
    parser.add_argument(
        "--truck-capacity-g",
        type=float,
        default=803_333_330.0,
        help="Capacidad de peso por camion en gramos",
    )
    parser.add_argument(
        "--truck-capacity-cm3",
        type=float,
        default=3_750_000.0,
        help="Capacidad de volumen por camion en centimetros cubicos",
    )
    parser.add_argument(
        "--num-trucks",
        type=int,
        default=4,
        help="Cantidad de camiones disponibles",
    )
    parser.add_argument(
        "--day",
        type=str,
        default="2026-12-03",
        help="Fecha de salida en formato yyyy-mm-dd (ejemplo: 2026-12-03)",
    )
    parser.add_argument(
        "--service-minutes",
        type=float,
        default=5.0,
        help="Minutos de servicio por parada",
    )
    parser.add_argument(
        "--avg-speed-kmh",
        type=float,
        default=25.0,
        help="Velocidad promedio para estimar tiempos de viaje",
    )
    parser.add_argument(
        "--cost-per-km",
        type=float,
        default=1200.0,
        help="Costo transporte en $/km para KPI",
    )
    parser.add_argument(
        "--diesel-km-per-liter",
        type=float,
        default=6.5,
        help="Rendimiento diesel en km/L para KPI",
    )
    parser.add_argument(
        "--co2-kg-per-liter",
        type=float,
        default=2.68,
        help="Factor de emision CO2 en kg/L para KPI",
    )
    parser.add_argument(
        "--start-minute",
        type=float,
        default=540.0,
        help="Minuto de inicio del turno (540 = 09:00)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directorio donde se guardan resultados (casoBase_res)",
    )
    parser.add_argument(
        "--distance-mode",
        type=str,
        choices=["road", "haversine"],
        default="road",
        help="Modo de distancia: road=red vial real, haversine=aproximacion geodesica",
    )
    parser.add_argument(
        "--graph-path",
        type=Path,
        default=DEFAULT_GRAPH_PATH,
        help="Ruta al .graphml de la red vial de Santiago",
    )
    return parser.parse_args()


def clean_rut(rut: object) -> str:
    """Normaliza RUT para generar ids consistentes."""
    if pd.isna(rut):
        return ""
    return str(rut).replace(".", "").replace("-", "").strip().upper()


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia Haversine en kilometros."""
    r = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def format_minute(minute_value: float) -> str:
    """Convierte minutos absolutos a HH:MM (y D+N si cruza medianoche)."""
    total = int(round(minute_value))
    days = total // 1440
    minute_in_day = total % 1440
    hh = minute_in_day // 60
    mm = minute_in_day % 60
    if days > 0:
        return f"D+{days} {hh:02d}:{mm:02d}"
    return f"{hh:02d}:{mm:02d}"


def _to_lower_ascii_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza nombres de columnas para facilitar merges robustos."""
    df2 = df.copy()
    df2.columns = [str(c).strip().lower() for c in df2.columns]
    return df2


def prepare_orders_dataframe(orders_xlsx: Path, dispatch_csv: Path, day: str) -> pd.DataFrame:
    """
    Carga y fusiona pedidos desde:
    - vrp_orders.xlsx (cabecera comercial)
    - df_despacho.csv (coordenadas y dia de entrega)
    """
    df_orders_raw = pd.read_excel(orders_xlsx)
    df_dispatch_raw = pd.read_csv(dispatch_csv)

    df_orders = _to_lower_ascii_columns(df_orders_raw)
    df_dispatch = _to_lower_ascii_columns(df_dispatch_raw)

    # Normalizacion de columnas de df_orders para merge.
    rename_orders = {
        "número de orden": "id_pedido",
        "nombre cliente": "nombre_cliente",
        "dirección cliente": "direccion_cliente",
        "fecha de despacho solicitada": "fecha_despacho_solicitada",
        "peso_total_kg": "peso_total_kg_xlsx",
        "volumen_total_m3": "volumen_total_m3_xlsx",
        "direccion_ruteo": "direccion_ruteo_xlsx",
        "comuna": "comuna_xlsx",
    }
    for old, new in rename_orders.items():
        if old in df_orders.columns:
            df_orders = df_orders.rename(columns={old: new})

    # Normalizacion de columnas de df_dispatch.
    if "día" in df_dispatch.columns:
        df_dispatch = df_dispatch.rename(columns={"día": "dia"})
    if "dirección" in df_dispatch.columns:
        df_dispatch = df_dispatch.rename(columns={"dirección": "direccion_ruteo"})
    if "latitud" not in df_dispatch.columns and "latitud" in df_dispatch_raw.columns:
        df_dispatch["latitud"] = df_dispatch_raw["latitud"]
    if "longitud" not in df_dispatch.columns and "longitud" in df_dispatch_raw.columns:
        df_dispatch["longitud"] = df_dispatch_raw["longitud"]

    # Filtra por fecha elegida (formato yyyy-mm-dd).
    try:
        target_date = datetime.strptime(day, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(
            f"Formato invalido para --day: '{day}'. Usa yyyy-mm-dd (ejemplo: 2026-12-03)."
        ) from exc

    if "fecha_entrega" in df_dispatch.columns:
        parsed_dates = pd.to_datetime(df_dispatch["fecha_entrega"], errors="coerce").dt.date
        df_dispatch_day = df_dispatch[parsed_dates == target_date].copy()
    elif "dia" in df_dispatch.columns:
        # Fallback si no existe fecha_entrega: usa dia del mes.
        df_dispatch_day = df_dispatch[pd.to_numeric(df_dispatch["dia"], errors="coerce") == target_date.day].copy()
    else:
        raise ValueError("No existe columna 'fecha_entrega' ni 'dia' en df_despacho.csv para filtrar.")

    if df_dispatch_day.empty:
        raise ValueError(f"No hay pedidos para la fecha {target_date.isoformat()} en {dispatch_csv}.")

    # Merge por id_pedido (columna compartida esperada).
    if "id_pedido" not in df_orders.columns:
        raise ValueError("No se encontro columna 'id_pedido' (Numero de Orden) en vrp_orders.xlsx.")
    merged = df_dispatch_day.merge(df_orders, on="id_pedido", how="left", suffixes=("", "_orders"))

    # Asegura coordenadas y direccion.
    if "direccion_ruteo" not in merged.columns and "direccion_ruteo_xlsx" in merged.columns:
        merged["direccion_ruteo"] = merged["direccion_ruteo_xlsx"]
    if "direccion_ruteo" not in merged.columns:
        merged["direccion_ruteo"] = ""
    if "comuna" not in merged.columns and "comuna_xlsx" in merged.columns:
        merged["comuna"] = merged["comuna_xlsx"]
    if "comuna" not in merged.columns:
        merged["comuna"] = ""

    # Asegura columnas latitud/longitud con nombres consistentes.
    if "latitud" not in merged.columns:
        if "latitud_orders" in merged.columns:
            merged["latitud"] = merged["latitud_orders"]
        elif "latitud_x" in merged.columns:
            merged["latitud"] = merged["latitud_x"]
    if "longitud" not in merged.columns:
        if "longitud_orders" in merged.columns:
            merged["longitud"] = merged["longitud_orders"]
        elif "longitud_x" in merged.columns:
            merged["longitud"] = merged["longitud_x"]

    merged["latitud"] = pd.to_numeric(merged["latitud"], errors="coerce")
    merged["longitud"] = pd.to_numeric(merged["longitud"], errors="coerce")
    merged = merged.dropna(subset=["latitud", "longitud"]).copy()
    if merged.empty:
        raise ValueError("No quedaron pedidos con coordenadas validas tras la fusion.")

    # Ventanas forzadas a todo el dia, como se solicito.
    merged["a_ventana"] = 540
    merged["b_ventana"] = 1260

    # Construccion de id_nodo robusto.
    if "rut_clean" not in merged.columns:
        if "id_cliente" in merged.columns:
            merged["rut_clean"] = merged["id_cliente"].apply(clean_rut)
        else:
            merged["rut_clean"] = ""
    if "id_nodo" not in merged.columns:
        merged["id_nodo"] = merged["id_pedido"].astype(str).str.strip() + "_" + merged["rut_clean"].astype(str)
    else:
        merged["id_nodo"] = merged["id_nodo"].astype(str)

    # Conversiones de demanda con unidad nativa de trabajo:
    # - peso en gramos (g)
    # - volumen en centimetros cubicos (cm3)
    merged["peso_pedido"] = pd.to_numeric(merged.get("peso_pedido"), errors="coerce")
    merged["volumen_pedido"] = pd.to_numeric(merged.get("volumen_pedido"), errors="coerce")
    merged["peso_total_kg_xlsx"] = pd.to_numeric(merged.get("peso_total_kg_xlsx"), errors="coerce")
    merged["volumen_total_m3_xlsx"] = pd.to_numeric(merged.get("volumen_total_m3_xlsx"), errors="coerce")

    # En df_despacho el peso_pedido viene en gramos.
    # Fallback desde vrp_orders (kg -> g).
    merged["demand_g"] = merged["peso_pedido"].where(
        merged["peso_pedido"].notna(), merged["peso_total_kg_xlsx"] * 1000.0
    )
    # En df_despacho el volumen_pedido viene en cm3.
    # Fallback desde vrp_orders (m3 -> cm3).
    merged["demand_cm3"] = merged["volumen_pedido"].where(
        merged["volumen_pedido"].notna(), merged["volumen_total_m3_xlsx"] * 1_000_000.0
    )

    merged["demand_g"] = pd.to_numeric(merged["demand_g"], errors="coerce")
    merged["demand_cm3"] = pd.to_numeric(merged["demand_cm3"], errors="coerce")
    merged = merged.dropna(subset=["demand_g", "demand_cm3"]).copy()
    if merged.empty:
        raise ValueError("No quedaron pedidos con demanda valida (g y cm3).")

    # Columnas auxiliares solo para visualizacion/reporte humano.
    merged["demand_kg"] = merged["demand_g"] / 1000.0
    merged["demand_m3"] = merged["demand_cm3"] / 1_000_000.0

    return merged.reset_index(drop=True)


def resolve_depot_coordinates_exact(df_orders: pd.DataFrame, depot_address: str) -> DepotResolution:
    """
    Resuelve coordenadas del depot priorizando la direccion exacta entregada:
    1) Geocodifica la direccion de --depot-address.
    2) Si la geocodificacion falla, usa fallback al centroide de pedidos del dia.
    Las rutas de clientes NO usan clusterizacion.
    """
    geocoded_lat: Optional[float] = None
    geocoded_lon: Optional[float] = None

    try:
        geocoded_lat, geocoded_lon = geocode_depot(depot_address)
    except Exception:
        geocoded_lat = None
        geocoded_lon = None

    # Usa la direccion exacta geocodificada cuando este disponible.
    if geocoded_lat is not None and geocoded_lon is not None:
        return DepotResolution(
            geocoded_lat=geocoded_lat,
            geocoded_lon=geocoded_lon,
            final_lat=float(geocoded_lat),
            final_lon=float(geocoded_lon),
            method="geocoded_exact_address",
            num_clusters_dbscan=0,
        )

    # Fallback robusto si el geocoder no responde o no encuentra la direccion.
    return DepotResolution(
        geocoded_lat=None,
        geocoded_lon=None,
        final_lat=float(df_orders["latitud"].mean()),
        final_lon=float(df_orders["longitud"].mean()),
        method="fallback_orders_centroid_geocode_failed",
        num_clusters_dbscan=0,
    )


def build_road_distance_data(
    df_orders: pd.DataFrame,
    depot_lat: float,
    depot_lon: float,
    depot_node_id: str,
    graph_path: Path,
) -> Tuple[object, pd.DataFrame, Dict[str, Dict[str, object]]]:
    """
    Construye matriz de distancias viales reales entre todos los nodos del dia
    (clientes + depot) usando el pipeline del modulo grafo.

    Retorna:
    - grafo vial cargado
    - matriz de distancias en km (index/columns = id_nodo)
    - diccionario de rutas osmnx por tramo (origen->destino)
    """
    try:
        from grafo.network_builder import get_santiago_graph
        from grafo.routing import calculate_routing_for_day
    except Exception as exc:
        raise RuntimeError(
            "No se pudieron cargar modulos de red vial (osmnx/scipy/sklearn). "
            "Verifica que ejecutes con el Python del entorno capstone: "
            ".\\capstone\\Scripts\\python.exe"
        ) from exc

    graph = get_santiago_graph(filepath=str(graph_path), force_download=False)

    df_routing = df_orders[["id_nodo", "latitud", "longitud"]].copy()
    depot_row = pd.DataFrame(
        [{"id_nodo": depot_node_id, "latitud": depot_lat, "longitud": depot_lon}]
    )
    df_routing = pd.concat([df_routing, depot_row], ignore_index=True)

    matriz_m, info_rutas = calculate_routing_for_day(df_routing, graph)
    if matriz_m.empty:
        raise ValueError("No se pudo construir matriz vial de distancias (matriz vacia).")

    matriz_km = matriz_m / 1000.0
    return graph, matriz_km, info_rutas


def _lookup_distance_km(
    source_node_id: str,
    target_node_id: str,
    source_lat: float,
    source_lon: float,
    target_lat: float,
    target_lon: float,
    distance_mode: str,
    road_matrix_km: Optional[pd.DataFrame],
) -> float:
    """
    Busca distancia entre nodos:
    - road: usa matriz vial si existe valor finito.
    - fallback: haversine.
    """
    if distance_mode == "road" and road_matrix_km is not None:
        try:
            val = float(road_matrix_km.loc[source_node_id, target_node_id])
            if math.isfinite(val):
                return val
        except Exception:
            pass
    return haversine_km(source_lat, source_lon, target_lat, target_lon)


def build_single_nn_route(
    pending_indices: set[int],
    df_orders: pd.DataFrame,
    depot_lat: float,
    depot_lon: float,
    depot_node_id: str,
    truck_capacity_g: float,
    truck_capacity_cm3: float,
    distance_mode: str,
    road_matrix_km: Optional[pd.DataFrame],
) -> Tuple[List[int], float, float, float]:
    """
    Construye una ruta NN (depot -> clientes -> depot) para UN viaje/tour.
    Retorna:
    - lista de indices de pedidos atendidos en la ruta
    - distancia total de la ruta
    - carga total usada en gramos
    - carga total usada en centimetros cubicos
    """
    current_lat = depot_lat
    current_lon = depot_lon
    current_node_id = depot_node_id
    remaining_g = truck_capacity_g
    remaining_cm3 = truck_capacity_cm3
    local_available = set(pending_indices)

    chosen: List[int] = []
    route_distance = 0.0
    load_used_g = 0.0
    load_used_cm3 = 0.0

    while True:
        feasible = []
        for idx in local_available:
            row = df_orders.loc[idx]
            demand_g = float(row["demand_g"])
            demand_cm3 = float(row["demand_cm3"])
            if demand_g <= remaining_g + 1e-9 and demand_cm3 <= remaining_cm3 + 1e-9:
                feasible.append(idx)

        if not feasible:
            break

        # NN: selecciona el pedido factible mas cercano al nodo actual.
        best_idx = None
        best_dist = float("inf")
        for idx in feasible:
            row = df_orders.loc[idx]
            candidate_node_id = str(row["id_nodo"])
            dist = _lookup_distance_km(
                source_node_id=current_node_id,
                target_node_id=candidate_node_id,
                source_lat=current_lat,
                source_lon=current_lon,
                target_lat=float(row["latitud"]),
                target_lon=float(row["longitud"]),
                distance_mode=distance_mode,
                road_matrix_km=road_matrix_km,
            )
            if dist < best_dist:
                best_dist = dist
                best_idx = idx

        row = df_orders.loc[best_idx]
        demand_g = float(row["demand_g"])
        demand_cm3 = float(row["demand_cm3"])

        chosen.append(best_idx)
        route_distance += best_dist
        load_used_g += demand_g
        load_used_cm3 += demand_cm3
        remaining_g -= demand_g
        remaining_cm3 -= demand_cm3
        local_available.remove(best_idx)
        current_lat = float(row["latitud"])
        current_lon = float(row["longitud"])
        current_node_id = str(row["id_nodo"])

    # Cierra la ruta volviendo al depot si hubo al menos una parada.
    if chosen:
        route_distance += _lookup_distance_km(
            source_node_id=current_node_id,
            target_node_id=depot_node_id,
            source_lat=current_lat,
            source_lon=current_lon,
            target_lat=depot_lat,
            target_lon=depot_lon,
            distance_mode=distance_mode,
            road_matrix_km=road_matrix_km,
        )

    return chosen, route_distance, load_used_g, load_used_cm3


def build_routes_round_robin(
    df_orders: pd.DataFrame,
    depot_lat: float,
    depot_lon: float,
    depot_node_id: str,
    truck_capacity_g: float,
    truck_capacity_cm3: float,
    num_trucks: int,
    start_minute: float,
    service_minutes: float,
    avg_speed_kmh: float,
    distance_mode: str,
    road_matrix_km: Optional[pd.DataFrame],
) -> Tuple[Dict[int, List[TruckRoute]], pd.DataFrame]:
    """
    Planifica rutas por rondas (round-robin) sobre camiones fisicos.
    Cada camion puede tener multiples rutas/tours durante el turno unico.
    """
    if num_trucks < 1:
        raise ValueError("num_trucks debe ser >= 1")
    if truck_capacity_g <= 0:
        raise ValueError("truck_capacity_g debe ser > 0")
    if truck_capacity_cm3 <= 0:
        raise ValueError("truck_capacity_cm3 debe ser > 0")
    if avg_speed_kmh <= 0:
        raise ValueError("avg_speed_kmh debe ser > 0")

    pending_indices = set(df_orders.index.tolist())
    unassigned_records = []

    # Marca pedidos imposibles por capacidad individual.
    impossible = []
    for idx in list(pending_indices):
        row = df_orders.loc[idx]
        demand_g = float(row["demand_g"])
        demand_cm3 = float(row["demand_cm3"])
        if demand_g > truck_capacity_g + 1e-9 or demand_cm3 > truck_capacity_cm3 + 1e-9:
            impossible.append(idx)
    for idx in impossible:
        row = df_orders.loc[idx]
        unassigned_records.append(
            {
                "id_pedido": row["id_pedido"],
                "id_nodo": row["id_nodo"],
                "reason": (
                    f"Demanda supera capacidad: "
                    f"{float(row['demand_g']):.0f} g vs {truck_capacity_g:.0f} g, "
                    f"{float(row['demand_cm3']):.0f} cm3 vs {truck_capacity_cm3:.0f} cm3"
                ),
            }
        )
        pending_indices.remove(idx)

    truck_routes: Dict[int, List[TruckRoute]] = {t: [] for t in range(1, num_trucks + 1)}
    truck_current_time: Dict[int, float] = {t: start_minute for t in range(1, num_trucks + 1)}
    truck_next_route_id: Dict[int, int] = {t: 1 for t in range(1, num_trucks + 1)}

    rr_truck = 1
    while pending_indices:
        truck_id = rr_truck
        rr_truck = (rr_truck % num_trucks) + 1

        chosen, route_distance, load_used_g, load_used_cm3 = build_single_nn_route(
            pending_indices=pending_indices,
            df_orders=df_orders,
            depot_lat=depot_lat,
            depot_lon=depot_lon,
            depot_node_id=depot_node_id,
            truck_capacity_g=truck_capacity_g,
            truck_capacity_cm3=truck_capacity_cm3,
            distance_mode=distance_mode,
            road_matrix_km=road_matrix_km,
        )

        # Si no pudo construir ruta con pendientes existentes, rompe para evitar loop infinito.
        if not chosen:
            break

        # Construye detalle temporal de paradas.
        start_time = truck_current_time[truck_id]
        current_time = start_time
        current_lat = depot_lat
        current_lon = depot_lon
        current_node_id = depot_node_id
        stops: List[RouteStop] = []
        for stop_num, idx in enumerate(chosen, start=1):
            row = df_orders.loc[idx]
            dist_km = _lookup_distance_km(
                source_node_id=current_node_id,
                target_node_id=str(row["id_nodo"]),
                source_lat=current_lat,
                source_lon=current_lon,
                target_lat=float(row["latitud"]),
                target_lon=float(row["longitud"]),
                distance_mode=distance_mode,
                road_matrix_km=road_matrix_km,
            )
            travel_min = (dist_km / avg_speed_kmh) * 60.0
            arrival = current_time + travel_min
            service_start = arrival
            service_end = service_start + service_minutes

            stop = RouteStop(
                stop_number=stop_num,
                order_id=str(row["id_pedido"]),
                node_id=str(row["id_nodo"]),
                address=str(row.get("direccion_ruteo", "")),
                comuna=str(row.get("comuna", "")),
                lat=float(row["latitud"]),
                lon=float(row["longitud"]),
                demand_g=float(row["demand_g"]),
                demand_cm3=float(row["demand_cm3"]),
                distance_from_previous_km=dist_km,
                arrival_min=arrival,
                service_start_min=service_start,
                service_end_min=service_end,
                status="Entregado",
            )
            stops.append(stop)

            current_time = service_end
            current_lat = float(row["latitud"])
            current_lon = float(row["longitud"])
            current_node_id = str(row["id_nodo"])

        # Regreso al depot.
        back_km = (
            _lookup_distance_km(
                source_node_id=current_node_id,
                target_node_id=depot_node_id,
                source_lat=current_lat,
                source_lon=current_lon,
                target_lat=depot_lat,
                target_lon=depot_lon,
                distance_mode=distance_mode,
                road_matrix_km=road_matrix_km,
            )
            if stops
            else 0.0
        )
        back_min = (back_km / avg_speed_kmh) * 60.0
        end_time = current_time + back_min

        route = TruckRoute(
            truck_id=truck_id,
            route_id=truck_next_route_id[truck_id],
            start_min=start_time,
            end_min=end_time,
            distance_km=route_distance,
            load_used_g=load_used_g,
            load_used_cm3=load_used_cm3,
            stops=stops,
        )
        truck_routes[truck_id].append(route)
        truck_next_route_id[truck_id] += 1
        truck_current_time[truck_id] = end_time

        for idx in chosen:
            pending_indices.remove(idx)

    # Si quedaron pendientes tras intentar rutear, registrar como no asignados.
    for idx in sorted(pending_indices):
        row = df_orders.loc[idx]
        unassigned_records.append(
            {
                "id_pedido": row["id_pedido"],
                "id_nodo": row["id_nodo"],
                "reason": "No asignado por saturacion de secuencia heuristica en la configuracion actual.",
            }
        )

    unassigned_df = pd.DataFrame(unassigned_records)
    return truck_routes, unassigned_df


def _safe_pct(numerator: float, denominator: float) -> Optional[float]:
    """Retorna porcentaje o None si el denominador es cero."""
    if denominator <= 0:
        return None
    return (numerator / denominator) * 100.0


def _avg(values: List[float]) -> Optional[float]:
    """Promedio simple o None si la lista esta vacia."""
    if not values:
        return None
    return sum(values) / len(values)


def _format_kpi_value(value: Optional[float], decimals: int = 2) -> str:
    """Formatea valor KPI; deja celda en blanco si no existe dato."""
    if value is None:
        return ""
    return f"{value:.{decimals}f}"


def compute_kpis(
    truck_routes: Dict[int, List[TruckRoute]],
    unassigned_df: pd.DataFrame,
    num_trucks: int,
    truck_capacity_g: float,
    truck_capacity_cm3: float,
    compute_minutes: float,
    cost_per_km: float,
    diesel_km_per_liter: float,
    co2_kg_per_liter: float,
) -> List[Tuple[str, str]]:
    """
    Calcula KPIs para el reporte.
    Factores aplicados por hiperparametro:
    - costo transporte: cost_per_km ($/km)
    - rendimiento diesel: diesel_km_per_liter (km/L)
    - emisiones: co2_kg_per_liter (kgCO2/L)
    """
    all_routes = [route for routes in truck_routes.values() for route in routes]
    all_stops = [stop for route in all_routes for stop in route.stops]

    delivered_qty = len(all_stops)
    backlog_qty = int(len(unassigned_df))
    requested_qty = delivered_qty + backlog_qty

    total_distance_km = sum(route.distance_km for route in all_routes)
    distance_relative = (total_distance_km / delivered_qty) if delivered_qty > 0 else None
    transport_cost = total_distance_km * cost_per_km
    liters_estimated = (total_distance_km / diesel_km_per_liter) if diesel_km_per_liter > 0 else None
    co2_per_km = (
        co2_kg_per_liter / diesel_km_per_liter
        if diesel_km_per_liter > 0
        else None
    )
    co2_total_kg = (total_distance_km * co2_per_km) if co2_per_km is not None else None
    co2_per_order_kg = (co2_total_kg / delivered_qty) if (co2_total_kg is not None and delivered_qty > 0) else None

    used_vehicles = sum(1 for routes in truck_routes.values() if len(routes) > 0)
    idle_vehicles = max(num_trucks - used_vehicles, 0)
    fleet_capacity_fixed = float(num_trucks)

    total_route_hours = sum(max(route.end_min - route.start_min, 0.0) for route in all_routes) / 60.0

    # Con ventana global [540,1260] y sin enforcement, la espera se considera 0.
    total_wait_min = 0.0
    total_wait_accum_min = 0.0

    tardiness_values = [max(0.0, stop.arrival_min - 1260.0) for stop in all_stops]
    on_time_count = sum(1 for t in tardiness_values if t <= 1e-9)
    on_time_pct = _safe_pct(on_time_count, delivered_qty) if delivered_qty > 0 else None
    tardy_only = [t for t in tardiness_values if t > 1e-9]
    avg_tardiness_min = _avg(tardy_only) if tardy_only else 0.0

    backlog_pct = _safe_pct(backlog_qty, requested_qty) if requested_qty > 0 else None

    util_peso_by_route = [
        _safe_pct(route.load_used_g, truck_capacity_g) for route in all_routes if truck_capacity_g > 0
    ]
    util_vol_by_route = [
        _safe_pct(route.load_used_cm3, truck_capacity_cm3) for route in all_routes if truck_capacity_cm3 > 0
    ]
    util_peso_by_route = [v for v in util_peso_by_route if v is not None]
    util_vol_by_route = [v for v in util_vol_by_route if v is not None]

    util_peso_pct = _avg(util_peso_by_route)
    util_vol_pct = _avg(util_vol_by_route)
    util_avg_capacity_pct = _avg(
        [(p + v) / 2.0 for p, v in zip(util_peso_by_route, util_vol_by_route)]
    )
    vacancia_pct = (100.0 - util_avg_capacity_pct) if util_avg_capacity_pct is not None else None

    route_loads_kg = [route.load_used_g / 1000.0 for route in all_routes]
    if route_loads_kg:
        mean_load_kg = sum(route_loads_kg) / len(route_loads_kg)
        mean_abs_dev_load_kg = sum(abs(v - mean_load_kg) for v in route_loads_kg) / len(route_loads_kg)
    else:
        mean_abs_dev_load_kg = None

    # KPI list (ordenado para parecerse al formato solicitado).
    return [
        ("Funcion Objetivo Total ($)", _format_kpi_value(transport_cost, 2)),
        ("Costos de Ruta por Transporte ($)", _format_kpi_value(transport_cost, 2)),
        ("Costos Fijos por Uso de Flota ($)", ""),
        ("Valor de Penalizacion por Espera ($)", ""),
        ("Tiempo de Espera Total (min)", _format_kpi_value(total_wait_min, 1)),
        ("Distancia Total Recorrida (km)", _format_kpi_value(total_distance_km, 2)),
        ("Distancia Relativa (km/pedido)", _format_kpi_value(distance_relative, 2)),
        ("Vehiculos Utilizados", _format_kpi_value(float(used_vehicles), 1)),
        ("Vehiculos en Desuso", _format_kpi_value(float(idle_vehicles), 1)),
        ("Capacidad Flota Fija", _format_kpi_value(fleet_capacity_fixed, 1)),
        ("Tiempo Total en Ruta (horas)", _format_kpi_value(total_route_hours, 2)),
        ("% Entregas a Tiempo", _format_kpi_value(on_time_pct, 1)),
        ("Tardanza Promedio (min)", _format_kpi_value(avg_tardiness_min, 1)),
        ("% Pedidos No Atendidos (Backlog)", _format_kpi_value(backlog_pct, 1)),
        ("Pedidos No Atendidos (qty)", _format_kpi_value(float(backlog_qty), 1)),
        ("% Utilizacion Promedio Capacidad Vehiculos", _format_kpi_value(util_avg_capacity_pct, 1)),
        ("% Utilizacion Volumen", _format_kpi_value(util_vol_pct, 1)),
        ("% Utilizacion Peso", _format_kpi_value(util_peso_pct, 1)),
        ("Desviacion Media de Carga (kg)", _format_kpi_value(mean_abs_dev_load_kg, 1)),
        ("Tasa de Desocupacion (%)", _format_kpi_value(vacancia_pct, 1)),
        ("Espera Total Acumulada (min)", _format_kpi_value(total_wait_accum_min, 1)),
        ("Emisiones CO2 Totales (kg)", _format_kpi_value(co2_total_kg, 2)),
        ("Emisiones CO2 por Pedido (kg)", _format_kpi_value(co2_per_order_kg, 3)),
        ("Litros Diesel Estimados", _format_kpi_value(liters_estimated, 2)),
        ("Tiempo de Computo (min)", _format_kpi_value(compute_minutes, 2)),
    ]


def write_routes_markdown(
    output_path: Path,
    truck_routes: Dict[int, List[TruckRoute]],
    unassigned_df: pd.DataFrame,
    run_config: Dict[str, object],
    depot_info: DepotResolution,
    kpis: List[Tuple[str, str]],
) -> None:
    """Genera reporte markdown estilo operativo (similar a resultados/rutas)."""
    total_routes = sum(len(v) for v in truck_routes.values())
    total_stops = sum(len(route.stops) for routes in truck_routes.values() for route in routes)
    total_distance = sum(route.distance_km for routes in truck_routes.values() for route in routes)

    lines: List[str] = []
    lines.append(f"# Reporte Heuristica TSP Caso Base - {run_config['run_label']}")
    lines.append("")
    lines.append("## Parametros de Ejecucion")
    lines.append("| Parametro | Valor |")
    lines.append("| :--- | :--- |")
    lines.append(f"| Depot address | {run_config['depot_address']} |")
    lines.append(f"| Depot final (lat, lon) | ({depot_info.final_lat:.6f}, {depot_info.final_lon:.6f}) |")
    lines.append(f"| Metodo depot | {depot_info.method} |")
    lines.append("| Clusters DBSCAN usados para depot | 0 (desactivado) |")
    lines.append(f"| Fecha seleccionada | {run_config['day']} |")
    lines.append(f"| Modo distancia | {run_config['distance_mode']} |")
    lines.append(f"| Capacidad peso camion | {run_config['truck_capacity_g']:.0f} g |")
    lines.append(f"| Capacidad volumen camion | {run_config['truck_capacity_cm3']:.0f} cm3 |")
    lines.append(f"| Cantidad camiones | {run_config['num_trucks']} |")
    lines.append(f"| Velocidad promedio | {run_config['avg_speed_kmh']} km/h |")
    lines.append(f"| Costo transporte KPI | {run_config['cost_per_km']} $/km |")
    lines.append(f"| Rendimiento diesel KPI | {run_config['diesel_km_per_liter']} km/L |")
    lines.append(f"| Factor CO2 KPI | {run_config['co2_kg_per_liter']} kg/L |")
    lines.append(f"| Inicio turno | {format_minute(float(run_config['start_minute']))} |")
    lines.append("| Ventana operativa usada | [540, 1260] para todos los pedidos |")
    lines.append("| Regla turno | Turno unico: cada camion sigue con nuevas rutas hasta intentar todos los pedidos del dia |")
    lines.append("")

    lines.append("## Resumen Global")
    lines.append("| Metrica | Valor |")
    lines.append("| :--- | :--- |")
    lines.append(f"| Rutas totales | {total_routes} |")
    lines.append(f"| Paradas entregadas | {total_stops} |")
    lines.append(f"| Distancia total | {total_distance:.2f} km |")
    lines.append(f"| Pedidos no asignados | {len(unassigned_df)} |")
    lines.append("")

    lines.append("## KPIs")
    lines.append("| KPI | Valor |")
    lines.append("| :--- | :--- |")
    for kpi_name, kpi_value in kpis:
        lines.append(f"| {kpi_name} | {kpi_value} |")
    lines.append("")

    lines.append("## Desglose por Camion")
    lines.append(
        "| Camion | Rutas | Paradas | Distancia (km) | Carga total (g) | Carga total (cm3) | Inicio | Fin |"
    )
    lines.append("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    for truck_id, routes in truck_routes.items():
        total_paradas = sum(len(r.stops) for r in routes)
        dist = sum(r.distance_km for r in routes)
        load_g = sum(r.load_used_g for r in routes)
        load_cm3 = sum(r.load_used_cm3 for r in routes)
        if routes:
            start = min(r.start_min for r in routes)
            end = max(r.end_min for r in routes)
            start_txt = format_minute(start)
            end_txt = format_minute(end)
        else:
            start_txt = "-"
            end_txt = "-"
        lines.append(
            f"| {truck_id} | {len(routes)} | {total_paradas} | {dist:.2f} | "
            f"{load_g:.0f} | {load_cm3:.0f} | {start_txt} | {end_txt} |"
        )
    lines.append("")

    # Detalle ruta por ruta
    for truck_id, routes in truck_routes.items():
        lines.append(f"## Camion {truck_id}")
        lines.append("")
        if not routes:
            lines.append("- Sin rutas asignadas.")
            lines.append("")
            continue

        for route in routes:
            lines.append(f"### Ruta {route.route_id} (Camion {truck_id})")
            lines.append("| Metrica | Valor |")
            lines.append("| :--- | :--- |")
            lines.append(f"| Inicio | {format_minute(route.start_min)} |")
            lines.append(f"| Llegada a Depot | {format_minute(route.end_min)} |")
            lines.append(f"| Fin | {format_minute(route.end_min)} |")
            lines.append(f"| Distancia | {route.distance_km:.2f} km |")
            lines.append(f"| Carga acumulada (g) | {route.load_used_g:.0f} |")
            lines.append(f"| Carga acumulada (cm3) | {route.load_used_cm3:.0f} |")
            lines.append(f"| Carga acumulada (kg) | {route.load_used_g / 1000.0:.2f} |")
            lines.append(f"| Carga acumulada (m3) | {route.load_used_cm3 / 1_000_000.0:.4f} |")
            lines.append("")

            lines.append(
                "| # | Nodo | Pedido | Dist. desde previo (km) | Llegada | Inicio Serv. | Fin Serv. | "
                "Demanda (g) | Demanda (cm3) | Demanda (kg) | Demanda (m3) | Comuna | Estado |"
            )
            lines.append(
                "| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: |"
            )
            for stop in route.stops:
                lines.append(
                    f"| {stop.stop_number} | {stop.node_id} | {stop.order_id} | "
                    f"{stop.distance_from_previous_km:.2f} | {format_minute(stop.arrival_min)} | "
                    f"{format_minute(stop.service_start_min)} | {format_minute(stop.service_end_min)} | "
                    f"{stop.demand_g:.0f} | {stop.demand_cm3:.0f} | {stop.demand_g / 1000.0:.2f} | {stop.demand_cm3 / 1_000_000.0:.4f} | "
                    f"{stop.comuna} | {stop.status} |"
                )
            lines.append("")

    if not unassigned_df.empty:
        lines.append("## Pedidos No Asignados / No Entregados")
        lines.append("| Pedido | Nodo | Motivo |")
        lines.append("| :--- | :--- | :--- |")
        for _, row in unassigned_df.iterrows():
            lines.append(f"| {row['id_pedido']} | {row['id_nodo']} | {row['reason']} |")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_routes_csv(output_path: Path, truck_routes: Dict[int, List[TruckRoute]]) -> None:
    """Exporta detalle tabular de paradas para analisis rapido en Excel."""
    fieldnames = [
        "truck_id",
        "route_id",
        "stop_number",
        "node_id",
        "order_id",
        "address",
        "comuna",
        "lat",
        "lon",
        "distance_from_previous_km",
        "arrival",
        "service_start",
        "service_end",
        "demand_g",
        "demand_cm3",
        "demand_kg",
        "demand_m3",
        "status",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for truck_id, routes in truck_routes.items():
            for route in routes:
                for stop in route.stops:
                    writer.writerow(
                        {
                            "truck_id": truck_id,
                            "route_id": route.route_id,
                            "stop_number": stop.stop_number,
                            "node_id": stop.node_id,
                            "order_id": stop.order_id,
                            "address": stop.address,
                            "comuna": stop.comuna,
                            "lat": stop.lat,
                            "lon": stop.lon,
                            "distance_from_previous_km": f"{stop.distance_from_previous_km:.4f}",
                            "arrival": format_minute(stop.arrival_min),
                            "service_start": format_minute(stop.service_start_min),
                            "service_end": format_minute(stop.service_end_min),
                            "demand_g": f"{stop.demand_g:.0f}",
                            "demand_cm3": f"{stop.demand_cm3:.0f}",
                            "demand_kg": f"{stop.demand_g / 1000.0:.6f}",
                            "demand_m3": f"{stop.demand_cm3 / 1_000_000.0:.6f}",
                            "status": stop.status,
                        }
                    )


def write_unassigned_csv(output_path: Path, unassigned_df: pd.DataFrame) -> None:
    """Exporta pedidos no asignados/no entregados."""
    if unassigned_df.empty:
        pd.DataFrame(columns=["id_pedido", "id_nodo", "reason"]).to_csv(output_path, index=False)
    else:
        unassigned_df.to_csv(output_path, index=False)


def write_interactive_map(
    output_path: Path,
    truck_routes: Dict[int, List[TruckRoute]],
    depot_lat: float,
    depot_lon: float,
    depot_node_id: str,
    distance_mode: str,
    road_graph: Optional[object],
    road_info_rutas: Optional[Dict[str, Dict[str, object]]],
) -> None:
    """Genera mapa HTML interactivo con rutas por camion (folium + layers)."""
    m = folium.Map(location=[depot_lat, depot_lon], zoom_start=11, tiles="CartoDB positron")

    # Resumen de llegadas al depot para mostrarlo en el popup principal del depot.
    depot_arrivals: List[Tuple[float, int, int]] = []
    for truck_id, routes in truck_routes.items():
        for route in routes:
            depot_arrivals.append((route.end_min, truck_id, route.route_id))
    depot_arrivals.sort(key=lambda x: x[0])

    if depot_arrivals:
        arrivals_html = "<br>".join(
            [
                f"Camion {truck_id} - Ruta {route_id}: {format_minute(arrival_min)}"
                for arrival_min, truck_id, route_id in depot_arrivals
            ]
        )
    else:
        arrivals_html = "Sin retornos registrados"

    depot_popup = (
        "Depot<br>"
        f"Lat/Lon: ({depot_lat:.6f}, {depot_lon:.6f})<br>"
        "<b>Llegadas al depot:</b><br>"
        f"{arrivals_html}"
    )

    folium.Marker(
        location=[depot_lat, depot_lon],
        tooltip="Depot (ver llegadas)",
        popup=folium.Popup(depot_popup, max_width=420),
        icon=folium.Icon(color="black", icon="home", prefix="fa"),
    ).add_to(m)

    colors = [
        "red",
        "blue",
        "green",
        "purple",
        "orange",
        "darkred",
        "cadetblue",
        "darkpurple",
        "pink",
        "black",
    ]

    for truck_id, routes in truck_routes.items():
        color = colors[(truck_id - 1) % len(colors)]
        fg = folium.FeatureGroup(name=f"Camion {truck_id}", show=True)
        # Numeracion global de visitas por camion (1, 2, 3, ...), incluso si el camion tiene varias rutas.
        truck_visit_order = 0

        for route in routes:
            sequence_ids = [depot_node_id] + [s.node_id for s in route.stops] + [depot_node_id]
            fallback_coords = [(depot_lat, depot_lon)] + [(s.lat, s.lon) for s in route.stops] + [(depot_lat, depot_lon)]

            for seg_idx, (orig_id, dest_id) in enumerate(zip(sequence_ids[:-1], sequence_ids[1:])):
                drew_real_segment = False
                if distance_mode == "road" and road_graph is not None and road_info_rutas is not None:
                    key = f"{orig_id}->{dest_id}"
                    info = road_info_rutas.get(key)
                    if info is not None:
                        osmnx_path = info.get("ruta_nodos_osmnx", [])
                        if isinstance(osmnx_path, list) and len(osmnx_path) > 1:
                            seg_coords = []
                            for u, v in zip(osmnx_path[:-1], osmnx_path[1:]):
                                edge_data = road_graph.get_edge_data(u, v)
                                if edge_data and 0 in edge_data and "geometry" in edge_data[0]:
                                    for x, y in edge_data[0]["geometry"].coords:
                                        seg_coords.append((y, x))
                                else:
                                    if not seg_coords:
                                        seg_coords.append((road_graph.nodes[u]["y"], road_graph.nodes[u]["x"]))
                                    seg_coords.append((road_graph.nodes[v]["y"], road_graph.nodes[v]["x"]))
                            if seg_coords:
                                folium.PolyLine(
                                    locations=seg_coords,
                                    color=color,
                                    weight=4,
                                    opacity=0.85,
                                    tooltip=f"Camion {truck_id} - Ruta {route.route_id}",
                                ).add_to(fg)
                                drew_real_segment = True

                if not drew_real_segment:
                    seg_line = [fallback_coords[seg_idx], fallback_coords[seg_idx + 1]]
                    folium.PolyLine(
                        locations=seg_line,
                        color=color,
                        weight=4,
                        opacity=0.65,
                        dash_array="8",
                        tooltip=f"Camion {truck_id} - Ruta {route.route_id} (fallback)",
                    ).add_to(fg)

            for stop in route.stops:
                truck_visit_order += 1
                arrival_label = format_minute(stop.arrival_min)
                popup = (
                    f"Camion {truck_id} | Ruta {route.route_id}<br>"
                    f"Parada {stop.stop_number}<br>"
                    f"Orden visita camion: {truck_visit_order}<br>"
                    f"Pedido: {stop.order_id}<br>"
                    f"Nodo: {stop.node_id}<br>"
                    f"Comuna: {stop.comuna}<br>"
                    f"Demanda g: {stop.demand_g:.0f}<br>"
                    f"Demanda cm3: {stop.demand_cm3:.0f}<br>"
                    f"Demanda kg: {stop.demand_g / 1000.0:.2f}<br>"
                    f"Demanda m3: {stop.demand_cm3 / 1_000_000.0:.4f}<br>"
                    f"Llegada: {arrival_label}"
                )
                folium.CircleMarker(
                    location=(stop.lat, stop.lon),
                    radius=6,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.9,
                    popup=folium.Popup(popup, max_width=350),
                    tooltip=f"C{truck_id}-V{truck_visit_order} | Llegada {arrival_label}",
                ).add_to(fg)

                # Etiqueta visible con el numero de visita del camion.
                folium.Marker(
                    location=(stop.lat, stop.lon),
                    icon=folium.DivIcon(
                        html=(
                            f'<div style="font-size:10px;font-weight:bold;color:white;'
                            f'background:{color};border-radius:10px;padding:1px 4px;'
                            f'border:1px solid white;">{truck_visit_order}</div>'
                        ),
                        icon_size=(18, 18),
                        icon_anchor=(9, 9),
                    ),
                    popup=folium.Popup(
                        f"Camion {truck_id} - Visita {truck_visit_order}<br>Llegada: {arrival_label}",
                        max_width=300,
                    ),
                    tooltip=f"Camion {truck_id} - Visita {truck_visit_order} - Llegada {arrival_label}",
                ).add_to(fg)

        fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    m.save(str(output_path))


def write_summary_readme(
    output_dir: Path,
    run_label: str,
    run_config: Dict[str, object],
    depot_info: DepotResolution,
    truck_routes: Dict[int, List[TruckRoute]],
    unassigned_df: pd.DataFrame,
) -> None:
    """README de la carpeta de resultados generados."""
    total_routes = sum(len(v) for v in truck_routes.values())
    total_stops = sum(len(r.stops) for v in truck_routes.values() for r in v)
    total_distance = sum(r.distance_km for v in truck_routes.values() for r in v)

    lines: List[str] = []
    lines.append("# casoBase_res - Resultados Heuristica TSP Caso Base")
    lines.append("")
    lines.append("Este directorio contiene salidas generadas desde:")
    lines.append("")
    lines.append("- `casoBase/run_caso_base_tsp.py`")
    lines.append("")
    lines.append("## Ejecucion registrada")
    lines.append("")
    lines.append(f"- Run label: `{run_label}`")
    lines.append(f"- Fecha: `{run_config['day']}`")
    lines.append(f"- Depot address: `{run_config['depot_address']}`")
    lines.append(f"- Depot final: `({depot_info.final_lat:.6f}, {depot_info.final_lon:.6f})`")
    lines.append(f"- Metodo depot: `{depot_info.method}`")
    lines.append(f"- Modo distancia: `{run_config['distance_mode']}`")
    lines.append(f"- Capacidad camion (g): `{run_config['truck_capacity_g']:.0f}`")
    lines.append(f"- Capacidad camion (cm3): `{run_config['truck_capacity_cm3']:.0f}`")
    lines.append(f"- Velocidad promedio: `{run_config['avg_speed_kmh']}` km/h")
    lines.append(f"- Costo transporte KPI: `{run_config['cost_per_km']}` $/km")
    lines.append(f"- Rendimiento diesel KPI: `{run_config['diesel_km_per_liter']}` km/L")
    lines.append(f"- Factor CO2 KPI: `{run_config['co2_kg_per_liter']}` kg/L")
    lines.append(f"- N camiones: `{run_config['num_trucks']}`")
    lines.append("")
    lines.append("## Artefactos")
    lines.append("")
    lines.append(f"- `mapa_rutas_tsp_{run_label}.html`: mapa interactivo por camion.")
    lines.append(f"- `rutas_tsp_{run_label}.md`: resumen y detalle de paradas por camion/ruta.")
    lines.append(f"- `paradas_tsp_{run_label}.csv`: detalle tabular de cada parada.")
    lines.append(f"- `no_asignados_tsp_{run_label}.csv`: pedidos no asignados/no entregados.")
    lines.append("")
    lines.append("## Resumen")
    lines.append("")
    lines.append(f"- Rutas totales: `{total_routes}`")
    lines.append(f"- Paradas entregadas: `{total_stops}`")
    lines.append(f"- Distancia total: `{total_distance:.2f} km`")
    lines.append(f"- Pedidos no asignados: `{len(unassigned_df)}`")
    lines.append("")
    lines.append("## Nota metodologica")
    lines.append("")
    lines.append("No se aplico clusterizacion para asignar clientes a rutas.")
    lines.append("No se aplico DBSCAN para ajustar el depot: se usa la geocodificacion exacta de --depot-address.")
    lines.append("El mapa HTML muestra la numeracion de visita por camion en cada parada.")
    lines.append("El popup del depot incluye la hora de llegada por camion/ruta.")
    lines.append("El markdown de rutas incluye KPIs calculados para costo de transporte, diesel y emisiones.")
    lines.append("Costos fijos y penalizacion por espera quedan en blanco hasta definir su regla.")
    lines.append(
        "KPI actuales: "
        f"costo transporte={run_config['cost_per_km']} $/km, "
        f"rendimiento={run_config['diesel_km_per_liter']} km/L, "
        f"factor emisiones={run_config['co2_kg_per_liter']} kgCO2/L."
    )
    if run_config["distance_mode"] == "road":
        lines.append("Las distancias de ruteo se calcularon sobre red vial real de Santiago.")
    else:
        lines.append("Las distancias de ruteo se calcularon con aproximacion Haversine.")

    (output_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Ejecucion principal del pipeline caso base TSP."""
    t0 = time.perf_counter()
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # 1) Cargar y preparar pedidos del dia.
    df_orders = prepare_orders_dataframe(args.orders_xlsx, args.dispatch_csv, args.day)

    # 2) Resolver coordenadas de depot usando geocodificacion exacta.
    depot_info = resolve_depot_coordinates_exact(df_orders, args.depot_address)

    # 3) Preparar contexto de distancias (viales reales o haversine).
    depot_node_id = "DEPOT_01_BASE"
    road_graph = None
    road_matrix_km = None
    road_info_rutas = None
    if args.distance_mode == "road":
        road_graph, road_matrix_km, road_info_rutas = build_road_distance_data(
            df_orders=df_orders,
            depot_lat=depot_info.final_lat,
            depot_lon=depot_info.final_lon,
            depot_node_id=depot_node_id,
            graph_path=args.graph_path,
        )

    # 4) Rutear sin ventanas (forzadas a jornada completa) y sin clusterizacion de clientes.
    truck_routes, unassigned_df = build_routes_round_robin(
        df_orders=df_orders,
        depot_lat=depot_info.final_lat,
        depot_lon=depot_info.final_lon,
        depot_node_id=depot_node_id,
        truck_capacity_g=args.truck_capacity_g,
        truck_capacity_cm3=args.truck_capacity_cm3,
        num_trucks=args.num_trucks,
        start_minute=args.start_minute,
        service_minutes=args.service_minutes,
        avg_speed_kmh=args.avg_speed_kmh,
        distance_mode=args.distance_mode,
        road_matrix_km=road_matrix_km,
    )

    # 5) Persistir salidas.
    run_label = args.day
    md_path = args.output_dir / f"rutas_tsp_{run_label}.md"
    csv_path = args.output_dir / f"paradas_tsp_{run_label}.csv"
    unassigned_path = args.output_dir / f"no_asignados_tsp_{run_label}.csv"
    map_path = args.output_dir / f"mapa_rutas_tsp_{run_label}.html"

    run_config = {
        "run_label": run_label,
        "day": args.day,
        "depot_address": args.depot_address,
        "distance_mode": args.distance_mode,
        "truck_capacity_g": args.truck_capacity_g,
        "truck_capacity_cm3": args.truck_capacity_cm3,
        "avg_speed_kmh": args.avg_speed_kmh,
        "cost_per_km": args.cost_per_km,
        "diesel_km_per_liter": args.diesel_km_per_liter,
        "co2_kg_per_liter": args.co2_kg_per_liter,
        "num_trucks": args.num_trucks,
        "start_minute": args.start_minute,
    }

    compute_minutes = (time.perf_counter() - t0) / 60.0
    kpis = compute_kpis(
        truck_routes=truck_routes,
        unassigned_df=unassigned_df,
        num_trucks=args.num_trucks,
        truck_capacity_g=args.truck_capacity_g,
        truck_capacity_cm3=args.truck_capacity_cm3,
        compute_minutes=compute_minutes,
        cost_per_km=args.cost_per_km,
        diesel_km_per_liter=args.diesel_km_per_liter,
        co2_kg_per_liter=args.co2_kg_per_liter,
    )

    write_routes_markdown(md_path, truck_routes, unassigned_df, run_config, depot_info, kpis)
    write_routes_csv(csv_path, truck_routes)
    write_unassigned_csv(unassigned_path, unassigned_df)
    write_interactive_map(
        map_path,
        truck_routes,
        depot_info.final_lat,
        depot_info.final_lon,
        depot_node_id=depot_node_id,
        distance_mode=args.distance_mode,
        road_graph=road_graph,
        road_info_rutas=road_info_rutas,
    )
    write_summary_readme(args.output_dir, run_label, run_config, depot_info, truck_routes, unassigned_df)

    total_routes = sum(len(v) for v in truck_routes.values())
    total_stops = sum(len(r.stops) for v in truck_routes.values() for r in v)
    print(f"Pedidos del dia procesados: {len(df_orders)}")
    print(f"Rutas construidas: {total_routes}")
    print(f"Paradas entregadas: {total_stops}")
    print(f"No asignados: {len(unassigned_df)}")
    print(f"Reporte markdown: {md_path}")
    print(f"Mapa HTML: {map_path}")


if __name__ == "__main__":
    main()
