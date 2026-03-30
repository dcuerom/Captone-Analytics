from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

try:
    # Ejecutando como paquete: python -m modelo.prueba
    from .bootstrap_runtime import bootstrap_local_pydeps
except ImportError:
    # Ejecutando como script: python modelo/prueba.py
    from bootstrap_runtime import bootstrap_local_pydeps

_BOOTSTRAP_STATUS = bootstrap_local_pydeps(required_packages=("numpy", "pymoo"))

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
    from pymoo.core.problem import ElementwiseProblem
except ModuleNotFoundError as exc:
    if _BOOTSTRAP_STATUS == "invalid":
        raise ModuleNotFoundError(
            "No se pudo importar pymoo. Se detecto `/.pydeps` incompleto y se deshabilito "
            "para evitar conflictos de dependencias. "
            "Usa un entorno virtual sano o reinstala dependencias en `.pydeps`."
        ) from exc
    raise

try:
    # Ejecutando como paquete: python -m modelo.prueba
    from .funciones import DELTA_DEFAULT, Z_0, tau_ij_vec
except ImportError:
    # Ejecutando como script: python modelo/prueba.py
    from funciones import DELTA_DEFAULT, Z_0, tau_ij_vec


def build_travel_time_tensor_from_distance(
    distance_ij: np.ndarray,
    z_t: np.ndarray,
    dia_semana: int,
    delta: float = DELTA_DEFAULT,
) -> np.ndarray:
    """
    Construye T_tij en minutos usando tau_ij_vec (Fleischmann) para cada intervalo t.

    ConvenciÃ³n:
    - Si z_t inicia en 0: hora = Z_0 + z_t.
    - Si z_t inicia en 1: hora = Z_0 + (z_t - 1).
    """
    distance_ij = np.asarray(distance_ij, dtype=float)
    z_t = np.asarray(z_t, dtype=float)

    if distance_ij.ndim != 2 or distance_ij.shape[0] != distance_ij.shape[1]:
        raise ValueError("distance_ij debe tener forma (N, N).")

    n_nodes = distance_ij.shape[0]
    t_count = z_t.shape[0]
    travel_time_tij = np.zeros((t_count, n_nodes, n_nodes), dtype=float)

    flat_dist = distance_ij.reshape(-1)
    z_shift = 1.0 if np.min(z_t) >= 1.0 else 0.0
    for t_idx, z_value in enumerate(z_t):
        departure_hour = float(Z_0 + (z_value - z_shift))
        departure_vec = np.full_like(flat_dist, departure_hour, dtype=float)
        travel_hours = tau_ij_vec(
            distancia_km=flat_dist,
            t=departure_vec,
            dia_semana=dia_semana,
            delta=delta,
        )
        travel_minutes = (travel_hours * 60.0).reshape(n_nodes, n_nodes)
        np.fill_diagonal(travel_minutes, 0.0)
        travel_time_tij[t_idx] = travel_minutes

    return travel_time_tij


@dataclass
class TDVRPTWData:
    """
    Estructura de datos para el modelo VRPTW con intervalos de tiempo.

    Convenciones:
    - Nodo 0 = depÃ³sito.
    - Nodos 1..N-1 = clientes.
    - x[k, t, i, j] representa si el camiÃ³n k usa el arco i->j en el intervalo t.
    """

    cost_ij: np.ndarray
    demand_volume_i: np.ndarray
    demand_mass_i: np.ndarray
    cap_volume_k: np.ndarray
    cap_mass_k: np.ndarray
    a_i: np.ndarray
    b_i: np.ndarray
    service_var_i: np.ndarray
    service_fixed: float
    z_t: np.ndarray
    dmax_k: np.ndarray | float
    travel_time_tij: np.ndarray | None = None
    distance_ij: np.ndarray | None = None
    dia_semana: int = 0
    delta_fleischmann: float = DELTA_DEFAULT
    k11: Sequence[int] = field(default_factory=list)
    k12: Sequence[int] = field(default_factory=list)
    k21: Sequence[int] = field(default_factory=list)
    k22: Sequence[int] = field(default_factory=list)
    depot_index: int = 0
    big_m: float = 1e5
    volume_factor: float = 0.8
    enforce_capacity: bool = False

    def validate(self) -> None:
        self.cost_ij = np.asarray(self.cost_ij, dtype=float)
        self.demand_volume_i = np.asarray(self.demand_volume_i, dtype=float)
        self.demand_mass_i = np.asarray(self.demand_mass_i, dtype=float)
        self.cap_volume_k = np.asarray(self.cap_volume_k, dtype=float)
        self.cap_mass_k = np.asarray(self.cap_mass_k, dtype=float)
        self.a_i = np.asarray(self.a_i, dtype=float)
        self.b_i = np.asarray(self.b_i, dtype=float)
        self.service_var_i = np.asarray(self.service_var_i, dtype=float)
        self.z_t = np.asarray(self.z_t, dtype=float)

        n_nodes = self.cost_ij.shape[0]

        if self.cost_ij.shape != (n_nodes, n_nodes):
            raise ValueError("cost_ij debe tener forma (N, N).")
        if self.demand_volume_i.shape[0] != n_nodes:
            raise ValueError("demand_volume_i debe tener largo N.")
        if self.demand_mass_i.shape[0] != n_nodes:
            raise ValueError("demand_mass_i debe tener largo N.")
        if self.a_i.shape[0] != n_nodes:
            raise ValueError("a_i debe tener largo N.")
        if self.b_i.shape[0] != n_nodes:
            raise ValueError("b_i debe tener largo N.")
        if self.service_var_i.shape[0] != n_nodes:
            raise ValueError("service_var_i debe tener largo N.")
        # En esta fase se desprecia S_i y solo se usa tiempo fijo de atencion.
        self.service_var_i = np.zeros_like(self.service_var_i, dtype=float)
        if self.cap_volume_k.shape[0] != self.cap_mass_k.shape[0]:
            raise ValueError("cap_volume_k y cap_mass_k deben tener igual largo K.")
        if not (0 <= int(self.dia_semana) <= 6):
            raise ValueError("dia_semana debe estar entre 0 (Lunes) y 6 (Domingo).")

        if self.travel_time_tij is None:
            if self.distance_ij is None:
                raise ValueError(
                    "Debes entregar travel_time_tij o distance_ij para construir T_tij."
                )
            self.distance_ij = np.asarray(self.distance_ij, dtype=float)
            if self.distance_ij.shape != (n_nodes, n_nodes):
                raise ValueError("distance_ij debe tener forma (N, N).")
            self.travel_time_tij = build_travel_time_tensor_from_distance(
                distance_ij=self.distance_ij,
                z_t=self.z_t,
                dia_semana=self.dia_semana,
                delta=self.delta_fleischmann,
            )
        else:
            self.travel_time_tij = np.asarray(self.travel_time_tij, dtype=float)

        # Evitar NaN/Inf en tiempos de viaje para no generar CV infinito.
        if not np.all(np.isfinite(self.travel_time_tij)):
            finite_vals = self.travel_time_tij[np.isfinite(self.travel_time_tij)]
            finite_max = float(np.max(finite_vals)) if finite_vals.size > 0 else 0.0
            cap_value = max(float(self.big_m), finite_max, 1.0)
            self.travel_time_tij = np.nan_to_num(
                self.travel_time_tij,
                nan=cap_value,
                posinf=cap_value,
                neginf=0.0,
            )

        if self.travel_time_tij.ndim != 3:
            raise ValueError("travel_time_tij debe tener forma (T, N, N).")
        if self.travel_time_tij.shape[1:] != (n_nodes, n_nodes):
            raise ValueError("travel_time_tij debe tener forma (T, N, N).")
        if self.z_t.shape[0] != self.travel_time_tij.shape[0]:
            raise ValueError("z_t debe tener largo T.")

        if np.isscalar(self.dmax_k):
            self.dmax_k = np.full(self.cap_volume_k.shape[0], float(self.dmax_k), dtype=float)
        else:
            self.dmax_k = np.asarray(self.dmax_k, dtype=float)
            if self.dmax_k.shape[0] != self.cap_volume_k.shape[0]:
                raise ValueError("dmax_k debe ser escalar o de largo K.")

        for group_name, group in self.truck_groups.items():
            for k in group:
                if k < 0 or k >= self.cap_volume_k.shape[0]:
                    raise ValueError(f"CamiÃ³n {k} en {group_name} estÃ¡ fuera de rango.")

    @property
    def truck_groups(self) -> Dict[str, Sequence[int]]:
        return {"k11": self.k11, "k12": self.k12, "k21": self.k21, "k22": self.k22}


class TDVRPTWProblem(ElementwiseProblem):
    """
    Problema VRPTW con discretizaciÃ³n temporal en PyMoo.

    Implementa la formulaciÃ³n de tu modelo con:
    - Variables de arco binarias x_(i,t,j),k (codificadas y umbralizadas desde [0,1]).
    - Variables de tiempo de llegada ts_i,k (reales no negativas).
    - FunciÃ³n objetivo de costo por arco.
    - Restricciones de capacidad, flujo, ventanas, tiempos y retorno a CD.
    """

    def __init__(self, data: TDVRPTWData):
        self.instance = data
        self.instance.validate()

        self.k_count = int(self.instance.cap_volume_k.shape[0])
        self.t_count = int(self.instance.travel_time_tij.shape[0])
        self.n_nodes = int(self.instance.cost_ij.shape[0])
        self.depot = int(self.instance.depot_index)
        self.customers = [i for i in range(self.n_nodes) if i != self.depot]

        self.n_x = self.k_count * self.t_count * self.n_nodes * self.n_nodes
        self.n_ts = self.k_count * self.n_nodes
        n_var = self.n_x + self.n_ts

        xl = np.zeros(n_var, dtype=float)
        xu = np.ones(n_var, dtype=float)
        xu[self.n_x :] = self._compute_ts_upper_bound()

        super().__init__(
            n_var=n_var,
            n_obj=1,
            n_ieq_constr=self._count_constraints(),
            xl=xl,
            xu=xu,
        )

    def decode_solution(self, decision_vector: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Retorna (x_binaria, ts) desde el vector de decisiÃ³n de PyMoo."""
        x_raw = decision_vector[: self.n_x].reshape(
            self.k_count, self.t_count, self.n_nodes, self.n_nodes
        )
        x_bin = (x_raw >= 0.5).astype(np.int8)

        # Sin auto-arcos i->i.
        for i in range(self.n_nodes):
            x_bin[:, :, i, i] = 0

        ts = decision_vector[self.n_x :].reshape(self.k_count, self.n_nodes)
        return x_bin, ts

    def _compute_ts_upper_bound(self) -> float:
        latest_window = float(np.max(self.instance.b_i))
        latest_interval_end = float(np.max(540 + 60 * self.instance.z_t))
        max_departure = 1020.0
        extra = float(self.instance.service_fixed + np.max(self.instance.travel_time_tij))
        return max(latest_window, latest_interval_end, max_departure) + extra

    def _assigned_trucks(self) -> List[int]:
        assigned = set()
        for trucks in self.instance.truck_groups.values():
            assigned.update(int(k) for k in trucks)
        return sorted(assigned)

    def _departure_target_by_truck(self) -> Dict[int, float]:
        """
        Resuelve targets de salida cuando un camiÃ³n aparece en mÃ¡s de un subconjunto.
        Estrategia: usar la salida mÃ¡s temprana (mÃ­nimo objetivo).
        """
        mapping = {"k11": 540.0, "k12": 900.0, "k21": 660.0, "k22": 1020.0}
        targets: Dict[int, float] = {}
        for group_name, trucks in self.instance.truck_groups.items():
            objective = mapping[group_name]
            for k in trucks:
                k = int(k)
                if k in targets:
                    targets[k] = min(targets[k], objective)
                else:
                    targets[k] = objective
        return targets

    def _count_constraints(self) -> int:
        k = self.k_count
        t = self.t_count
        n = self.n_nodes
        c = len(self.customers)
        assigned_trucks = self._assigned_trucks()
        n_assigned = len(assigned_trucks)

        # Todas expresadas como G <= 0; igualdades se modelan con +/- expresiÃ³n.
        count = 0
        if self.instance.enforce_capacity:
            count += k  # (1) capacidad volumen
            count += k  # (2) capacidad masa
        count += 2 * k * c  # (3) conservaciÃ³n de flujo
        count += 2 * c  # (4) un camiÃ³n llega al cliente
        count += 2 * c  # (5) un camiÃ³n sale del cliente
        count += k * t * n * (n - 1)  # (6) coherencia temporal / eliminaciÃ³n subtours
        count += 2 * c  # (7) ventanas de tiempo
        count += 2 * k * t * c  # (8) tiempo de atenciÃ³n en intervalo
        count += k * c  # (9) nodo sin atenciÃ³n no tiene ts
        count += 2 * n_assigned  # (10-13) salida CD por camiÃ³n asignado
        count += k  # (14) duraciÃ³n mÃ¡xima de ruta
        count += 2 * n_assigned  # (15-18) vuelta CD por camiÃ³n asignado
        return count

    def _evaluate(self, x: np.ndarray, out: dict, *args, **kwargs) -> None:
        x_bin, ts = self.decode_solution(x)
        d = self.instance
        g_parts: List[np.ndarray] = []
        customers = np.asarray(self.customers, dtype=int)
        t_count = self.t_count
        n_nodes = self.n_nodes
        depot = self.depot

        # Objetivo: min sum_k sum_t sum_i sum_j x_(i,t,j),k * C_ij
        objective = float(np.sum(x_bin * d.cost_ij[None, None, :, :]))

        # Pre-calculos compartidos.
        x_customers_out = x_bin[:, :, customers, :]  # (K, T, C, N)
        x_customers_in = x_bin[:, :, :, customers]   # (K, T, N, C)
        outgoing_ki = np.sum(x_customers_out, axis=(1, 3), dtype=float)  # (K, C)
        incoming_ki = np.sum(x_customers_in, axis=(1, 2), dtype=float)    # (K, C)

        # (1) y (2) Capacidad (opcional)
        if d.enforce_capacity:
            used_volume_k = np.sum(outgoing_ki * d.demand_volume_i[customers][None, :], axis=1)
            used_mass_k = np.sum(outgoing_ki * d.demand_mass_i[customers][None, :], axis=1)
            g_parts.append(used_volume_k - d.volume_factor * d.cap_volume_k)
            g_parts.append(used_mass_k - d.cap_mass_k)

        # (3) Conservacion de flujo en clientes: salida - entrada = 0
        flow = outgoing_ki - incoming_ki
        g_parts.append(flow.ravel())
        g_parts.append((-flow).ravel())

        # (4) A cada cliente llega un unico camion (considerando todo k,t,i)
        incoming_j = np.sum(x_customers_in, axis=(0, 1, 2), dtype=float)
        expr_in = incoming_j - 1.0
        g_parts.append(expr_in)
        g_parts.append(-expr_in)

        # (5) Desde cada cliente sale un unico camion (considerando todo k,t,j)
        outgoing_i = np.sum(x_customers_out, axis=(0, 1, 3), dtype=float)
        expr_out = outgoing_i - 1.0
        g_parts.append(expr_out)
        g_parts.append(-expr_out)

        # (6) Coherencia temporal / eliminacion de subtours
        non_diag_mask = ~np.eye(n_nodes, dtype=bool)
        for t in range(t_count):
            lhs_t = (
                ts[:, :, None]
                + d.service_fixed
                + d.travel_time_tij[t][None, :, :]
                - ts[:, None, :]
                - d.big_m * (1.0 - x_bin[:, t, :, :])
            )
            g_parts.append(lhs_t[:, non_diag_mask].ravel())

        # (7) Ventanas de tiempo por cliente
        ts_sum_customer = np.sum(ts[:, customers], axis=0, dtype=float)
        g_parts.append(d.a_i[customers] - ts_sum_customer)
        g_parts.append(ts_sum_customer - d.b_i[customers])

        # (8) Tiempo de atencion en intervalo
        lower_t = (480.0 + 60.0 * d.z_t)[None, :, None]
        upper_t = (540.0 + 60.0 * d.z_t)[None, :, None]
        visit_ktj = np.sum(x_customers_in, axis=2, dtype=float)
        ts_kj = ts[:, customers][:, None, :]
        g8_low = lower_t - ts_kj - d.big_m * (1.0 - visit_ktj)
        g8_up = ts_kj - upper_t - d.big_m * (1.0 - visit_ktj)
        g_parts.append(g8_low.ravel())
        g_parts.append(g8_up.ravel())

        # (9) Nodo sin atencion no debe tener tiempo de atencion activo
        g_parts.append((ts[:, customers] - d.big_m * outgoing_ki).ravel())

        # (10-13) Horas de salida del CD (colapsando duplicados por camion)
        departure_targets = self._departure_target_by_truck()
        dep_idx = np.asarray(sorted(departure_targets.keys()), dtype=int)
        dep_target_vec = np.asarray([departure_targets[int(k)] for k in dep_idx], dtype=float)
        dep_expr = ts[dep_idx, depot] - dep_target_vec
        g_parts.append(dep_expr)
        g_parts.append(-dep_expr)

        # (14) Duracion maxima de ruta
        route_duration_k = np.sum(
            x_bin * d.travel_time_tij[None, :, :, :],
            axis=(1, 2, 3),
            dtype=float,
        )
        g_parts.append(route_duration_k - d.dmax_k)

        # (15-18) Vuelta al CD por camion asignado
        assigned = np.asarray(self._assigned_trucks(), dtype=int)
        returns_cd_k = np.sum(x_bin[:, :, customers, depot], axis=(1, 2), dtype=float)
        returns_expr = returns_cd_k[assigned] - 1.0
        g_parts.append(returns_expr)
        g_parts.append(-returns_expr)

        g = np.concatenate([np.asarray(part, dtype=float).ravel() for part in g_parts], axis=0)

        out["F"] = np.array([objective], dtype=float)
        out["G"] = g

def build_toy_tdvrptw_data(
    n_customers: int = 6,
    n_trucks: int = 4,
    n_intervals: int = 13,
    seed: int = 42,
) -> TDVRPTWData:
    """
    Crea una instancia pequeÃ±a de juguete para pruebas de integraciÃ³n.
    """
    rng = np.random.default_rng(seed)
    n_nodes = n_customers + 1  # + depÃ³sito

    distance_km = rng.uniform(1.0, 18.0, size=(n_nodes, n_nodes)).astype(float)
    np.fill_diagonal(distance_km, 0.0)
    # Costo base del arco: aquÃ­ se asimila a distancia (puedes cambiarlo por costo monetario real).
    base_cost = distance_km.copy()

    demand_volume = np.zeros(n_nodes, dtype=float)
    demand_mass = np.zeros(n_nodes, dtype=float)
    demand_volume[1:] = rng.uniform(0.3, 1.8, size=n_customers)
    demand_mass[1:] = rng.uniform(30.0, 180.0, size=n_customers)

    cap_volume = np.full(n_trucks, 8.0, dtype=float)
    cap_mass = np.full(n_trucks, 1200.0, dtype=float)

    a_i = np.zeros(n_nodes, dtype=float)
    b_i = np.full(n_nodes, 1440.0, dtype=float)
    # Ventanas distribuidas en la jornada para permitir turnos manana/tarde.
    day_start = 540.0  # 09:00
    day_end = 540.0 + 60.0 * n_intervals  # fin del ultimo intervalo
    a_i[1:] = day_start + rng.integers(0, max(1, int(day_end - day_start - 180.0)), size=n_customers)
    b_i[1:] = a_i[1:] + rng.integers(90, 240, size=n_customers)
    b_i[1:] = np.minimum(b_i[1:], day_end)
    b_i[1:] = np.maximum(b_i[1:], a_i[1:] + 30.0)

    service_var = np.zeros(n_nodes, dtype=float)

    z_t = np.arange(1, n_intervals + 1, dtype=float)  # 1,2,... -> 09:00, 10:00, ...
    dmax = np.full(n_trucks, 480.0, dtype=float)

    # Reparto simple de camiones por turnos/rutas.
    groups = [[], [], [], []]
    for idx in range(n_trucks):
        groups[idx % 4].append(idx)

    return TDVRPTWData(
        cost_ij=base_cost,
        distance_ij=distance_km,
        dia_semana=0,
        delta_fleischmann=DELTA_DEFAULT,
        demand_volume_i=demand_volume,
        demand_mass_i=demand_mass,
        cap_volume_k=cap_volume,
        cap_mass_k=cap_mass,
        a_i=a_i,
        b_i=b_i,
        service_var_i=service_var,
        service_fixed=7.0,
        z_t=z_t,
        dmax_k=dmax,
        k11=groups[0],
        k12=groups[1],
        k21=groups[2],
        k22=groups[3],
        big_m=1e4,
        volume_factor=0.8,
    )

