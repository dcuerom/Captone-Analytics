from __future__ import annotations

import numpy as np
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.optimize import minimize

from modelo_final import TDVRPTWProblem, build_toy_tdvrptw_data


def ejecutar_prueba_tdvrptw(pop_size: int = 80, n_gen: int = 60, seed: int = 42) -> None:
    data = build_toy_tdvrptw_data(n_customers=6, n_trucks=4, n_intervals=4, seed=seed)
    problem = TDVRPTWProblem(data)

    algorithm = GA(
        pop_size=pop_size,
        sampling=FloatRandomSampling(),
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
        print("No se encontró solución candidata.")
        return

    x_bin, ts = problem.decode_solution(res.X)
    print("\n=== Resultado de Prueba ===")
    print(f"Objetivo (costo total): {float(res.F[0]):.3f}")
    print(f"Violación total de restricciones (CV): {float(res.CV):.6f}")
    print(f"Arcos activos: {int(np.sum(x_bin))}")
    print(f"Min ts: {float(np.min(ts)):.2f} | Max ts: {float(np.max(ts)):.2f}")


if __name__ == "__main__":
    ejecutar_prueba_tdvrptw()
