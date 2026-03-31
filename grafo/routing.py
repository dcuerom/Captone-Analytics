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
    
    # Pre-filtrar nodos únicos de osmnx para acelerar búsqueda
    target_nodes = set(osmnx_nodos)
    
    # En lugar de N x N A* paths, realizamos 1 expansión radial de Dijkstra por cada Origen ÚNICO
    # Esto disminuye la carga exponencialmente desde O(N^2) hacia O(N) accesos en árbol.
    unique_sources = list(set(osmnx_nodos))
    
    # Diccionario de caché radial {source_osmnx: (lengths_dict, paths_dict)}
    dijkstra_radial_cache = {}
    
    for origen_gra in unique_sources:
        try:
            # Dijkstra evalúa tooodo el subgrafo alcanzable simultáneamente respetando las calles reales
            lengths, paths = nx.single_source_dijkstra(G, origen_gra, weight='length')
            
            # MEMORY FIX (OOM Prevention): 
            # Interceptar y guardar de la RAM masiva SÓLO las rutas hacia los destinos de nuestro clúster particular.
            filtered_lengths = {tgt: lengths[tgt] for tgt in target_nodes if tgt in lengths}
            filtered_paths = {tgt: paths[tgt] for tgt in target_nodes if tgt in paths}
            
            dijkstra_radial_cache[origen_gra] = (filtered_lengths, filtered_paths)
            
            # Orden de destrucción forzada de diccionarios gigantes (500,000 llaves) a Garbage Collector
            del lengths
            del paths
            
        except Exception as e:
            # Si el nodo es completamente inalcanzable (isla de asfalto desconectada)
            dijkstra_radial_cache[origen_gra] = ({}, {})

    # Ahora simplemente cruzamos el producto cartesiano O(N^2) con diccionarios Hash en O(1) puro
    for i in range(n):
        for j in range(n):
            if i != j:
                origen_gra = osmnx_nodos[i]
                destino_gra = osmnx_nodos[j]
                
                origen_id = ids_nodos[i]
                destino_id = ids_nodos[j]
                
                lengths_dict, paths_dict = dijkstra_radial_cache.get(origen_gra, ({}, {}))
                
                if destino_gra in lengths_dict:
                    dist_mts = lengths_dict[destino_gra]
                    ruta = paths_dict[destino_gra]
                else:
                    dist_mts = float('inf')
                    ruta = []
                
                matriz.loc[origen_id, destino_id] = round(dist_mts, 3)
                info_rutas[f"{origen_id}->{destino_id}"] = {
                    "distancia_m": round(dist_mts, 3),
                    "ruta_nodos_osmnx": ruta
                }
                
    print(f"Matriz y rutas calculadas mediante {len(unique_sources)} saltos Dijkstra exitosamente.")
    return matriz, info_rutas
