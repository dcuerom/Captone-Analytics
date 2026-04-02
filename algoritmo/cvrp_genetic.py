import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.optimize import minimize

# Importar dependencias directas del pipeline paralelo
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from grafo.cvrp_parser import parse_cvrp_instance
from grafo.cvrp_clustering import run_euclidean_clustering
from grafo.cvrp_grafo import calculate_euclidean_routing
from modelo.cvrp_pymoo_problem import CVRPEuclideanProblem

def resolver_cluster_cvrp(cluster_idx, df_cluster, matriz_dist, depot_id, cap_peso, df_nodos):
    """
    Ejecuta Algoritmo Genético de PyMoo basado en Permutaciones
    sobre CVRPEuclideanProblem.
    """
    clientes = [id_n for id_n in matriz_dist.index if id_n != depot_id]
    n_clientes = len(clientes)
    
    if n_clientes == 0:
        return {"rutas": [], "costo_total": 0.0, "detalle_camiones": [], "detalle_nodos": {}}
        
    problem = CVRPEuclideanProblem(
        df_cluster=df_cluster, 
        matriz_dist=matriz_dist, 
        depot_id=depot_id,
        cap_peso=cap_peso
    )
    
    # 2. Configurar Algoritmo GA de Permutación
    algorithm = GA(
        pop_size=100,
        sampling=PermutationRandomSampling(),
        crossover=OrderCrossover(),
        mutation=InversionMutation(),
        eliminate_duplicates=False
    )
    
    print(f"      [PyMoo] Optimizando Cluster {cluster_idx} ({n_clientes} clientes)...")
    res = minimize(
        problem,
        algorithm,
        termination=('n_gen', 700), # Mayor fuerza bruta al GA ya que f(x) es O(N) muy rapido
        seed=42,
        verbose=False,
        save_history=False
    )
    
    if res.X is None:
        raise ValueError(f"Fallo en GA PyMoo para clúster {cluster_idx}.")
        
    f_val = float(res.F.flat[0])
    print(f"      PyMoo Terminado. Distancia Óptima Aproximada = {f_val:.2f}")
    
    dict_out = problem.evaluar_completo(res.X)
    
    # Integrar las coordenadas en dict_out["detalle_nodos"]
    df_idx = df_nodos.set_index('id_nodo')
    for nodo_id, data in dict_out["detalle_nodos"].items():
        if nodo_id in df_idx.index:
            row = df_idx.loc[nodo_id]
            data["x"] = float(row.get('x', 0.0))
            data["y"] = float(row.get('y', 0.0))
            
    return dict_out

def generar_informes(resultados_globales, out_dir):
    """
    Genera el informe solicitado y lo exporta a CSV.
    Campos solicitados:
    - Resumen: Cluster, Clase K, Turno, Salida CD, Retorno CD, Viaje Efectivo, Dist, Clientes
    - Nodos: Cluster, clase, nodo, coordenadas, distancia, peso
    """
    resumen_filas = []
    detalle_filas = []
    
    for cluster_id, dict_out in resultados_globales.items():
        rutas_camiones = dict_out.get("rutas", [])
        detalle_cam = dict_out.get("detalle_camiones", [])
        detalle_nodos = dict_out.get("detalle_nodos", {})
        
        for idx_camion, ruta in enumerate(rutas_camiones):
            cam_info = detalle_cam[idx_camion]
            dist_total_camion = cam_info["dist_total_m"]
            
            # Agrupar las filas de resumen
            resumen_filas.append({
                "Cluster": cluster_id,
                "Clase K": "K11", # Placeholder fijo
                "Turno": "Mañana", # Placeholder fijo
                "Salida CD": "09:00",
                "Retorno CD": "18:00",
                "Viaje Efectivo (Hrs aprox)": round(dist_total_camion / 40.0, 2), # Simulación vel 40/hr
                "Dist": round(dist_total_camion, 2),
                "Clientes": len(ruta)
            })
            
            # Agrupar el detalle para cada nodo de la ruta
            for nodo in ruta:
                nodo_info = detalle_nodos[nodo]
                detalle_filas.append({
                    "Cluster": cluster_id,
                    "clase": "K11",
                    "nodo": nodo,
                    "coordenadas": f"({nodo_info.get('x', 0.0)}, {nodo_info.get('y', 0.0)})",
                    "distancia": round(nodo_info.get('dist_arco_m', 0.0), 2),
                    "peso": nodo_info.get('peso_g', 0.0)
                })
                
    # Armado y exporte
    df_resumen = pd.DataFrame(resumen_filas)
    df_detalle = pd.DataFrame(detalle_filas)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    res_path = os.path.join(out_dir, f"CVRP_Resumen_{timestamp}.csv")
    det_path = os.path.join(out_dir, f"CVRP_Detalle_{timestamp}.csv")
    
    df_resumen.to_csv(res_path, index=False)
    df_detalle.to_csv(det_path, index=False)
    
    print("\n[Éxito] Reportes Exportados:")
    print(" ->", res_path)
    print(" ->", det_path)
    
    return res_path, det_path

def disparar_rutina_cvrp_clasico(vrp_filepath: str):
    print("=== INICIANDO CVRP CLÁSICO (TSPLIB: Distancias Euclidianas) ===")
    
    # 1. Parsear 
    parser_data = parse_cvrp_instance(vrp_filepath)
    df_nodos = parser_data["df_nodos"]
    depot_id = parser_data["depot_id"]
    k_trucks = parser_data["k_trucks"]
    cap_peso = parser_data["capacity"]
    
    print(f"Instancia: {parser_data['name']}")
    print(f"Dimensión: {parser_data['dimension']}, Capacidad Q: {cap_peso}, Vehículos Meta: {k_trucks}")
    
    # Separar base/depósito
    df_depot = df_nodos[df_nodos['id_nodo'] == depot_id].copy()
    df_clientes = df_nodos[df_nodos['id_nodo'] != depot_id].copy()
    
    # 2. Clusters en espacio Euclidiano (Por defecto 1 sólo si son sub-100 nodos)
    # Por las instrucciones, mantenemos la lógica; pasamos k_trucks pero podemos dejar todo en 1.
    # Usemos K clústeres si se desean clústers estables:
    clusters_dict, outliers = run_euclidean_clustering(df_clientes, df_depot, k_trucks=k_trucks)
    
    out_dir = os.path.join(base_dir, 'resultados', 'cvrp')
    os.makedirs(out_dir, exist_ok=True)
    
    resultados_globales = {}
    
    dist_total_modelo = 0.0
    
    # 3. Procesar iterativamente cada sub-cluster
    for cluster_id, df_cluster in clusters_dict.items():
        matriz_dist, _ = calculate_euclidean_routing(df_cluster, df_depot)
        
        dict_out = resolver_cluster_cvrp(
            cluster_id, 
            df_cluster, 
            matriz_dist, 
            depot_id, 
            cap_peso,
            df_nodos
        )
        
        dist_total_modelo += dict_out["costo_total"]
        resultados_globales[cluster_id] = dict_out

    print(f"\n>>>> Optimo Encontrado CVRP Consolidado (Total Distancia): {dist_total_modelo:.2f}")

    # 4. Generar reportes tabulares
    generar_informes(resultados_globales, out_dir)
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
    else:
        # Default de prueba
        ruta = os.path.join(base_dir, "Instancias de Prueba VRP", "A", "A-n32-k5.vrp")
        
    disparar_rutina_cvrp_clasico(ruta)
