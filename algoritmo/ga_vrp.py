import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM

# Importar el modelo definido en la carpeta de modelo (descomentar cuando sea necesario)
# import sys; sys.path.append('..')
# from modelo.vrp_pymoo import VRPModel

def ejecutar_algoritmo_genetico(problem, pop_size=100, n_gen=50):
    """
    Configura y ejecuta un algoritmo genético genérico (NSGA-II) usando PyMoo.
    Puedes cambiar a otros algoritmos como GA, NSGA3, dependiendo de los requerimientos.
    """
    algorithm = NSGA2(
        pop_size=pop_size,
        sampling=FloatRandomSampling(),
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True
    )

    print(f"Iniciando optimización con PyMoo (n_gen={n_gen}, pop_size={pop_size})...")
    res = minimize(
        problem,
        algorithm,
        ('n_gen', n_gen),
        seed=42,
        verbose=True
    )
    
    return res

if __name__ == "__main__":
    print("Módulo de algoritmo genético inicializado.")
    # Ejemplo de uso de la integración:
    # problem = VRPModel()
    # resultado = ejecutar_algoritmo_genetico(problem)
    # print("Mejor solución del espacio de diseño:", resultado.X)
    # print("Valores objetivos:", resultado.F)
