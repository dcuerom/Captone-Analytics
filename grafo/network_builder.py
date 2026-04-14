import hashlib
import os
import sys
from typing import Optional

import networkx as nx
import osmnx as ox

# Agregar la ruta base para permitir importar modules de otros directorios
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.map.graph_storage import download_graph_from_storage


def _safe_remove(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def _sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_checksum(checksum_path: str) -> Optional[str]:
    if not os.path.exists(checksum_path):
        return None
    try:
        content = open(checksum_path, "r", encoding="utf-8").read().strip()
    except Exception:
        return None
    if not content:
        return None
    token = content.split()[0].strip().lower()
    if len(token) != 64:
        return None
    return token


def _write_checksum(filepath: str) -> None:
    checksum_path = f"{filepath}.sha256"
    try:
        checksum = _sha256_file(filepath)
        with open(checksum_path, "w", encoding="utf-8") as f:
            f.write(f"{checksum}  {os.path.basename(filepath)}\n")
    except Exception as exc:
        print(f"Aviso: no se pudo escribir checksum del grafo ({exc}).")


def _load_local_graph_if_valid(filepath: str) -> Optional[nx.MultiDiGraph]:
    if not os.path.exists(filepath):
        return None

    checksum_path = f"{filepath}.sha256"
    expected_checksum = _load_checksum(checksum_path)
    if expected_checksum is not None:
        try:
            current_checksum = _sha256_file(filepath)
            if current_checksum != expected_checksum:
                print(f"Aviso: checksum de grafo no coincide en {filepath}. Se regenerara automaticamente.")
                _safe_remove(filepath)
                _safe_remove(checksum_path)
                return None
        except Exception as exc:
            print(f"Aviso: no se pudo verificar checksum de grafo ({exc}). Se regenerara automaticamente.")
            _safe_remove(filepath)
            _safe_remove(checksum_path)
            return None

    size = os.path.getsize(filepath)
    if size <= 0:
        print(f"Aviso: archivo de grafo vacio detectado en {filepath}. Se regenerara automaticamente.")
        _safe_remove(filepath)
        _safe_remove(checksum_path)
        return None

    try:
        print(f"Cargando grafo desde {filepath}...")
        graph = ox.load_graphml(filepath)
        print(f"Grafo cargado: {len(graph.nodes)} nodos, {len(graph.edges)} aristas.")
        if expected_checksum is None:
            _write_checksum(filepath)
        return graph
    except Exception as exc:
        print(f"Aviso: archivo de grafo local corrupto o invalido ({exc}). Se regenerara automaticamente.")
        _safe_remove(filepath)
        _safe_remove(checksum_path)
        return None


def get_santiago_graph(filepath: str = "grafo/santiago_routing_graph.graphml", force_download: bool = False) -> nx.MultiDiGraph:
    """
    Carga o descarga el grafo de calles del Gran Santiago.
    Descarga desde Supabase (Storage) si no esta localmente.
    """
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    if force_download:
        _safe_remove(filepath)
        _safe_remove(f"{filepath}.sha256")

    local_graph = _load_local_graph_if_valid(filepath)
    if local_graph is not None:
        return local_graph

    try:
        download_graph_from_storage(local_filepath=filepath)
    except Exception as exc:
        print(f"Aviso: No se pudo bajar el grafo desde Supabase: {exc}. Se intentara descargar desde OSM.")

    local_graph = _load_local_graph_if_valid(filepath)
    if local_graph is not None:
        return local_graph

    print("Descargando grafo de Santiago mediante osmnx (puede tardar varios minutos)...")
    custom_filter = (
        '["highway"]["area"!~"yes"]["highway"!~"motorway|motorway_link|trunk|trunk_link"]'
        '["motor_vehicle"!~"no"]["motorcar"!~"no"]'
        '["access"!~"private"]'
    )

    place_query = [
        "Provincia de Santiago, Chile",
        "San Bernardo, Chile",
        "Puente Alto, Chile",
    ]
    try:
        graph = ox.graph_from_place(
            place_query,
            network_type="drive",
            custom_filter=custom_filter,
            simplify=True,
        )

        print(f"Grafo descargado. Nodos: {len(graph.nodes)}, Aristas: {len(graph.edges)}")
        print(f"Guardando grafo en {filepath} para futuras ejecuciones...")
        try:
            ox.save_graphml(graph, filepath)
            _write_checksum(filepath)
        except Exception as save_err:
            print(f"Aviso: no se pudo guardar el grafo localmente ({save_err}). La ejecucion continuara en memoria.")
        return graph
    except Exception as exc:
        print(f"Error al descargar el grafo de Santiago: {exc}")
        raise


if __name__ == "__main__":
    get_santiago_graph()
