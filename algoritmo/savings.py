"""
Semilla de Clarke-Wright para inicializar el GA.

Retorna una secuencia plana de ids de clientes (sin depot), util como
permutacion inicial para el cromosoma del algoritmo genetico.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd


def _route_load(
    route: List[str],
    vol_map: Dict[str, float],
    peso_map: Dict[str, float],
) -> Tuple[float, float]:
    vol = sum(float(vol_map.get(n, 0.0)) for n in route)
    peso = sum(float(peso_map.get(n, 0.0)) for n in route)
    return vol, peso


def clarke_wright_savings(
    df_cluster: pd.DataFrame,
    matriz_dist: pd.DataFrame,
    depot_id: str,
    cap_vol_cm3: float,
    cap_peso_g: float,
    d_max_min: float,  # reservado para compatibilidad de firma
    speed_kmh: float = 25.0,  # reservado para compatibilidad de firma
) -> List[str]:
    # Construccion defensiva para no romper el pipeline si entra basura.
    if matriz_dist is None or matriz_dist.empty:
        return []

    clientes = [n for n in matriz_dist.index.tolist() if n != depot_id]
    if not clientes:
        return []

    if len(clientes) == 1:
        return clientes[:]

    vol_col = "volumen_pedido_cm3" if "volumen_pedido_cm3" in df_cluster.columns else "volumen_pedido"
    peso_col = "peso_pedido_g" if "peso_pedido_g" in df_cluster.columns else "peso_pedido"

    vol_map: Dict[str, float] = {}
    peso_map: Dict[str, float] = {}

    if "id_nodo" in df_cluster.columns:
        df_idx = df_cluster.set_index("id_nodo")
        for cid in clientes:
            if cid in df_idx.index:
                row = df_idx.loc[cid]
                if isinstance(row, pd.DataFrame):
                    row = row.iloc[0]
                vol_map[cid] = float(row.get(vol_col, 0.0))
                peso_map[cid] = float(row.get(peso_col, 0.0))
            else:
                vol_map[cid] = 0.0
                peso_map[cid] = 0.0
    else:
        for cid in clientes:
            vol_map[cid] = 0.0
            peso_map[cid] = 0.0

    # Inicio: una ruta por cliente.
    routes: List[List[str]] = [[c] for c in clientes]
    route_of: Dict[str, int] = {c: i for i, c in enumerate(clientes)}

    savings: List[Tuple[float, str, str]] = []
    for i in clientes:
        for j in clientes:
            if i == j:
                continue
            try:
                s = float(matriz_dist.loc[depot_id, i]) + float(matriz_dist.loc[depot_id, j]) - float(matriz_dist.loc[i, j])
            except Exception:
                continue
            savings.append((s, i, j))

    savings.sort(key=lambda x: x[0], reverse=True)

    for _, i, j in savings:
        ri = route_of.get(i)
        rj = route_of.get(j)
        if ri is None or rj is None or ri == rj:
            continue

        route_i = routes[ri]
        route_j = routes[rj]
        if not route_i or not route_j:
            continue

        # Regla clasica: solo unir extremos para no crear ciclos.
        can_merge = (route_i[-1] == i and route_j[0] == j) or (route_j[-1] == j and route_i[0] == i)
        if not can_merge:
            continue

        merged = route_i + route_j if route_i[-1] == i else route_j + route_i
        vol, peso = _route_load(merged, vol_map, peso_map)
        if vol > cap_vol_cm3 or peso > cap_peso_g:
            continue

        # Aplicar merge.
        routes[ri] = merged
        routes[rj] = []
        for c in merged:
            route_of[c] = ri

    ordered_routes = [r for r in routes if r]
    ordered_routes.sort(key=len, reverse=True)

    seeded_perm: List[str] = []
    for r in ordered_routes:
        seeded_perm.extend(r)

    # Garantizar cobertura total.
    seen = set(seeded_perm)
    for c in clientes:
        if c not in seen:
            seeded_perm.append(c)
            seen.add(c)

    return seeded_perm

