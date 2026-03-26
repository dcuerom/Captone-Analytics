from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np


@dataclass
class SavingsSeedResult:
    decision_vector: np.ndarray
    routes_by_truck: Dict[int, List[int]]
    used_trucks: List[int]


def _route_volume(route: Sequence[int], demand_volume_i: np.ndarray) -> float:
    return float(np.sum(demand_volume_i[list(route)])) if route else 0.0


def _route_mass(route: Sequence[int], demand_mass_i: np.ndarray) -> float:
    return float(np.sum(demand_mass_i[list(route)])) if route else 0.0


def _route_feasible_for_truck(
    route: Sequence[int],
    truck: int,
    demand_volume_i: np.ndarray,
    demand_mass_i: np.ndarray,
    cap_volume_k: np.ndarray,
    cap_mass_k: np.ndarray,
    volume_factor: float,
) -> bool:
    vol = _route_volume(route, demand_volume_i)
    mass = _route_mass(route, demand_mass_i)
    return vol <= volume_factor * cap_volume_k[truck] and mass <= cap_mass_k[truck]


def _clarke_wright_routes(
    distance_ij: np.ndarray,
    customers: List[int],
    demand_volume_i: np.ndarray,
    demand_mass_i: np.ndarray,
    cap_volume_ref: float,
    cap_mass_ref: float,
    volume_factor: float,
    rng: np.random.Generator,
) -> List[List[int]]:
    """
    Clarke & Wright Savings clásico para CVRP (multi-ruta).
    """
    routes: List[List[int]] = [[i] for i in customers]
    route_of = {i: idx for idx, i in enumerate(customers)}

    savings = []
    for a_idx in range(len(customers)):
        i = customers[a_idx]
        for b_idx in range(a_idx + 1, len(customers)):
            j = customers[b_idx]
            s = float(distance_ij[0, i] + distance_ij[0, j] - distance_ij[i, j])
            # Pequeño jitter para desempates reproducibles.
            savings.append((s + 1e-6 * rng.random(), i, j))
    savings.sort(reverse=True, key=lambda x: x[0])

    def route_capacity_ok(route: Sequence[int]) -> bool:
        vol = _route_volume(route, demand_volume_i)
        mass = _route_mass(route, demand_mass_i)
        return vol <= volume_factor * cap_volume_ref and mass <= cap_mass_ref

    for _, i, j in savings:
        ri = route_of.get(i, None)
        rj = route_of.get(j, None)
        if ri is None or rj is None or ri == rj:
            continue

        route_i = routes[ri]
        route_j = routes[rj]
        if not route_i or not route_j:
            continue

        merged = None
        if route_i[-1] == i and route_j[0] == j:
            merged = route_i + route_j
        elif route_i[0] == i and route_j[-1] == j:
            merged = route_j + route_i
        elif route_i[0] == i and route_j[0] == j:
            merged = list(reversed(route_i)) + route_j
        elif route_i[-1] == i and route_j[-1] == j:
            merged = route_i + list(reversed(route_j))

        if merged is None:
            continue
        if not route_capacity_ok(merged):
            continue

        routes[ri] = merged
        routes[rj] = []
        for c in merged:
            route_of[c] = ri

    routes = [r for r in routes if r]
    return routes


def _split_or_merge_to_truck_count(
    routes: List[List[int]],
    target_count: int,
    demand_volume_i: np.ndarray,
    demand_mass_i: np.ndarray,
    cap_volume_ref: float,
    cap_mass_ref: float,
    volume_factor: float,
) -> List[List[int]]:
    """
    Ajusta cantidad de rutas al número de camiones.
    - Si faltan rutas: divide rutas largas.
    - Si sobran rutas: intenta fusionar rutas factibles.
    """
    routes = [list(r) for r in routes]

    # Split
    while len(routes) < target_count:
        idx = max(range(len(routes)), key=lambda i: len(routes[i]), default=-1)
        if idx < 0 or len(routes[idx]) <= 1:
            break
        r = routes[idx]
        cut = len(r) // 2
        left = r[:cut]
        right = r[cut:]
        routes[idx] = left
        routes.append(right)

    # Merge
    def feasible_merge(a: Sequence[int], b: Sequence[int]) -> bool:
        merged = list(a) + list(b)
        vol = _route_volume(merged, demand_volume_i)
        mass = _route_mass(merged, demand_mass_i)
        return vol <= volume_factor * cap_volume_ref and mass <= cap_mass_ref

    while len(routes) > target_count:
        merged_any = False
        best_pair = None
        best_size = None
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                if feasible_merge(routes[i], routes[j]):
                    size = len(routes[i]) + len(routes[j])
                    if best_pair is None or size < best_size:
                        best_pair = (i, j)
                        best_size = size
        if best_pair is None:
            break
        i, j = best_pair
        routes[i] = routes[i] + routes[j]
        routes.pop(j)
        merged_any = True
        if not merged_any:
            break

    return routes


def _departure_target_by_truck(data) -> Dict[int, float]:
    targets = {k: 540.0 for k in range(int(data.cap_volume_k.shape[0]))}
    mapping = {"k11": 540.0, "k12": 900.0, "k21": 660.0, "k22": 1020.0}
    for group_name, value in mapping.items():
        for k in getattr(data, group_name):
            targets[int(k)] = value
    return targets


def _assign_routes_to_trucks(routes: List[List[int]], data) -> Dict[int, List[int]]:
    k_count = int(data.cap_volume_k.shape[0])
    trucks = list(range(k_count))
    dep_target = _departure_target_by_truck(data)
    trucks_sorted = sorted(trucks, key=lambda k: dep_target[k])

    def route_key(route: Sequence[int]) -> float:
        if not route:
            return float("inf")
        return float(np.min(data.a_i[list(route)]))

    routes_sorted = sorted(routes, key=route_key)

    routes_by_truck: Dict[int, List[int]] = {}
    remaining = set(trucks_sorted)
    for route in routes_sorted:
        picked = None
        for k in trucks_sorted:
            if k not in remaining:
                continue
            if _route_feasible_for_truck(
                route=route,
                truck=k,
                demand_volume_i=data.demand_volume_i,
                demand_mass_i=data.demand_mass_i,
                cap_volume_k=data.cap_volume_k,
                cap_mass_k=data.cap_mass_k,
                volume_factor=data.volume_factor,
            ):
                picked = k
                break
        if picked is None and remaining:
            picked = next(iter(remaining))
        if picked is not None:
            routes_by_truck[picked] = list(route)
            remaining.remove(picked)

    for k in remaining:
        routes_by_truck[k] = []
    return routes_by_truck


def _interval_index_from_time(current_min: float, z_t: np.ndarray) -> int:
    starts = 480.0 + 60.0 * z_t
    ends = 540.0 + 60.0 * z_t
    if current_min <= starts[0]:
        return 0
    if current_min >= ends[-1]:
        return len(z_t) - 1
    mask = (current_min >= starts) & (current_min <= ends)
    if np.any(mask):
        return int(np.argmax(mask))
    idx = int(np.searchsorted(starts, current_min, side="right") - 1)
    return int(np.clip(idx, 0, len(z_t) - 1))


def build_savings_seed(problem, seed: int = 42) -> SavingsSeedResult:
    """
    Construye un individuo inicial factible aproximado usando Clarke & Wright.
    """
    data = problem.instance
    rng = np.random.default_rng(seed)

    n_nodes = problem.n_nodes
    k_count = problem.k_count
    t_count = problem.t_count
    depot = problem.depot
    customers = [i for i in range(n_nodes) if i != depot]

    # Referencia conservadora para C&W.
    cap_volume_ref = float(np.min(data.cap_volume_k))
    cap_mass_ref = float(np.min(data.cap_mass_k))

    routes = _clarke_wright_routes(
        distance_ij=np.asarray(data.cost_ij, dtype=float),
        customers=customers,
        demand_volume_i=data.demand_volume_i,
        demand_mass_i=data.demand_mass_i,
        cap_volume_ref=cap_volume_ref,
        cap_mass_ref=cap_mass_ref,
        volume_factor=float(data.volume_factor),
        rng=rng,
    )

    routes = _split_or_merge_to_truck_count(
        routes=routes,
        target_count=k_count,
        demand_volume_i=data.demand_volume_i,
        demand_mass_i=data.demand_mass_i,
        cap_volume_ref=cap_volume_ref,
        cap_mass_ref=cap_mass_ref,
        volume_factor=float(data.volume_factor),
    )

    routes_by_truck = _assign_routes_to_trucks(routes, data)

    x = np.zeros((k_count, t_count, n_nodes, n_nodes), dtype=float)
    ts = np.zeros((k_count, n_nodes), dtype=float)

    dep_target = _departure_target_by_truck(data)
    s0 = float(data.service_var_i[depot])

    for k in range(k_count):
        route_customers = routes_by_truck.get(k, [])
        ts[k, depot] = dep_target[k] - s0

        if not route_customers:
            continue

        route_nodes = [depot] + route_customers + [depot]
        current = ts[k, depot]

        for i, j in zip(route_nodes[:-1], route_nodes[1:]):
            t_idx = _interval_index_from_time(float(current), data.z_t)
            x[k, t_idx, i, j] = 1.0

            travel = float(data.travel_time_tij[t_idx, i, j])
            if not np.isfinite(travel):
                travel = float(data.big_m) / 10.0

            current = current + float(data.service_var_i[i]) + float(data.service_fixed) + travel

            if j != depot:
                current = max(current, float(data.a_i[j]))
                ts[k, j] = current

    vec = np.zeros(problem.n_var, dtype=float)
    vec[: problem.n_x] = x.reshape(-1)
    ts_flat = ts.reshape(-1)
    ts_lb = problem.xl[problem.n_x :]
    ts_ub = problem.xu[problem.n_x :]
    vec[problem.n_x :] = np.clip(ts_flat, ts_lb, ts_ub)

    used_trucks = [k for k, r in routes_by_truck.items() if len(r) > 0]
    return SavingsSeedResult(
        decision_vector=vec,
        routes_by_truck=routes_by_truck,
        used_trucks=used_trucks,
    )
