"""
algoritmo/genetic_algorithm.py

Orquestación del Algoritmo Genético usando PyMoo Oficial (Minimize) y ElementwiseProblem
para el TDVRPTW.
"""

import os
import sys
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gestion_flota.gestor import asignar_y_reportar
import pandas as pd
import numpy as np
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from grafo.main import execute_vrp_pipeline, clean_rut
from grafo.visualizer import plot_optimized_routes
from modelo.pymoo_problem import TDVRPTWProblem

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.optimize import minimize
from pymoo.core.sampling import Sampling
import concurrent.futures

from algoritmo.savings import clarke_wright_savings

class SavingsSeededSampling(Sampling):
    def __init__(self, savings_seed, n_clientes):
        super().__init__()
        self.savings_seed = savings_seed
        self.n_clientes = n_clientes

    def _do(self, problem, n_samples, **kwargs):
        X = np.array([np.random.permutation(self.n_clientes) for _ in range(n_samples)])
        if self.savings_seed is not None and len(self.savings_seed) == self.n_clientes:
            X[0] = self.savings_seed
        return X

def optimizar_pymoo_ga(cluster_idx, df_cluster, matriz_dist, depot_id, dia_semana=0, holgura_ventana=30.0,
                       pop_size=100, n_gen=2000, alpha_espera=50000.0, cap_vol_cm3=3750000.0, cap_peso_g=803333.33):
    """
    Ejecuta el Algoritmo Genético de PyMoo basado en Permutaciones
    sobre el problema ElementwiseProblem TDVRPTW.
    """
    clientes = [id_n for id_n in matriz_dist.index if id_n != depot_id]
    n_clientes = len(clientes)
    
    # 1. Instanciar Problema Pymoo
    problem = TDVRPTWProblem(
        df_cluster=df_cluster, 
        matriz_dist_m=matriz_dist, 
        depot_id=depot_id,
        t_inicio=540.0,
        cap_vol_cm3=cap_vol_cm3, 
        cap_peso_g=cap_peso_g,
        factor_s=0.94,
        dia_semana=dia_semana,
        alpha_espera=alpha_espera,  # Penalización por minuto de espera (balanceado vs costo_fijo_camion=100k)
        d_max_min=240.0,       # Duración máxima estricta del turno completo (4 horas)
        holgura_ventana=holgura_ventana
    )

    if n_clientes == 0:
        return {"F": 0.0, "G": 0.0, "rutas": [], "tiempos_llegada": {},
                "dist_total_m": 0.0, "costo_total": 0.0, "t_inicio": 540.0, "t_fin": 540.0, "duracion_min": 0.0}
        
    if n_clientes == 1:
        return problem.evaluar_completo([0])

    # 2. Heurística de Ahorros
    print(f"      [{cluster_idx}] Calculando Ahorros (Clarke-Wright) para semilla inicial...")
    savings_route_ids = clarke_wright_savings(
        df_cluster, matriz_dist, depot_id, 
        cap_vol_cm3=cap_vol_cm3, cap_peso_g=cap_peso_g, d_max_min=240.0, speed_kmh=25.0
    )
    id_to_idx = {cid: i for i, cid in enumerate(clientes)}
    savings_route_idx = np.array([id_to_idx[cid] for cid in savings_route_ids]) if savings_route_ids else None

    # 3. Configurar Algoritmo GA de Permutación con Semilla
    algorithm = GA(
        pop_size=pop_size,
        sampling=SavingsSeededSampling(savings_seed=savings_route_idx, n_clientes=n_clientes),
        crossover=OrderCrossover(),
        mutation=InversionMutation(prob=0.3),
        eliminate_duplicates=False  # Desactivado: evita error numpy inhomogeneous con permutaciones
    )
    
    print(f"      [{cluster_idx}] Iniciando Minimize de PyMoo...")
    # 4. Minimización
    res = minimize(
        problem,
        algorithm,
        termination=('n_gen', n_gen),
        seed=42,
        verbose=False,
        save_history=False
    )
    
    if res.X is None:
        # === DIAGNÓSTICO DE INFACTIBILIDAD ===
        print(f"\n      ⚠️  [INFACTIBLE] Clúster {cluster_idx}: No se encontró solución factible en {res.algorithm.n_gen} generaciones.")
        print(f"      Analizando la mejor solución infactible de la población final...\n")
        
        # Obtener el individuo con menor constraint violation de la última población
        pop = res.pop
        if pop is not None and len(pop) > 0:
            cv_arr = pop.get("CV").flatten()
            best_infeasible_idx = cv_arr.argmin()
            best_x = pop.get("X")[best_infeasible_idx]
            best_cv = cv_arr[best_infeasible_idx]
            best_f = pop.get("F")[best_infeasible_idx].flat[0]
            
            print(f"      Mejor individuo infactible: F = {best_f:.2f} | CV (violación total) = {best_cv:.2f}")
            
            # Re-evaluar para obtener detalles granulares
            detalles = problem.evaluar_completo(best_x)
            detalle_nodos = detalles.get("detalle_nodos", {})
            detalle_camiones = detalles.get("detalle_camiones", [])
            
            # --- Violaciones de Ventana de Tiempo ---
            nodos_violados = {nid: d for nid, d in detalle_nodos.items() if not d.get("cumple_ventana", True)}
            if nodos_violados:
                print(f"\n      ❌ VIOLACIONES DE VENTANA DE TIEMPO ({len(nodos_violados)} nodos - Tolera +{holgura_ventana} min):")
                for nid, d in nodos_violados.items():
                    t_llegada = d.get("t_inicio_servicio", 0)
                    b_v_relaxed = d.get("b_ventana_relaxed", d.get("b_ventana", 1440) + holgura_ventana)
                    viola = d.get("t_violacion_min", 0)
                    h_lleg = f"{int(t_llegada)//60:02d}:{int(t_llegada)%60:02d}"
                    h_cierre_rel = f"{int(b_v_relaxed)//60:02d}:{int(b_v_relaxed)%60:02d}"
                    print(f"        - {nid}: Servicio a las {h_lleg} | Cierre (+{holgura_ventana}m): {h_cierre_rel} | Exceso: {viola:.0f} min")
            else:
                print(f"\n      ✅ Ventanas de tiempo: Sin violaciones (Tolerancia {holgura_ventana} min incluida).")
            
            # --- Resumen de esperas excesivas ---
            nodos_espera = {nid: d for nid, d in detalle_nodos.items() if d.get("t_espera_min", 0) > 30}
            if nodos_espera:
                espera_total = sum(d["t_espera_min"] for d in nodos_espera.values())
                print(f"\n      ⏳ ESPERAS EXCESIVAS (>30 min) en {len(nodos_espera)} nodos | Total: {espera_total:.0f} min")
                for nid, d in nodos_espera.items():
                    print(f"        - {nid}: {d['t_espera_min']:.0f} min de espera")
            
            # --- Camiones utilizados ---
            n_camiones = len(detalle_camiones)
            print(f"\n      🚚 Camiones requeridos: {n_camiones}")
            for i, dc in enumerate(detalle_camiones):
                h_sal = f"{int(dc['t_salida_deposito'])//60:02d}:{int(dc['t_salida_deposito'])%60:02d}"
                h_ret = f"{int(dc['t_retorno_deposito'])//60:02d}:{int(dc['t_retorno_deposito'])%60:02d}"
                print(f"        Camión {i+1} ({dc.get('subconjunto_k','?')}): {h_sal} → {h_ret} | {dc.get('n_clientes',0)} clientes | {dc.get('dist_total_m',0)/1000:.1f} km")
            
            print(f"\n      Restricción total acumulada (CV): {best_cv:.2f} minutos de infactibilidad.")
            print(f"      Sugerencia: Aumentar pop_size, n_gen, o relajar restricciones de capacidad/tiempo.\n")
        
        raise ValueError(f"El GA de PyMoo no pudo hallar soluciones factibles para el clúster {cluster_idx}. CV mínimo alcanzado: {best_cv:.2f}")
        
    f_val = float(res.F.flat[0])
    cv_val = float(res.CV.flat[0]) if res.CV is not None else 0.0
    print(f"      PyMoo Terminado. Mejor Solución Factible: F = {f_val:.2f} // CV = {cv_val:.2f}")
    
    # Re-evaluar el mejor cromosoma para obtener las métricas detalladas
    return problem.evaluar_completo(res.X)



def min_a_hora(minutos: float) -> str:
    """Convierte minutos desde medianoche a formato HH:MM."""
    h = int(minutos) // 60
    m = int(minutos) % 60
    return f"{h:02d}:{m:02d}"


def disparar_rutina_ga(fecha_target='2026-12-04', holgura_ventana=30.0, max_camiones=20,
                       pop_size=50, n_gen=2000, alpha_espera=50000.0, cap_vol_cm3=3750000.0, cap_peso_g=803333.33):
    print(f"=== INICIANDO TDVRPTW - GA OFICIAL PYMOO [{fecha_target}] ===")
    t0 = time.time()
    
    data_path = os.path.join(base_dir, 'DatosSimulados', 'df_despacho.csv')
    try:
        df = pd.read_csv(data_path)
    except Exception:
        print("CSV de datos no encontrado en DatosSimulados.")
        return

    # Extraer dinámicamente el día de la semana (0=Lunes, 6=Domingo)
    dia_semana_target = pd.to_datetime(fecha_target).weekday()
    
    if 'fecha_entrega' in df.columns:
        df_filtro = df[df['fecha_entrega'] == fecha_target].copy()
    else:
        df_filtro = df.copy()
    print(f"Pedidos capturados para {fecha_target} (Día {dia_semana_target}): {len(df_filtro)}")
    
    if 'id_cliente' in df_filtro.columns and 'id_pedido' in df_filtro.columns:
        df_filtro['rut_clean'] = df_filtro['id_cliente'].apply(clean_rut)
        df_filtro['id_nodo'] = df_filtro['id_pedido'].astype(str).str.strip() + "_" + df_filtro['rut_clean']
    
    # Normalizar nombres de columnas geográficas al estándar minuscula del pipeline
    df_filtro.rename(columns={'Latitud': 'latitud', 'Longitud': 'longitud', 'Dirección': 'direccion_ruteo'}, inplace=True)
    
    temp_excel_path = os.path.join(base_dir, 'EDA', 'df_despacho.csv')
    os.makedirs(os.path.dirname(temp_excel_path), exist_ok=True)
    df_filtro.to_csv(temp_excel_path, index=False)
    
    matrices_km_o_m, rutas_dict, G, depot_coords = execute_vrp_pipeline(input_file=temp_excel_path)
    
    out_dir = os.path.join(base_dir, 'resultados', 'rutas')
    mapa_dir = os.path.join(base_dir, 'resultados', 'mapa_rutas')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(mapa_dir, exist_ok=True)
    depot_id = "DEPOT_01_BASE"
    
    MAX_CAMIONES_GLOBALES = max_camiones  # <--- Parámetro dinámico para la flota
    resultados_globales = {}
    
    tasks = []
    for cluster_id, matriz_dist in matrices_km_o_m.items():
        tasks.append((cluster_id, df_filtro, matriz_dist, depot_id, dia_semana_target, holgura_ventana,
                      pop_size, n_gen, alpha_espera, cap_vol_cm3, cap_peso_g))

    max_w = max(1, (os.cpu_count() or 2) // 2)
    print(f"\n[PyMoo] Iniciando procesamiento paralelo de clústeres con {max_w} workers (Seguridad CPU activa)...")
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_w) as executor:
        future_to_cluster = {
            executor.submit(optimizar_pymoo_ga, *task): task[0]
            for task in tasks
        }
        
        for future in concurrent.futures.as_completed(future_to_cluster):
            cluster_id = future_to_cluster[future]
            try:
                dict_out = future.result()
                resultados_globales[cluster_id] = dict_out
                print(f"[PyMoo] Cluster {cluster_id} Finalizado.")
            except Exception as e:
                print(f"Error procesando {cluster_id}: {e}")
            
    t1 = time.time()
    tiempo_total_min = (t1 - t0) / 60.0

    # LLAMADA AL GESTOR DE FLOTA GLOBAL
    asignar_y_reportar(
        resultados_clusters=resultados_globales,
        max_vehiculos=MAX_CAMIONES_GLOBALES,
        df_filtro=df_filtro,
        depot_id=depot_id,
        fecha_target=fecha_target,
        tipo_algoritmo="Hibrido Savings GA",
        out_dir=out_dir,
        rutas_dict_global=rutas_dict,
        G=G,
        mapa_dir=mapa_dir,
        depot_coords=depot_coords,
        tiempo_computo_min=tiempo_total_min
    )
        
    print(f"\n[Éxito] Optimización y Asignación de Flota finalizada.")

if __name__ == "__main__":
    disparar_rutina_ga()

