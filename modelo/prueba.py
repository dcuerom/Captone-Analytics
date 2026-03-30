from __future__ import annotations

import argparse
import os
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
    from pymoo.algorithms.soo.nonconvex.ga import GA
    from pymoo.core.repair import Repair
    from pymoo.core.sampling import Sampling
    from pymoo.operators.crossover.sbx import SBX
    from pymoo.operators.mutation.pm import PM
    from pymoo.operators.sampling.rnd import FloatRandomSampling
    from pymoo.optimize import minimize
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
    from .modelo_final import TDVRPTWProblem, build_toy_tdvrptw_data
    from .heuristica_savings import SavingsSeedResult, build_savings_seed
    from .datos_diarios import build_daily_problem_from_csv
except ImportError:
    # Ejecutando como script: python modelo/prueba.py
    from modelo_final import TDVRPTWProblem, build_toy_tdvrptw_data
    from heuristica_savings import SavingsSeedResult, build_savings_seed
    from datos_diarios import build_daily_problem_from_csv


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


class TDVRPTWRepair(Repair):
    """
    Reparacion ligera para bajar violaciones de restricciones en GA.
    """

    def _do(self, problem, X, **kwargs):
        X_work = np.asarray(X, dtype=float)
        if X_work.ndim == 1:
            X_work = X_work[None, :]

        X_out = X_work.copy()
        n_x = int(problem.n_x)
        k_count = int(problem.k_count)
        t_count = int(problem.t_count)
        n_nodes = int(problem.n_nodes)
        depot = int(problem.depot)
        customers = list(problem.customers)
        dep_target = problem._departure_target_by_truck()
        data = problem.instance

        ts_lb = np.asarray(problem.xl[n_x:], dtype=float).reshape(k_count, n_nodes)
        ts_ub = np.asarray(problem.xu[n_x:], dtype=float).reshape(k_count, n_nodes)

        for row in X_out:
            x_raw = row[:n_x].reshape(k_count, t_count, n_nodes, n_nodes)
            x_raw = np.clip(x_raw, 0.0, 1.0)

            # Prohibir auto-arcos.
            for i in range(n_nodes):
                x_raw[:, :, i, i] = 0.0
            row[:n_x] = x_raw.reshape(-1)

            x_bin = (x_raw >= 0.5).astype(np.int8)

            ts = row[n_x:].reshape(k_count, n_nodes)
            ts = np.clip(ts, ts_lb, ts_ub)

            # Fijar salida del deposito por subconjunto.
            for k, target in dep_target.items():
                ts[int(k), depot] = float(target)

            # Si nodo no es atendido por camion k, forzar ts=0 (alineado con restriccion 9).
            # Si es atendido, acercar ts a ventana [a_i, b_i].
            for k in range(k_count):
                for i in customers:
                    served = float(np.sum(x_bin[k, :, i, :]))
                    if served <= 0.5:
                        ts[k, i] = 0.0
                    else:
                        ts[k, i] = float(np.clip(ts[k, i], data.a_i[i], data.b_i[i]))

            row[n_x:] = ts.reshape(-1)

        if np.asarray(X).ndim == 1:
            return X_out[0]
        return X_out


def _print_seed_summary(seed_result: SavingsSeedResult) -> None:
    print("\n=== Semilla Heurística (Clarke & Wright) ===")
    print(f"Camiones usados por la heurística: {seed_result.used_trucks}")
    for k, route in seed_result.routes_by_truck.items():
        if route:
            txt = " -> ".join([f"C{c}" for c in route])
            print(f"  Camión {k}: DEPOT -> {txt} -> DEPOT")
        else:
            print(f"  Camión {k}: sin clientes asignados")


def _node_label(node: int, depot: int, node_labels: Dict[int, str] | None = None) -> str:
    if node_labels and node in node_labels:
        return str(node_labels[node])
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


def _format_route(
    nodes: Sequence[int],
    depot: int,
    node_labels: Dict[int, str] | None = None,
) -> str:
    return " -> ".join(_node_label(n, depot, node_labels=node_labels) for n in nodes)


def imprimir_rutas_camiones(
    x_bin: np.ndarray,
    depot: int,
    node_labels: Dict[int, str] | None = None,
) -> None:
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
            f"t{t + 1}:{_node_label(i, depot, node_labels)}->{_node_label(j, depot, node_labels)}"
            for t, i, j in arcs
        )
        print(f"Camión {k}:")
        print(f"  Arcos activos ({len(arcs)}): {arcs_txt}")

        if len(main_route) > 1:
            print(f"  Ruta principal: {_format_route(main_route, depot, node_labels=node_labels)}")
        else:
            print("  Ruta principal: sin salida desde DEPOT")

        if residual_routes:
            for idx, rr in enumerate(residual_routes, start=1):
                print(
                    f"  Subruta residual {idx}: {_format_route(rr, depot, node_labels=node_labels)}"
                )

        if unused_arcs:
            ua = ", ".join(
                f"t{t + 1}:{_node_label(i, depot, node_labels)}->{_node_label(j, depot, node_labels)}"
                for t, i, j in unused_arcs
            )
            print(f"  Arcos no incorporados en reconstrucción: {ua}")


def ejecutar_prueba_tdvrptw(
    pop_size: int = 80,
    n_gen: int = 60,
    seed: int = 42,
    use_heuristic_seed: bool = True,
    n_heuristic_seeds: int = 4,
    use_toy_data: bool = False,
    csv_path: str = "DatosSimulados/df_despacho.csv",
    target_date: str | None = None,
    max_orders: int | None = 40,
    n_trucks: int = 20,
    cost_per_km: float = 130.0,
    crossover_prob: float = 0.9,
    crossover_eta: float = 15.0,
    mutation_prob: float = 0.05,
    mutation_eta: float = 20.0,
) -> None:
    """
    Prueba de humo del modelo TD-VRPTW:
    - Instancia sintética.
    - Construcción de T_tij desde distancia usando modelo de Fleischmann.
    - Optimización con GA en PyMoo.
    """
    node_labels: Dict[int, str] | None = None
    if use_toy_data:
        data = build_toy_tdvrptw_data(n_customers=6, n_trucks=4, n_intervals=13, seed=seed)
        print("Modo datos: instancia sintética (toy).")
    else:
        csv_abs = csv_path
        if not os.path.isabs(csv_abs):
            csv_abs = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..",
                csv_path,
            )
        bundle = build_daily_problem_from_csv(
            csv_path=csv_abs,
            target_date=target_date,
            max_orders=max_orders,
            seed=seed,
            n_trucks=n_trucks,
            cost_per_km=cost_per_km,
        )
        data = bundle.problem_data
        node_labels = bundle.node_labels
        print(
            f"Modo datos: despacho diario real | fecha={bundle.selected_date} | "
            f"pedidos={len(bundle.daily_dispatch)} | camiones={n_trucks} | costo_km={cost_per_km} | "
            f"distancias={bundle.distance_source} | dia_semana={data.dia_semana}"
        )

    problem = TDVRPTWProblem(data)
    assigned_trucks = sorted(
        set(int(k) for group in data.truck_groups.values() for k in group)
    )
    n_customers = len(problem.customers)
    if n_customers < len(assigned_trucks):
        print(
            "Aviso de factibilidad estructural: hay menos clientes que camiones asignados "
            f"({n_customers} < {len(assigned_trucks)}). "
            "Con restricciones de salida/retorno = 1 por camion, es dificil o imposible hallar factibles."
        )

    sampling = FloatRandomSampling()
    if use_heuristic_seed:
        n_seed = max(1, int(n_heuristic_seeds))
        seed_vectors = []
        best_seed_result = None
        best_seed_cv = float("inf")
        best_seed_f = float("inf")

        for s_idx in range(n_seed):
            local_seed = int(seed + 97 * s_idx)
            seed_result = build_savings_seed(problem, seed=local_seed)
            seed_eval = problem.evaluate(
                seed_result.decision_vector,
                return_values_of=["F", "CV"],
                return_as_dictionary=True,
            )
            seed_f = float(np.ravel(seed_eval["F"])[0])
            seed_cv = float(np.ravel(seed_eval["CV"])[0])
            print(
                f"Semilla heuristica {s_idx + 1}/{n_seed} "
                f"(seed={local_seed}) -> F: {seed_f:.3f}, CV: {seed_cv:.6f}"
            )
            seed_vectors.append(seed_result.decision_vector)
            if seed_cv < best_seed_cv or (np.isclose(seed_cv, best_seed_cv) and seed_f < best_seed_f):
                best_seed_cv = seed_cv
                best_seed_f = seed_f
                best_seed_result = seed_result

        if best_seed_result is not None:
            _print_seed_summary(best_seed_result)
            print(f"Mejor semilla heuristica -> F: {best_seed_f:.3f}, CV: {best_seed_cv:.6f}")

        sampling = SavingsSeedSampling(seed_vectors)

    algorithm = GA(
        pop_size=pop_size,
        sampling=sampling,
        crossover=SBX(prob=crossover_prob, eta=crossover_eta),
        mutation=PM(prob=mutation_prob, eta=mutation_eta),
        repair=TDVRPTWRepair(),
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
        imprimir_rutas_camiones(x_bin, depot=problem.depot, node_labels=node_labels)
        return

    x_bin, ts = problem.decode_solution(res.X)
    print("\n=== Resultado de Prueba ===")
    print(f"Objetivo (costo total): {float(res.F[0]):.3f}")
    print(f"Violación total de restricciones (CV): {float(res.CV):.6f}")
    print(f"Arcos activos: {int(np.sum(x_bin))}")
    print(f"Min ts: {float(np.min(ts)):.2f} | Max ts: {float(np.max(ts)):.2f}")
    imprimir_rutas_camiones(x_bin, depot=problem.depot, node_labels=node_labels)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prueba de humo del modelo TD-VRPTW en PyMoo")
    parser.add_argument("--pop-size", type=int, default=80, help="Tamaño de población")
    parser.add_argument("--n-gen", type=int, default=60, help="Número de generaciones")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria")
    parser.add_argument("--n-heuristic-seeds", type=int, default=4, help="Cantidad de semillas Clarke & Wright para inicializar la poblacion")
    parser.add_argument("--csv-path", type=str, default="DatosSimulados/df_despacho.csv", help="Ruta al CSV de despacho")
    parser.add_argument("--fecha", type=str, default=None, help="Fecha de despacho (YYYY-MM-DD). Si se omite, usa la primera disponible")
    parser.add_argument("--max-orders", type=int, default=40, help="Máximo de pedidos del día para pruebas")
    parser.add_argument("--n-trucks", type=int, default=20, help="Cantidad de camiones para la prueba diaria")
    parser.add_argument("--cost-per-km", type=float, default=130.0, help="Costo por km para construir C_ij")
    parser.add_argument("--crossover-prob", type=float, default=0.9, help="Probabilidad de crossover SBX")
    parser.add_argument("--crossover-eta", type=float, default=15.0, help="Eta de crossover SBX")
    parser.add_argument("--mutation-prob", type=float, default=0.05, help="Probabilidad de mutacion PM")
    parser.add_argument("--mutation-eta", type=float, default=20.0, help="Eta de mutacion PM")
    parser.add_argument("--use-toy-data", action="store_true", help="Usa instancia sintética en vez del CSV diario")
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
        n_heuristic_seeds=args.n_heuristic_seeds,
        use_toy_data=args.use_toy_data,
        csv_path=args.csv_path,
        target_date=args.fecha,
        max_orders=args.max_orders,
        n_trucks=args.n_trucks,
        cost_per_km=args.cost_per_km,
        crossover_prob=args.crossover_prob,
        crossover_eta=args.crossover_eta,
        mutation_prob=args.mutation_prob,
        mutation_eta=args.mutation_eta,
    )
