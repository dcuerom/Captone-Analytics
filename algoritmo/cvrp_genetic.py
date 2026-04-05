import os
import sys
import pandas as pd
import numpy as np
import time
from datetime import datetime
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.optimize import minimize

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from grafo.cvrp_parser import parse_cvrp_instance
from grafo.cvrp_clustering import run_euclidean_agglomerative_clustering
from grafo.cvrp_grafo import calculate_euclidean_routing
from modelo.cvrp_pymoo_problem import CVRPEuclideanProblem

def resolver_cluster_cvrp(cluster_idx, df_cluster, matriz_dist, depot_id, cap_peso, df_nodos, k_trucks):
    clientes = [id_n for id_n in matriz_dist.index if id_n != depot_id]
    n_clientes = len(clientes)
    
    if n_clientes == 0:
        return {"rutas": [], "costo_total": 0.0, "detalle_camiones": [], "detalle_nodos": {}}
        
    if n_clientes == 1:
        print(f"      [PyMoo] Cluster {cluster_idx} tiene solo 1 cliente. Evaluación directa sin GA.")
        problem = CVRPEuclideanProblem(
            df_cluster=df_cluster, 
            matriz_dist=matriz_dist, 
            depot_id=depot_id,
            cap_peso=cap_peso,
            k_trucks=k_trucks
        )
        dict_out = problem.evaluar_completo(np.array([0]))
        
        df_idx = df_nodos.set_index('id_nodo')
        for nodo_id, data in dict_out["detalle_nodos"].items():
            if nodo_id in df_idx.index:
                row = df_idx.loc[nodo_id]
                data["x"] = float(row.get('x', 0.0))
                data["y"] = float(row.get('y', 0.0))
                
        return dict_out

    problem = CVRPEuclideanProblem(
        df_cluster=df_cluster, 
        matriz_dist=matriz_dist, 
        depot_id=depot_id,
        cap_peso=cap_peso,
        k_trucks=k_trucks
    )
    
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
        termination=('n_gen', 700),
        seed=42,
        verbose=False,
        save_history=False
    )
    
    if res.X is None:
        raise ValueError(f"Fallo en GA PyMoo para clúster {cluster_idx}.")
        
    f_val = float(res.F.flat[0])
    print(f"      PyMoo Terminado. Distancia Óptima Aproximada = {f_val:.2f}")
    
    dict_out = problem.evaluar_completo(res.X)
    
    df_idx = df_nodos.set_index('id_nodo')
    for nodo_id, data in dict_out["detalle_nodos"].items():
        if nodo_id in df_idx.index:
            row = df_idx.loc[nodo_id]
            data["x"] = float(row.get('x', 0.0))
            data["y"] = float(row.get('y', 0.0))
            
    return dict_out

def min_a_hora(minutos: float) -> str:
    h = int(minutos) // 60
    m = int(minutos) % 60
    return f"{h:02d}:{m:02d}"

def generar_informes(resultados_globales, out_dir, tiempo_ejecucion_segundos, instance_name):
    resumen_filas = []
    detalle_filas = []
    
    global_truck_id_offset = 0
    
    for cluster_id, dict_out in resultados_globales.items():
        rutas_camiones = dict_out.get("rutas", [])
        detalle_cam = dict_out.get("detalle_camiones", [])
        detalle_nodos = dict_out.get("detalle_nodos", {})
        
        unique_trucks_in_cluster = set(c["id_camion_fisico"] for c in detalle_cam) if detalle_cam else {0}
        max_truck_in_cluster = max(unique_trucks_in_cluster)

        
        for idx_camion, ruta in enumerate(rutas_camiones):
            cam_info = detalle_cam[idx_camion]
            
            t_salida = min_a_hora(cam_info["t_salida_deposito"])
            t_retorno = min_a_hora(cam_info["t_retorno_deposito"])
            
            mapped_truck_id = cam_info["id_camion_fisico"] + global_truck_id_offset
            
            resumen_filas.append({
                "ID Físico Camión": mapped_truck_id,
                "Cluster": cluster_id,
                "Clase K / Plantilla": cam_info["subconjunto_k"],
                "Turno": cam_info["turno_operacion"],
                "Salida CD": t_salida,
                "Retorno CD": t_retorno,
                "Viaje Efectivo (min)": round(cam_info["t_viaje_efectivo_min"], 2),
                "Dist Total": round(cam_info["dist_total_m"], 2),
                "Clientes Atendidos": cam_info["n_clientes"],
                "Peso": cam_info["peso_total"],
                "Tiempo Solución (segundos)": round(tiempo_ejecucion_segundos, 1)
            })
            
            # Nodo de salida deposito
            detalle_filas.append({
                "ID Físico": mapped_truck_id,
                "Turno": cam_info["turno_operacion"],
                "Cluster": cluster_id,
                "Subconjunto": cam_info["subconjunto_k"],
                "nodo": "DEPOT",
                "Hora Llegada": t_salida,
                "coordenadas": "N/A",
                "distancia_tramo": 0.0,
                "peso_tramo": 0.0
            })
            
            for nodo in ruta:
                nodo_info = detalle_nodos[nodo]
                t_llegada = min_a_hora(nodo_info.get('t_llegada_real', 0.0))
                
                detalle_filas.append({
                    "ID Físico": mapped_truck_id,
                    "Turno": cam_info["turno_operacion"],
                    "Cluster": cluster_id,
                    "Subconjunto": cam_info["subconjunto_k"],
                    "nodo": nodo,
                    "Hora Llegada": t_llegada,
                    "coordenadas": f"({nodo_info.get('x', 0.0)}, {nodo_info.get('y', 0.0)})",
                    "distancia_tramo": round(nodo_info.get('dist_arco_m', 0.0), 2),
                    "peso_tramo": nodo_info.get('peso_g', 0.0)
                })
            
            # Retorno
            detalle_filas.append({
                "ID Físico": mapped_truck_id,
                "Turno": cam_info["turno_operacion"],
                "Cluster": cluster_id,
                "Subconjunto": cam_info["subconjunto_k"],
                "nodo": "DEPOT (RETORNO)",
                "Hora Llegada": t_retorno,
                "coordenadas": "N/A",
                "distancia_tramo": round(cam_info.get("dist_retorno_m", 0.0), 2),
                "peso_tramo": 0.0
            })
            
        global_truck_id_offset += max_truck_in_cluster
                
    df_resumen = pd.DataFrame(resumen_filas)
    df_detalle = pd.DataFrame(detalle_filas)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    res_path = os.path.join(out_dir, f"CVRP_{instance_name}_Resumen_{timestamp}.csv")
    det_path = os.path.join(out_dir, f"CVRP_{instance_name}_Detalle_{timestamp}.csv")
    
    df_resumen.to_csv(res_path, index=False)
    df_detalle.to_csv(det_path, index=False)
    
    print("\n[Éxito] Reportes Exportados:")
    print(" ->", res_path)
    print(" ->", det_path)
    
    return res_path, det_path

def disparar_rutina_cvrp_clasico(vrp_filepath: str):
    start_time = time.time()
    print("=== INICIANDO CVRP CLÁSICO (TSPLIB, Operativa Constreñida) ===")
    
    parser_data = parse_cvrp_instance(vrp_filepath)
    df_nodos = parser_data["df_nodos"]
    depot_id = parser_data["depot_id"]
    k_trucks = parser_data["k_trucks"]
    cap_peso = parser_data["capacity"]
    
    print(f"Instancia: {parser_data['name']}")
    print(f"Dimensión: {parser_data['dimension']}, Capacidad QA: {cap_peso}, Vehículos Meta: {k_trucks}")
    
    df_depot = df_nodos[df_nodos['id_nodo'] == depot_id].copy()

    clusters_dict, outliers = run_euclidean_agglomerative_clustering(
        df=df_nodos[df_nodos['id_nodo'] != depot_id], 
        df_depot=df_depot, 
        n_clusters=k_trucks
    )

    out_dir = os.path.join(base_dir, 'resultados', 'cvrp')
    os.makedirs(out_dir, exist_ok=True)
    
    resultados_globales = {}
    dist_total_modelo = 0.0
    
    for cluster_id, df_cluster_latlon in clusters_dict.items():
        
        matriz_dist, _ = calculate_euclidean_routing(df_cluster_latlon, df_depot)
        
        dict_out = resolver_cluster_cvrp(
            cluster_id, 
            df_cluster_latlon, 
            matriz_dist, 
            depot_id, 
            cap_peso,
            df_nodos,
            k_trucks
        )
        
        dist_total_modelo += dict_out["costo_total"]
        resultados_globales[cluster_id] = dict_out

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\n>>>> Optimo Encontrado CVRP Consolidado (Total Distancia Grilla): {dist_total_modelo:.2f}")
    print(f">>>> Tiempo de Cómputo Total: {elapsed_time:.2f} segundos")

    generar_informes(resultados_globales, out_dir, elapsed_time, parser_data['name'])
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
    else:
        ruta = os.path.join(base_dir, "Instancias de Prueba VRP", "A", "A-n32-k5.vrp")
        
    disparar_rutina_cvrp_clasico(ruta)
