"""
tiempos_viaje.py — Función de Tiempo de Viaje con Variación Temporal

Referencia:
    Fleischmann, B., Gietz, M. y Gnutzmann, S. (2004).
    Time-Varying Travel Times in Vehicle Routing.
    Transportation Science, 38(2), 160-173.

Modelo matemático (ec. 2.2):
    Sea τ_ijk = tiempo mínimo de viaje (i→j) cuando la partida ocurre en el intervalo Z_k.
    El día se divide en K intervalos horarios Z_k = [z_{k-1}, z_k).

    La función de tiempo de viaje τ_ij(t) se define como:

        τ_ij(t) = τ_ijk                               si z_{k-1} + δ_{ij,k-1} ≤ t ≤ z_k - δ_ijk
        τ_ij(t) = τ_ijk + (t - z_k + δ_ijk) * s_ijk  si z_k - δ_ijk ≤ t ≤ z_k + δ_ijk

    donde la pendiente de transición entre intervalos es:
        s_ijk = (τ_{ij,k+1} - τ_ijk) / (2 * δ_ijk)

    y δ_ijk es el parámetro de suavizado en la frontera z_k (elegido como δ = 0.25 h por defecto),
    con δ_ij0 = δ_ijK = 0 (sin suavizado en los extremos del horizonte).

Parámetros del problema:
    - K  = 13 intervalos (k = 1...13)
    - Horizonte de planificación: [z_0, z_K] = [09:00, 21:00] horas
    - Longitud de cada intervalo: 1 hora
    - Velocidades en km/h → tiempos de viaje obtenidos en horas.
"""

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constantes del horizonte de planificación
# ---------------------------------------------------------------------------

Z_0 = 540.0    # Hora de inicio del horizonte (09:00 = 9 * 60 min)
Z_K = 1260.0   # Hora de fin del horizonte   (21:00 = 21 * 60 min)
K   = 13       # Número de intervalos Z_k

# Breakpoints z_k para k = 0, 1, ..., K  (14 puntos delimitan 13 intervalos)
Z_BREAKPOINTS = np.linspace(Z_0, Z_K, K + 1)   # [540, 600, 660, ..., 1260]

# Parámetro δ de suavizado en la linealización (en minutos)
DELTA_DEFAULT = 15.0

# ---------------------------------------------------------------------------
# Matriz de velocidades por hora y día de semana (km/h)
#
# Índice fila : hora del día  (0 = 00:00, 1 = 01:00, ..., 23 = 23:00)
# Índice col  : día de semana (0 = Lunes, 1 = Martes, ..., 6 = Domingo)
# ---------------------------------------------------------------------------

SPEED_TABLE_KMH = np.array([
    # Lun  Mar  Mié  Jue  Vie  Sáb  Dom
    [  34,  33,  33,  32,  32,  30,  31],  # 00:00
    [  35,  34,  33,  33,  33,  32,  32],  # 01:00
    [  35,  35,  34,  34,  34,  33,  33],  # 02:00
    [  37,  37,  35,  35,  34,  33,  34],  # 03:00
    [  38,  39,  37,  36,  35,  33,  34],  # 04:00
    [  39,  39,  38,  38,  38,  34,  34],  # 05:00
    [  35,  36,  36,  36,  36,  37,  36],  # 06:00
    [  24,  24,  24,  24,  26,  38,  37],  # 07:00
    [  20,  19,  20,  20,  23,  35,  38],  # 08:00
    [  23,  21,  22,  21,  24,  32,  36],  # 09:00 → k=1
    [  25,  23,  24,  23,  25,  29,  34],  # 10:00 → k=2
    [  25,  24,  24,  23,  24,  27,  33],  # 11:00 → k=3
    [  25,  23,  23,  23,  23,  25,  32],  # 12:00 → k=4
    [  25,  24,  23,  23,  22,  24,  31],  # 13:00 → k=5
    [  26,  25,  24,  24,  22,  25,  32],  # 14:00 → k=6
    [  26,  25,  25,  25,  21,  28,  32],  # 15:00 → k=7
    [  25,  24,  24,  23,  19,  29,  32],  # 16:00 → k=8
    [  21,  20,  20,  19,  17,  29,  32],  # 17:00 → k=9
    [  18,  17,  17,  16,  19,  29,  32],  # 18:00 → k=10
    [  22,  21,  20,  20,  24,  29,  31],  # 19:00 → k=11
    [  28,  27,  26,  26,  26,  28,  31],  # 20:00 → k=12
    [  30,  29,  29,  29,  27,  29,  32],  # 21:00 → k=13
    [  32,  31,  30,  30,  29,  30,  33],  # 22:00
    [  33,  32,  31,  31,  29,  30,  34],  # 23:00
], dtype=float)

# Velocidades sólo para los K intervalos del horizonte [09:00, 21:00)
# Como Z_0 ahora es 540, para obtener el índice de fila (hora 9) dividimos por 60
_SPEED_HORIZON = SPEED_TABLE_KMH[int(Z_0 / 60): int(Z_0 / 60) + K, :]   # shape (13, 7)


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def velocidad_para_intervalo(k: int, dia_semana: int) -> float:
    """
    Devuelve la velocidad media (km/h) para el intervalo k (1-indexado) y el día de la semana.

    Parámetros
    ----------
    k : int
        Índice del intervalo horario, k ∈ {1, …, K}.
        El intervalo k cubre [z_{k-1}, z_k) = [Z_0 + k-1, Z_0 + k) horas.
    dia_semana : int
        Día de la semana (0=Lunes, …, 6=Domingo).

    Retorna
    -------
    float : velocidad media en km/h.
    """
    if not (1 <= k <= K):
        raise ValueError(f"k debe estar en [1, {K}], se recibió k={k}")
    if not (0 <= dia_semana <= 6):
        raise ValueError(f"dia_semana debe estar en [0, 6], se recibió {dia_semana}")
    return _SPEED_HORIZON[k - 1, dia_semana]


def tau_minimo(distancia_km: float, k: int, dia_semana: int) -> float:
    """
    Calcula τ_ijk = tiempo mínimo de viaje para una distancia dada en el intervalo k.
    Se asume velocidad constante dentro del intervalo.

    τ_ijk = (distancia_ij / velocidad_k) * 60  [minutos]
    """
    v = velocidad_para_intervalo(k, dia_semana)
    if v == 0.0:
        return float('inf')
    return (distancia_km / v) * 60.0


def tau_ij(distancia_km: float, t: float, dia_semana: int, delta: float = DELTA_DEFAULT) -> float:
    """
    Función ESCALAR de tiempo de viaje variable τ_ij(t) según Fleischmann et al. (2004), ec. 2.2.

    Recibe un único tiempo de partida t (float) y retorna un único valor (float).
    Para uso con arrays o variables de decisión de PyMoo, usar `tau_ij_vec`.

    Implementación de la ecuación (2.2):

        Región estable (interior del intervalo k):
            τ_ij(t) = τ_ijk
            válida cuando: z_{k-1} + δ_{ij,k-1} ≤ t ≤ z_k - δ_ijk

        Región de transición (vecindad de la frontera z_k):
            τ_ij(t) = τ_ijk + (t - z_k + δ_ijk) · s_ijk
            válida cuando: z_k - δ_ijk ≤ t ≤ z_k + δ_ijk

        con pendiente: s_ijk = (τ_{ij,k+1} - τ_ijk) / (2 · δ_ijk)

    Parámetros
    ----------
    distancia_km : float
        Distancia de la ruta i→j en km (salida de `calculate_routing_for_day`).
    t : float
        Hora de partida escalar en minutos desde medianoche. Ej: 570 = 09:30.
    dia_semana : int
        Día de la semana (0=Lunes, …, 6=Domingo).
    delta : float, opcional
        Parámetro de suavizado δ en minutos (default = 15.0 min).

    Retorna
    -------
    float : tiempo de viaje estimado en minutos.
    """
    if distancia_km == 0.0:
        return 0.0

    t_clamped = float(np.clip(t, Z_0, Z_K))

    k_idx = int(np.searchsorted(Z_BREAKPOINTS, t_clamped, side='right')) - 1
    k_idx = int(np.clip(k_idx, 0, K - 1))
    k     = k_idx + 1

    z_prev = Z_BREAKPOINTS[k_idx]
    z_curr = Z_BREAKPOINTS[k_idx + 1]

    tau_k = tau_minimo(distancia_km, k, dia_semana)

    delta_right = 0.0 if k == K else delta
    if k < K and t_clamped >= z_curr - delta_right:
        tau_k1 = tau_minimo(distancia_km, k + 1, dia_semana)
        s = (tau_k1 - tau_k) / (2.0 * delta_right) if delta_right > 0 else 0.0
        return tau_k + (t_clamped - z_curr + delta_right) * s

    delta_left = 0.0 if k == 1 else delta
    if k > 1 and t_clamped <= z_prev + delta_left:
        tau_k_prev = tau_minimo(distancia_km, k - 1, dia_semana)
        s = (tau_k - tau_k_prev) / (2.0 * delta_left) if delta_left > 0 else 0.0
        return tau_k_prev + (t_clamped - z_prev + delta_left) * s

    return tau_k


def tau_ij_vec(
    distancia_km: np.ndarray,
    t: np.ndarray,
    dia_semana: int,
    delta: float = DELTA_DEFAULT
) -> np.ndarray:
    """
    Función VECTORIZADA de tiempo de viaje τ_ij(t) — compatible con variables de decisión PyMoo.

    Implementa la misma ecuación (2.2) de Fleischmann et al. (2004) que `tau_ij`, pero
    opera sobre arrays NumPy de forma eficiente. Es la versión correcta para usar dentro
    del método `_evaluate()` del modelo PyMoo cuando `t` es una variable de decisión.

    Diseño vectorial:
    -----------------
    Para cada par (distancia_km[i], t[i]), calcula τ_ij usando operaciones matriciales:
      1. Identifica el intervalo k activo para cada t[i] con `np.searchsorted` vectorizado.
      2. Construye tensores (N_arcos × K) de τ_ijk y aplica condiciones booleanas.
      3. El resultado es un array de forma equivalente a distancia_km / t.

    Parámetros
    ----------
    distancia_km : np.ndarray, shape (N,) o escalar
        Distancias de cada arco i→j en km.
        Puede ser un escalar, un vector 1-D o un array de cualquier forma.
    t : np.ndarray, shape (N,) o escalar
        Tiempos de partida en horas desde medianoche para cada arco.
        Debe ser compatible en forma con `distancia_km` (broadcast numpy estándar).
        En el contexto del modelo VRP, cada t[i] es la hora de salida del nodo i,
        almacenada como variable de decisión continua en el vector `x` de PyMoo.
    dia_semana : int
        Día de la semana (0=Lunes, …, 6=Domingo). Constante para toda la evaluación.
    delta : float, opcional
        Parámetro de suavizado δ en horas (default = 0.25 h).

    Retorna
    -------
    np.ndarray : tiempos de viaje en horas, misma forma que las entradas.

    Ejemplo en PyMoo
    ----------------
    En el método `_evaluate` del modelo VRP, los tiempos de partida t_{ij}
    son variables de decisión extraídas del cromosoma x:

        def _evaluate(self, x, out, *args, **kwargs):
            # x tiene shape (pop_size, n_var) en modo vectorizado
            # Supongamos que x[:, idx_t] contiene los tiempos de partida
            t_decision = x[:, idx_t]          # shape (pop_size,)
            dist_arco  = distancias[i, j]     # float constante del arco

            tiempos = tau_ij_vec(dist_arco, t_decision, dia_semana=0)
            # tiempos tiene shape (pop_size,) → un tiempo por individuo
    """
    d = np.asarray(distancia_km, dtype=float)
    t_arr = np.asarray(t, dtype=float)
    t_c   = np.clip(t_arr, Z_0, Z_K)

    # Resultado inicializado en cero (los arcos d=0 son auto-loops)
    result = np.zeros_like(d, dtype=float)
    mask_nonzero = (d != 0.0)

    if not np.any(mask_nonzero):
        return result

    # Velocidades del horizonte: shape (K, 7)
    speeds = _SPEED_HORIZON[:, dia_semana]   # shape (K,)

    # Identificar intervalo k activo para cada elemento
    # k_idx: 0-indexado, shape igual a t_arr
    k_idx = np.searchsorted(Z_BREAKPOINTS, t_c, side='right') - 1
    k_idx = np.clip(k_idx, 0, K - 1).astype(int)
    k_1indexed = k_idx + 1   # 1-indexado para la tabla de velocidades

    # τ_ijk para el intervalo activo de cada muestra (convertido a minutos)
    v_k  = speeds[k_idx]                        # shape igual a t_arr
    tau_k_arr = np.where(v_k > 0, (d / v_k) * 60.0, np.inf)

    z_prev_arr = Z_BREAKPOINTS[k_idx]           # z_{k-1} para cada muestra
    z_curr_arr = Z_BREAKPOINTS[np.minimum(k_idx + 1, K)]  # z_k para cada muestra

    # --- Zona de transición derecha: t ≥ z_k - δ  (y k < K) ---
    is_last = (k_1indexed == K)
    delta_right = np.where(is_last, 0.0, delta)

    in_right = mask_nonzero & ~is_last & (t_c >= z_curr_arr - delta_right)
    if np.any(in_right):
        k_next_idx = np.minimum(k_idx + 1, K - 1)
        v_k1 = speeds[k_next_idx]
        tau_k1_arr = np.where(v_k1 > 0, (d / v_k1) * 60.0, np.inf)
        dr = delta_right
        s = np.where(dr > 0, (tau_k1_arr - tau_k_arr) / (2.0 * dr), 0.0)
        result = np.where(in_right,
                          tau_k_arr + (t_c - z_curr_arr + dr) * s,
                          result)

    # --- Zona de transición izquierda: t ≤ z_{k-1} + δ  (y k > 1) ---
    is_first = (k_1indexed == 1)
    delta_left = np.where(is_first, 0.0, delta)

    in_left = mask_nonzero & ~is_first & (t_c <= z_prev_arr + delta_left) & ~in_right
    if np.any(in_left):
        k_prev_idx = np.maximum(k_idx - 1, 0)
        v_kp = speeds[k_prev_idx]
        tau_kp_arr = np.where(v_kp > 0, (d / v_kp) * 60.0, np.inf)
        dl = delta_left
        s = np.where(dl > 0, (tau_k_arr - tau_kp_arr) / (2.0 * dl), 0.0)
        result = np.where(in_left,
                          tau_kp_arr + (t_c - z_prev_arr + dl) * s,
                          result)

    # --- Zona estable ---
    in_stable = mask_nonzero & ~in_right & ~in_left
    result = np.where(in_stable, tau_k_arr, result)

    return result


# ---------------------------------------------------------------------------
# Conversión de matrices de distancia → matrices de tiempo
# ---------------------------------------------------------------------------

def distancia_a_tiempo_matrix(
    matriz_distancias: pd.DataFrame,
    t: float,
    dia_semana: int,
    delta: float = DELTA_DEFAULT
) -> pd.DataFrame:
    """
    Convierte una matriz NxN de distancias (km) generada por `routing.py` en una
    matriz de tiempos de viaje (horas) usando τ_ij(t).

    Parámetros
    ----------
    matriz_distancias : pd.DataFrame
        Matriz NxN con distancias en km. Índice y columnas son `id_nodo`.
        Corresponde directamente a la salida de `calculate_routing_for_day()`.
    t : float
        Hora de partida (horas desde medianoche). Ej: 9.5 = 09:30.
    dia_semana : int
        Día de la semana (0=Lunes, …, 6=Domingo).
    delta : float, opcional
        Parámetro de suavizado δ (default = 0.25 h).

    Retorna
    -------
    pd.DataFrame : Matriz NxN de tiempos de viaje en horas, con los mismos
                   índices y columnas que `matriz_distancias`.
    """
    ids = list(matriz_distancias.index)
    tiempo_matrix = pd.DataFrame(0.0, index=ids, columns=ids)

    for i in ids:
        for j in ids:
            if i == j:
                tiempo_matrix.loc[i, j] = 0.0
            else:
                dist = float(matriz_distancias.loc[i, j])
                if np.isinf(dist) or np.isnan(dist):
                    tiempo_matrix.loc[i, j] = float('inf')
                else:
                    tiempo_matrix.loc[i, j] = tau_ij(dist, t, dia_semana, delta)

    return tiempo_matrix


def matrices_distancia_a_tiempo(
    matrices_por_cluster: dict,
    t: float,
    dia_semana: int,
    delta: float = DELTA_DEFAULT
) -> dict:
    """
    Convierte el diccionario completo de matrices de distancia (salida de
    `execute_vrp_pipeline`) en matrices de tiempo de viaje.

    Parámetros
    ----------
    matrices_por_cluster : dict
        { cluster_id: DataFrame NxN de distancias en km }
        Salida directa de `execute_vrp_pipeline()` en `grafo/main.py`.
    t : float
        Hora de partida (horas desde medianoche).
    dia_semana : int
        Día de la semana (0=Lunes, …, 6=Domingo).
    delta : float, opcional
        Parámetro de suavizado δ (default = 0.25 h).

    Retorna
    -------
    dict : { cluster_id: DataFrame NxN de tiempos de viaje en horas }

    Ejemplo
    -------
    >>> from grafo.main import execute_vrp_pipeline
    >>> from modelo.funciones import matrices_distancia_a_tiempo
    >>>
    >>> matrices_km, rutas, _ = execute_vrp_pipeline(sample_size=50)
    >>> matrices_h = matrices_distancia_a_tiempo(matrices_km, t=9.0, dia_semana=0)
    >>> print(matrices_h[0])
    """
    return {
        cid: distancia_a_tiempo_matrix(df_dist, t, dia_semana, delta)
        for cid, df_dist in matrices_por_cluster.items()
    }
