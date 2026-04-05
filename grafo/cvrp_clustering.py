import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from typing import Dict, Tuple

def run_euclidean_agglomerative_clustering(
    df: pd.DataFrame, 
    df_depot: pd.DataFrame, 
    n_clusters: int
) -> Tuple[Dict[int, pd.DataFrame], pd.DataFrame]:
    """
    Agrupa los nodos basado puramente en sus coordenadas Euclidianas X, Y usando 
    Clustering Aglomerativo con enlace de varianza Ward.
    """
    X = df[['x', 'y']].to_numpy(dtype=float)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    agglomerative = AgglomerativeClustering(n_clusters=n_clusters, metric='euclidean', linkage='ward')
    labels = agglomerative.fit_predict(X_scaled)
    
    df_clustered = df.copy()
    df_clustered['cluster_label'] = labels
    
    valid_clusters = np.unique(labels)
    clusters_dict = {}
    
    for c in valid_clusters:
        clusters_dict[c] = df_clustered[df_clustered['cluster_label'] == c].copy()
        
    outliers = pd.DataFrame(columns=df.columns) # Agglomerative no produce ruido
    
    print(f"Clustering Euclidiano completado: {len(valid_clusters)} clusters formados usando Agglomerative Clustering (Ward).")
    return clusters_dict, outliers
