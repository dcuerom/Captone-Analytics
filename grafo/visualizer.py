import osmnx as ox
import networkx as nx
import folium
import pandas as pd
from typing import Dict, Any, Optional

SANTIAGO_CENTER = (-33.4489, -70.6693)
SANTIAGO_BOUNDS_SW = (-33.75, -71.05)
SANTIAGO_BOUNDS_NE = (-33.20, -70.35)


def _build_santiago_base_map(zoom_start: int = 11) -> folium.Map:
    m = folium.Map(
        location=[SANTIAGO_CENTER[0], SANTIAGO_CENTER[1]],
        zoom_start=zoom_start,
        tiles="CartoDB positron",
        control_scale=True,
    )
    # Mantiene el mapa enfocado en RM/Santiago para navegación y zoom inicial.
    m.fit_bounds([
        [SANTIAGO_BOUNDS_SW[0], SANTIAGO_BOUNDS_SW[1]],
        [SANTIAGO_BOUNDS_NE[0], SANTIAGO_BOUNDS_NE[1]],
    ])
    return m


def _best_edge_coords(G: nx.MultiDiGraph, u: Any, v: Any):
    edge_data = G.get_edge_data(u, v)
    if not edge_data:
        return [(G.nodes[u]['y'], G.nodes[u]['x']), (G.nodes[v]['y'], G.nodes[v]['x'])]

    # MultiDiGraph puede tener múltiples keys; elegimos la arista más corta.
    best = min(
        edge_data.values(),
        key=lambda e: float(e.get("length", float("inf")))
    )
    geom = best.get("geometry")
    if geom is not None:
        return [(y, x) for x, y in geom.coords]

    return [(G.nodes[u]['y'], G.nodes[u]['x']), (G.nodes[v]['y'], G.nodes[v]['x'])]


def _build_route_coords_from_osmnx_path(G: nx.MultiDiGraph, ruta_nodos: list):
    route_coords = []
    for u, v in zip(ruta_nodos[:-1], ruta_nodos[1:]):
        segment = _best_edge_coords(G, u, v)
        if not segment:
            continue
        if route_coords and route_coords[-1] == segment[0]:
            route_coords.extend(segment[1:])
        else:
            route_coords.extend(segment)
    return route_coords

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
        m = _build_santiago_base_map(zoom_start=11)
        m.save(filepath)
        return
        
    print(f"Añadiendo {len(list_of_routes)} rutas interactivas al mapa...")
    
    # Calcular centro para el mapa usando el primer nodo de la primera ruta
    first_route_nodes = list_of_routes[0][1]
    _ = G.nodes[first_route_nodes[0]]['y']
    _ = G.nodes[first_route_nodes[0]]['x']
    m = _build_santiago_base_map(zoom_start=11)
    
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue', 'darkpurple', 'pink', 'black']
    
    for i, (nombre_ruta, ruta_nodos) in enumerate(list_of_routes):
        color = colors[i % len(colors)]
        
        # Ensamblar las coordenadas geométricas exactas de las aristas recorridas
        route_coords = _build_route_coords_from_osmnx_path(G, ruta_nodos)
                
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
    filepath: str = "mapa_clusters_santiago.html",
    df_depot: pd.DataFrame = None
):
    """
    Genera un mapa HTML con Folium coloreando cada nodo según su clúster de DBSCAN.
    Los outliers se grafican en negro.
    El depósito se grafica de manera independiente si se proporciona en df_depot.
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
                tooltip=f"Outlier | Nodo: {row.get('id_nodo', 'N/A')} | Orden: {row.get('Número de orden', 'N/A')}"
            ).add_to(m)

    # Graficar Depósito Independientemente
    if df_depot is not None and not df_depot.empty:
        for idx, row in df_depot.iterrows():
            folium.Marker(
                location=[row['latitud'], row['longitud']],
                icon=folium.Icon(color='black', icon='home', prefix='fa'),
                tooltip=f"Depósito: {row.get('id_nodo', 'N/A')} (Base Central)"
            ).add_to(m)

    # Graficar Clusters Válidos
    for i, (c_id, df_c) in enumerate(clusters_dict.items()):
        color = colors[i % len(colors)]
        
        for idx, row in df_c.iterrows():
            folium.CircleMarker(
                location=[row['latitud'], row['longitud']],
                radius=5,
                color=color,
                fill=True,
                fill_opacity=0.9,
                tooltip=f"Nodo: {row.get('id_nodo', 'N/A')} | Orden: {row.get('Número de orden', 'N/A')} | Cluster: {c_id}"
            ).add_to(m)

    m.save(filepath)
    print(f"Mapa de clusters guardado exitosamente en {filepath}")

if __name__ == "__main__":
    print("Módulo 'visualizer' listo. Importa 'plot_network_and_routes' o 'plot_cluster_results'.")


def plot_optimized_routes(
    rutas_por_camion: list,
    df_cluster: pd.DataFrame,
    info_rutas_astar: dict,
    depot_id: str,
    cluster_id: any,
    G: nx.MultiDiGraph,
    filepath: str = "mapa_rutas_optimizadas.html"
):
    """
    Dibuja las rutas optimizadas (GA o Tabu) sobre el grafo de Santiago.
    
    Parámetros:
    - rutas_por_camion: lista de listas con id_nodo de cada camión. Ej: [['n1','n2'], ['n3']]
    - df_cluster: DataFrame del cluster con columnas latitud, longitud, id_nodo.
    - info_rutas_astar: dict con claves 'id_origen->id_destino' y valores {'ruta_nodos_osmnx': [...]}
    - depot_id: identificador del nodo depósito.
    - cluster_id: ID del cluster para el título del mapa.
    - G: grafo OSMnx de la red vial.
    - filepath: ruta donde guardar el HTML.
    """
    print(f"Generando mapa de rutas optimizadas para Cluster {cluster_id}...")

    # Construir diccionario rápido de coordenadas por id_nodo
    coord_dict = {}
    if not df_cluster.empty and 'id_nodo' in df_cluster.columns:
        for _, row in df_cluster.iterrows():
            coord_dict[row['id_nodo']] = (float(row['latitud']), float(row['longitud']))

    # Coordenadas del depósito (fallback al centroide de Santiago)
    depot_coords = coord_dict.get(depot_id, SANTIAGO_CENTER)
    m = _build_santiago_base_map(zoom_start=12)

    colors = ['red', 'blue', 'green', 'purple', 'orange',
              'darkred', 'cadetblue', 'darkpurple', 'pink', 'black']

    # Marcar el depósito
    folium.Marker(
        location=depot_coords,
        icon=folium.Icon(color='black', icon='home', prefix='fa'),
        tooltip=f"Depósito ({depot_id})"
    ).add_to(m)

    for k_idx, ruta in enumerate(rutas_por_camion):
        color = colors[k_idx % len(colors)]
        secuencia = [depot_id] + ruta + [depot_id]

        for step, (origen_id, destino_id) in enumerate(zip(secuencia[:-1], secuencia[1:])):
            clave = f"{origen_id}->{destino_id}"
            clave_inv = f"{destino_id}->{origen_id}"

            # Intentar trazar la ruta A* real
            ruta_osmnx = None
            if clave in info_rutas_astar:
                ruta_osmnx = info_rutas_astar[clave].get('ruta_nodos_osmnx', [])
            if ruta_osmnx and len(ruta_osmnx) > 1:
                # Trazar usando geometría real de calles
                route_coords = _build_route_coords_from_osmnx_path(G, ruta_osmnx)

                if route_coords:
                    folium.PolyLine(
                        locations=route_coords,
                        color=color,
                        weight=4,
                        opacity=0.85,
                        tooltip=f"Camión {k_idx+1} | Tramo {step+1}: {origen_id} → {destino_id}"
                    ).add_to(m)
            else:
                # Fallback: línea recta entre coordenadas
                c_origen = coord_dict.get(origen_id) or depot_coords
                c_destino = coord_dict.get(destino_id) or depot_coords
                folium.PolyLine(
                    locations=[c_origen, c_destino],
                    color=color,
                    weight=3,
                    opacity=0.6,
                    dash_array='8',
                    tooltip=f"Camión {k_idx+1} | Tramo {step+1} (sin ruta OSMnx)"
                ).add_to(m)

        # Marcar clientes de este camión con numeración
        for i, nodo_id in enumerate(ruta):
            coords = coord_dict.get(nodo_id)
            if coords:
                folium.CircleMarker(
                    location=coords,
                    radius=7,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.9,
                    tooltip=f"Camión {k_idx+1} | Parada {i+1}: {nodo_id}"
                ).add_to(m)
                folium.map.Marker(
                    location=coords,
                    icon=folium.DivIcon(
                        html=f'<div style="font-size:9px;color:white;background:{color};'
                             f'border-radius:50%;width:18px;height:18px;text-align:center;'
                             f'line-height:18px;font-weight:bold;">{i+1}</div>',
                        icon_size=(18, 18),
                        icon_anchor=(9, 9)
                    )
                ).add_to(m)

    m.save(filepath)
    print(f"Mapa de rutas optimizadas guardado en: {filepath}")

def plot_global_flota_interactive(
    flota: list,
    df_global: pd.DataFrame,
    rutas_dict_global: dict,
    depot_id: str,
    G: nx.MultiDiGraph,
    filepath: str = "mapa_rutas_global.html",
    depot_coords: tuple = None
):
    """
    Dibuja TODAS las rutas (turnos y clusters combinados) según la distribución FÍSICA de Camiones.
    Utiliza multiples FeatureGroups para que cada Camión/Cluster pueda ser activado/desactivado desde el LayerControl.
    """
    print(f"Generando Mapa Híbrido Interactivo de Flota Global en {filepath}...")
    
    # Coordenadas Globales
    coord_dict = {}
    if not df_global.empty:
        for _, row in df_global.iterrows():
            if pd.notna(row.get('latitud')) and pd.notna(row.get('longitud')):
                coord_dict[row['id_nodo']] = (float(row['latitud']), float(row['longitud']))
            
    if not coord_dict:
        print("Atención: No hay nodos para graficar globalmente.")
        return
        
    if depot_coords is None:
        depot_coords = coord_dict.get(depot_id, SANTIAGO_CENTER)
    
    m = _build_santiago_base_map(zoom_start=11)
    
    colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'cadetblue', 'darkblue', 'pink', 'lightgreen', 'black', 'red']
    
    folium.Marker(
        location=depot_coords,
        icon=folium.Icon(color='black', icon='home', prefix='fa'),
        tooltip=f"Base Central ({depot_id})"
    ).add_to(m)
    
    # Iteración Transversal por Flota Fija
    for vehiculo in flota:
        if not vehiculo.bloques: 
            continue
            
        color = colors[vehiculo.id_vehiculo % len(colors)]
        
        # Cada Bloque (turno + cluster) es un FeatureGroup controlable individualmente
        for b in vehiculo.bloques:
            fg_name = f"🚚 Vehículo Físico {vehiculo.id_vehiculo} | 🏢 Clúster {b.cluster_id} [{b.turno_op}]"
            fg = folium.FeatureGroup(name=fg_name, show=True)
            
            # Recuperar info A* propia de ese clúster particular
            info_astar = rutas_dict_global.get(b.cluster_id, {})
            ruta_pura = b.ruta
            secuencia = [depot_id] + ruta_pura + [depot_id]
            
            for step, (origen_id, destino_id) in enumerate(zip(secuencia[:-1], secuencia[1:])):
                clave = f"{origen_id}->{destino_id}"
                clave_inv = f"{destino_id}->{origen_id}"
                
                ruta_osmnx = None
                if clave in info_astar:
                    ruta_osmnx = info_astar[clave].get('ruta_nodos_osmnx', [])
                    
                if ruta_osmnx and len(ruta_osmnx) > 1:
                    route_coords = _build_route_coords_from_osmnx_path(G, ruta_osmnx)
                            
                    if route_coords:
                        folium.PolyLine(
                            locations=route_coords,
                            color=color, weight=5, opacity=0.8,
                            tooltip=f"Vehículo {vehiculo.id_vehiculo} | Tramo {step+1}"
                        ).add_to(fg)
                else:
                    c_origen = coord_dict.get(origen_id) or depot_coords
                    c_destino = coord_dict.get(destino_id) or depot_coords
                    folium.PolyLine(
                        locations=[c_origen, c_destino],
                        color=color, weight=4, opacity=0.6, dash_array='10',
                        tooltip=f"Vehículo {vehiculo.id_vehiculo} | Tramo {step+1} (Recto)"
                    ).add_to(fg)
                    
            for i, nodo_id in enumerate(ruta_pura):
                coords = coord_dict.get(nodo_id)
                if coords:
                    folium.CircleMarker(
                        location=coords, radius=8, color=color,
                        fill=True, fill_color=color, fill_opacity=0.9,
                        tooltip=f"Vehículo {vehiculo.id_vehiculo} ({b.turno_op}) | Stop {i+1}: {nodo_id} | Clúster {b.cluster_id}"
                    ).add_to(fg)
                    folium.Marker(
                        location=coords,
                        icon=folium.DivIcon(
                            html=f'<div style="font-size:10px;color:white;background:transparent;'
                                 f'text-align:center;font-weight:bold;">{i+1}</div>',
                            icon_size=(20, 20),
                            icon_anchor=(10, 10)
                        )
                    ).add_to(fg)
            
            fg.add_to(m)
            
    folium.LayerControl(collapsed=False).add_to(m)
    m.save(filepath)
    print(f"[Map Viewer] UI Interfaz del mapa consolidado guardada en: {filepath}")
