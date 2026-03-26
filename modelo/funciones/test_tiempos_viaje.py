"""
test_tiempos_viaje.py — Instancia de prueba de la función de tiempos de viaje
sobre los arcos generados por el pipeline de `grafo/main.py`.

Este script:
  1. Ejecuta `execute_vrp_pipeline` con una muestra pequeña de pedidos.
  2. Toma las matrices de distancia (km) resultantes por cluster.
  3. Aplica la función τ_ij(t) de Fleischmann et al. (2004) para convertirlas
     en matrices de tiempos de viaje (horas) para distintos intervalos horarios.
  4. Imprime un reporte comparativo por arco con distancia y cada tiempo estimado.

Uso:
    cd /Users/dacm/udd/Captone-Analytics
    source capstone/bin/activate
    python modelo/funciones/test_tiempos_viaje.py
"""

import sys
import os
import pandas as pd
import numpy as np

# --- Ajuste de paths para que Python encuentre los módulos del proyecto ---
ROOT_DIR  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GRAFO_DIR = os.path.join(ROOT_DIR, 'grafo')
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, GRAFO_DIR)

from main import execute_vrp_pipeline
from modelo.funciones import (
    matrices_distancia_a_tiempo,
    distancia_a_tiempo_matrix,
    tau_ij_vec,
    Z_BREAKPOINTS,
)

# ---------------------------------------------------------------------------
# Parámetros de la instancia de prueba
# ---------------------------------------------------------------------------

SAMPLE_SIZE = 60    # Muestra suficiente para que DBSCAN forme al menos un cluster
DIA_SEMANA  = 0     # Lunes

# Horarios de partida a evaluar (minutos desde medianoche)
HORARIOS_PRUEBA = [540.0, 600.0, 780.0, 1020.0, 1200.0]
NOMBRES_HORARIOS = ["09:00", "10:00", "13:00", "17:00", "20:00"]

# ---------------------------------------------------------------------------
# 1. Ejecutar el pipeline de grafo para obtener matrices de distancia (km)
# ---------------------------------------------------------------------------

print("=" * 70)
print("  TEST: Tiempos de Viaje con Variación Temporal (Fleischmann, 2004)")
print("=" * 70)
print(f"\n  Muestra: {SAMPLE_SIZE} pedidos | Día: Lunes\n")

matrices_km, rutas_por_cluster = execute_vrp_pipeline(sample_size=SAMPLE_SIZE)

n_clusters = len(matrices_km)
print(f"\n  ✓ Pipeline finalizado. {n_clusters} cluster(s) generados.\n")

# ---------------------------------------------------------------------------
# 1b. Construir mapa id_nodo → Número de orden
#     (mismo campo que muestra el tooltip del mapa en visualizer.py línea 142)
# ---------------------------------------------------------------------------
# execute_vrp_pipeline devuelve matrices con índice = id_nodo.
# Para correlacionar con el mapa, necesitamos el 'Número de orden' que es la
# parte del id_nodo antes del '_'. Ej: 'ORD-CL-202612-001037_6283572K' -> 'ORD-CL-202612-001037'
import pandas as pd

def id_nodo_a_orden(id_nodo: str) -> str:
    """Extrae el 'Número de orden' desde un id_nodo de la forma '<orden>_<rut>'."""
    if id_nodo == 'DEPOT_01_BASE':
        return 'DEPOT'
    partes = str(id_nodo).rsplit('_', 1)   # split por el último '_' (rut puede tener '_')
    return partes[0] if len(partes) > 1 else id_nodo

# ---------------------------------------------------------------------------
# 2. Convertir matrices km → tiempos para cada horario de prueba
# ---------------------------------------------------------------------------

print("=" * 70)
print("  Convirtiendo matrices de distancia → tiempos de viaje (horas)")
print("=" * 70)

# Diccionario: horario → { cluster_id → DataFrame de tiempos }
matrices_tiempo_por_horario = {
    t: matrices_distancia_a_tiempo(matrices_km, t=t, dia_semana=DIA_SEMANA)
    for t in HORARIOS_PRUEBA
}

# ---------------------------------------------------------------------------
# 3. Reporte de arcos: por cluster, imprimir todos los arcos con sus tiempos
# ---------------------------------------------------------------------------

for cid, matriz_km in matrices_km.items():
    nodos = list(matriz_km.index)
    n     = len(nodos)
    arcos = [(i, j) for i in nodos for j in nodos if i != j]

    print(f"\n{'─' * 70}")
    print(f"  CLUSTER {cid}  |  {n} nodo(s)  |  {len(arcos)} arco(s)")
    print(f"{'─' * 70}")

    # Encabezado de la tabla
    col_horarios = "".join(f"  {h:>8}" for h in NOMBRES_HORARIOS)
    print(f"  {'Arco i → j':<42}  {'Dist(km)':>8}" + col_horarios + "  [tiempos en min]")
    print("  " + "-" * (42 + 10 + len(NOMBRES_HORARIOS) * 10 + 20))

    for (origen, destino) in arcos:
        dist = float(matriz_km.loc[origen, destino])
        if np.isinf(dist):
            continue   # Arcos sin conexión → se omiten del reporte

        # Usar 'Número de orden' para alinear con los tooltips del mapa HTML
        orden_origen  = id_nodo_a_orden(str(origen))
        orden_destino = id_nodo_a_orden(str(destino))
        etiqueta = f"{orden_origen:<22} → {orden_destino:<22}"

        tiempos_min = []
        for t in HORARIOS_PRUEBA:
            t_min = float(matrices_tiempo_por_horario[t][cid].loc[origen, destino])
            tiempos_min.append(round(t_min, 2))  # Ya está en minutos

        tiempo_cols = "".join(f"  {v:>8.2f}" for v in tiempos_min)
        print(f"  {etiqueta:<47}  {dist:>8.3f}" + tiempo_cols)

# ---------------------------------------------------------------------------
# 4. Resumen estadístico por cluster y horario
# ---------------------------------------------------------------------------

print(f"\n{'=' * 70}")
print("  RESUMEN: Tiempo promedio de viaje por cluster y horario (min)")
print(f"{'=' * 70}")
print(f"  {'Cluster':<12}" + "".join(f"  {h:>8}" for h in NOMBRES_HORARIOS))
print("  " + "-" * (12 + len(NOMBRES_HORARIOS) * 10))

for cid, matriz_km in matrices_km.items():
    fila = f"  {f'Cluster {cid}':<12}"
    for t in HORARIOS_PRUEBA:
        df_t = matrices_tiempo_por_horario[t][cid]
        # Obtener sólo las celdas fuera de la diagonal (arcos reales)
        mask = ~np.eye(len(df_t), dtype=bool)
        valores = df_t.values[mask].astype(float)
        finitos = valores[np.isfinite(valores)]
        promedio_min = np.mean(finitos) if len(finitos) > 0 else float('nan')
        fila += f"  {promedio_min:>8.2f}"
    print(fila)

print(f"\n  ✓ Test completado exitosamente.")

# ---------------------------------------------------------------------------
# 5. Validación tau_ij_vec: verificar consistencia con versión escalar
#    (relevante para confirmar compatibilidad con PyMoo donde t es array)
# ---------------------------------------------------------------------------

print(f"\n{'=' * 70}")
print("  VALIDACIÓN tau_ij_vec (versión vectorizada para PyMoo)")
print(f"{'=' * 70}")

from modelo.funciones.tiempos_viaje import tau_ij

dist_test = np.array([2.0, 5.0, 10.0, 15.0, 20.0])
t_test    = np.array([540.0, 630.0, 780.0, 1038.0, 1200.0])
dia_test  = 0  # Lunes

# Vectorizado
vec_result = tau_ij_vec(dist_test, t_test, dia_test)

# Escalar, uno a uno
scalar_result = np.array([
    tau_ij(d, t, dia_test) for d, t in zip(dist_test, t_test)
])

print(f"\n  {'dist(km)':<12} {'t(min)':<10} {'escalar(min)':<16} {'vec(min)':<14} {'match?'}")
print("  " + "-" * 62)
for d, t, s, v in zip(dist_test, t_test, scalar_result, vec_result):
    match = "✓" if abs(s - v) < 1e-9 else "✗ DIFERENCIA"
    print(f"  {d:<12.1f} {t:<10.1f} {s:<16.4f} {v:<14.4f} {match}")

all_match = np.allclose(scalar_result, vec_result)
print(f"\n  {'✓ tau_ij_vec es consistente con tau_ij (escalar).' if all_match else '✗ INCONSISTENCIA DETECTADA — revisar implementación.'}")
print(f"\n  Uso en PyMoo (_evaluate):")
print(f"    t_decision = x[:, idx_t]                         # array shape (pop_size,)")
print(f"    tiempos    = tau_ij_vec(dist_ij, t_decision, dia_semana=0)  # array shape (pop_size,)")
