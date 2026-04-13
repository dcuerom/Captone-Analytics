import pandas as pd
import os
from typing import Optional
from .geocoder import geocode_orders, geocode_depot
from .network_builder import get_santiago_graph
from .clustering import run_clustering_pipeline
from .routing import calculate_routing_for_day
from .visualizer import plot_cluster_results

def clean_rut(rut) -> str:
    if pd.isna(rut):
        return ""
    return str(rut).replace('.', '').replace('-', '').strip().upper()

# Global placeholder for workers to avoid pickling overhead
_global_G = None

def _init_worker(G):
    """Inicializa cada proceso con el grafo cargado una única vez."""
    global _global_G
    _global_G = G

def _process_cluster_routing(c_id, df_cluster, df_depot):
    """Función global requerida para pickling en multiprocessing."""
    global _global_G
    print(f"      [Proceso] Iniciando Ruteo para Cluster {c_id} ({len(df_cluster)} pedidos)...")
    df_cluster_with_depot = pd.concat([df_cluster, df_depot], ignore_index=True)
    matriz, info_rutas = calculate_routing_for_day(df_cluster_with_depot, _global_G)
    return c_id, matriz, info_rutas

def execute_vrp_pipeline(
    input_file: str = 'EDA/df_despacho.csv', 
    depot_address: str = "Santa Elena, Santiago., Bogotá - Sierra Bella, Santiago, RM (Metropolitana)",
    sample_size: int = None,
    clustering_time_column: str = 'a_ventana',
    clustering_default_window_start_hour: int = 9,
    clustering_alpha_time: float = 10.0,
    clustering_eps: float = 0.3,
    clustering_min_samples: int = 3,
    clustering_rescue_threshold: float = 0.8,
    force_outlier_rescue: bool = True,
    routing_max_workers: Optional[int] = None,
):
    """
    Gran instancia principal: Ejecuta toda la lógica de formación para el grafo dirigido
    combinando Cluster-First + Route-Second con llamadas optimizadas a A*.
    """
    print("=== INICIANDO PIPELINE VRP COMPLETO ===")
    
    # 1. Carga de datos
    print(f"\n[Paso 1] Cargando datos desde {input_file}...")
    if str(input_file).endswith('.csv'):
        df = pd.read_csv(input_file)
    else:
        df = pd.read_excel(input_file)
    
    # Normalización basada en df_despacho.csv
    if 'Dirección' in df.columns:
        df.rename(columns={'Dirección': 'direccion_ruteo'}, inplace=True)
    if 'Latitud' in df.columns:
        df.rename(columns={'Latitud': 'latitud'}, inplace=True)
    if 'Longitud' in df.columns:
        df.rename(columns={'Longitud': 'longitud'}, inplace=True)
        
    if 'direccion_ruteo' in df.columns:
        df.dropna(subset=['direccion_ruteo'], inplace=True)
    
    # Crear ID único previo al clústering
    if 'id_cliente' in df.columns and 'id_pedido' in df.columns:
        df['rut_clean'] = df['id_cliente'].apply(clean_rut)
        df['id_nodo'] = df['id_pedido'].astype(str).str.strip() + "_" + df['rut_clean']
    
    if sample_size and len(df) > sample_size:
        print(f"Tomando una muestra aleatoria de {sample_size} pedidos para la ejecución...")
        df = df.sample(n=sample_size, random_state=50).copy()
    else:
        print(f"Procesando {len(df)} pedidos totales...")
    
    # 2. Geocodificación de Pedidos
    print("\n[Paso 2] Geocodificando pedidos...")
    df_geo = geocode_orders(df)
    df_geo.dropna(subset=['latitud', 'longitud'], inplace=True)
    
    # 3. Datos del Depósito
    print(f"\n[Paso 3] Geocodificando Depósito: {depot_address}")
    lat_d, lon_d = geocode_depot(depot_address)
    depot_id = "DEPOT_01_BASE"
    df_depot = pd.DataFrame([{
        'id_pedido': 'DEPOT_01',
        'id_cliente': 'BASE',
        'latitud': lat_d,
        'longitud': lon_d,
        'id_nodo': depot_id,
        'direccion_ruteo': depot_address
    }])
    
    # 4. Clustering (Cluster-First)
    print("\n[Paso 4] Agrupando pedidos (DBSCAN Cluster-First Geo-Temporal)...")
    clusters_dict, outliers, pairs_for_astar = run_clustering_pipeline(
        df_geo,
        depot_id=depot_id,
        id_column='id_nodo',
        force_outlier_rescue=force_outlier_rescue,
        time_column=clustering_time_column,
        default_window_start_hour=clustering_default_window_start_hour,
        alpha_time=clustering_alpha_time,
        eps=clustering_eps,
        min_samples=clustering_min_samples,
        rescue_threshold=clustering_rescue_threshold,
    )
    
    # 5. Carga del Grafo de Calles
    print("\n[Paso 5] Cargando Grafo de Red Vial...")
    graph_base_dir = os.path.dirname(os.path.abspath(__file__))
    graph_path = os.path.join(graph_base_dir, 'santiago_routing_graph.graphml')
    G = get_santiago_graph(filepath=graph_path)
    
    # 6. Ruteo Exhaustivo por Cluster (Route-Second)
    print("\n[Paso 6] Generando Matrices de Distancia (A*) estrictamente por Cluster...")
    matrices_por_cluster = {}
    rutas_por_cluster = {}
    
    import concurrent.futures

    if routing_max_workers is None:
        try:
            routing_max_workers = int(os.getenv("ROUTING_MAX_WORKERS", "1"))
        except Exception:
            routing_max_workers = 1
    routing_max_workers = max(1, int(routing_max_workers))

    if routing_max_workers == 1:
        print("Ejecutando ruteo en modo estable (1 worker, menor consumo de RAM)...")
        for c_id, df_cluster in clusters_dict.items():
            print(f"      [Proceso] Iniciando Ruteo para Cluster {c_id} ({len(df_cluster)} pedidos)...")
            df_cluster_with_depot = pd.concat([df_cluster, df_depot], ignore_index=True)
            matriz, info_rutas = calculate_routing_for_day(df_cluster_with_depot, G)
            matrices_por_cluster[c_id] = matriz
            rutas_por_cluster[c_id] = info_rutas
            print(f"      [Éxito] Cluster {c_id} procesado.")
    else:
        max_auto = max(1, (os.cpu_count() or 2) // 2)
        max_workers = max(1, min(routing_max_workers, max_auto))
        print(f"Ejecutando procesamiento paralelo con {max_workers} núcleos (Seguridad RAM activa)...")

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=max_workers,
            initializer=_init_worker,
            initargs=(G,)
        ) as executor:
            # Lanzar tareas sin pasar el Grafo G como argumento (ya está inicializando en el proceso worker)
            futures = [
                executor.submit(_process_cluster_routing, c_id, df_cluster, df_depot)
                for c_id, df_cluster in clusters_dict.items()
            ]

            # Recolectar resultados
            for future in concurrent.futures.as_completed(futures):
                c_id, matriz, info_rutas = future.result()
                matrices_por_cluster[c_id] = matriz
                rutas_por_cluster[c_id] = info_rutas
                print(f"      [Éxito] Cluster {c_id} procesado.")
        
    print("\n=== GENERANDO VISUALIZACIÓN === ")
    try:
        # Recuperamos e inyectamos el base_dir
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out_map_path = os.path.join(base_dir, 'resultados', 'mapa_rutas', 'mapa_clusters_santiago.html')
        os.makedirs(os.path.dirname(out_map_path), exist_ok=True)
        # Pasamos a plot_cluster_results el diccionario base y df_depot de forma separada
        plot_cluster_results(clusters_dict, outliers, filepath=out_map_path, df_depot=df_depot)
    except Exception as e:
        print(f"Advertencia: No se pudo generar la visualización HTML. Error: {e}")
        
    # print("\n=== PIPELINE FINALIZADO EXITOSAMENTE ===")
    # print(f"Clusters procesados: {len(matrices_por_cluster)}")
    # print(f"Clientes Outliers (ruido geográfico inasignable): {len(outliers)}")
    
    return matrices_por_cluster, rutas_por_cluster, G, (lat_d, lon_d)

if __name__ == "__main__":
    # Test opcional para verificar la integración local
    execute_vrp_pipeline(sample_size=100)
