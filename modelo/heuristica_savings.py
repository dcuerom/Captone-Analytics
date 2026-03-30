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
            k = int(k)
            targets[k] = min(targets[k], value)
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
        best_score = None
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
                score = _route_time_violation_for_truck(
                    route_customers=route,
                    truck=k,
                    data=data,
                    dep_target=dep_target,
                )
                if picked is None or score < best_score:
                    picked = k
                    best_score = score
        if picked is None and remaining:
            # Si no hay factibles por capacidad (poco probable en esta etapa),
            # igual privilegiamos menor violacion temporal.
            picked = min(
                remaining,
                key=lambda kk: _route_time_violation_for_truck(
                    route_customers=route,
                    truck=kk,
                    data=data,
                    dep_target=dep_target,
                ),
            )
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


def _interval_bounds(z_t: np.ndarray, t_idx: int) -> Tuple[float, float]:
    lower = float(480.0 + 60.0 * z_t[t_idx])
    upper = float(540.0 + 60.0 * z_t[t_idx])
    return lower, upper


def _build_route_plan_for_truck(
    route_customers: Sequence[int],
    truck: int,
    data,
    dep_target: Dict[int, float],
) -> Tuple[List[Tuple[int, int, int]], Dict[int, float], float]:
    """
    Retorna:
    - plan de arcos [(t, i, j), ...]
    - ts por cliente de la ruta
    - score de violacion temporal acumulada (0 es mejor)
    """
    depot = 0
    route_nodes = [depot] + list(route_customers) + [depot]
    current = float(dep_target[truck])
    plan: List[Tuple[int, int, int]] = []
    ts_route: Dict[int, float] = {}
    violation = 0.0

    for i, j in zip(route_nodes[:-1], route_nodes[1:]):
        if j == depot:
            t_idx = _interval_index_from_time(current, data.z_t)
            plan.append((t_idx, i, j))
            travel = float(data.travel_time_tij[t_idx, i, j])
            if not np.isfinite(travel):
                travel = float(data.big_m) / 10.0
                violation += float(data.big_m) / 10.0
            current = current + float(data.service_fixed) + travel
            continue

        best = None
        for t_idx in range(len(data.z_t)):
            travel = float(data.travel_time_tij[t_idx, i, j])
            if not np.isfinite(travel):
                continue
            arrival = current + float(data.service_fixed) + travel
            service_start = max(arrival, float(data.a_i[j]))

            lower_t, upper_t = _interval_bounds(data.z_t, t_idx)
            v_interval = max(lower_t - service_start, 0.0) + max(service_start - upper_t, 0.0)
            v_window = max(service_start - float(data.b_i[j]), 0.0)
            score = v_interval + v_window
            cand = (score, service_start, t_idx)
            if best is None or cand < best:
                best = cand

        if best is None:
            # Penalizacion fuerte si no hay tiempo de viaje finito.
            t_idx = _interval_index_from_time(current, data.z_t)
            plan.append((t_idx, i, j))
            violation += float(data.big_m) / 10.0
            current = current + float(data.big_m) / 10.0
            ts_route[j] = current
            continue

        score, service_start, t_idx = best
        plan.append((int(t_idx), i, j))
        ts_route[j] = float(service_start)
        current = float(service_start)
        violation += float(score)

    return plan, ts_route, float(violation)


def _route_time_violation_for_truck(
    route_customers: Sequence[int],
    truck: int,
    data,
    dep_target: Dict[int, float],
) -> float:
    _, _, violation = _build_route_plan_for_truck(
        route_customers=route_customers,
        truck=truck,
        data=data,
        dep_target=dep_target,
    )
    return float(violation)


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

    for k in range(k_count):
        route_customers = routes_by_truck.get(k, [])
        ts[k, depot] = dep_target[k]

        if not route_customers:
            continue

        plan, ts_route, _ = _build_route_plan_for_truck(
            route_customers=route_customers,
            truck=k,
            data=data,
            dep_target=dep_target,
        )
        for t_idx, i, j in plan:
            x[k, t_idx, i, j] = 1.0
        for j, ts_j in ts_route.items():
            ts[k, j] = float(ts_j)

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
