import osmnx as ox
import networkx as nx
import os
import sys
from typing import Optional

# Agregar la ruta base para permitir importar modules de otros directorios
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.map.graph_storage import download_graph_from_storage


def _safe_remove(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def _load_local_graph_if_valid(filepath: str) -> Optional[nx.MultiDiGraph]:
    if not os.path.exists(filepath):
        return None

    size = os.path.getsize(filepath)
    if size <= 0:
        print(f"Aviso: archivo de grafo vacío detectado en {filepath}. Se regenerará automáticamente.")
        _safe_remove(filepath)
        return None

    try:
        print(f"Cargando grafo desde {filepath}...")
        G = ox.load_graphml(filepath)
        print(f"Grafo cargado: {len(G.nodes)} nodos, {len(G.edges)} aristas.")
        return G
    except Exception as e:
        print(f"Aviso: archivo de grafo local corrupto o inválido ({e}). Se regenerará automáticamente.")
        _safe_remove(filepath)
        return None

def get_santiago_graph(filepath: str = 'grafo/santiago_routing_graph.graphml', force_download: bool = False) -> nx.MultiDiGraph:
    """
    Carga o descarga el grafo de calles del Gran Santiago.
    Descarga desde Supabase (Storage) si no está localmente.
    """
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    if force_download:
        _safe_remove(filepath)

    # 1) Intento local (si existe y está sano)
    local_graph = _load_local_graph_if_valid(filepath)
    if local_graph is not None:
        return local_graph

    # 2) Intento descargar desde Storage (Supabase) y volver a validar
    try:
        download_graph_from_storage(local_filepath=filepath)
    except Exception as e:
        print(f"Aviso: No se pudo bajar el grafo desde Supabase: {e}. Se intentará descargar desde OSM.")

    local_graph = _load_local_graph_if_valid(filepath)
    if local_graph is not None:
        return local_graph
        
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
        try:
            ox.save_graphml(G, filepath)
        except Exception as save_err:
            print(f"Aviso: no se pudo guardar el grafo localmente ({save_err}). La ejecución continuará en memoria.")
        return G
    except Exception as e:
        print(f"Error al descargar el grafo de Santiago: {e}")
        raise e

if __name__ == "__main__":
    # Test directo
    # Se recomienda correr esto una vez para preparar el archivo santiago_routing_graph.graphml
    g = get_santiago_graph()
