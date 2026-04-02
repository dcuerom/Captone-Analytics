import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from typing import Dict, Tuple

def run_euclidean_clustering(df: pd.DataFrame, df_depot: pd.DataFrame, k_trucks: int = None) -> Tuple[Dict[int, pd.DataFrame], pd.DataFrame]:
    """
    Agrupa los nodos basado puramente en sus coordenadas Euclidianas X, Y.
    Utiliza KMeans si se conoce la cantidad de camiones esperados (k_trucks),
    o heurística si no se provee. Retorna clusters_dict y outliers_df.
    """
    if k_trucks is None or k_trucks <= 1:
        # Si no hay K o es 1, todo a un solo cluster
        clusters_dict = {1: df.copy()}
        outliers = pd.DataFrame(columns=df.columns)
        return clusters_dict, outliers
        
    X = df[['x', 'y']].to_numpy(dtype=float)
    
    # Asegurarnos de no pedir más clusters que el número de nodos
    n_clusters = min(k_trucks, len(X))
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    labels = kmeans.fit_predict(X)
    
    df_clustered = df.copy()
    df_clustered['cluster_label'] = labels
    
    clusters_dict = {}
    for c in range(n_clusters):
        clusters_dict[c+1] = df_clustered[df_clustered['cluster_label'] == c].copy()
        
    outliers = pd.DataFrame(columns=df.columns) # KMeans no deja outliers nativamente
    
    print(f"Clustering Euclidiano completado: {n_clusters} clusters formados usando KMeans.")
    return clusters_dict, outliers

