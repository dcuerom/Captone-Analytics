"""
modelo/pymoo_problem.py

Alojador del Evaluador TDVRPTW basado en la estructura de PyMoo (ElementwiseProblem).
- Utiliza la función vectorial tau_ij_vec para calcular tiempos asimétricos.
- Las restricciones (Volumen, Peso, Ventana de Tiempo) son "Hard Constraints" alimentadas en out["G"].
- out["F"] maneja puramente el costo optimizado (sumatoria de distancia).
"""

import numpy as np
import pandas as pd
from pymoo.core.problem import ElementwiseProblem

import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from modelo.funciones.tiempos_viaje import tau_ij_vec

class TDVRPTWProblem(ElementwiseProblem):
    def __init__(self, df_cluster, matriz_dist_m, depot_id, 
                 t_inicio=540.0, cap_vol_cm3=10_000_000, cap_peso_g=5_000_000, 
                 dia_semana=0, factor_s=1.2, d_max_min=240.0, alpha_espera=1.0, holgura_ventana=30.0):
        
        self.df_cluster = df_cluster.copy()
        
        # Guardaremos el array de IDs en orden, ignorando al depot_id
        self.clientes_ids = [c for c in matriz_dist_m.index if c != depot_id]
        n_clientes = len(self.clientes_ids)
        
        # Mapeados rápidos de demandas para no usar pandas internamente
        self.vol_dict = {}
        self.peso_dict = {}
        self.a_dict = {}
        self.b_dict = {}
        
        df_idx = self.df_cluster.set_index('id_nodo')
        for cid in self.clientes_ids:
            if cid in df_idx.index:
                # Soporte para ambas convenciones de nombres de columnas
                vol_col = 'volumen_pedido_cm3' if 'volumen_pedido_cm3' in df_idx.columns else 'volumen_pedido'
                peso_col = 'peso_pedido_g' if 'peso_pedido_g' in df_idx.columns else 'peso_pedido'
                
                # Manejar duplicados silenciosos si existiesen (tomando el primer registro)
                row = df_idx.loc[cid]
                if isinstance(row, pd.DataFrame):
                    row = row.iloc[0]
                    
                self.vol_dict[cid] = float(row.get(vol_col, 0.0))
                self.peso_dict[cid] = float(row.get(peso_col, 0.0))
                self.a_dict[cid] = float(row.get('a_ventana', 0.0))
                self.b_dict[cid] = float(row.get('b_ventana', 1440.0))
            else:
                self.vol_dict[cid], self.peso_dict[cid], self.a_dict[cid], self.b_dict[cid] = 0.0, 0.0, 0.0, 1440.0
                
        self.matriz_dist = matriz_dist_m
        self.depot_id = depot_id
        
        self.t_inicio = t_inicio
        self.cap_vol_cm3 = cap_vol_cm3
        self.cap_peso_g = cap_peso_g
        self.dia_semana = dia_semana
        self.factor_s = factor_s
        self.aten_fijo = 5.0 # Minutos de atención
        self.d_max_min = d_max_min # Límite de duración total del turno (Restricción 14)
        self.alpha_espera = alpha_espera # Peso de penalización por tiempo de espera
        self.holgura_ventana = holgura_ventana # Tolerancia para violaciones de ventana de tiempo
        
        # ElementwiseProblem configurado:
        # n_var = permutación de índices de [0... n_clientes-1]
        # n_obj = 1 (Minimizar F: distancia total * S + penalización espera)
        # n_ieq_constr = 1 (Sumatoria de todas las roturas hard en tiempo y capacidad)
        
        super().__init__(n_var=n_clientes, 
                         n_obj=1, 
                         n_ieq_constr=1, 
                         xl=0, 
                         xu=n_clientes - 1, 
                         vtype=int)

        # Plantillas de ventanas de salida (K11, K12, K21, K22)
        # El modelo permite salir en cualquier momento dentro de estos rangos.
        self.ventanas_salida_turnos = [
            [[540.0, 720.0], [900.0, 1080.0]],   # Plantilla K1: Mañana [09:00-12:00], Tarde [15:00-18:00]
            [[660.0, 840.0], [1020.0, 1200.0]]   # Plantilla K2: Mañana [11:00-14:00], Tarde [17:00-20:00]
        ]
        self.costo_fijo_camion = 100000 # Castigo por usar un nuevo camión físico
        
    def _evaluate(self, x, out, *args, **kwargs):
        """
        x: Cromosoma Permutación de enteros (0..n-1), que mapean a self.clientes_ids.
        Al ser un ElementwiseProblem, x es arr de 1D. Utilizaremos np.array en tau_ij_vec
        para cumplir la regla requerida de vectorización, evaluando unitariamente.
        """
        # Extraer orden propuesto por X
        ruta_candidata = [self.clientes_ids[i] for i in x]
        
        dist_total_m = 0.0
        restricciones_fail = 0.0 # Acumulador de penalizaciones g(x) <= 0
        espera_total = 0.0 # Acumulador de espera total para penalización en F
        
        vol_actual = 0.0
        peso_actual = 0.0
        rutas_camiones = []
        ruta_act = []
        tiempos_llegada = {}
        
        num_camiones_fisicos = 1
        plantilla_idx = 0
        ventanas_actual = self.ventanas_salida_turnos[plantilla_idx]
        turno_idx = 0
        
        # El camión tiene libertad de salir en cualquier momento de la ventana.
        # Por defecto, iniciamos en el tiempo más temprano (Earliest Departure).
        cam_t_salida = ventanas_actual[turno_idx][0] 
        t_actual = cam_t_salida
        nodo_previo = self.depot_id
        detalle_nodos = {}
        detalle_camiones = []  # Métricas por camión
        
        # Contadores del camión actual
        cam_t_viaje = 0.0
        cam_t_espera = 0.0
        cam_t_servicio = 0.0
        cam_dist = 0.0
        
        # --- LÓGICA JIT (Just-In-Time) PARA LA SALIDA INICIAL ---
        # Antes de empezar, ajustamos la salida del primer camión si es posible
        if ruta_candidata:
            c1 = ruta_candidata[0]
            dist_c1 = float(self.matriz_dist.loc[self.depot_id, c1])
            # Estimación de viaje con salida más temprana
            t_v_c1_est = float(tau_ij_vec(np.array([dist_c1]), np.array([cam_t_salida]), self.dia_semana)[0])
            t_lleg_est = cam_t_salida + t_v_c1_est
            if t_lleg_est < self.a_dict[c1]:
                # Hay espera. Retrasamos la salida del depósito.
                espera_evitable = self.a_dict[c1] - t_lleg_est
                # No podemos salir después del fin de la ventana de salida del CD
                cam_t_salida = min(cam_t_salida + espera_evitable, ventanas_actual[turno_idx][1])
                t_actual = cam_t_salida

        for cliente_id in ruta_candidata:
            vol_p = self.vol_dict[cliente_id]
            peso_p = self.peso_dict[cliente_id]
            
            # 1. Proyección de la ruta para prever Restricción 14 (Conducción d_max) incluyendo retorno
            dist_arco_tent = float(self.matriz_dist.loc[nodo_previo, cliente_id])
            t_viaj_tent = float(tau_ij_vec(np.array([dist_arco_tent]), np.array([t_actual]), self.dia_semana)[0])
            t_ini_tent = max(t_actual + t_viaj_tent, self.a_dict[cliente_id])
            t_fin_tent = t_ini_tent + self.aten_fijo
            
            # Limite superior relajado (b_p + holgura_ventana)
            b_p_tent = self.b_dict[cliente_id]
            b_p_relaxed_tent = b_p_tent + self.holgura_ventana
            
            dist_retorno_tent = float(self.matriz_dist.loc[cliente_id, self.depot_id])
            t_viaj_ret_tent = float(tau_ij_vec(np.array([dist_retorno_tent]), np.array([t_fin_tent]), self.dia_semana)[0])
            
            # Cálculo modificado: Duración de todo el viaje partiendo desde la base hasta retornar a ella
            t_retorno_estimado = t_fin_tent + t_viaj_ret_tent
            duracion_turno_estimada = t_retorno_estimado - cam_t_salida
            
            # SPLIT CONDICIONAL (Activa regreso al depósito si se violan capacidades o la duración del turno supera el bloque d_max)
            if (vol_actual + vol_p > self.cap_vol_cm3) or (peso_actual + peso_p > self.cap_peso_g) or (duracion_turno_estimada > self.d_max_min):
                # Regreso del camión actual al depósito
                dist_reg = float(self.matriz_dist.loc[nodo_previo, self.depot_id])
                d_ret = np.array([dist_reg])
                t_ret = np.array([t_actual])
                t_viaje_reg = float(tau_ij_vec(distancia_m=d_ret, t=t_ret, dia_semana=self.dia_semana)[0])
                
                cam_t_viaje += t_viaje_reg
                cam_dist += dist_reg
                dist_total_m += dist_reg
                
                # Solo registrar el turno si tuvo al menos 1 cliente
                if ruta_act:
                    detalle_camiones.append({
                        "t_viaje_efectivo_min": cam_t_viaje,
                        "t_espera_total_min": cam_t_espera,
                        "t_servicio_total_min": cam_t_servicio,
                        "dist_total_m": cam_dist,
                        "t_salida_deposito": cam_t_salida,
                        "t_retorno_deposito": t_actual + t_viaje_reg,
                        "n_clientes": len(ruta_act),
                        "dist_retorno_m": dist_reg,
                        "t_viaje_retorno_min": t_viaje_reg,
                        "id_camion_fisico": num_camiones_fisicos,
                        "turno_operacion": "Mañana" if turno_idx == 0 else "Tarde",
                        "subconjunto_k": f"K{plantilla_idx+1}{turno_idx+1}"
                    })
                    rutas_camiones.append(ruta_act)
                
                # LÓGICA MULTI-VIAJE (K11->K12 o K21->K22)
                t_retorno_anterior = t_actual + t_viaje_reg
                turno_idx += 1
                
                # Intentamos re-usar el camión si tiene tiempo de descanso (120 min)
                puebe_reuse = False
                if turno_idx < len(ventanas_actual):
                    t_min_salida_descanso = t_retorno_anterior + 120.0 # 2 horas de break
                    if t_min_salida_descanso <= ventanas_actual[turno_idx][1]:
                        puebe_reuse = True
                        cam_t_salida = max(ventanas_actual[turno_idx][0], t_min_salida_descanso)
                
                if puebe_reuse:
                    # El MISMO camión físico toma el siguiente turno tras su descanso
                    # Aplicamos JIT para el nuevo turno si es necesario
                    # (cliente_id es el que no cupo en el turno anterior)
                    dist_next = float(self.matriz_dist.loc[self.depot_id, cliente_id])
                    t_v_next = float(tau_ij_vec(np.array([dist_next]), np.array([cam_t_salida]), self.dia_semana)[0])
                    if cam_t_salida + t_v_next < self.a_dict[cliente_id]:
                        espera_extra = self.a_dict[cliente_id] - (cam_t_salida + t_v_next)
                        cam_t_salida = min(cam_t_salida + espera_extra, ventanas_actual[turno_idx][1])
                else:
                    # El camión anterior no puede o no tiene más turnos. Nuevo camión físico.
                    num_camiones_fisicos += 1
                    plantilla_idx = (plantilla_idx + 1) % len(self.ventanas_salida_turnos)
                    ventanas_actual = self.ventanas_salida_turnos[plantilla_idx]
                    turno_idx = 0
                    cam_t_salida = ventanas_actual[turno_idx][0]
                    
                    # Aplicamos JIT para el nuevo camión físico
                    dist_next = float(self.matriz_dist.loc[self.depot_id, cliente_id])
                    t_v_next = float(tau_ij_vec(np.array([dist_next]), np.array([cam_t_salida]), self.dia_semana)[0])
                    if cam_t_salida + t_v_next < self.a_dict[cliente_id]:
                        espera_extra = self.a_dict[cliente_id] - (cam_t_salida + t_v_next)
                        cam_t_salida = min(cam_t_salida + espera_extra, ventanas_actual[turno_idx][1])

                # Reseteo camión
                vol_actual = 0.0
                peso_actual = 0.0
                t_actual = cam_t_salida
                nodo_previo = self.depot_id
                ruta_act = []
                cam_t_viaje = 0.0
                cam_t_espera = 0.0
                cam_t_servicio = 0.0
                cam_dist = 0.0
        
            # Tránsito hacia cliente
            dist_arco = float(self.matriz_dist.loc[nodo_previo, cliente_id])
            
            d_arr = np.array([dist_arco])
            t_arr = np.array([t_actual])
            
            t_viaje_arr = tau_ij_vec(distancia_m=d_arr, t=t_arr, dia_semana=self.dia_semana)
            t_viaje = float(t_viaje_arr[0])
            
            t_llegada_real = t_actual + t_viaje
            
            a_p = self.a_dict[cliente_id]
            b_p = self.b_dict[cliente_id]
            
            t_espera = 0.0
            t_violacion = 0.0
            
            # NUEVO: Lógica de Ventanas Suaves (15 min suavizamiento en ambos extremos)
            # Solo aplicable a clientes (a_p y b_p vienen de a_dict/b_dict que solo tienen clientes)
            suavizamiento = 15.0
            a_p_eff = a_p - suavizamiento
            b_p_eff = b_p + suavizamiento
            
            t_espera = 0.0
            t_violacion = 0.0
            
            if t_llegada_real < a_p_eff:
                t_espera = a_p_eff - t_llegada_real
                t_inicio_servicio = a_p_eff
            else:
                t_inicio_servicio = t_llegada_real
                
            if t_inicio_servicio > b_p_eff:
                t_violacion = t_inicio_servicio - b_p_eff
                restricciones_fail += t_violacion
            
            cam_t_viaje += t_viaje
            cam_t_espera += t_espera
            cam_t_servicio += self.aten_fijo
            cam_dist += dist_arco
            espera_total += t_espera  # Acumular espera global para penalización en F
            
            detalle_nodos[cliente_id] = {
                "t_salida_anterior": t_actual,
                "dist_arco_m": dist_arco,
                "t_viaje_min": t_viaje,
                "t_llegada_real": t_llegada_real,
                "a_ventana": a_p,
                "b_ventana": b_p,
                "a_ventana_relaxed": a_p - suavizamiento,
                "b_ventana_relaxed": b_p + suavizamiento,
                "t_espera_min": t_espera,
                "t_inicio_servicio": t_inicio_servicio,
                "t_servicio_min": self.aten_fijo,
                "volumen_cm3": vol_p,
                "peso_g": peso_p,
                "t_violacion_min": t_violacion,
                "cumple_ventana": t_violacion <= 0.0
            }
                
            t_actual = t_inicio_servicio + self.aten_fijo
            dist_total_m += dist_arco
            vol_actual += vol_p
            peso_actual += peso_p
            nodo_previo = cliente_id
            
            ruta_act.append(cliente_id)
            tiempos_llegada[cliente_id] = t_inicio_servicio
            
        # Regreso del último camión
        t_retorno = t_actual  # t_actual ya incluye el tiempo de atención del último cliente
        if ruta_act:
            dist_reg_final = float(self.matriz_dist.loc[nodo_previo, self.depot_id])
            d_arr_ret = np.array([dist_reg_final])
            t_arr_ret = np.array([t_actual])
            t_viaje_ret = float(tau_ij_vec(distancia_m=d_arr_ret, t=t_arr_ret, dia_semana=self.dia_semana)[0])
            t_retorno = t_actual + t_viaje_ret
            
            cam_t_viaje += t_viaje_ret
            cam_dist += dist_reg_final
            dist_total_m += dist_reg_final
            
            detalle_camiones.append({
                "t_viaje_efectivo_min": cam_t_viaje,
                "t_espera_total_min": cam_t_espera,
                "t_servicio_total_min": cam_t_servicio,
                "dist_total_m": cam_dist,
                "t_salida_deposito": cam_t_salida,
                "t_retorno_deposito": t_retorno,
                "n_clientes": len(ruta_act),
                "dist_retorno_m": dist_reg_final,
                "t_viaje_retorno_min": t_viaje_ret,
                "id_camion_fisico": num_camiones_fisicos,
                "turno_operacion": "Mañana" if turno_idx == 0 else "Tarde",
                "subconjunto_k": f"K{plantilla_idx+1}{turno_idx+1}"
            })
            
            rutas_camiones.append(ruta_act)
            
        # ASIGNACIÓN DE SALIDAS (PyMoo standard)
        # Solo F y G pueden ir en out — PyMoo apila TODAS las claves del dict
        # en un array numpy para la población completa, y las claves con shapes
        # variables (listas de rutas, dicts) provocan errores de forma inhomogénea.
        costo_vehiculos = num_camiones_fisicos * self.costo_fijo_camion
        penalizacion_espera = self.alpha_espera * espera_total
        out["F"] = np.array([(dist_total_m * self.factor_s) + costo_vehiculos + penalizacion_espera])
        out["G"] = np.array([restricciones_fail])
        
        # Datos extra se guardan en instancia para consulta posterior
        self.last_eval_details = {
            "rutas": rutas_camiones,
            "tiempos_llegada": tiempos_llegada,
            "detalle_nodos": detalle_nodos,
            "detalle_camiones": detalle_camiones,
            "dist_total_m": dist_total_m,
            "costo_total": dist_total_m * self.factor_s,
            "t_inicio": self.t_inicio,
            "t_fin": t_retorno,
            "duracion_min": t_retorno - self.t_inicio,
            "restricciones_fail": restricciones_fail
        }
    
    def evaluar_completo(self, x):
        """Evalúa un cromosoma y retorna el dict completo de métricas."""
        out = {}
        self._evaluate(x, out)
        return self.last_eval_details.copy()
