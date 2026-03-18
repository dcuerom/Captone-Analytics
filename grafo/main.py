import pandas as pd
import os
from network_builder import get_santiago_graph
from routing import calculate_routing_for_day

def process_daily_routing(df_dia: pd.DataFrame, graph_filepath: str = 'santiago_routing_graph.graphml'):
    """
    Función principal que procesa un DataFrame con pedidos diarios.
    
    Condiciones mínimas exigidas en el DataFrame de entrada:
    - Rut / RUT
    - Número de orden
    - fecha de despacho
    - latitudp
    - longitud
    - volumen total_m3 / volumen_total_m3
    - peso_total_kg
    
    Devuelve:
    - matriz_distancias: pd.DataFrame (N x N) con las rutas más cortas (km).
    - info_rutas: Diccionario con la estructura de nodos OSMNX visitados.
    """
    columnas_esperadas = [
        'latitud', 'longitud'
    ]
    
    # Validar existencia mínima de lat/lon
    faltan = [col for col in columnas_esperadas if col not in df_dia.columns]
    if faltan:
        raise ValueError(f"El DataFrame no cumple con las columnas mínimas. Faltan: {faltan}")
        
    print(f"--- Procesando ruteo de red estricta para {len(df_dia)} pedidos ---")
    
    # 1. Obtener/Cargar el Grafo Base de Santiago (sin autopistas)
    # Se busca el path relativo al script para poder encontrar santiago_routing_graph.graphml fácilmente
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_graph_path = os.path.join(base_dir, graph_filepath)
    
    G = get_santiago_graph(filepath=full_graph_path)
    
    # 2. Calcular matriz y rutas usando A*
    matriz_distancias, info_rutas = calculate_routing_for_day(df_dia, G)
    
    return matriz_distancias, info_rutas

if __name__ == "__main__":
    print("Módulo 'grafo' listo. Importa 'process_daily_routing' y pásale el DataFrame del día.")
