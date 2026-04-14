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

        # 2. Regla de unicidad de jornada (No repetir K11, K12, etc. en el mismo vehículo)
        for b_asignado in self.bloques:
            if b_asignado.subc_k == bloque.subc_k:
                return False
                
        # 3. Regla física temporal de superposición
        if not self.bloques:
            return True
        ultimo = self.bloques[-1]
        # RESTRICCIÓN 21: Garantizar 120 min de descanso entre jornadas
        return bloque.t_salida >= ultimo.t_retorno + 120.0
        
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
    mapa_dir=None,
    depot_coords=None,
    tiempo_computo_min=0.0
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
                
    # 2. Ordenamiento FFD (First Fit Decreasing) por duración de la ruta (Mayor a Menor)
    todos_bloques.sort(key=lambda b: (b.t_retorno - b.t_salida), reverse=True)
    
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
            
    # 4. Construcción de DataFrames para exportación CSV
    def min_a_hora(minutos: float) -> str:
        h = int(minutos) // 60
        m = int(minutos) % 60
        return f"{h:02d}:{m:02d}"
    
    # === DataFrame 1: Resumen de Camiones (Tiempos de Turnos) ===
    filas_resumen = []
    for vehiculo in flota:
        if not vehiculo.bloques:
            continue
        for b in vehiculo.bloques:
            tv = float(b.dc.get("t_viaje_efectivo_min", 0))
            te = float(b.dc.get("t_espera_total_min", 0))
            ts = float(b.dc.get("t_servicio_total_min", 0))
            dd = float(b.dc.get("dist_total_m", 0)) / 1000.0
            nc = b.dc.get("n_clientes", 0)
            
            filas_resumen.append({
                "Vehiculo_Fisico": vehiculo.id_vehiculo,
                "Cluster": b.cluster_id,
                "Clase_K": b.subc_k,
                "Turno": b.turno_op,
                "Salida_CD": min_a_hora(b.t_salida),
                "Retorno_CD": min_a_hora(b.t_retorno),
                "Viaje_Efectivo_min": round(tv, 1),
                "Espera_min": round(te, 1),
                "Servicio_min": round(ts, 1),
                "Distancia_km": round(dd, 1),
                "Clientes": nc
            })
    
    df_resumen = pd.DataFrame(filas_resumen)
    
    # === DataFrame 2: Detalle Completo de Paradas ===
    filas_detalle = []
    for vehiculo in flota:
        if not vehiculo.bloques:
            continue
        
        global_idx = 0
        for b in vehiculo.bloques:
            d_coords_str = f"({depot_coords[0]:.4f}, {depot_coords[1]:.4f})" if depot_coords else "(-33.4489, -70.6693)"
            
            # Fila de salida del depósito
            filas_detalle.append({
                "Vehiculo_Fisico": vehiculo.id_vehiculo,
                "Secuencia": global_idx,
                "Cluster_Visitado": b.cluster_id,
                "Clase_K": b.subc_k,
                "Nodo": depot_id,
                "Direccion": "Base Depósito",
                "Coordenadas": d_coords_str,
                "Distancia_Recorrida_km": 0.0,
                "Tiempo_Viaje_min": 0.0,
                "Hora_Llegada": min_a_hora(b.t_salida),
                "Ventana": "—",
                "Cierre_Relajado": "—",
                "Inicio_Servicio": min_a_hora(b.t_salida),
                "Tiempo_Servicio_min": "—",
                "Vol_L": "—",
                "Peso_kg": "—",
                "Tiempo_Espera_min": "—",
                "Violacion_Vol": 0.0,
                "Violacion_Peso": 0.0,
                "Violacion_Ventana_min": "—",
                "Estado": "🚗"
            })
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
                b_v_rel = float(det.get("b_ventana_relaxed", b_v + 30.0))
                t_serv_ini = float(det.get("t_inicio_servicio", 0))
                t_serv_dur = float(det.get("t_servicio_min", 0))
                
                vol_l = float(det.get("volumen_cm3", 0)) / 1000.0
                peso_kg = float(det.get("peso_g", 0)) / 1000.0
                
                espera = float(det.get("t_espera_min", 0))
                viola_v = float(det.get("t_violacion_min", 0))
                
                ok = det.get("cumple_ventana", True)
                estado = "✅" if ok and espera == 0 else ("⏳" if ok else "❌")
                
                filas_detalle.append({
                    "Vehiculo_Fisico": vehiculo.id_vehiculo,
                    "Secuencia": global_idx,
                    "Cluster_Visitado": b.cluster_id,
                    "Clase_K": b.subc_k,
                    "Nodo": nodo,
                    "Direccion": dir_real,
                    "Coordenadas": coordenadas_str,
                    "Distancia_Recorrida_km": round(dist_km, 2),
                    "Tiempo_Viaje_min": round(t_viaje, 1),
                    "Hora_Llegada": min_a_hora(t_real),
                    "Ventana": f"[{min_a_hora(a_v)}, {min_a_hora(b_v)}]",
                    "Cierre_Relajado": min_a_hora(b_v_rel),
                    "Inicio_Servicio": min_a_hora(t_serv_ini),
                    "Tiempo_Servicio_min": round(t_serv_dur, 1),
                    "Vol_L": round(vol_l, 1),
                    "Peso_kg": round(peso_kg, 1),
                    "Tiempo_Espera_min": round(espera, 1),
                    "Violacion_Vol": 0.0,
                    "Violacion_Peso": 0.0,
                    "Violacion_Ventana_min": round(viola_v, 1),
                    "Estado": estado
                })
                global_idx += 1
            
            # Fila de retorno al depósito
            dist_ret = float(b.dc.get("dist_retorno_m", 0)) / 1000.0
            t_ret = float(b.dc.get("t_viaje_retorno_min", 0))
            d_coords_str = f"({depot_coords[0]:.4f}, {depot_coords[1]:.4f})" if depot_coords else "(-33.4489, -70.6693)"
            
            filas_detalle.append({
                "Vehiculo_Fisico": vehiculo.id_vehiculo,
                "Secuencia": global_idx,
                "Cluster_Visitado": b.cluster_id,
                "Clase_K": b.subc_k,
                "Nodo": depot_id,
                "Direccion": "Base Depósito",
                "Coordenadas": d_coords_str,
                "Distancia_Recorrida_km": round(dist_ret, 2),
                "Tiempo_Viaje_min": round(t_ret, 1),
                "Hora_Llegada": min_a_hora(b.t_retorno),
                "Ventana": "—",
                "Cierre_Relajado": "—",
                "Inicio_Servicio": "—",
                "Tiempo_Servicio_min": "—",
                "Vol_L": "—",
                "Peso_kg": "—",
                "Tiempo_Espera_min": "—",
                "Violacion_Vol": 0.0,
                "Violacion_Peso": 0.0,
                "Violacion_Ventana_min": "—",
                "Estado": "🏠"
            })
            global_idx += 1
    
    df_detalle = pd.DataFrame(filas_detalle)
    
    # === Exportación a 2 CSVs ===
    csv_resumen = os.path.join(out_dir, f'resumen_camiones_{tipo_algoritmo.lower().replace(" ", "")}_{fecha_target}.csv')
    csv_detalle = os.path.join(out_dir, f'detalle_paradas_{tipo_algoritmo.lower().replace(" ", "")}_{fecha_target}.csv')
    
    df_resumen.to_csv(csv_resumen, index=False, encoding='utf-8-sig')
    df_detalle.to_csv(csv_detalle, index=False, encoding='utf-8-sig')
    
    print(f"\n[Gestor Flota] Resumen de camiones guardado en: {csv_resumen}")
    print(f"[Gestor Flota] Detalle de paradas guardado en: {csv_detalle}")
    
    # === CSV 3: KPIs Globales ===
    vehiculos_usados = sum(1 for v in flota if v.bloques)
    tasa_utilizacion_flota = (vehiculos_usados / max_vehiculos) * 100 if max_vehiculos > 0 else 0
    total_clientes = len(detalle_nodos_global)
    
    # Entregas a tiempo (cumple ventana)
    entregas_a_tiempo = sum(1 for d in detalle_nodos_global.values() if d.get("cumple_ventana", True))
    pct_entregas_a_tiempo = (entregas_a_tiempo / total_clientes * 100) if total_clientes > 0 else 0
    
    # Tardanza promedio (solo nodos con violación)
    tardanzas = [d.get("t_violacion_min", 0) for d in detalle_nodos_global.values() if d.get("t_violacion_min", 0) > 0]
    tardanza_promedio = sum(tardanzas) / len(tardanzas) if tardanzas else 0.0
    
    # Tiempo total en ruta (horas) — suma de tiempos efectivos de todos los bloques
    tiempo_total_ruta_min = 0.0
    viaje_efectivo_total = 0.0
    servicio_total = 0.0
    vol_total_cargado = 0.0
    peso_total_cargado = 0.0
    
    for vehiculo in flota:
        for b in vehiculo.bloques:
            t_sal = b.t_salida
            t_ret = b.t_retorno
            tiempo_total_ruta_min += (t_ret - t_sal)
            viaje_efectivo_total += float(b.dc.get("t_viaje_efectivo_min", 0))
            servicio_total += float(b.dc.get("t_servicio_total_min", 0))
    
    tiempo_total_ruta_h = tiempo_total_ruta_min / 60.0
    
    # Volumen y peso total cargado (de todos los nodos visitados)
    for d in detalle_nodos_global.values():
        vol_total_cargado += float(d.get("volumen_cm3", 0))
        peso_total_cargado += float(d.get("peso_g", 0))
    
    # Capacidades totales disponibles (por cada bloque/turno usado)
    cap_vol_por_turno = 3_750_000  # cm3
    cap_peso_por_turno = 803_333.33  # g
    # Cambiamos sum(len(v.bloques) for v in flota) por len(todos_bloques) para incluir turnos adicionales/tercerizados
    total_turnos_usados = len(todos_bloques)
    cap_vol_total = cap_vol_por_turno * total_turnos_usados if total_turnos_usados > 0 else 1
    cap_peso_total = cap_peso_por_turno * total_turnos_usados if total_turnos_usados > 0 else 1
    
    pct_util_vol = (vol_total_cargado / cap_vol_total) * 100
    pct_util_peso = (peso_total_cargado / cap_peso_total) * 100
    pct_util_promedio = (pct_util_vol + pct_util_peso) / 2.0
    
    # Desviación media de carga (kg)
    cargas_por_turno_kg = []
    for vehiculo in flota:
        for b in vehiculo.bloques:
            carga_turno = sum(float(detalle_nodos_global.get(nodo, {}).get("peso_g", 0)) for nodo in b.ruta) / 1000.0
            cargas_por_turno_kg.append(carga_turno)
    desviacion_media_carga_kg = float(pd.Series(cargas_por_turno_kg).std()) if cargas_por_turno_kg else 0.0
    
    # Tasa de desocupación
    tasa_desocupacion = (espera_total_global / (viaje_efectivo_total + servicio_total)) * 100 if (viaje_efectivo_total + servicio_total) > 0 else 0
    
    # Emisiones CO2 (Factor: 2.68 kg CO2/litro diesel, rendimiento 6.5 km/litro para camión urbano)
    rendimiento_km_por_litro = 6.5
    factor_co2_kg_por_litro = 2.68 if rendimiento_km_por_litro > 0 else 0
    dist_total_km = dist_total_global / 1000.0
    litros_consumidos = dist_total_km / rendimiento_km_por_litro
    co2_total_kg = litros_consumidos * factor_co2_kg_por_litro
    co2_por_pedido_kg = co2_total_kg / total_clientes if total_clientes > 0 else 0
    
    # Pedidos no atendidos (backlog) — outliers del clustering que no entraron
    total_pedidos_input = len(df_filtro[df_filtro['id_nodo'] != depot_id]) if 'id_nodo' in df_filtro.columns else len(df_filtro)
    pedidos_no_atendidos = total_pedidos_input - total_clientes
    pct_backlog = (pedidos_no_atendidos / total_pedidos_input * 100) if total_pedidos_input > 0 else 0
    
    # Función objetivo compuesta
    alpha_espera = 50000.0  # Mismo multiplicador usado en el algoritmo genético
    costo_fijo_camion = 100000.0  # Opex por activación de camión físico
    
    fo_costo_ruta = costo_total_global
    costo_flota = vehiculos_usados * costo_fijo_camion
    costo_espera_penalizada = espera_total_global * alpha_espera
    
    fo_total = fo_costo_ruta + costo_flota + costo_espera_penalizada
    
    kpis = {
        "KPI": [
            "Función Objetivo Total ($)",
            "Costos de Ruta por Transporte ($)",
            "Costos Fijos por Uso de Flota ($)",
            "Valor de Penalización por Espera ($)",
            "Tiempo de Espera Total (min)",
            "Distancia Total Recorrida (km)",
            "Distancia Relativa (km/pedido)",
            "Vehículos Utilizados",
            "Vehículos en Desuso",
            "Capacidad Flota Fija",
            "Tiempo Total en Ruta (horas)",
            "% Entregas a Tiempo",
            "Tardanza Promedio (min)",
            "% Pedidos No Atendidos (Backlog)",
            "Pedidos No Atendidos (qty)",
            "% Utilización Promedio Capacidad Vehículos",
            "% Utilización Volumen",
            "% Utilización Peso",
            "Desviación Media de Carga (kg)",
            "Tasa de Desocupación (%)",
            "Espera Total Acumulada (min)",
            "Emisiones CO2 Totales (kg)",
            "Emisiones CO2 por Pedido (kg)",
            "Litros Diesel Estimados",
            "Tiempo de Cómputo (min)"

        ],
        "Valor": [
            round(fo_total, 2),
            round(fo_costo_ruta, 2),
            round(costo_flota, 2),
            round(costo_espera_penalizada, 2),
            round(espera_total_global, 1),
            round(dist_total_km, 2),
            round(dist_total_km / total_clientes, 2) if total_clientes > 0 else 0,
            vehiculos_usados,
            max_vehiculos - vehiculos_usados,
            max_vehiculos,
            round(tiempo_total_ruta_h, 2),
            round(pct_entregas_a_tiempo, 1),
            round(tardanza_promedio, 1),
            round(pct_backlog, 1),
            pedidos_no_atendidos,
            round(pct_util_promedio, 1),
            round(pct_util_vol, 1),
            round(pct_util_peso, 1),
            round(desviacion_media_carga_kg, 2),
            round(tasa_desocupacion, 1),
            round(espera_total_global, 1),
            round(co2_total_kg, 2),
            round(co2_por_pedido_kg, 3),
            round(litros_consumidos, 2),
            round(tiempo_computo_min, 2)
        ]
    }
    
    df_kpis = pd.DataFrame(kpis)
    csv_kpis = os.path.join(out_dir, f'kpis_{tipo_algoritmo.lower().replace(" ", "")}_{fecha_target}.csv')
    df_kpis.to_csv(csv_kpis, index=False, encoding='utf-8-sig')
    print(f"[Gestor Flota] KPIs guardados en: {csv_kpis}")
    
    # === CSV 4: Clientes Atendidos ===
    # Construir mapeo inverso nodo → cluster desde los resultados de optimización
    nodo_a_cluster = {}
    for cluster_id, dict_out in resultados_clusters.items():
        for ruta in dict_out.get("rutas", []):
            for nodo in ruta:
                nodo_a_cluster[nodo] = cluster_id
    
    nodos_atendidos = set(detalle_nodos_global.keys())
    filas_clientes = []
    
    for _, row in df_filtro.iterrows():
        id_nodo = row.get('id_nodo', '')
        if id_nodo == depot_id:
            continue
        
        lat = float(row.get('latitud', 0.0))
        lng = float(row.get('longitud', 0.0))
        
        # Cluster desde el mapeo inverso de resultados
        cluster_asignado = nodo_a_cluster.get(id_nodo, 'Sin Cluster (Outlier)')
        
        atendido = "Sí" if id_nodo in nodos_atendidos else "No"
        
        filas_clientes.append({
            "id_nodo": id_nodo,
            "Cluster": cluster_asignado,
            "Latitud": lat,
            "Longitud": lng,
            "Atendido": atendido,
            "Fecha": fecha_target
        })
    
    df_clientes = pd.DataFrame(filas_clientes)
    csv_clientes = os.path.join(out_dir, f'clientes_atendidos_{tipo_algoritmo.lower().replace(" ", "")}_{fecha_target}.csv')
    df_clientes.to_csv(csv_clientes, index=False, encoding='utf-8-sig')
    print(f"[Gestor Flota] Clientes atendidos guardado en: {csv_clientes}")
    
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
            filepath=mapa_file,
            depot_coords=depot_coords
        )
    
    return df_resumen, df_detalle
