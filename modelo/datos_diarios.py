from __future__ import annotations

import os
import unicodedata
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

try:
    # Ejecutando como paquete: python -m modelo.prueba
    from .bootstrap_runtime import bootstrap_local_pydeps
except ImportError:
    # Ejecutando como script: python modelo/datos_diarios.py
    from bootstrap_runtime import bootstrap_local_pydeps

_BOOTSTRAP_STATUS = bootstrap_local_pydeps(required_packages=("numpy", "pandas"))

try:
    import numpy as np
except ModuleNotFoundError as exc:
    if _BOOTSTRAP_STATUS == "invalid":
        raise ModuleNotFoundError(
            "No se pudo importar numpy. Se detecto `/.pydeps` incompleto y se deshabilito "
            "para evitar el error `numpy._core._multiarray_umath`. "
            "Usa un entorno virtual sano o reinstala dependencias en `.pydeps`."
        ) from exc
    raise

try:
    import pandas as pd
except ModuleNotFoundError as exc:
    if _BOOTSTRAP_STATUS == "invalid":
        raise ModuleNotFoundError(
            "No se pudo importar pandas. Se detecto `/.pydeps` incompleto y se deshabilito "
            "para evitar conflictos de dependencias. "
            "Usa un entorno virtual sano o reinstala dependencias en `.pydeps`."
        ) from exc
    raise

try:
    from .modelo_final import TDVRPTWData
except ImportError:
    from modelo_final import TDVRPTWData


@dataclass
class DailyProblemBundle:
    problem_data: TDVRPTWData
    selected_date: str
    daily_dispatch: pd.DataFrame
    distance_matrix_km: pd.DataFrame
    node_labels: Dict[int, str]
    distance_source: str


def _norm_col(name: str) -> str:
    txt = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode("ascii")
    return txt.lower().strip().replace(" ", "_")


def _normalize_identifier(value: object) -> str:
    if pd.isna(value):
        return ""
    txt = str(value).strip()
    try:
        as_float = float(txt)
        if np.isfinite(as_float) and as_float.is_integer():
            return str(int(as_float))
    except Exception:
        pass
    return txt


def _clean_rut(value: object) -> str:
    return _normalize_identifier(value).replace(".", "").replace("-", "").upper()


def _infer_is_house(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    txt = _norm_col(str(value))
    if "casa" in txt:
        return True
    if "apart" in txt or "depto" in txt or "depart" in txt:
        return False
    return False


def _standardize_dispatch_columns(df: pd.DataFrame) -> pd.DataFrame:
    candidates = {
        "id_pedido": ["id_pedido", "numero_de_orden", "numero_orden"],
        "id_cliente": ["id_cliente", "rut"],
        "tipo_vivienda": ["tipo_vivienda", "tipo_de_vivienda"],
        "direccion": ["direccion", "direccion_ruteo"],
        "comuna": ["comuna"],
        "latitud": ["latitud", "latitude"],
        "longitud": ["longitud", "longitude"],
        "fecha_entrega": ["fecha_entrega", "fecha_de_entrega", "fecha_despacho"],
        "dia": ["dia", "d_a", "dia_semana"],
        "a_ventana": ["a_ventana", "ventana_inicio", "a"],
        "b_ventana": ["b_ventana", "ventana_fin", "b"],
        "peso_pedido": ["peso_pedido", "peso_total_kg"],
        "volumen_pedido": ["volumen_pedido", "volumen_total_m3", "volumen_total"],
    }

    norm_map = {_norm_col(c): c for c in df.columns}
    rename = {}
    for target, options in candidates.items():
        source = None
        for opt in options:
            if opt in norm_map:
                source = norm_map[opt]
                break
        if source is not None:
            rename[source] = target

    out = df.rename(columns=rename).copy()
    required = [
        "id_pedido",
        "id_cliente",
        "latitud",
        "longitud",
        "fecha_entrega",
        "a_ventana",
        "b_ventana",
        "peso_pedido",
        "volumen_pedido",
    ]
    missing = [c for c in required if c not in out.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas en despacho: {missing}")
    return out


def _prepare_daily_dispatch(
    csv_path: str,
    target_date: Optional[str] = None,
    max_orders: Optional[int] = None,
    seed: int = 42,
) -> tuple[pd.DataFrame, str]:
    df_raw = pd.read_csv(csv_path)
    df = _standardize_dispatch_columns(df_raw)

    df["fecha_entrega"] = pd.to_datetime(df["fecha_entrega"], errors="coerce").dt.date
    df["latitud"] = pd.to_numeric(df["latitud"], errors="coerce")
    df["longitud"] = pd.to_numeric(df["longitud"], errors="coerce")
    df["a_ventana"] = pd.to_numeric(df["a_ventana"], errors="coerce")
    df["b_ventana"] = pd.to_numeric(df["b_ventana"], errors="coerce")
    df["peso_pedido"] = pd.to_numeric(df["peso_pedido"], errors="coerce")
    df["volumen_pedido"] = pd.to_numeric(df["volumen_pedido"], errors="coerce")
    df["id_pedido"] = df["id_pedido"].apply(_normalize_identifier)
    df["id_cliente"] = df["id_cliente"].apply(_normalize_identifier)

    df = df.dropna(
        subset=[
            "fecha_entrega",
            "latitud",
            "longitud",
            "a_ventana",
            "b_ventana",
            "peso_pedido",
            "volumen_pedido",
        ]
    ).copy()
    if df.empty:
        raise ValueError("No hay registros validos en el archivo de despacho.")

    available_dates = sorted(df["fecha_entrega"].astype(str).unique())
    if target_date is None:
        selected_date = available_dates[0]
    else:
        selected_date = str(pd.to_datetime(target_date).date())
        if selected_date not in available_dates:
            raise ValueError(
                f"La fecha {selected_date} no existe en el CSV. "
                f"Fechas disponibles (primeras 10): {available_dates[:10]}"
            )

    day_df = df[df["fecha_entrega"].astype(str) == selected_date].copy()
    if day_df.empty:
        raise ValueError(f"No hay pedidos para la fecha {selected_date}.")

    if max_orders is not None and len(day_df) > max_orders:
        day_df = day_df.sample(n=max_orders, random_state=seed).copy()

    day_df = day_df.sort_values("id_pedido").reset_index(drop=True)
    return day_df, selected_date


def _load_graph(graph_path: str):
    import osmnx as ox

    if os.path.exists(graph_path):
        return ox.load_graphml(graph_path)

    try:
        from grafo.network_builder import get_santiago_graph
    except Exception as exc:
        raise RuntimeError(
            "No se encontro el grafo local y no fue posible usar grafo/network_builder.py. "
            "Asegura que exista grafo/santiago_routing_graph.graphml o configura dependencias de descarga."
        ) from exc

    return get_santiago_graph(filepath=graph_path)


def _haversine_matrix_km(df_nodes: pd.DataFrame) -> pd.DataFrame:
    lat = np.radians(df_nodes["latitud"].to_numpy(dtype=float))
    lon = np.radians(df_nodes["longitud"].to_numpy(dtype=float))
    ids = df_nodes["id_nodo"].astype(str).tolist()

    dlat = lat[:, None] - lat[None, :]
    dlon = lon[:, None] - lon[None, :]
    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(lat[:, None]) * np.cos(lat[None, :]) * (np.sin(dlon / 2.0) ** 2)
    )
    c = 2.0 * np.arcsin(np.minimum(1.0, np.sqrt(a)))
    km = 6371.0 * c
    np.fill_diagonal(km, 0.0)
    return pd.DataFrame(km, index=ids, columns=ids)


def _compute_distance_matrix_km(
    day_df: pd.DataFrame,
    graph_path: str,
    depot_lat: float,
    depot_lon: float,
) -> Tuple[pd.DataFrame, str]:
    routing_df = pd.DataFrame(
        {
            "Número de orden": day_df["id_pedido"].astype(str).str.strip(),
            "RUT": day_df["id_cliente"].astype(str).str.strip(),
            "latitud": day_df["latitud"].astype(float),
            "longitud": day_df["longitud"].astype(float),
        }
    )
    routing_df = routing_df.dropna(subset=["latitud", "longitud"]).copy()

    depot_row = pd.DataFrame(
        [
            {
                "Número de orden": "DEPOT_01",
                "RUT": "BASE",
                "latitud": float(depot_lat),
                "longitud": float(depot_lon),
            }
        ]
    )
    routing_input = pd.concat([routing_df, depot_row], ignore_index=True)
    routing_input["id_nodo"] = (
        routing_input["Número de orden"].astype(str).str.strip()
        + "_"
        + routing_input["RUT"].apply(_clean_rut)
    )

    try:
        from grafo.routing import calculate_routing_for_day

        G = _load_graph(graph_path=graph_path)
        matriz_km, _ = calculate_routing_for_day(routing_input, G)
        if not matriz_km.empty:
            return matriz_km, "grafo_astar"
    except Exception as exc:
        print(
            f"Aviso: no fue posible calcular distancias con grafo/A* ({exc}). "
            "Se usara fallback geodesico (Haversine) para pruebas."
        )

    matriz_km = _haversine_matrix_km(routing_input)
    return matriz_km, "haversine_fallback"


def build_daily_problem_from_csv(
    csv_path: str,
    target_date: Optional[str] = None,
    max_orders: Optional[int] = 40,
    seed: int = 42,
    n_trucks: int = 20,
    cost_per_km: float = 130.0,
    depot_lat: float = -33.4489,
    depot_lon: float = -70.6693,
    graph_path: Optional[str] = None,
) -> DailyProblemBundle:
    if n_trucks < 2:
        raise ValueError("n_trucks debe ser al menos 2.")

    day_df, selected_date = _prepare_daily_dispatch(
        csv_path=csv_path,
        target_date=target_date,
        max_orders=max_orders,
        seed=seed,
    )

    if graph_path is None:
        graph_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "grafo",
            "santiago_routing_graph.graphml",
        )

    matriz_km, distance_source = _compute_distance_matrix_km(
        day_df=day_df,
        graph_path=graph_path,
        depot_lat=depot_lat,
        depot_lon=depot_lon,
    )
    depot_node_id = "DEPOT_01_BASE"
    if depot_node_id not in matriz_km.index:
        raise ValueError(
            f"No se encontro el nodo de deposito '{depot_node_id}' en la matriz de distancias."
        )
    ordered_ids = [depot_node_id] + [nid for nid in matriz_km.index if nid != depot_node_id]
    matriz_km = matriz_km.loc[ordered_ids, ordered_ids].copy()

    node_ids = list(matriz_km.index)
    n_nodes = len(node_ids)

    day_lookup = day_df.copy()
    day_lookup["id_pedido"] = day_lookup["id_pedido"].apply(_normalize_identifier)
    day_lookup = day_lookup.set_index("id_pedido", drop=False)

    distance_ij = matriz_km.to_numpy(dtype=float, copy=True)
    distance_ij[~np.isfinite(distance_ij)] = 1e6
    np.fill_diagonal(distance_ij, 0.0)
    cost_ij = distance_ij * float(cost_per_km)

    demand_volume_i = np.zeros(n_nodes, dtype=float)
    demand_mass_i = np.zeros(n_nodes, dtype=float)
    a_i = np.zeros(n_nodes, dtype=float)
    b_i = np.full(n_nodes, 1440.0, dtype=float)
    service_var_i = np.zeros(n_nodes, dtype=float)

    node_labels: Dict[int, str] = {}
    for idx, node_id in enumerate(node_ids):
        if node_id == "DEPOT_01_BASE":
            node_labels[idx] = "DEPOT"
            continue

        order_id = str(node_id).rsplit("_", 1)[0]
        if order_id not in day_lookup.index:
            node_labels[idx] = order_id
            continue

        row = day_lookup.loc[order_id]
        if isinstance(row, pd.DataFrame):
            row = row.iloc[0]

        demand_volume_i[idx] = float(row["volumen_pedido"])
        demand_mass_i[idx] = float(row["peso_pedido"])
        a_i[idx] = float(row["a_ventana"])
        b_i[idx] = float(row["b_ventana"])

        service_var_i[idx] = 0.0
        node_labels[idx] = order_id

    # Capacity not limiting yet: high values + disabled constraints.
    cap_volume_k = np.full(n_trucks, 1e15, dtype=float)
    cap_mass_k = np.full(n_trucks, 1e15, dtype=float)

    # Same trucks in K11/K12 and same trucks in K21/K22.
    half = n_trucks // 2
    turno1 = list(range(0, half))
    turno2 = list(range(half, n_trucks))

    selected_dt = pd.to_datetime(selected_date).date()
    dia_semana = int(selected_dt.weekday())

    data = TDVRPTWData(
        cost_ij=cost_ij,
        distance_ij=distance_ij,
        dia_semana=dia_semana,
        demand_volume_i=demand_volume_i,
        demand_mass_i=demand_mass_i,
        cap_volume_k=cap_volume_k,
        cap_mass_k=cap_mass_k,
        a_i=a_i,
        b_i=b_i,
        service_var_i=service_var_i,
        service_fixed=7.0,
        z_t=np.arange(1, 14, dtype=float),  # 09:00..21:00
        dmax_k=np.full(n_trucks, 1e6, dtype=float),
        k11=turno1,
        k12=turno1,
        k21=turno2,
        k22=turno2,
        big_m=1e6,
        volume_factor=0.8,
        enforce_capacity=False,
    )

    return DailyProblemBundle(
        problem_data=data,
        selected_date=selected_date,
        daily_dispatch=day_df,
        distance_matrix_km=matriz_km,
        node_labels=node_labels,
        distance_source=distance_source,
    )
