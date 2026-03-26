import pandas as pd
import networkx as nx
import osmnx as ox
from typing import Dict, Tuple, Any

def clean_rut(rut: str) -> str:
    """Elimina puntos y guiones del RUT para construir la llave principal."""
    if not isinstance(rut, str):
        rut = str(rut)
    return rut.replace('.', '').replace('-', '').strip().upper()

def calculate_routing_for_day(df_day: pd.DataFrame, G: nx.MultiDiGraph) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Calcula la red estricta en función del día, determinando la ruta mínima
    con A Star (A*) y generando una matriz de distancias en metros.
    
    Requisitos del dataframe:
    Debe contener al menos: 'Rut' o 'RUT', 'Número de orden' o 'Número de Orden', 'latitud', 'longitud'
    """
    df = df_day.copy()
    
    # El id_nodo ya viene construido desde la orquestación (main.py o clustering.py)
    if 'id_nodo' not in df.columns:
        raise ValueError("El DataFrame debe contener la columna 'id_nodo' pre-calculada.")
    
    df_validos = df.dropna(subset=['latitud', 'longitud']).copy()
    
    if len(df_validos) == 0:
        print("Atención: No hay coordenadas válidas para calcular rutas este día.")
        return pd.DataFrame(), {}
        
    print(f"Calculando rutas para {len(df_validos)} nodos (pedidos) usando A*...")
    
    # 2. Asociar cada coordenada al nodo más cercano en el grafo de calles
    xs = df_validos['longitud'].tolist()
    ys = df_validos['latitud'].tolist()
    
    # nearest_nodes vectorizado es eficiente
    nearest_nodes_list = ox.distance.nearest_nodes(G, X=xs, Y=ys)
    df_validos['osmnx_node'] = nearest_nodes_list
    
    # 3. Generar la matriz de distancias cruzada usando A* (en m)
    ids_nodos = df_validos['id_nodo'].tolist()
    osmnx_nodos = df_validos['osmnx_node'].tolist()
    
    n = len(ids_nodos)
    
    # Configurar el origen matricial N x N
    matriz = pd.DataFrame(index=ids_nodos, columns=ids_nodos, dtype=float)
    # Diagonal principal es 0
    for idi in ids_nodos:
        matriz.loc[idi, idi] = 0.0
        
    info_rutas = {}
    
    for i in range(n):
        for j in range(n):
            if i != j:
                origen_gra = osmnx_nodos[i]
                destino_gra = osmnx_nodos[j]
                
                origen_id = ids_nodos[i]
                destino_id = ids_nodos[j]
                
                # Para evitar cálculos dobles si el grafo fuese no dirigido
                # Pero la red vehicular es MultiDiGraph (dirigido, con sentidos de calle),
                # por lo que matriz[i,j] no necesariamente es igual a matriz[j,i]
                
                try:
                    # Se usa astar_path con el peso 'length' que osmnx ya calculó en metros
                    ruta = nx.astar_path(G, origen_gra, destino_gra, weight='length')
                    
                    # Calcular la distancia sumando el 'length'
                    dist_mts = nx.path_weight(G, ruta, weight='length')
                    
                except nx.NetworkXNoPath:
                    # En caso de que áreas no estén conectadas en la red estricta
                    dist_mts = float('inf')
                    ruta = []
                
                matriz.loc[origen_id, destino_id] = round(dist_mts, 3)
                info_rutas[f"{origen_id}->{destino_id}"] = {
                    "distancia_m": round(dist_mts, 3),
                    "ruta_nodos_osmnx": ruta
                }
                
    print("Matriz y rutas calculadas exitosamente.")
    return matriz, info_rutas
