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

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from grafo.main import execute_vrp_pipeline, clean_rut
from grafo.visualizer import plot_optimized_routes
from modelo.pymoo_problem import TDVRPTWProblem
from algoritmo.config import DEFAULT_OPTIMIZATION_CONFIG

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.optimize import minimize

def _merge_config(config: dict | None) -> dict:
    out = DEFAULT_OPTIMIZATION_CONFIG.copy()
    if isinstance(config, dict):
        out.update({k: v for k, v in config.items() if v is not None})
    return out


def _load_input_dataframe(input_csv_path: str | None) -> tuple[pd.DataFrame, str]:
    if input_csv_path:
        df = pd.read_csv(input_csv_path)
        return df, input_csv_path

    candidate_eda = os.path.join(base_dir, 'EDA', 'df_despacho.csv')
    candidate_sim = os.path.join(base_dir, 'DatosSimulados', 'df_despacho.csv')

    if os.path.exists(candidate_eda):
        try:
            df_eda = pd.read_csv(candidate_eda)
            if not df_eda.empty:
                return df_eda, candidate_eda
        except Exception:
            pass

    if os.path.exists(candidate_sim):
        df_sim = pd.read_csv(candidate_sim)
        return df_sim, candidate_sim

    raise FileNotFoundError(f"No se encontró una fuente de datos válida: {candidate_eda} ni {candidate_sim}")


def _normalize_date_series(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values, errors='coerce').dt.strftime('%Y-%m-%d')


def optimizar_pymoo_ga(cluster_idx, df_cluster, matriz_dist, depot_id, dia_semana=0, config: dict | None = None):
    """
    Ejecuta el Algoritmo Genético de PyMoo basado en Permutaciones
    sobre el problema ElementwiseProblem TDVRPTW.
    """
    clientes = [id_n for id_n in matriz_dist.index if id_n != depot_id]
    n_clientes = len(clientes)
    
    cfg = _merge_config(config)

    # 1. Instanciar Problema Pymoo
    problem = TDVRPTWProblem(
        df_cluster=df_cluster, 
        matriz_dist_m=matriz_dist, 
        depot_id=depot_id,
        t_inicio=float(cfg["t_inicio"]),
        cap_vol_cm3=float(cfg["cap_vol_cm3"]),
        cap_peso_g=float(cfg["cap_peso_g"]),
        factor_s=float(cfg["factor_s"]),
        dia_semana=dia_semana,
        alpha_espera=float(cfg["alpha_espera"]),  # Penalización por minuto de espera (balanceado vs costo_fijo_camion=100k)
        d_max_min=float(cfg["d_max_min"]),
    )
    problem.costo_fijo_camion = float(cfg.get("costo_fijo_camion", 0.0))

    if n_clientes == 0:
        return {"F": 0.0, "G": 0.0, "rutas": [], "tiempos_llegada": {},
                "dist_total_m": 0.0, "costo_total": 0.0, "t_inicio": 540.0, "t_fin": 540.0, "duracion_min": 0.0}
        
    if n_clientes == 1:
        return problem.evaluar_completo([0])

    # 2. Configurar Algoritmo GA de Permutación
    algorithm = GA(
        pop_size=int(cfg["ga_pop_size"]),
        sampling=PermutationRandomSampling(),
        crossover=OrderCrossover(),
        mutation=InversionMutation(),
        eliminate_duplicates=False  # Desactivado: evita error numpy inhomogeneous con permutaciones
    )
    
    print("      Iniciando Minimize de PyMoo...")
    # 3. Minimización
    res = minimize(
        problem,
        algorithm,
        termination=('n_gen', int(cfg["ga_n_gen"])),
        seed=int(cfg["ga_seed"]),
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
                print(f"\n      ❌ VIOLACIONES DE VENTANA DE TIEMPO ({len(nodos_violados)} nodos):")
                for nid, d in nodos_violados.items():
                    t_llegada = d.get("t_inicio_servicio", 0)
                    b_v = d.get("b_ventana", 1440)
                    viola = d.get("t_violacion_min", 0)
                    h_lleg = f"{int(t_llegada)//60:02d}:{int(t_llegada)%60:02d}"
                    h_cierre = f"{int(b_v)//60:02d}:{int(b_v)%60:02d}"
                    print(f"        - {nid}: Servicio a las {h_lleg} | Cierre ventana: {h_cierre} | Exceso: {viola:.0f} min")
            else:
                print(f"\n      ✅ Ventanas de tiempo: Sin violaciones.")
            
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


def disparar_rutina_ga(
    input_csv_path: str = None,
    fecha_target: str = None,
    max_vehiculos_globales: int | None = 20,
    config: dict | None = None,
):
    print("=== INICIANDO TDVRPTW - GA OFICIAL PYMOO ===")
    cfg = _merge_config(config)

    df, data_path = _load_input_dataframe(input_csv_path)
    if df.empty:
        raise ValueError(f"La fuente de datos está vacía: {data_path}. Carga un CSV con pedidos antes de optimizar.")

    if fecha_target is None:
        if 'fecha_entrega' in df.columns and not df['fecha_entrega'].dropna().empty:
            normalized_dates = _normalize_date_series(df['fecha_entrega']).dropna()
            if not normalized_dates.empty:
                fecha_target = str(sorted(normalized_dates.unique())[-1])
            else:
                fecha_target = pd.Timestamp.now().strftime('%Y-%m-%d')
        else:
            fecha_target = pd.Timestamp.now().strftime('%Y-%m-%d')

    # Extraer dinámicamente el día de la semana (0=Lunes, 6=Domingo)
    dia_semana_target = pd.to_datetime(fecha_target).weekday()
    
    if 'fecha_entrega' in df.columns:
        normalized_source_dates = _normalize_date_series(df['fecha_entrega'])
        target_str = pd.to_datetime(fecha_target, errors='coerce').strftime('%Y-%m-%d')
        df_filtro = df[normalized_source_dates == target_str].copy()
        if df_filtro.empty:
            available_dates = sorted(normalized_source_dates.dropna().unique().tolist())
            available_text = ", ".join(available_dates[:12]) if available_dates else "sin fechas válidas"
            raise ValueError(
                f"No hay pedidos para la fecha {target_str}. "
                f"Fechas disponibles en la fuente ({data_path}): {available_text}"
            )
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
    
    matrices_km_o_m, rutas_dict, G, depot_coords = execute_vrp_pipeline(
        input_file=temp_excel_path,
        clustering_time_column=str(cfg["clustering_time_column"]),
        clustering_default_window_start_hour=int(cfg["clustering_default_window_start_hour"]),
        clustering_alpha_time=float(cfg["clustering_alpha_time"]),
        clustering_eps=float(cfg["clustering_eps"]),
        clustering_min_samples=int(cfg["clustering_min_samples"]),
        clustering_rescue_threshold=float(cfg["clustering_rescue_threshold"]),
        force_outlier_rescue=bool(cfg["force_outlier_rescue"]),
    )
    
    out_dir = os.path.join(base_dir, 'resultados', 'rutas')
    mapa_dir = os.path.join(base_dir, 'resultados', 'mapa_rutas')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(mapa_dir, exist_ok=True)
    depot_id = "DEPOT_01_BASE"
    
    MAX_CAMIONES_GLOBALES = int(max_vehiculos_globales if max_vehiculos_globales is not None else cfg["max_vehiculos_globales"])
    resultados_globales = {}
    
    for cluster_id, matriz_dist in matrices_km_o_m.items():
        print(f"\n[PyMoo] Optimizando Cluster {cluster_id} con {len(matriz_dist)-1} clientes...")
        try:
            dict_out = optimizar_pymoo_ga(
                cluster_id,
                df_filtro,
                matriz_dist,
                depot_id,
                dia_semana=dia_semana_target,
                config=cfg,
            )
            
            rutas_asignadas  = dict_out["rutas"]
            resultados_globales[cluster_id] = dict_out

            
            pass
            
        except Exception as e:
            print(f"Error procesando {cluster_id}: {e}")
            
    # LLAMADA AL GESTOR DE FLOTA GLOBAL
    asignar_y_reportar(
        resultados_clusters=resultados_globales,
        max_vehiculos=MAX_CAMIONES_GLOBALES,
        df_filtro=df_filtro,
        depot_id=depot_id,
        fecha_target=fecha_target,
        tipo_algoritmo="Genético PyMoo",
        out_dir=out_dir,
        rutas_dict_global=rutas_dict,
        G=G,
        mapa_dir=mapa_dir,
        depot_coords=depot_coords
    )
        
    print(f"\n[Éxito] Optimización y Asignación de Flota finalizada.")
    return {
        "fecha_target": fecha_target,
        "dia_semana_target": int(dia_semana_target),
        "clusters_optimizados": int(len(resultados_globales)),
        "max_vehiculos_globales": int(MAX_CAMIONES_GLOBALES),
        "source_csv": data_path,
        "config_applied": cfg,
    }

if __name__ == "__main__":
    disparar_rutina_ga()
