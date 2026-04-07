"""
heuristica_construccion.py
==========================
Implementa la heurística de Clarke & Wright Savings para el CVRP Euclidiano.

Objetivo:
---------
Generar una permutación inicial de clientes de alta calidad que sirva como
"semilla" (warm start) para el Algoritmo Genético en PyMoo. Esto transforma
el GA puro en un Algoritmo Híbrido / Memético, acelerando la convergencia
y reduciendo el espacio de búsqueda infactible.

Algoritmo de Clarke & Wright Savings (1964):
--------------------------------------------
1. Construir rutas triviales: Depósito → Cliente_i → Depósito  (una por cliente).
2. Calcular el "ahorro" de fusionar dos rutas que visitan i y j:
       saving(i,j) = d(depot, i) + d(depot, j) - d(i, j)
3. Ordenar todos los pares (i,j) por ahorro descendente.
4. Fusionar rutas si no se viola la capacidad del vehículo.
5. La permutación resultante es el orden aplanado de visitas en todas las rutas.
"""

import numpy as np
import pandas as pd
from typing import List


def clarke_wright_savings(
    clientes_ids: List[str],
    depot_id: str,
    matriz_dist: pd.DataFrame,
    peso_dict: dict,
    cap_peso: float
) -> List[int]:
    """
    Ejecuta el algoritmo de Ahorros de Clarke & Wright y devuelve una
    permutación de índices (0-based sobre `clientes_ids`) lista para
    inyectar al GA de PyMoo.

    Parámetros
    ----------
    clientes_ids : list[str]
        Lista ordenada de IDs de cliente (sin el depósito).
    depot_id : str
        ID del nodo depósito en la matriz de distancias.
    matriz_dist : pd.DataFrame
        Matriz de distancias Euclidiana cuadrada (nodo × nodo).
    peso_dict : dict
        Mapa {cliente_id: demanda} con la demanda de cada cliente.
    cap_peso : float
        Capacidad máxima de carga de un vehículo.

    Retorna
    -------
    list[int]
        Permutación de índices 0-based que representa la secuencia óptima
        heurística de visitas. Lista de largo == len(clientes_ids).
    """
    n = len(clientes_ids)
    idx = {cid: i for i, cid in enumerate(clientes_ids)}

    # --- Paso 1: Calcular ahorros para todos los pares (i, j), i ≠ j ---
    savings = []
    for i in range(n):
        for j in range(i + 1, n):
            ci = clientes_ids[i]
            cj = clientes_ids[j]
            d_depot_i = float(matriz_dist.loc[depot_id, ci])
            d_depot_j = float(matriz_dist.loc[depot_id, cj])
            d_ij = float(matriz_dist.loc[ci, cj])
            s = d_depot_i + d_depot_j - d_ij
            savings.append((s, ci, cj))

    # Ordenar de mayor a menor ahorro
    savings.sort(key=lambda x: x[0], reverse=True)

    # --- Paso 2: Inicializar rutas triviales (una ruta por cliente) ---
    # Representamos cada ruta como una lista de cliente-ids
    rutas = [[cid] for cid in clientes_ids]
    carga_ruta = {i: peso_dict.get(cid, 0.0) for i, cid in enumerate(clientes_ids)}

    # Diccionario de pertenencia: cliente_id → índice de ruta
    pertenencia = {cid: i for i, cid in enumerate(clientes_ids)}

    # --- Paso 3: Fusionar rutas aplicando ahorros ---
    for s, ci, cj in savings:
        r_i = pertenencia.get(ci)
        r_j = pertenencia.get(cj)

        # Condiciones para fusionar:
        # 1) Están en rutas distintas
        # 2) ci es el ÚLTIMO nodo de su ruta (o ruta de 1 elemento) → se añade al final
        # 3) cj es el PRIMER nodo de su ruta (o ruta de 1 elemento) → se añade al inicio
        # 4) La carga combinada no excede la capacidad
        if r_i is None or r_j is None or r_i == r_j:
            continue

        ruta_i = rutas[r_i]
        ruta_j = rutas[r_j]

        if ruta_i is None or ruta_j is None:
            continue

        carga_combinada = carga_ruta[r_i] + carga_ruta[r_j]
        if carga_combinada > cap_peso:
            continue

        # ci debe ser el último de su ruta, cj el primero de la suya
        ci_es_final = (ruta_i[-1] == ci)
        cj_es_inicio = (ruta_j[0] == cj)

        if not (ci_es_final and cj_es_inicio):
            # Intentar inversión: ci como inicio de ruta i, fusionar al revés
            ci_es_inicio = (ruta_i[0] == ci)
            cj_es_final = (ruta_j[-1] == cj)
            if ci_es_inicio and cj_es_final:
                # Invertir ruta i
                rutas[r_i] = list(reversed(ruta_i))
                ruta_i = rutas[r_i]
                # Ahora ci es el final de ruta_i
            else:
                continue

        # Fusionar: ruta_i + ruta_j
        nueva_ruta = ruta_i + ruta_j
        nueva_carga = carga_combinada

        # Actualizar estructura de datos
        nuevo_idx = r_i
        rutas[nuevo_idx] = nueva_ruta
        carga_ruta[nuevo_idx] = nueva_carga
        rutas[r_j] = None  # Marcar como absorbida

        for nodo in nueva_ruta:
            pertenencia[nodo] = nuevo_idx

    # --- Paso 4: Aplanar rutas → permutación de índices ---
    orden_clientes = []
    for ruta in rutas:
        if ruta is not None:
            orden_clientes.extend(ruta)

    # Convertir IDs a índices 0-based
    permutacion = [idx[cid] for cid in orden_clientes]

    return permutacion


def generar_semilla_cw(
    clientes_ids: List[str],
    depot_id: str,
    matriz_dist: pd.DataFrame,
    peso_dict: dict,
    cap_peso: float
) -> np.ndarray:
    """
    Wrapper conveniente que devuelve la permutación como np.ndarray de int,
    listo para ser usado como individuo en PyMoo.
    """
    perm = clarke_wright_savings(clientes_ids, depot_id, matriz_dist, peso_dict, cap_peso)
    return np.array(perm, dtype=int)
