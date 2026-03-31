"""
gestion_flota/gestor.py

Orquestador Global de Vehículos.
Recibe los diccionarios de resultados optimizados de cada clúster y los redistribuye inter-cluster
para optimizar la utilización de una Flota Fija Global mediante asignación de turnos multiplexados.
"""

import os
import datetime
import pandas as pd
import networkx as nx
from typing import Optional
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafo.visualizer import plot_global_flota_interactive

class BloqueRuta:
    def __init__(self, cluster_id, ruta, detalle_camion, idx_en_cluster):
        self.cluster_id = cluster_id
        self.ruta = ruta
        self.dc = detalle_camion
        self.idx_en_cluster = idx_en_cluster
        self.t_salida = float(detalle_camion.get("t_salida_deposito", 540))
        self.t_retorno = float(detalle_camion.get("t_retorno_deposito", 0))
        self.turno_op = detalle_camion.get("turno_operacion", "-")
        self.subc_k = detalle_camion.get("subconjunto_k", "-")

class VehiculoGlobal:
    def __init__(self, id_vehiculo):
        self.id_vehiculo = id_vehiculo
        self.bloques = []
        self.plantilla_base = None # Almacenará 'K1' o 'K2' para forzar homogeneidad
        
    def puede_absorber(self, bloque: BloqueRuta) -> bool:
        # Extraemos el prefijo de la plantilla (ej: 'K1' de 'K11')
        tipo_k = bloque.subc_k[:2] if len(bloque.subc_k) >= 2 else None
        
        # 1. Regla estructural de turno (No cruzar K1 con K2)
        if self.plantilla_base is not None and tipo_k is not None:
            if self.plantilla_base != tipo_k:
                return False
                
        # 2. Regla física temporal de superposición
        if not self.bloques:
            return True
        ultimo = self.bloques[-1]
        return bloque.t_salida >= ultimo.t_retorno
        
    def asignar(self, bloque: BloqueRuta):
        if self.plantilla_base is None:
            tipo_k = bloque.subc_k[:2] if len(bloque.subc_k) >= 2 else None
            if tipo_k:
                self.plantilla_base = tipo_k
        self.bloques.append(bloque)


def asignar_y_reportar(
    resultados_clusters, 
    max_vehiculos, 
    df_filtro, 
    depot_id, 
    fecha_target, 
    tipo_algoritmo="Genético PyMoo", 
    out_dir=None,
    rutas_dict_global=None,
    G: Optional[nx.MultiDiGraph] = None,
    mapa_dir=None
):
    """
    1. Desempaqueta todos los resultados intra-cluster.
    2. Pasa los bloques (rutas) a una flota fija mediante orden Greedy (Prioridad de Salida).
    3. Genera un reporte Markdown global agrupado por vehículo.
    """
    if out_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out_dir = os.path.join(base_dir, 'resultados', 'rutas')
        
    # 1. Recolección de Sub-Rutas
    todos_bloques = []
    detalle_nodos_global = {}
    
    t_fin_global = 0.0
    dist_total_global = 0.0
    costo_total_global = 0.0
    violaciones_globales = 0
    espera_total_global = 0.0
    violacion_total_global = 0.0
    
    for cluster_id, dict_out in resultados_clusters.items():
        rutas = dict_out.get("rutas", [])
        detalle_camiones = dict_out.get("detalle_camiones", [])
        nodos_dict = dict_out.get("detalle_nodos", {})
        
        detalle_nodos_global.update(nodos_dict)
        dist_total_global += float(dict_out.get("dist_total_m", 0.0))
        costo_total_global += float(dict_out.get("costo_total", 0.0))
        
        # Conteo métricas soft constraints
        for d in nodos_dict.values():
            if d.get("t_espera_min", 0) > 0:
                espera_total_global += d["t_espera_min"]
            if not d.get("cumple_ventana", True):
                violaciones_globales += 1
                violacion_total_global += d["t_violacion_min"]
                
        for k_idx, ruta in enumerate(rutas):
            dc = detalle_camiones[k_idx] if k_idx < len(detalle_camiones) else {}
            bloque = BloqueRuta(cluster_id, ruta, dc, k_idx)
            todos_bloques.append(bloque)
            
            if bloque.t_retorno > t_fin_global:
                t_fin_global = bloque.t_retorno
                
    # 2. Ordenamiento Temporal Puro (Earliest Departure First)
    todos_bloques.sort(key=lambda b: (b.t_salida, b.t_retorno))
    
    # 3. Empaquetamiento en Flota Fija
    flota = [VehiculoGlobal(v_id) for v_id in range(1, max_vehiculos + 1)]
    bloques_huerfanos = []
    
    for b in todos_bloques:
        asignado = False
        for vehiculo in flota:
            if vehiculo.puede_absorber(b):
                vehiculo.asignar(b)
                asignado = True
                break
        
        if not asignado:
            # Si superamos la capacidad global instalada, registramos como huérfano (necesita camión extra / Tercerizado)
            bloques_huerfanos.append(b)
            
    # 4. Generación del Reporte Transversal
    def min_a_hora(minutos: float) -> str:
        h = int(minutos) // 60
        m = int(minutos) % 60
        return f"{h:02d}:{m:02d}"
        
    md = f"# Reporte Gestión Flota Inter-Cluster - {tipo_algoritmo} - {fecha_target}\n\n"
    
    # === KPI GLOBALES ===
    vehiculos_usados = sum(1 for v in flota if v.bloques)
    tasa_utilizacion = (vehiculos_usados / max_vehiculos) * 100 if max_vehiculos > 0 else 0
    t_ini_global = 540.0
    duracion_global_h = int(t_fin_global - t_ini_global) // 60
    duracion_global_m = int(t_fin_global - t_ini_global) % 60
    
    md += f"### KPIs Globales de Utilización\n"
    md += f"| Métrica | Valor |\n| :--- | :--- |\n"
    md += f"| Total Clientes Atendidos | {len(detalle_nodos_global)} |\n"
    md += f"| Total Nodos con Violación (Hard Constr.) | {violaciones_globales} |\n"
    md += f"| Distancia Global Consolidada | {dist_total_global:,.1f} m ({dist_total_global/1000:.2f} km) |\n"
    md += f"| Capacidad Flota Fija | {max_vehiculos} Camiones Homogéneos |\n"
    md += f"| Flota Utilizada | {vehiculos_usados} Camiones ({tasa_utilizacion:.1f}%) |\n"
    md += f"| Rutas Tercerizadas (Exceso Flota) | {len(bloques_huerfanos)} Subrutas |\n\n"
    
    if violaciones_globales > 0:
        md += f"### ⚠️ Reporte Global de Infactibilidad Estricta\n"
        md += f"Existen **{violaciones_globales}** nodos que violan su Cierre de Ventana.\n"
        for nodo_id, d in detalle_nodos_global.items():
            if not d.get("cumple_ventana", True):
                v_min = d.get("t_violacion_min", 0)
                b_v = d.get("b_ventana", 1440)
                t_serv = d.get("t_inicio_servicio", 0)
                md += f"- **{nodo_id}**: Visitado {min_a_hora(t_serv)} | Límite legal {min_a_hora(b_v)} | Infracción: **{v_min:.0f} min**.\n"
        md += "\n"
        
    if bloques_huerfanos:
        md += f"### ❌ Excedente de Flota (Vehículos Tercerizados Necesarios)\n"
        md += f"El pool global de {max_vehiculos} camiones fue insuficiente por solapamiento horario. Las siguientes rutas no cupieron:\n"
        for b in bloques_huerfanos:
            md += f"- Cluster **{b.cluster_id}** | Turno **{b.turno_op}** ({b.subc_k}) | Salida: {min_a_hora(b.t_salida)}\n"
        md += "\n"
        
    md += "---\n\n"
    
    # === DESGLOSE AGRUPADO POR VEHÍCULO FÍSICO ===
    for vehiculo in flota:
        if not vehiculo.bloques:
            continue
            
        md += f"## Vehículo Físico GLOBAL {vehiculo.id_vehiculo}\n\n"
        
        # Subtabla del vehículo
        md += "### Tiempos de Turnos\n"
        md += "| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |\n"
        md += "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
        for b in vehiculo.bloques:
            tv = float(b.dc.get("t_viaje_efectivo_min", 0))
            te = float(b.dc.get("t_espera_total_min", 0))
            ts = float(b.dc.get("t_servicio_total_min", 0))
            dd = float(b.dc.get("dist_total_m", 0)) / 1000.0
            nc = b.dc.get("n_clientes", 0)
            
            md += (f"| {b.cluster_id} | {b.subc_k} | {b.turno_op} | {min_a_hora(b.t_salida)} | {min_a_hora(b.t_retorno)} "
                   f"| {tv:.1f} m | {te:.1f} m | {ts:.1f} m | {dd:.1f} km | {nc} |\n")
        md += "\n"
        
        # Tabla gigante iterada por bloques
        md += f"### Desglose Completo de Paradas\n"
        md += "| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Tiempo de viaje | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |\n"
        md += "| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
        
        global_idx = 0
        for b in vehiculo.bloques:
            # 0 de salida del bloque
            md += f"| {global_idx} | {b.cluster_id} | {b.subc_k} | {depot_id} | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 0.0 m | {min_a_hora(b.t_salida)} | — | {min_a_hora(b.t_salida)} | — | — | — | — | 0.0 | 0.0 | — | 🚗 |\n"
            global_idx += 1
            
            for nodo in b.ruta:
                det = detalle_nodos_global.get(nodo, {})
                df_match = df_filtro.loc[df_filtro['id_nodo'] == nodo]
                dir_real = str(df_match['direccion_ruteo'].values[0]).replace('|', ',') if not df_match.empty else "N/A"
                
                lat = float(df_match['latitud'].values[0]) if not df_match.empty else 0.0
                lng = float(df_match['longitud'].values[0]) if not df_match.empty else 0.0
                coordenadas_str = f"({lat:.4f}, {lng:.4f})"
                
                dist_km = float(det.get("dist_arco_m", 0)) / 1000.0
                t_viaje = float(det.get("t_viaje_min", 0))
                t_real = float(det.get("t_llegada_real", 0))
                a_v = float(det.get("a_ventana", 0))
                b_v = float(det.get("b_ventana", 1440))
                t_serv_ini = float(det.get("t_inicio_servicio", 0))
                t_serv_dur = float(det.get("t_servicio_min", 0))
                
                vol_l = float(det.get("volumen_cm3", 0)) / 1000.0
                peso_kg = float(det.get("peso_g", 0)) / 1000.0
                
                espera = float(det.get("t_espera_min", 0))
                str_espera = f"{espera:.0f} m" if espera > 0 else "0 m"
                
                viola_v = float(det.get("t_violacion_min", 0))
                str_viola = f"{viola_v:.0f} m" if viola_v > 0 else "0 m"
                
                # Las variables de vol y peso como son hard-constraints serán 0 siempre por definición
                viol_vol_str = "0.0"
                viol_peso_str = "0.0"
                
                ok = det.get("cumple_ventana", True)
                estado = "✅" if ok and espera == 0 else ("⏳" if ok else "❌")
                
                md += (f"| {global_idx} | {b.cluster_id} | {b.subc_k} | {nodo} | {dir_real} | {coordenadas_str} | {dist_km:.2f} km | {t_viaje:.1f} m "
                       f"| {min_a_hora(t_real)} | [{min_a_hora(a_v)}, {min_a_hora(b_v)}] | {min_a_hora(t_serv_ini)} "
                       f"| {t_serv_dur:.1f} m | {vol_l:.1f} | {peso_kg:.1f} | {str_espera} | {viol_vol_str} | {viol_peso_str} | {str_viola} | {estado} |\n")
                global_idx += 1
                
            # Fin del bloque (Retorno a la Base)
            dist_ret = float(b.dc.get("dist_retorno_m", 0)) / 1000.0
            t_ret = float(b.dc.get("t_viaje_retorno_min", 0))
            md += f"| {global_idx} | {b.cluster_id} | {b.subc_k} | {depot_id} | Base Depósito | (-33.4489, -70.6693) | {dist_ret:.2f} km | {t_ret:.1f} m | {min_a_hora(b.t_retorno)} | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |\n"
            global_idx += 1
            
        md += "\n---\n"
        
    out_file = os.path.join(out_dir, f'ruta_flotaglobal_{tipo_algoritmo.lower().replace(" ", "")}_{fecha_target}.md')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(md)
        
    print(f"\n[Gestor Flota] Flota mapeada y reporte Markdown guardado en: {out_file}")
    
    if G is not None and rutas_dict_global is not None:
        if mapa_dir is None:
            mapa_dir = os.path.join(os.path.dirname(out_dir), 'mapa_rutas')
            os.makedirs(mapa_dir, exist_ok=True)
            
        mapa_file = os.path.join(mapa_dir, f'mapa_flotaglobal_{tipo_algoritmo.lower().replace(" ", "")}_{fecha_target}.html')
        plot_global_flota_interactive(
            flota=flota,
            df_global=df_filtro,
            rutas_dict_global=rutas_dict_global,
            depot_id=depot_id,
            G=G,
            filepath=mapa_file
        )
    
    return md
