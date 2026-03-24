from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

import numpy as np
from pymoo.core.problem import ElementwiseProblem


@dataclass
class TDVRPTWData:
    """
    Estructura de datos para el modelo VRPTW con intervalos de tiempo.

    Convenciones:
    - Nodo 0 = depósito.
    - Nodos 1..N-1 = clientes.
    - x[k, t, i, j] representa si el camión k usa el arco i->j en el intervalo t.
    """

    cost_ij: np.ndarray
    travel_time_tij: np.ndarray
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
    k11: Sequence[int] = field(default_factory=list)
    k12: Sequence[int] = field(default_factory=list)
    k21: Sequence[int] = field(default_factory=list)
    k22: Sequence[int] = field(default_factory=list)
    depot_index: int = 0
    big_m: float = 1e5
    volume_factor: float = 0.8

    def validate(self) -> None:
        n_nodes = self.cost_ij.shape[0]

        if self.cost_ij.shape != (n_nodes, n_nodes):
            raise ValueError("cost_ij debe tener forma (N, N).")
        if self.travel_time_tij.ndim != 3:
            raise ValueError("travel_time_tij debe tener forma (T, N, N).")
        if self.travel_time_tij.shape[1:] != (n_nodes, n_nodes):
            raise ValueError("travel_time_tij debe tener forma (T, N, N).")
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
        if self.cap_volume_k.shape[0] != self.cap_mass_k.shape[0]:
            raise ValueError("cap_volume_k y cap_mass_k deben tener igual largo K.")
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
                    raise ValueError(f"Camión {k} en {group_name} está fuera de rango.")

    @property
    def truck_groups(self) -> Dict[str, Sequence[int]]:
        return {"k11": self.k11, "k12": self.k12, "k21": self.k21, "k22": self.k22}


class TDVRPTWProblem(ElementwiseProblem):
    """
    Problema VRPTW con discretización temporal en PyMoo.

    Implementa la formulación de tu modelo con:
    - Variables de arco binarias x_(i,t,j),k (codificadas y umbralizadas desde [0,1]).
    - Variables de tiempo de llegada ts_i,k (reales no negativas).
    - Función objetivo de costo por arco.
    - Restricciones de capacidad, flujo, ventanas, tiempos y retorno a CD.
    """

    def __init__(self, data: TDVRPTWData):
        self.data = data
        self.data.validate()

        self.k_count = int(self.data.cap_volume_k.shape[0])
        self.t_count = int(self.data.travel_time_tij.shape[0])
        self.n_nodes = int(self.data.cost_ij.shape[0])
        self.depot = int(self.data.depot_index)
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
        """Retorna (x_binaria, ts) desde el vector de decisión de PyMoo."""
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
        latest_window = float(np.max(self.data.b_i))
        latest_interval_end = float(np.max(540 + 60 * self.data.z_t))
        max_departure = 1020.0
        extra = float(np.max(self.data.service_var_i) + self.data.service_fixed + np.max(self.data.travel_time_tij))
        return max(latest_window, latest_interval_end, max_departure) + extra

    def _count_constraints(self) -> int:
        k = self.k_count
        t = self.t_count
        n = self.n_nodes
        c = len(self.customers)
        grouped_trucks = sum(len(group) for group in self.data.truck_groups.values())

        # Todas expresadas como G <= 0; igualdades se modelan con +/- expresión.
        count = 0
        count += k  # (1) capacidad volumen
        count += k  # (2) capacidad masa
        count += 2 * k * c  # (3) conservación de flujo
        count += 2 * c  # (4) un camión llega al cliente
        count += 2 * c  # (5) un camión sale del cliente
        count += k * t * n * (n - 1)  # (6) coherencia temporal / eliminación subtours
        count += 2 * c  # (7) ventanas de tiempo
        count += 2 * k * t * c  # (8) tiempo de atención en intervalo
        count += k * c  # (9) nodo sin atención no tiene ts
        count += 2 * grouped_trucks  # (10-13) salida CD por grupo
        count += k  # (14) duración máxima de ruta
        count += 2 * grouped_trucks  # (15-18) vuelta CD por grupo
        return count

    def _evaluate(self, x: np.ndarray, out: dict, *args, **kwargs) -> None:
        x_bin, ts = self.decode_solution(x)
        d = self.data
        g: List[float] = []

        # Objetivo: min sum_k sum_t sum_i sum_j x_(i,t,j),k * C_ij
        objective = float(np.sum(x_bin * d.cost_ij[None, None, :, :]))

        # (1) Capacidad volumétrica por camión (con factor 0.8)
        for k in range(self.k_count):
            used_volume = 0.0
            for i in self.customers:
                used_volume += d.demand_volume_i[i] * np.sum(x_bin[k, :, i, :])
            g.append(used_volume - d.volume_factor * d.cap_volume_k[k])

        # (2) Capacidad de masa por camión
        for k in range(self.k_count):
            used_mass = 0.0
            for i in self.customers:
                used_mass += d.demand_mass_i[i] * np.sum(x_bin[k, :, i, :])
            g.append(used_mass - d.cap_mass_k[k])

        # (3) Conservación de flujo en clientes: salida - entrada = 0
        for k in range(self.k_count):
            for i in self.customers:
                flow = float(np.sum(x_bin[k, :, i, :]) - np.sum(x_bin[k, :, :, i]))
                g.append(flow)
                g.append(-flow)

        # (4) A cada cliente llega un único camión (considerando todo k,t,i)
        for j in self.customers:
            incoming = float(np.sum(x_bin[:, :, :, j]))
            expr = incoming - 1.0
            g.append(expr)
            g.append(-expr)

        # (5) Desde cada cliente sale un único camión (considerando todo k,t,j)
        for i in self.customers:
            outgoing = float(np.sum(x_bin[:, :, i, :]))
            expr = outgoing - 1.0
            g.append(expr)
            g.append(-expr)

        # (6) Coherencia temporal / eliminación de subtours
        for k in range(self.k_count):
            for t in range(self.t_count):
                for i in range(self.n_nodes):
                    for j in range(self.n_nodes):
                        if i == j:
                            continue
                        lhs = (
                            ts[k, i]
                            + d.service_var_i[i]
                            + d.service_fixed
                            + d.travel_time_tij[t, i, j]
                            - ts[k, j]
                            - d.big_m * (1.0 - x_bin[k, t, i, j])
                        )
                        g.append(float(lhs))

        # (7) Ventanas de tiempo por cliente
        for i in self.customers:
            ts_sum = float(np.sum(ts[:, i]))
            g.append(float(d.a_i[i] - ts_sum))
            g.append(float(ts_sum - d.b_i[i]))

        # (8) Tiempo de atención en intervalo
        for k in range(self.k_count):
            for t in range(self.t_count):
                lower_t = float(480.0 + 60.0 * d.z_t[t])
                upper_t = float(540.0 + 60.0 * d.z_t[t])
                for j in self.customers:
                    visit_in_interval = float(np.sum(x_bin[k, t, :, j]))
                    g.append(lower_t - ts[k, j] - d.big_m * (1.0 - visit_in_interval))
                    g.append(ts[k, j] - upper_t - d.big_m * (1.0 - visit_in_interval))

        # (9) Nodo sin atención no debe tener tiempo de atención activo
        for k in range(self.k_count):
            for i in self.customers:
                served = float(np.sum(x_bin[k, :, i, :]))
                g.append(float(ts[k, i] - d.big_m * served))

        # (10-13) Horas de salida del CD según sub-conjunto de camiones
        departure_targets = {"k11": 540.0, "k12": 900.0, "k21": 660.0, "k22": 1020.0}
        s0 = float(d.service_var_i[self.depot])
        for group_name, trucks in d.truck_groups.items():
            target = departure_targets[group_name]
            for k in trucks:
                expr = float(ts[k, self.depot] + s0 - target)
                g.append(expr)
                g.append(-expr)

        # (14) Duración máxima de ruta
        for k in range(self.k_count):
            route_duration = float(np.sum(x_bin[k] * d.travel_time_tij))
            g.append(route_duration - float(d.dmax_k[k]))

        # (15-18) Vuelta al CD según sub-conjunto de camiones
        for _, trucks in d.truck_groups.items():
            for k in trucks:
                returns_cd = float(np.sum(x_bin[k, :, self.customers, self.depot]))
                expr = returns_cd - 1.0
                g.append(expr)
                g.append(-expr)

        out["F"] = np.array([objective], dtype=float)
        out["G"] = np.array(g, dtype=float)


def build_toy_tdvrptw_data(
    n_customers: int = 6,
    n_trucks: int = 4,
    n_intervals: int = 4,
    seed: int = 42,
) -> TDVRPTWData:
    """
    Crea una instancia pequeña de juguete para pruebas de integración.
    """
    rng = np.random.default_rng(seed)
    n_nodes = n_customers + 1  # + depósito

    base_cost = rng.integers(5, 30, size=(n_nodes, n_nodes)).astype(float)
    np.fill_diagonal(base_cost, 0.0)

    travel_time = np.zeros((n_intervals, n_nodes, n_nodes), dtype=float)
    for t in range(n_intervals):
        congestion_factor = 1.0 + 0.15 * t
        travel_time[t] = base_cost * congestion_factor
        np.fill_diagonal(travel_time[t], 0.0)

    demand_volume = np.zeros(n_nodes, dtype=float)
    demand_mass = np.zeros(n_nodes, dtype=float)
    demand_volume[1:] = rng.uniform(0.3, 1.8, size=n_customers)
    demand_mass[1:] = rng.uniform(30.0, 180.0, size=n_customers)

    cap_volume = np.full(n_trucks, 8.0, dtype=float)
    cap_mass = np.full(n_trucks, 1200.0, dtype=float)

    a_i = np.zeros(n_nodes, dtype=float)
    b_i = np.full(n_nodes, 1440.0, dtype=float)
    a_i[1:] = 480 + rng.integers(0, 180, size=n_customers)
    b_i[1:] = a_i[1:] + rng.integers(120, 300, size=n_customers)

    service_var = np.zeros(n_nodes, dtype=float)
    service_var[1:] = rng.integers(5, 20, size=n_customers)

    z_t = np.arange(n_intervals, dtype=float)
    dmax = np.full(n_trucks, 480.0, dtype=float)

    # Reparto simple de camiones por turnos/rutas.
    groups = [[], [], [], []]
    for idx in range(n_trucks):
        groups[idx % 4].append(idx)

    return TDVRPTWData(
        cost_ij=base_cost,
        travel_time_tij=travel_time,
        demand_volume_i=demand_volume,
        demand_mass_i=demand_mass,
        cap_volume_k=cap_volume,
        cap_mass_k=cap_mass,
        a_i=a_i,
        b_i=b_i,
        service_var_i=service_var,
        service_fixed=10.0,
        z_t=z_t,
        dmax_k=dmax,
        k11=groups[0],
        k12=groups[1],
        k21=groups[2],
        k22=groups[3],
        big_m=1e4,
        volume_factor=0.8,
    )
