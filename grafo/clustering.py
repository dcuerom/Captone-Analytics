import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple
from itertools import permutations

# =====================================================================
# TAREA 1: Extracción y Transformación de Datos
# =====================================================================
def build_feature_matrix(
    df: pd.DataFrame, 
    time_column: str = 'tiempo_minutos', 
    default_window_start_hour: int = 9
) -> Tuple[np.ndarray, pd.DataFrame]:
    """
    Construye la matriz N x 3 con [Latitud, Longitud, Tiempo_Minutos].
    Si el dataframe trae la columna especificada en 'time_column', la utiliza,
    permitiendo que cada cliente tenga su ventana específica. 
    De lo contrario, asume el valor por defecto provisto (ej. 9:00 -> 540).
    """
    df_clean = df.copy()
    
    # Manejo de nombres de columna
    col_lat = 'latitud' if 'latitud' in df_clean.columns else 'Latitud'
    col_lon = 'longitud' if 'longitud' in df_clean.columns else 'Longitud'
    
    # Descartar nulos espaciales
    df_clean = df_clean.dropna(subset=[col_lat, col_lon]).copy()
    
    # Manejar Tiempo Dinámico
    if time_column in df_clean.columns:
        # Se forza la conversión numérica (cualquier basura se va a NaN y luego al default)
        df_clean['tiempo_minutos_modelo'] = pd.to_numeric(df_clean[time_column], errors='coerce')
        df_clean['tiempo_minutos_modelo'].fillna(default_window_start_hour * 60, inplace=True)
    else:
        df_clean['tiempo_minutos_modelo'] = default_window_start_hour * 60
    
    # Crear la matriz N x 3
    X = df_clean[[col_lat, col_lon, 'tiempo_minutos_modelo']].to_numpy(dtype=float)
    
    return X, df_clean

# =====================================================================
# TAREA 2: Normalización y Ponderación
# =====================================================================
def normalize_and_weight(X: np.ndarray, alpha_time: float = 1.0) -> Tuple[np.ndarray, StandardScaler]:
    """
    Aplica StandardScaler para llevar las unidades espaciales y temporales
    a varianza 1 y media 0. Luego pondera la columna de tiempo por alpha_time.
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Ponderar la columna de tiempo (índice 2)
    X_scaled[:, 2] = X_scaled[:, 2] * alpha_time
    
    return X_scaled, scaler


# =====================================================================
# TAREA 3: Ejecución de DBSCAN
# =====================================================================
def run_dbscan(X_scaled: np.ndarray, eps: float = 0.5, min_samples: int = 5) -> np.ndarray:
    """
    Configura y ejecuta el algoritmo DBSCAN. Retorna los labels del clustering.
    - eps: radio de vecindad en espacio normalizado.
    - min_samples: mínima cantidad de puntos para núcleo denso.
    """
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X_scaled)
    return labels


# =====================================================================
# TAREA 4: Gestión de Clusters y Ruido (Outliers)
# =====================================================================
def manage_clusters_and_noise(
    df: pd.DataFrame, 
    labels: np.ndarray, 
    X_scaled: np.ndarray, 
    rescue_threshold: float = 1.0,
    force_rescue: bool = False
) -> Tuple[Dict[int, pd.DataFrame], pd.DataFrame]:
    """
    Agrupa clientes por cluster, aísla el ruido (-1) e intenta rescatar 
    aquellos outliers. Si force_rescue es True, los asigna al cluster 
    más cercano (centroide x,y,t) sin importar la distancia, dejando 0 outliers finales.
    """
    df['cluster_label'] = labels
    
    # Encontrar centroides de los clusters válidos
    valid_clusters = [lbl for lbl in np.unique(labels) if lbl != -1]
    centroids = {}
    for c in valid_clusters:
        idx_c = np.where(labels == c)[0]
        cent = np.mean(X_scaled[idx_c], axis=0)
        centroids[c] = cent

    # Heurística de Rescate de Outliers
    for i in range(len(labels)):
        if labels[i] == -1 and len(centroids) > 0:
            point = X_scaled[i]
            # Calcular distancias a todos los centroides
            distances = {c: np.linalg.norm(point - cent) for c, cent in centroids.items()}
            nearest_c = min(distances, key=distances.get)
            min_dist = distances[nearest_c]
            
            # Si el outlier está lo suficientemente cerca, o forzamos su rescate, lo reasignamos
            if force_rescue or min_dist <= rescue_threshold:
                df.iloc[i, df.columns.get_loc('cluster_label')] = nearest_c

    # Separación Lógica Final
    clusters_dict = {}
    for c in valid_clusters:
        clusters_dict[c] = df[df['cluster_label'] == c].copy()
        
    outliers = df[df['cluster_label'] == -1].copy()
    
    print(f"Clustering Result: {len(valid_clusters)} clusters formados.")
    print(f"Outliers restantes (no asignados): {len(outliers)}")
    
    return clusters_dict, outliers


# =====================================================================
# TAREA 5: Generación de Entradas para A*
# =====================================================================
def generate_astar_inputs(
    clusters_dict: Dict[int, pd.DataFrame], 
    depot_node_id: str, 
    id_column: str = 'id_nodo'
) -> Dict[int, List[Tuple[str, str]]]:
    """
    Itera sobre cada cluster, inyecta el ID del nodo Depósito y genera
    una lista exhaustiva de todos los pares origen-destino posibles intra-cluster,
    reduciendo drásticamente las permutaciones globales.
    
    Retorna: { cluster_id: [(origen, destino), (origen, destino), ...] }
    """
    cluster_pairs = {}
    
    for c_id, df_cluster in clusters_dict.items():
        if id_column not in df_cluster.columns:
            # Si id_nodo no está precalculado, generamos una lista genérica
            nodos = [f"NODO_{i}" for i in range(len(df_cluster))]
        else:
            nodos = df_cluster[id_column].tolist()
            
        # Añadir el depósito al cluster
        if depot_node_id not in nodos:
            nodos.append(depot_node_id)
            
        # Construcción de pares permutados (Grafo Dirigido -> A -> B y B -> A)
        # itertools.permutations genera todos los pares (u,v) sin (v,v).
        pares = list(permutations(nodos, 2))
        cluster_pairs[c_id] = pares
        
    return cluster_pairs


def run_clustering_pipeline(
    df: pd.DataFrame, 
    depot_id: str, 
    id_column: str = 'id_nodo', 
    force_outlier_rescue: bool = False,
    time_column: str = 'ventana_tiempo_minutos'
) -> Tuple[Dict, pd.DataFrame, Dict]:
    """
    Encapsula toda la lógica de clustering (Cluster-First) en un solo pipe.
    Retorna los DataFrames por cluster, los outliers y los pares listos para A*.
    Si 'force_outlier_rescue' es True, garantiza que la lista de outliers devuelta sea vacía 
    absorbiendo el ruido en el cluster estadísticamente más cercano en la norma x, y, tiempo.
    El parámetro time_column especifica qué columna usar para la 3ra dimensión (minutos desde las 00:00).
    """
    print("\n--- Ejecutando pre-procesamiento CLUSTER-FIRST ---")
    
    # 1. Extracción con Tiempo Dinámico
    X, df_clean = build_feature_matrix(df, time_column=time_column, default_window_start_hour=9)
    
    # 2. Normalización (alpha=1.0 por defecto, pero escalable)
    X_scaled, _ = normalize_and_weight(X, alpha_time=5.0)
    
    # 3. DBSCAN
    # Nota: Los hiperparámetros eps y min_samples requieren calibración 
    # según la densidad de la ciudad y el tamaño de la flota.
    labels = run_dbscan(X_scaled, eps=0.3, min_samples=5)
    
    # 4. Gestión
    clusters_dict, outliers = manage_clusters_and_noise(
        df_clean, labels, X_scaled, rescue_threshold=0.8, force_rescue=force_outlier_rescue
    )
    
    # 5. Generación de entradas
    pairs_for_astar = generate_astar_inputs(clusters_dict, depot_id, id_column=id_column)
    
    print("Pre-procesamiento finalizado.")
    return clusters_dict, outliers, pairs_for_astar
