from __future__ import annotations

import argparse
from typing import Dict, List, Sequence, Tuple

import numpy as np
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.core.sampling import Sampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.optimize import minimize

try:
    # Ejecutando como paquete: python -m modelo.prueba
    from .modelo_final import TDVRPTWProblem, build_toy_tdvrptw_data
    from .heuristica_savings import SavingsSeedResult, build_savings_seed
except ImportError:
    # Ejecutando como script: python modelo/prueba.py
    from modelo_final import TDVRPTWProblem, build_toy_tdvrptw_data
    from heuristica_savings import SavingsSeedResult, build_savings_seed


class SavingsSeedSampling(Sampling):
    """
    Muestreo inicial de PyMoo con inyección de una o más semillas heurísticas.
    """

    def __init__(self, seed_vectors: Sequence[np.ndarray]):
        super().__init__()
        self.seed_vectors = [np.asarray(v, dtype=float) for v in seed_vectors]

    def _do(self, problem, n_samples, **kwargs):
        # Base aleatoria para completar población.
        X = np.random.random((n_samples, problem.n_var))

        # Respetar límites de las variables de tiempo.
        if hasattr(problem, "n_x"):
            n_x = int(problem.n_x)
            ts_len = problem.n_var - n_x
            if ts_len > 0:
                lb = np.asarray(problem.xl[n_x:], dtype=float)
                ub = np.asarray(problem.xu[n_x:], dtype=float)
                X[:, n_x:] = lb + (ub - lb) * np.random.random((n_samples, ts_len))

        # Insertar semillas en los primeros individuos.
        n_seed = min(len(self.seed_vectors), n_samples)
        for i in range(n_seed):
            X[i, :] = self.seed_vectors[i]
        return X


def _print_seed_summary(seed_result: SavingsSeedResult) -> None:
    print("\n=== Semilla Heurística (Clarke & Wright) ===")
    print(f"Camiones usados por la heurística: {seed_result.used_trucks}")
    for k, route in seed_result.routes_by_truck.items():
        if route:
            txt = " -> ".join([f"C{c}" for c in route])
            print(f"  Camión {k}: DEPOT -> {txt} -> DEPOT")
        else:
            print(f"  Camión {k}: sin clientes asignados")


def _node_label(node: int, depot: int) -> str:
    return "DEPOT" if node == depot else f"C{node}"


def _extract_active_arcs_by_truck(x_bin: np.ndarray) -> Dict[int, List[Tuple[int, int, int]]]:
    """
    Retorna {k: [(t, i, j), ...]} con arcos activos por camión.
    """
    active: Dict[int, List[Tuple[int, int, int]]] = {}
    n_trucks = x_bin.shape[0]
    for k in range(n_trucks):
        idx = np.argwhere(x_bin[k] == 1)
        arcs = [(int(t), int(i), int(j)) for t, i, j in idx]
        arcs.sort(key=lambda a: (a[0], a[1], a[2]))
        if arcs:
            active[k] = arcs
    return active


def _reconstruct_path_from_arcs(
    arcs: Sequence[Tuple[int, int, int]],
    depot: int,
) -> Tuple[List[int], List[List[int]], List[Tuple[int, int, int]]]:
    """
    Reconstruye una ruta principal desde DEPOT y subrutas residuales.
    """
    indexed = list(enumerate(arcs))
    out_map: Dict[int, List[Tuple[int, int, int]]] = {}
    for arc_idx, (t, i, j) in indexed:
        out_map.setdefault(i, []).append((t, j, arc_idx))
    for i in out_map:
        out_map[i].sort(key=lambda x: (x[0], x[1]))

    used = set()

    def take_next(curr: int):
        for t, j, idx in out_map.get(curr, []):
            if idx not in used:
                used.add(idx)
                return t, j, idx
        return None

    main_route = [depot]
    current = depot
    guard = 0
    max_steps = len(arcs) + 2
    while guard < max_steps:
        guard += 1
        nxt = take_next(current)
        if nxt is None:
            break
        _, j, _ = nxt
        main_route.append(j)
        current = j

    residual_routes: List[List[int]] = []
    for start_idx, (_, i, _) in indexed:
        if start_idx in used:
            continue
        chain = [i]
        current = i
        guard = 0
        while guard < max_steps:
            guard += 1
            nxt = take_next(current)
            if nxt is None:
                break
            _, j, _ = nxt
            chain.append(j)
            current = j
        if len(chain) > 1:
            residual_routes.append(chain)

    unused_arcs = [arcs[idx] for idx, _ in indexed if idx not in used]
    return main_route, residual_routes, unused_arcs


def _format_route(nodes: Sequence[int], depot: int) -> str:
    return " -> ".join(_node_label(n, depot) for n in nodes)


def imprimir_rutas_camiones(x_bin: np.ndarray, depot: int) -> None:
    """
    Imprime rutas de texto por camión para camiones efectivamente usados.
    """
    active_by_truck = _extract_active_arcs_by_truck(x_bin)
    print("\n=== Rutas Por Camión (texto) ===")
    if not active_by_truck:
        print("No hay camiones utilizados (sin arcos activos).")
        return

    for k, arcs in active_by_truck.items():
        main_route, residual_routes, unused_arcs = _reconstruct_path_from_arcs(arcs, depot)

        arcs_txt = ", ".join(
            f"t{t + 1}:{_node_label(i, depot)}->{_node_label(j, depot)}" for t, i, j in arcs
        )
        print(f"Camión {k}:")
        print(f"  Arcos activos ({len(arcs)}): {arcs_txt}")

        if len(main_route) > 1:
            print(f"  Ruta principal: {_format_route(main_route, depot)}")
        else:
            print("  Ruta principal: sin salida desde DEPOT")

        if residual_routes:
            for idx, rr in enumerate(residual_routes, start=1):
                print(f"  Subruta residual {idx}: {_format_route(rr, depot)}")

        if unused_arcs:
            ua = ", ".join(
                f"t{t + 1}:{_node_label(i, depot)}->{_node_label(j, depot)}"
                for t, i, j in unused_arcs
            )
            print(f"  Arcos no incorporados en reconstrucción: {ua}")


def ejecutar_prueba_tdvrptw(
    pop_size: int = 80,
    n_gen: int = 60,
    seed: int = 42,
    use_heuristic_seed: bool = True,
) -> None:
    """
    Prueba de humo del modelo TD-VRPTW:
    - Instancia sintética.
    - Construcción de T_tij desde distancia usando modelo de Fleischmann.
    - Optimización con GA en PyMoo.
    """
    data = build_toy_tdvrptw_data(n_customers=6, n_trucks=4, n_intervals=4, seed=seed)
    problem = TDVRPTWProblem(data)

    sampling = FloatRandomSampling()
    if use_heuristic_seed:
        seed_result = build_savings_seed(problem, seed=seed)
        _print_seed_summary(seed_result)
        seed_eval = problem.evaluate(
            seed_result.decision_vector,
            return_values_of=["F", "CV"],
            return_as_dictionary=True,
        )
        seed_f = float(np.ravel(seed_eval["F"])[0])
        seed_cv = float(np.ravel(seed_eval["CV"])[0])
        print(f"Heurística inicial -> F: {seed_f:.3f}, CV: {seed_cv:.6f}")
        sampling = SavingsSeedSampling([seed_result.decision_vector])

    algorithm = GA(
        pop_size=pop_size,
        sampling=sampling,
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True,
    )

    print("Iniciando prueba TD-VRPTW en PyMoo...")
    res = minimize(
        problem,
        algorithm,
        ("n_gen", n_gen),
        seed=seed,
        verbose=True,
    )

    if res.X is None:
        # En problemas altamente restringidos, puede no aparecer factibilidad en pocas generaciones.
        # Igual reportamos el mejor individuo por CV para validar que el pipeline de optimización corre.
        best_idx = int(np.argmin(res.pop.get("CV")))
        best = res.pop[best_idx]
        best_cv = float(np.ravel(best.CV)[0])
        best_f = float(np.ravel(best.F)[0])
        x_bin, ts = problem.decode_solution(best.X)
        print("\n=== Resultado de Prueba (sin factible) ===")
        print("No se encontró solución factible en esta corrida corta.")
        print(f"Mejor CV encontrado: {best_cv:.6f}")
        print(f"Objetivo del mejor infeasible: {best_f:.3f}")
        print(f"Arcos activos: {int(np.sum(x_bin))}")
        print(f"Min ts: {float(np.min(ts)):.2f} | Max ts: {float(np.max(ts)):.2f}")
        imprimir_rutas_camiones(x_bin, depot=problem.depot)
        return

    x_bin, ts = problem.decode_solution(res.X)
    print("\n=== Resultado de Prueba ===")
    print(f"Objetivo (costo total): {float(res.F[0]):.3f}")
    print(f"Violación total de restricciones (CV): {float(res.CV):.6f}")
    print(f"Arcos activos: {int(np.sum(x_bin))}")
    print(f"Min ts: {float(np.min(ts)):.2f} | Max ts: {float(np.max(ts)):.2f}")
    imprimir_rutas_camiones(x_bin, depot=problem.depot)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prueba de humo del modelo TD-VRPTW en PyMoo")
    parser.add_argument("--pop-size", type=int, default=80, help="Tamaño de población")
    parser.add_argument("--n-gen", type=int, default=60, help="Número de generaciones")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria")
    parser.add_argument(
        "--no-heuristic-seed",
        action="store_true",
        help="Desactiva la inyección inicial de la heurística Clarke & Wright",
    )
    args = parser.parse_args()
    ejecutar_prueba_tdvrptw(
        pop_size=args.pop_size,
        n_gen=args.n_gen,
        seed=args.seed,
        use_heuristic_seed=not args.no_heuristic_seed,
    )
