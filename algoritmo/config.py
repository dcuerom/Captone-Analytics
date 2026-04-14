"""
Configuracion por defecto del optimizador TDVRPTW.

Mantiene un unico contrato de parametros entre:
- backend/api_server.py (GET /optimize-config, POST /optimize)
- algoritmo/genetic_algorithm.py (merge_config)
- frontend (panel Planning)
"""

DEFAULT_OPTIMIZATION_CONFIG = {
    # Modelo de costos/capacidades
    "t_inicio": 540.0,  # 09:00
    "cap_vol_cm3": 3_750_000.0,  # 3.75 m3
    "cap_peso_g": 803_333.0,  # 803.333 kg
    "factor_s": 1.2,
    "alpha_espera": 50_000.0,
    "costo_fijo_camion": 100_000.0,
    "d_max_min": 300.0,  # 5h por bloque
    # Algoritmo genetico
    "ga_pop_size": 100,
    "ga_n_gen": 200,
    "ga_seed": 42,
    # Operacion global
    "max_vehiculos_globales": 20,
    # Clustering
    "clustering_time_column": "a_ventana",
    "clustering_default_window_start_hour": 9,
    "clustering_alpha_time": 10.0,
    "clustering_eps": 0.3,
    "clustering_min_samples": 3,
    "clustering_rescue_threshold": 0.8,
    "force_outlier_rescue": True,
    # Operacion de deposito (se puede sobreescribir por API)
    "depot_address": "Santa Elena - Sierra Bella, Santiago, RM, Chile",
}
