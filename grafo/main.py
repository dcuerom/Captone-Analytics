import pandas as pd
import os
from grafo.geocoder import geocode_orders, geocode_depot
from grafo.network_builder import get_santiago_graph
from grafo.clustering import run_clustering_pipeline
from grafo.routing import calculate_routing_for_day
from grafo.visualizer import plot_cluster_results

def clean_rut(rut) -> str:
    if pd.isna(rut):
        return ""
    return str(rut).replace('.', '').replace('-', '').strip().upper()

def execute_vrp_pipeline(
    input_file: str = 'EDA/vrp_orders.xlsx', 
    depot_address: str = "Plaza de Armas, Santiago, Chile",
    sample_size: int = None
):
    """
    Gran instancia principal: Ejecuta toda la lógica de formación para el grafo dirigido
    combinando Cluster-First + Route-Second con llamadas optimizadas a A*.
    """
    print("=== INICIANDO PIPELINE VRP COMPLETO ===")
    
    # 1. Carga de datos
    print(f"\n[Paso 1] Cargando datos desde {input_file}...")
    df = pd.read_excel(input_file)
    
    # Normalización básica requerida
    if 'Número de Orden' in df.columns:
        df.rename(columns={'Número de Orden': 'Número de orden'}, inplace=True)
    if 'Fecha de despacho Solicitada' in df.columns:
        df.rename(columns={'Fecha de despacho Solicitada': 'fecha de despacho'}, inplace=True)
    if 'volumen_total_m3' in df.columns:
        df.rename(columns={'volumen_total_m3': 'volumen total_m3'}, inplace=True)
        
    df.dropna(subset=['direccion_ruteo'], inplace=True)
    
    # Homogeneizar RUT y crear ID único previo al clústering
    if 'RUT' in df.columns:
        df['rut_clean'] = df['RUT'].apply(clean_rut)
        df['id_nodo'] = df['Número de orden'].astype(str).str.strip() + "_" + df['rut_clean']
    
    if sample_size and len(df) > sample_size:
        print(f"Tomando una muestra aleatoria de {sample_size} pedidos para la ejecución...")
        df = df.sample(n=sample_size, random_state=42).copy()
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
        'Número de orden': 'DEPOT_01',
        'RUT': 'BASE',
        'latitud': lat_d,
        'longitud': lon_d,
        'id_nodo': depot_id,
        'direccion_ruteo': depot_address
    }])
    
    # 4. Clustering (Cluster-First)
    print("\n[Paso 4] Agrupando pedidos (DBSCAN Cluster-First)...")
    clusters_dict, outliers, pairs_for_astar = run_clustering_pipeline(df_geo, depot_id=depot_id, id_column='id_nodo', force_outlier_rescue=True)
    
    # 5. Carga del Grafo de Calles (Reducción de I/O mediante Supabase Storage)
    print("\n[Paso 5] Cargando Grafo de Red Vial...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    graph_path = os.path.join(base_dir, 'santiago_routing_graph.graphml')
    G = get_santiago_graph(filepath=graph_path)
    
    # 6. Ruteo Exhaustivo por Cluster (Route-Second)
    print("\n[Paso 6] Generando Matrices de Distancia (A*) estrictamente por Cluster...")
    matrices_por_cluster = {}
    rutas_por_cluster = {}
    
    for c_id, df_cluster in clusters_dict.items():
        print(f"\n--- Procesando Ruteo para Cluster {c_id} con {len(df_cluster)} pedidos + 1 Depósito ---")
        
        # Inyectar el depósito al cluster (crear los pares ida/vuelta requeridos por el VRP)
        df_cluster_with_depot = pd.concat([df_cluster, df_depot], ignore_index=True)
        
        # Generar matriz NxN estricta de este cluster aislado
        matriz, info_rutas = calculate_routing_for_day(df_cluster_with_depot, G)
        
        matrices_por_cluster[c_id] = matriz
        rutas_por_cluster[c_id] = info_rutas
        
    print("\n=== GENERANDO VISUALIZACIÓN === ")
    try:
        # Recuperamos e inyectamos el base_dir
        out_map_path = os.path.join(base_dir, 'mapa_clusters_santiago.html')
        # Pasamos a plot_cluster_results el dict modificado o simplemente el base. 
        # Modificamos clusters_dict para contener la fila del depósito y se vea graficada
        diccionario_graficar = {}
        for c_id, df_c in clusters_dict.items():
            diccionario_graficar[c_id] = pd.concat([df_c, df_depot], ignore_index=True)
            
        plot_cluster_results(diccionario_graficar, outliers, filepath=out_map_path)
    except Exception as e:
        print(f"Advertencia: No se pudo generar la visualización HTML. Error: {e}")
        
    print("\n=== PIPELINE FINALIZADO EXITOSAMENTE ===")
    print(f"Clusters procesados: {len(matrices_por_cluster)}")
    print(f"Clientes Outliers (ruido geográfico inasignable): {len(outliers)}")
    
    return matrices_por_cluster, rutas_por_cluster, outliers

if __name__ == "__main__":
    # Test opcional para verificar la integración local
    execute_vrp_pipeline(sample_size=100)
