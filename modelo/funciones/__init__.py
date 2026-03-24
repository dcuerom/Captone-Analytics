"""
Package `modelo/funciones/`

Funciones matemáticas auxiliares para el modelo de optimización VRP.
Expone la función de tiempo de viaje variable (Fleischmann et al., 2004)
en versión escalar (tau_ij) y vectorizada/PyMoo-compatible (tau_ij_vec).
"""

from .tiempos_viaje import (
    tau_ij,
    tau_ij_vec,
    tau_minimo,
    velocidad_para_intervalo,
    distancia_a_tiempo_matrix,
    matrices_distancia_a_tiempo,
    Z_0,
    Z_K,
    K,
    Z_BREAKPOINTS,
    SPEED_TABLE_KMH,
    DELTA_DEFAULT,
)

__all__ = [
    "tau_ij",
    "tau_ij_vec",
    "tau_minimo",
    "velocidad_para_intervalo",
    "distancia_a_tiempo_matrix",
    "matrices_distancia_a_tiempo",
    "Z_0",
    "Z_K",
    "K",
    "Z_BREAKPOINTS",
    "SPEED_TABLE_KMH",
    "DELTA_DEFAULT",
]
