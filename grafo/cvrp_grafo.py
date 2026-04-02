import pandas as pd
import numpy as np
import math

def calculate_euclidean_routing(df_cluster: pd.DataFrame, df_depot: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Calcula una matriz de distancias euclidianas exactas (float) para
    el conjunto de nodos de un cluster más el depósito.
    Simula la estructura final esperada sin requerir A* de OSMnx.
    """
    # Concatenar todos los nodos
    df_all = pd.concat([df_cluster, df_depot], ignore_index=True)
    df_all['id_nodo'] = df_all['id_nodo'].astype(str)
    
    nodos = df_all['id_nodo'].tolist()
    x_coords = df_all['x'].tolist()
    y_coords = df_all['y'].tolist()
    
    n = len(nodos)
    
    # Crear dataframe base indexado
    matriz = pd.DataFrame(index=nodos, columns=nodos, dtype=float)
    info_rutas = {}
    
    for i in range(n):
        for j in range(n):
            if i == j:
                matriz.loc[nodos[i], nodos[j]] = 0.0
            else:
                x1, y1 = x_coords[i], y_coords[i]
                x2, y2 = x_coords[j], y_coords[j]
                
                # Distancia euclidiana exacta
                dist = math.hypot(x1 - x2, y1 - y2)
                
                matriz.loc[nodos[i], nodos[j]] = dist
                
                info_rutas[f"{nodos[i]}->{nodos[j]}"] = {
                    "distancia_m": dist,
                    "ruta_nodos_osmnx": [] # No hay ruta física
                }
                
    print(f"Generada matriz Euclidiana exacta para {n} nodos.")
    return matriz, info_rutas
