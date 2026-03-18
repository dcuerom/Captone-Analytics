import osmnx as ox
import networkx as nx
import folium
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

if __name__ == "__main__":
    print("Módulo 'visualizer' listo. Importa 'plot_network_and_routes'.")
