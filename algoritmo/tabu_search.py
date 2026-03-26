"""
algoritmo/tabu_search.py

Implementación de Algoritmo de Búsqueda Tabú para resolver el TDVRPTW.
Integra y procesa las evaluaciones usando directamente el PyMoo `ElementwiseProblem` del modelo,
sumando las violaciones de las Hard Constraints con Big-M para unificada lógica.
"""

import os
import sys
import random
import pandas as pd

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from grafo.main import execute_vrp_pipeline, clean_rut
from grafo.visualizer import plot_optimized_routes
from modelo.pymoo_problem import TDVRPTWProblem

# =========================================================
# CONFIGURACIONES DE LA BÚSQUEDA TABÚ
# =========================================================
MAX_ITER = 150
TABU_TENURE_BASE = 5
MAX_NEIGHBORS = 40
BIG_M_PENALTY = 1_000_000

class IndividuoTabu:
    def __init__(self, cromosoma):
        self.cromosoma = cromosoma
        self.fitness_efectivo = float('inf')  # F(x) + M * G(x)
        self.f_obj = float('inf')             # F(x) puro
        self.g_fail = float('inf')            # G(x) penalidades
        self.rutas = []
        self.tiempos_llegada = {}
        self.movimiento = None

def evaluar_con_pymoo(individuo, problem_instance):
    """
    Empaqueta el cromosoma para el Problem inyectado y suma costos + multas funcionales.
    """
    out = {}
    problem_instance._evaluate(individuo.cromosoma, out)
    
    individuo.f_obj = out["F"]
    individuo.g_fail = out.get("G", 0.0)
    
    # Fitness Efectivo (Coste + Multa masiva por restricciones)
    individuo.fitness_efectivo = individuo.f_obj + (individuo.g_fail * BIG_M_PENALTY)
    
    individuo.rutas = out["rutas"]
    individuo.tiempos_llegada = out["tiempos_llegada"]


def generar_vecinos(individuo, num_vecinos):
    vecinos = []
    n = len(individuo.cromosoma)
    if n < 2: return []
    
    intentos = 0
    movimientos_usados = set()
    
    while len(vecinos) < num_vecinos and intentos < num_vecinos * 3:
        i, j = random.sample(range(n), 2)
        i, j = min(i, j), max(i, j)
        mov_tuple = (i, j)
        
        if mov_tuple not in movimientos_usados:
            movimientos_usados.add(mov_tuple)
            nuevo_cromo = list(individuo.cromosoma)
            nuevo_cromo[i], nuevo_cromo[j] = nuevo_cromo[j], nuevo_cromo[i]
            
            vec = IndividuoTabu(nuevo_cromo)
            vec.movimiento = (individuo.cromosoma[i], individuo.cromosoma[j])
            vecinos.append(vec)
            
        intentos += 1
        
    return vecinos

def optimizar_cluster_tabu(cluster_idx, df_cluster, matriz_dist, depot_id):
    """Ejecuta Búsqueda Tabú acoplada al PyMoo Problem para evaluación."""
    problem = TDVRPTWProblem(
        df_cluster=df_cluster, 
        matriz_dist_m=matriz_dist, 
        depot_id=depot_id,
        t_inicio=540.0,
        factor_s=1.2
    )

    clientes = problem.clientes_ids
    if len(clientes) == 0:
        ind = IndividuoTabu([])
        ind.fitness_efectivo = 0.0
        ind.f_obj = 0.0
        ind.g_fail = 0.0
        return ind
        
    if len(clientes) == 1:
        ind = IndividuoTabu([0])
        evaluar_con_pymoo(ind, problem)
        return ind
        
    # 1. Solución Inicial (Greedy o Aleatoria pura)
    cromosoma_inicial = list(range(len(clientes)))
    random.shuffle(cromosoma_inicial)
    
    mejor_global = IndividuoTabu(cromosoma_inicial)
    evaluar_con_pymoo(mejor_global, problem)
    solucion_actual = mejor_global
    
    lista_tabu = {}
    
    for iteracion in range(MAX_ITER):
        vecinos = generar_vecinos(solucion_actual, MAX_NEIGHBORS)
        Mejor_vecino = None
        
        for vec in vecinos:
            evaluar_con_pymoo(vec, problem)
            
            mov_inverso = (vec.movimiento[1], vec.movimiento[0])
            es_tabu = (vec.movimiento in lista_tabu) or (mov_inverso in lista_tabu)
            
            # Criterio Aspiración
            if es_tabu and vec.fitness_efectivo < mejor_global.fitness_efectivo:
                es_tabu = False 
                
            if not es_tabu:
                if Mejor_vecino is None or vec.fitness_efectivo < Mejor_vecino.fitness_efectivo:
                    Mejor_vecino = vec
                    
        if Mejor_vecino is None and vecinos:
            Mejor_vecino = sorted(vecinos, key=lambda x: x.fitness_efectivo)[0]
        elif not vecinos:
            break
            
        solucion_actual = Mejor_vecino
        
        if solucion_actual.fitness_efectivo < mejor_global.fitness_efectivo:
            mejor_global = solucion_actual
            
        # Refrescar Tenures
        for mov in list(lista_tabu.keys()):
            lista_tabu[mov] -= 1
            if lista_tabu[mov] <= 0:
                del lista_tabu[mov]
                
        lista_tabu[solucion_actual.movimiento] = TABU_TENURE_BASE
        
    return mejor_global


def min_a_hora(minutos: float) -> str:
    """Convierte minutos desde medianoche a formato HH:MM."""
    h = int(minutos) // 60
    m = int(minutos) % 60
    return f"{h:02d}:{m:02d}"


def disparar_rutina_tabu():
    print("=== INICIANDO TDVRPTW - TABÚ CON EVALUADOR PYMOO ===")
    
    data_path = os.path.join(base_dir, 'DatosSimulados', 'df_despacho.csv')
    try:
        df = pd.read_csv(data_path)
    except Exception:
        print("CSV de datos no encontrado. Cancelando.")
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
    
    # Normalizar nombres de columnas geográficas al estándar minúscula del pipeline
    df_filtro.rename(columns={'Latitud': 'latitud', 'Longitud': 'longitud', 'Dirección': 'direccion_ruteo'}, inplace=True)
    
    temp_excel_path = os.path.join(base_dir, 'EDA', 'temp_vrp_orders.xlsx')
    os.makedirs(os.path.dirname(temp_excel_path), exist_ok=True)
    df_filtro.to_excel(temp_excel_path, index=False)
    
    matrices_km_o_m, rutas_dict, G = execute_vrp_pipeline(input_file=temp_excel_path)
    
    out_dir = os.path.join(base_dir, 'resultados', 'rutas')
    mapa_dir = os.path.join(base_dir, 'resultados', 'mapa_rutas')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(mapa_dir, exist_ok=True)
    depot_id = "DEPOT_01_BASE"
    
    reporte_rutas_md = f"# Reporte Búsqueda Tabú (Integración PyMoo) - {fecha_target}\n\n"
    
    for cluster_id, matriz_dist in matrices_km_o_m.items():
        print(f"\nTabú Cluster {cluster_id} con {len(matriz_dist)-1} clientes...")
        mejor_solucion = optimizar_cluster_tabu(cluster_id, df_filtro, matriz_dist, depot_id)
        
        # Extraer métricas adicionales del out almacenado en el individuo
        t_ini    = mejor_solucion.tiempos_llegada.get('__t_inicio__', 540.0)
        t_fin    = mejor_solucion.tiempos_llegada.get('__t_fin__', 0.0)
        dur_min  = mejor_solucion.tiempos_llegada.get('__duracion__', 0.0)
        dist_m   = mejor_solucion.f_obj / 1.2  # Revertir factor S para obtener distancia pura
        
        # Recuperar directamente desde la reevaluación del mejor cromosoma
        from modelo.pymoo_problem import TDVRPTWProblem
        prob_tmp = TDVRPTWProblem(df_cluster=df_filtro, matriz_dist_m=matriz_dist, depot_id=depot_id, t_inicio=540.0, factor_s=1.2)
        out_tmp = {}
        if mejor_solucion.cromosoma:
            prob_tmp._evaluate(mejor_solucion.cromosoma, out_tmp)
            t_ini   = out_tmp.get("t_inicio", 540.0)
            t_fin   = out_tmp.get("t_fin", 0.0)
            dur_min = out_tmp.get("duracion_min", 0.0)
            dist_m  = out_tmp.get("dist_total_m", mejor_solucion.f_obj)
        
        dur_h = int(dur_min) // 60
        dur_m_rest = int(dur_min) % 60
        
        print(f" -> Costo F(x): {mejor_solucion.f_obj:.2f} // Multa G(x): {mejor_solucion.g_fail:.2f} // Duración: {dur_h}h {dur_m_rest}min")
        
        reporte_rutas_md += f"## Cluster {cluster_id}\n"
        reporte_rutas_md += f"| Métrica | Valor |\n| :--- | :--- |\n"
        reporte_rutas_md += f"| **Distancia Total** | {dist_m:,.1f} m |\n"
        reporte_rutas_md += f"| **Costo Ruta (× factor S)** | {mejor_solucion.f_obj:,.2f} |\n"
        reporte_rutas_md += f"| **Penalidad (G)** | {mejor_solucion.g_fail:.2f} |\n"
        reporte_rutas_md += f"| **Hora Salida Depósito** | {min_a_hora(t_ini)} |\n"
        reporte_rutas_md += f"| **Hora Retorno Depósito** | {min_a_hora(t_fin)} |\n"
        reporte_rutas_md += f"| **Duración Total** | {dur_h}h {dur_m_rest}min |\n"
        reporte_rutas_md += f"| **Vehículos Asignados** | {len(mejor_solucion.rutas)} |\n\n"
        
        for k_idx, ruta in enumerate(mejor_solucion.rutas):
            reporte_rutas_md += f"### Camión {k_idx + 1}\n"
            reporte_rutas_md += "| # | Nodo | Llegada |\n"
            reporte_rutas_md += "| :--- | :--- | :--- |\n"
            reporte_rutas_md += f"| 0 | {depot_id} | {min_a_hora(t_ini)} |\n"
            
            for i, nodo in enumerate(ruta):
                t_arr = mejor_solucion.tiempos_llegada.get(nodo, 0)
                reporte_rutas_md += f"| {i+1} | {nodo} | {min_a_hora(t_arr)} |\n"
                
            reporte_rutas_md += f"| {len(ruta)+1} | {depot_id} | {min_a_hora(t_fin)} |\n\n"
                
        reporte_rutas_md += "\n---\n"
        
        # Visualizar en mapa si hay rutas
        if mejor_solucion.rutas:
            mapa_cluster_path = os.path.join(mapa_dir, f'rutas_tabu_cluster_{cluster_id}_{fecha_target}.html')
            info_astar = rutas_dict.get(cluster_id, {})
            df_cluster = df_filtro[df_filtro['id_nodo'].isin(
                [n for ruta in mejor_solucion.rutas for n in ruta]
            )].copy()
            try:
                plot_optimized_routes(
                    rutas_por_camion=mejor_solucion.rutas,
                    df_cluster=df_cluster,
                    info_rutas_astar=info_astar,
                    depot_id=depot_id,
                    cluster_id=cluster_id,
                    G=G,
                    filepath=mapa_cluster_path
                )
            except Exception as ve:
                print(f"  Advertencia: No se pudo generar mapa para cluster {cluster_id}: {ve}")
        
    out_file = os.path.join(out_dir, f'ruta_tabu_pymoo_{fecha_target}.md')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(reporte_rutas_md)
        
    print(f"\n[Éxito] Optimización finalizada exitosamente. Archivo: {out_file}")

if __name__ == "__main__":
    disparar_rutina_tabu()

