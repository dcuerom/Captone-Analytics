import osmnx as ox
import networkx as nx
import folium
import pandas as pd
from typing import Dict, Any, Optional

def plot_network_and_routes(
    G: nx.MultiDiGraph, 
    info_rutas: Optional[Dict[str, Any]] = None, 
    filepath: str = "grafo_rutas.html"
):
    """
    Exporta las rutas A* calculadas hacia un mapa interactivo (HTML) usando Folium.
    Extrae las geometrías reales de la red vial para un renderizado ultra-preciso.
    """
    print("Generando mapa interactivo en formato HTML mediante Folium...")
    
    list_of_routes = []
    if info_rutas:
        for k, info in info_rutas.items():
            ruta = info.get('ruta_nodos_osmnx', [])
            if len(ruta) > 1:
                list_of_routes.append((k, ruta))
                
    if not list_of_routes:
        print("Atención: No hay rutas para graficar. Generando mapa base...")
        nodes = ox.graph_to_gdfs(G, edges=False)
        center_lat = nodes['y'].mean()
        center_lng = nodes['x'].mean()
        m = folium.Map(location=[center_lat, center_lng], zoom_start=11)
        m.save(filepath)
        return
        
    print(f"Añadiendo {len(list_of_routes)} rutas interactivas al mapa...")
    
    # Calcular centro para el mapa usando el primer nodo de la primera ruta
    first_route_nodes = list_of_routes[0][1]
    center_lat = G.nodes[first_route_nodes[0]]['y']
    center_lng = G.nodes[first_route_nodes[0]]['x']
    m = folium.Map(location=[center_lat, center_lng], zoom_start=11, tiles="CartoDB positron")
    
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue', 'darkpurple', 'pink', 'black']
    
    for i, (nombre_ruta, ruta_nodos) in enumerate(list_of_routes):
        color = colors[i % len(colors)]
        
        # Ensamblar las coordenadas geométricas exactas de las aristas recorridas
        route_coords = []
        for u, v in zip(ruta_nodos[:-1], ruta_nodos[1:]):
            edge_data = G.get_edge_data(u, v)
            if edge_data is not None and 0 in edge_data and 'geometry' in edge_data[0]:
                # Trazo con curvatura real de calle
                geom = edge_data[0]['geometry']
                for x, y in geom.coords:
                    route_coords.append((y, x))
            else:
                # Trazo recto en intersecciones mínimas o nodos simplificados
                lat1, lng1 = G.nodes[u]['y'], G.nodes[u]['x']
                lat2, lng2 = G.nodes[v]['y'], G.nodes[v]['x']
                if not route_coords:
                    route_coords.append((lat1, lng1))
                route_coords.append((lat2, lng2))
                
        # Agregar la PolyLine al mapa Folium interactivo
        folium.PolyLine(
            locations=route_coords,
            color=color,
            weight=4,
            opacity=0.8,
            tooltip=f"Ruta: {nombre_ruta}"
        ).add_to(m)
        
        # Marcar los extremos de la ruta
        folium.Marker(route_coords[0], popup=f"Inicio: {nombre_ruta}").add_to(m)
        folium.Marker(route_coords[-1], popup=f"Fin: {nombre_ruta}", icon=folium.Icon(color="green")).add_to(m)
        
    m.save(filepath)
    print(f"Mapa interactivo con rutas guardado exitosamente en {filepath}")


def plot_cluster_results(
    clusters_dict: dict, 
    outliers: pd.DataFrame, 
    filepath: str = "mapa_clusters_santiago.html"
):
    """
    Genera un mapa HTML con Folium coloreando cada nodo según su clúster de DBSCAN.
    Los outliers se grafican en negro.
    """
    print(f"Generando visualización de clusters en {filepath}...")
    
    # Obtener el centro del mapa a partir del primer cluster o de los outliers
    center_lat, center_lng = -33.4489, -70.6693 # Default Santiago
    if clusters_dict:
        first_c = list(clusters_dict.keys())[0]
        if not clusters_dict[first_c].empty:
            center_lat = clusters_dict[first_c]['latitud'].mean()
            center_lng = clusters_dict[first_c]['longitud'].mean()
            
    m = folium.Map(location=[center_lat, center_lng], zoom_start=11, tiles="CartoDB positron")
    
    # Paleta de colores para usar en los distintos clusters
    colors = [
        'red', 'blue', 'green', 'purple', 'orange', 
        'darkred', 'cadetblue', 'darkpurple', 'pink', 'lightgray', 
        'lightgreen', 'darkblue', 'darkgreen', 'lightblue'
    ]
    
    # Graficar Outliers (Ruido)
    if not outliers.empty:
        for idx, row in outliers.iterrows():
            folium.CircleMarker(
                location=[row['latitud'], row['longitud']],
                radius=4,
                color='black',
                fill=True,
                fill_opacity=0.7,
                tooltip=f"Outlier: {row.get('Número de orden', 'N/A')}"
            ).add_to(m)

    # Graficar Clusters Válidos
    for i, (c_id, df_c) in enumerate(clusters_dict.items()):
        color = colors[i % len(colors)]
        
        for idx, row in df_c.iterrows():
            is_depot = row.get('RUT') == 'BASE'
            
            if is_depot:
                # El depósito se destaca con un marcador especial
                folium.Marker(
                    location=[row['latitud'], row['longitud']],
                    icon=folium.Icon(color=color, icon='home', prefix='fa'),
                    tooltip=f"Depósito (Cluster {c_id})"
                ).add_to(m)
            else:
                folium.CircleMarker(
                    location=[row['latitud'], row['longitud']],
                    radius=5,
                    color=color,
                    fill=True,
                    fill_opacity=0.9,
                    tooltip=f"Orden: {row.get('Número de orden', 'N/A')} | Cluster: {c_id}"
                ).add_to(m)

    m.save(filepath)
    print(f"Mapa de clusters guardado exitosamente en {filepath}")

if __name__ == "__main__":
    print("Módulo 'visualizer' listo. Importa 'plot_network_and_routes' o 'plot_cluster_results'.")
