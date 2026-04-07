"""
algoritmo/savings.py

Implementación del Algoritmo de Ahorros de Clarke-Wright adaptado para el TDVRPTW.
Genera una solución constructiva factible que luego servirá como semilla para PyMoo.
"""

import numpy as np
import pandas as pd

def calcular_ahorros(df_cluster, matriz_dist, depot_id):
    """
    Calcula la matriz de ahorros S(i,j) = D(depot, i) + D(depot, j) - D(i, j)
    y devuelve una lista de aristas ordenadas por ahorro descendente.
    """
    clientes = [c for c in matriz_dist.index if c != depot_id]
    ahorros = []
    
    for i in range(len(clientes)):
        for j in range(i + 1, len(clientes)):
            c1 = clientes[i]
            c2 = clientes[j]
            
            d_depot_c1 = matriz_dist.loc[depot_id, c1]
            d_c2_depot = matriz_dist.loc[c2, depot_id]
            d_c1_c2 = matriz_dist.loc[c1, c2]
            
            s_c1_c2 = d_depot_c1 + d_c2_depot - d_c1_c2
            
            # Considerar simetría/asimetría
            d_depot_c2 = matriz_dist.loc[depot_id, c2]
            d_c1_depot = matriz_dist.loc[c1, depot_id]
            d_c2_c1 = matriz_dist.loc[c2, c1]
            
            s_c2_c1 = d_depot_c2 + d_c1_depot - d_c2_c1
            
            ahorros.append({'i': c1, 'j': c2, 'ahorro': s_c1_c2})
            if c1 != c2 and d_c1_c2 != d_c2_c1:
                # Si es asimétrico real agregamos el otro sentido también
                ahorros.append({'i': c2, 'j': c1, 'ahorro': s_c2_c1})
                
    ahorros.sort(key=lambda x: x['ahorro'], reverse=True)
    return ahorros

def clarke_wright_savings(df_cluster, matriz_dist, depot_id, cap_vol_cm3, cap_peso_g, d_max_min=300.0, speed_kmh=25.0):
    """
    Heurística constructiva de Ahorros.
    Dado que las ventanas de tiempo son complejas, validamos estáticamente la capacidad 
    y hacemos una estimación simple de tiempo de ruta para `d_max_min`.
    La evaluación final fina la hará PyMoo.
    """
    clientes = [c for c in matriz_dist.index if c != depot_id]
    if not clientes:
        return []
    if len(clientes) == 1:
        return clientes
        
    ahorros = calcular_ahorros(df_cluster, matriz_dist, depot_id)
    
    # Extraer demandas a diccionarios
    vol_dict = {}
    peso_dict = {}
    df_idx = df_cluster.set_index('id_nodo')
    for cid in clientes:
        if cid in df_idx.index:
            row = df_idx.loc[cid]
            if isinstance(row, pd.DataFrame): row = row.iloc[0]
            v_col = 'volumen_pedido_cm3' if 'volumen_pedido_cm3' in df_idx.columns else 'volumen_pedido'
            p_col = 'peso_pedido_g' if 'peso_pedido_g' in df_idx.columns else 'peso_pedido'
            vol_dict[cid] = float(row.get(v_col, 0.0))
            peso_dict[cid] = float(row.get(p_col, 0.0))
        else:
            vol_dict[cid] = 0.0
            peso_dict[cid] = 0.0
            
    # Inicializar rutas discretas: un cliente por ruta
    # route_of[cliente] = id_ruta
    rutas = {c: [c] for c in clientes}
    route_of = {c: c for c in clientes}
    
    # Calcular demandas por ruta
    ruta_vol = {c: vol_dict[c] for c in clientes}
    ruta_peso = {c: peso_dict[c] for c in clientes}
    
    # Función de estimación de tiempo (ida + atención + retorno)
    # velocidad aprox = speed_kmh km/h => speed_kmh*1000/60 m/min
    m_per_min = speed_kmh * 1000.0 / 60.0
    def est_tiempo(r_list):
        t = 0.0
        n_prev = depot_id
        for n in r_list:
            t += float(matriz_dist.loc[n_prev, n]) / m_per_min
            t += 5.0 # aten_fijo
            n_prev = n
        t += float(matriz_dist.loc[n_prev, depot_id]) / m_per_min
        return t
        
    for ah in ahorros:
        c1, c2 = ah['i'], ah['j']
        r1, r2 = route_of[c1], route_of[c2]
        
        if r1 == r2:
            continue # Ya en la misma ruta
            
        # Verificar que c1 sea el final de r1 y c2 sea el inicio de r2
        if rutas[r1][-1] != c1 or rutas[r2][0] != c2:
            continue
            
        # Evaluar viabilidad de unificación
        new_vol = ruta_vol[r1] + ruta_vol[r2]
        new_peso = ruta_peso[r1] + ruta_peso[r2]
        
        if new_vol > cap_vol_cm3 or new_peso > cap_peso_g:
            continue 
            
        new_route_list = rutas[r1] + rutas[r2]
        if est_tiempo(new_route_list) > d_max_min:
            continue
            
        # Unificar! Mergear r2 dentro de r1
        rutas[r1] = new_route_list
        ruta_vol[r1] = new_vol
        ruta_peso[r1] = new_peso
        
        del rutas[r2]
        del ruta_vol[r2]
        del ruta_peso[r2]
        
        for n in new_route_list:
            route_of[n] = r1

    # Construir permutación final concatenando todas las rutas resultantes
    permutacion_final = []
    for r_id, r_list in rutas.items():
        permutacion_final.extend(r_list)
        
    # Validar que no falten ni sobren clientes
    assert set(permutacion_final) == set(clientes)
    
    return permutacion_final

