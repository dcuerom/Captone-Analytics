import osmnx as ox
import networkx as nx
import os
import sys

# Agregar la ruta base para permitir importar modules de otros directorios
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.map.graph_storage import download_graph_from_storage

def get_santiago_graph(filepath: str = 'grafo/santiago_routing_graph.graphml', force_download: bool = False) -> nx.MultiDiGraph:
    """
    Carga o descarga el grafo de calles del Gran Santiago.
    Descarga desde Supabase (Storage) si no está localmente.
    """
    # Intentar descargar de Supabase si no existe
    if not os.path.exists(filepath) or force_download:
        try:
            download_graph_from_storage(local_filepath=filepath)
        except Exception as e:
            print(f"Aviso: No se pudo bajar el grafo desde Supabase: {e}. Se intentará descargar desde OSM.")
            
    if os.path.exists(filepath):
        print(f"Cargando grafo desde {filepath}...")
        G = ox.load_graphml(filepath)
        print(f"Grafo cargado: {len(G.nodes)} nodos, {len(G.edges)} aristas.")
        return G
        
    print("Descargando grafo de Santiago mediante osmnx (puede tardar varios minutos)...")
    # Custom filter to exclude motorways and trunks, but allow normal driving roads
    custom_filter = (
        '["highway"]["area"!~"yes"]["highway"!~"motorway|motorway_link|trunk|trunk_link"]'
        '["motor_vehicle"!~"no"]["motorcar"!~"no"]'
        '["access"!~"private"]'
    )
    
    # Consultas para abarcar todo el "Gran Santiago" y no solo la comuna de "Santiago".
    # Provincia de Santiago incluye la mayoría (Las Condes, Providencia, Maipú, etc.)
    # Se añaden San Bernardo y Puente Alto por estar en provincias aledañas pero unidas urbanamente.
    place_query = [
        "Provincia de Santiago, Chile",
        "San Bernardo, Chile",
        "Puente Alto, Chile"
    ]    
    try:
        # Se requiere a veces añadir un buffer o usar retain_all=False para limpiar islas desconectadas.
        G = ox.graph_from_place(
            place_query, 
            network_type='drive', 
            custom_filter=custom_filter,
            simplify=True
        )
        
        print(f"Grafo descargado. Nodos: {len(G.nodes)}, Aristas: {len(G.edges)}")
        print(f"Guardando grafo en {filepath} para futuras ejecuciones...")
        ox.save_graphml(G, filepath)
        return G
    except Exception as e:
        print(f"Error al descargar el grafo de Santiago: {e}")
        raise e

if __name__ == "__main__":
    # Test directo
    # Se recomienda correr esto una vez para preparar el archivo santiago_routing_graph.graphml
    g = get_santiago_graph()
