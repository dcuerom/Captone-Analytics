"""
algoritmo/genetic_algorithm.py

Orquestación del Algoritmo Genético usando PyMoo Oficial (Minimize) y ElementwiseProblem
para el TDVRPTW.
"""

import os
import sys
import pandas as pd
import numpy as np

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

def optimizar_pymoo_ga(cluster_idx, df_cluster, matriz_dist, depot_id):
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
        cap_vol_cm3=10_000_000, 
        cap_peso_g=5_000_000,
        factor_s=1.2
    )

    if n_clientes == 0:
        return {"F": 0.0, "G": 0.0, "rutas": [], "tiempos_llegada": {},
                "dist_total_m": 0.0, "costo_total": 0.0, "t_inicio": 540.0, "t_fin": 540.0, "duracion_min": 0.0}
        
    if n_clientes == 1:
        return problem.evaluar_completo([0])

    # 2. Configurar Algoritmo GA de Permutación
    algorithm = GA(
        pop_size=50,
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
        termination=('n_gen', 100),
        seed=42,
        verbose=False,
        save_history=False
    )
    
    if res.X is None:
        raise ValueError(f"El GA de PyMoo no pudo hallar soluciones factibles para el clúster {cluster_idx}. Las Hard Constraints no se cumplieron.")
        
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


def disparar_rutina_ga():
    print("=== INICIANDO TDVRPTW - GA OFICIAL PYMOO ===")
    
    data_path = os.path.join(base_dir, 'DatosSimulados', 'df_despacho.csv')
    try:
        df = pd.read_csv(data_path)
    except Exception:
        print("CSV de datos no encontrado en DatosSimulados.")
        return
        
    fecha_target = '2026-12-03'
    if 'fecha_entrega' in df.columns:
        df_filtro = df[df['fecha_entrega'] == fecha_target].copy()
    else:
        df_filtro = df.copy()
    print(f"Pedidos capturados para {fecha_target}: {len(df_filtro)}")
    
    if 'id_cliente' in df_filtro.columns and 'id_pedido' in df_filtro.columns:
        df_filtro['rut_clean'] = df_filtro['id_cliente'].apply(clean_rut)
        df_filtro['id_nodo'] = df_filtro['id_pedido'].astype(str).str.strip() + "_" + df_filtro['rut_clean']
    
    # Normalizar nombres de columnas geográficas al estándar minuscula del pipeline
    df_filtro.rename(columns={'Latitud': 'latitud', 'Longitud': 'longitud', 'Dirección': 'direccion_ruteo'}, inplace=True)
    
    temp_excel_path = os.path.join(base_dir, 'EDA', 'df_despacho.csv')
    os.makedirs(os.path.dirname(temp_excel_path), exist_ok=True)
    df_filtro.to_csv(temp_excel_path, index=False)
    
    matrices_km_o_m, rutas_dict, G = execute_vrp_pipeline(input_file=temp_excel_path)
    
    out_dir = os.path.join(base_dir, 'resultados', 'rutas')
    mapa_dir = os.path.join(base_dir, 'resultados', 'mapa_rutas')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(mapa_dir, exist_ok=True)
    depot_id = "DEPOT_01_BASE"
    
    reporte_rutas_md = f"# Reporte GA (PyMoo Problem) - {fecha_target}\n\n"
    
    for cluster_id, matriz_dist in matrices_km_o_m.items():
        print(f"\n[PyMoo] Optimizando Cluster {cluster_id} con {len(matriz_dist)-1} clientes...")
        try:
            dict_out = optimizar_pymoo_ga(cluster_id, df_filtro, matriz_dist, depot_id)
            
            f_val       = float(dict_out.get("costo_total", 0.0))
            rutas_asignadas  = dict_out["rutas"]
            tiempos_llegada  = dict_out["tiempos_llegada"]
            detalle_nodos    = dict_out.get("detalle_nodos", {})
            g_fail      = float(dict_out.get("restricciones_fail", 0.0))
            dist_m      = float(dict_out.get("dist_total_m", 0.0))
            costo       = float(dict_out.get("costo_total", 0.0))
            t_ini       = float(dict_out.get("t_inicio", 540.0))
            t_fin       = float(dict_out.get("t_fin", 0.0))
            dur_min     = float(dict_out.get("duracion_min", 0.0))
            
            dur_h = int(dur_min) // 60
            dur_m = int(dur_min) % 60
            
            # Contar cumplimiento de ventanas
            total_nodos = len(detalle_nodos)
            nodos_ok = sum(1 for d in detalle_nodos.values() if d["cumple_ventana"])
            nodos_espera = sum(1 for d in detalle_nodos.values() if d["t_espera_min"] > 0)
            nodos_violados = total_nodos - nodos_ok
            espera_total = sum(d["t_espera_min"] for d in detalle_nodos.values())
            violacion_total = sum(d["t_violacion_min"] for d in detalle_nodos.values())
            
            reporte_rutas_md += f"## Cluster {cluster_id}\n\n"
            reporte_rutas_md += f"### Resumen Operativo\n"
            reporte_rutas_md += f"| Métrica | Valor |\n| :--- | :--- |\n"
            reporte_rutas_md += f"| Distancia Total | {dist_m:,.1f} m ({dist_m/1000:.2f} km) |\n"
            reporte_rutas_md += f"| Costo Ruta (F = dist × S) | {costo:,.2f} |\n"
            reporte_rutas_md += f"| Hora Salida Depósito | {min_a_hora(t_ini)} |\n"
            reporte_rutas_md += f"| Hora Retorno Depósito | {min_a_hora(t_fin)} |\n"
            reporte_rutas_md += f"| Duración Total | {dur_h}h {dur_m}min |\n"
            reporte_rutas_md += f"| Vehículos Asignados | {len(rutas_asignadas)} |\n\n"
            
            reporte_rutas_md += f"### Restricción 14: Cumplimiento de Ventanas de Tiempo\n"
            reporte_rutas_md += f"| Indicador | Valor |\n| :--- | :--- |\n"
            reporte_rutas_md += f"| Clientes atendidos en ventana | {nodos_ok}/{total_nodos} |\n"
            reporte_rutas_md += f"| Clientes con espera (llegada anticipada) | {nodos_espera} |\n"
            reporte_rutas_md += f"| Clientes con violación (llegada tardía) | {nodos_violados} |\n"
            reporte_rutas_md += f"| Tiempo de espera acumulado | {espera_total:.1f} min |\n"
            reporte_rutas_md += f"| Violación acumulada (G) | {violacion_total:.1f} min |\n\n"
            reporte_rutas_md += f"### Desglose de Tiempos por Camión\n"
            detalle_camiones = dict_out.get("detalle_camiones", [])
            reporte_rutas_md += "| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |\n"
            reporte_rutas_md += "| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
            for k_idx, dc in enumerate(detalle_camiones):
                tv = float(dc.get("t_viaje_efectivo_min", 0))
                te = float(dc.get("t_espera_total_min", 0))
                ts = float(dc.get("t_servicio_total_min", 0))
                dd = float(dc.get("dist_total_m", 0)) / 1000.0
                sal = float(dc.get("t_salida_deposito", 540))
                ret = float(dc.get("t_retorno_deposito", 0))
                nc = dc.get("n_clientes", 0)
                reporte_rutas_md += (
                    f"| {k_idx+1} | {min_a_hora(sal)} | {min_a_hora(ret)} "
                    f"| {tv:.1f} min | {te:.1f} min | {ts:.1f} min "
                    f"| {dd:.2f} km | {nc} |\n"
                )
            reporte_rutas_md += "\n"
            
            for k_idx, ruta in enumerate(rutas_asignadas):
                reporte_rutas_md += f"### Camión {k_idx + 1} — Detalle de Paradas\n"
                reporte_rutas_md += "| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |\n"
                reporte_rutas_md += "| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
                reporte_rutas_md += f"| 0 | {depot_id} | — | — | — | {min_a_hora(t_ini)} | — | {min_a_hora(t_ini)} | — | — | — | — | — | 🏠 |\n"
                
                for i, nodo in enumerate(ruta):
                    det = detalle_nodos.get(nodo, {})
                    dist_km = float(det.get("dist_arco_m", 0)) / 1000.0
                    t_viaje = float(det.get("t_viaje_min", 0))
                    vel_kmh = (dist_km / (t_viaje / 60.0)) if t_viaje > 0 else 0.0
                    
                    t_real  = float(det.get("t_llegada_real", 0))
                    a_v     = float(det.get("a_ventana", 0))
                    b_v     = float(det.get("b_ventana", 1440))
                    t_serv_ini  = float(det.get("t_inicio_servicio", 0))
                    t_serv_dur = float(det.get("t_servicio_min", 0))
                    vol_l      = float(det.get("volumen_cm3", 0)) / 1000.0
                    peso_kg    = float(det.get("peso_g", 0)) / 1000.0
                    espera  = float(det.get("t_espera_min", 0))
                    viola   = float(det.get("t_violacion_min", 0))
                    ok      = det.get("cumple_ventana", True)
                    
                    estado = "✅" if ok and espera == 0 else ("⏳" if ok else "❌")
                    espera_str = f"{espera:.0f} m" if espera > 0 else "—"
                    viola_str = f"{viola:.0f} m" if viola > 0 else "—"
                    
                    reporte_rutas_md += (
                        f"| {i+1} | {nodo} | {dist_km:.2f} | {t_viaje:.1f} m | {vel_kmh:.1f} "
                        f"| {min_a_hora(t_real)} "
                        f"| [{min_a_hora(a_v)},{min_a_hora(b_v)}] "
                        f"| {min_a_hora(t_serv_ini)} "
                        f"| {t_serv_dur:.1f} m | {vol_l:.1f} L | {peso_kg:.1f} kg "
                        f"| {espera_str} | {viola_str} | {estado} |\n"
                    )
                
                # Fila de retorno al depósito
                dc = detalle_camiones[k_idx] if k_idx < len(detalle_camiones) else {}
                dist_ret_km = float(dc.get("dist_retorno_m", 0)) / 1000.0
                t_retorno_min = float(dc.get("t_viaje_retorno_min", 0))
                vel_ret = (dist_ret_km / (t_retorno_min / 60.0)) if t_retorno_min > 0 else 0.0
                t_llegada_ret = float(dc.get("t_retorno_deposito", t_fin))
                
                reporte_rutas_md += f"| {len(ruta)+1} | {depot_id} | {dist_ret_km:.2f} | {t_retorno_min:.1f} m | {vel_ret:.1f} | {min_a_hora(t_llegada_ret)} | — | — | — | — | — | — | — | 🏠 |\n\n"
                
            reporte_rutas_md += "\n---\n"
            
            # Visualizar en mapa si hay rutas
            if rutas_asignadas:
                mapa_cluster_path = os.path.join(mapa_dir, f'rutas_ga_cluster_{cluster_id}_{fecha_target}.html')
                info_astar = rutas_dict.get(cluster_id, {})
                df_cluster = df_filtro[df_filtro['id_nodo'].isin(
                    [n for ruta in rutas_asignadas for n in ruta]
                )].copy()
                try:
                    plot_optimized_routes(
                        rutas_por_camion=rutas_asignadas,
                        df_cluster=df_cluster,
                        info_rutas_astar=info_astar,
                        depot_id=depot_id,
                        cluster_id=cluster_id,
                        G=G,
                        filepath=mapa_cluster_path
                    )
                except Exception as ve:
                    print(f"  Advertencia: No se pudo generar mapa para cluster {cluster_id}: {ve}")
            
        except Exception as e:
            print(f"Error procesando {cluster_id}: {e}")
            reporte_rutas_md += f"## Cluster {cluster_id}\n- *Fallo logístico o violación Hard constraint extrema*\n---\n"
            
    out_file = os.path.join(out_dir, f'ruta_genetico_pymoo_{fecha_target}.md')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(reporte_rutas_md)
        
    print(f"\n[Éxito] Optimización finalizada exitosamente. Archivo: {out_file}")

if __name__ == "__main__":
    disparar_rutina_ga()

