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
                 dia_semana=0, factor_s=1.2, d_max_min=300.0):
        
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
            try:
                self.vol_dict[cid] = float(df_idx.loc[cid, 'volumen_pedido_cm3'])
                self.peso_dict[cid] = float(df_idx.loc[cid, 'peso_pedido_g'])
                self.a_dict[cid] = float(df_idx.loc[cid, 'a_ventana']) if 'a_ventana' in df_idx.columns else 0.0
                self.b_dict[cid] = float(df_idx.loc[cid, 'b_ventana']) if 'b_ventana' in df_idx.columns else 1440.0
            except KeyError:
                self.vol_dict[cid], self.peso_dict[cid], self.a_dict[cid], self.b_dict[cid] = 0, 0, 0, 1440.0
                
        self.matriz_dist = matriz_dist_m
        self.depot_id = depot_id
        
        self.t_inicio = t_inicio
        self.cap_vol_cm3 = cap_vol_cm3
        self.cap_peso_g = cap_peso_g
        self.dia_semana = dia_semana
        self.factor_s = factor_s
        self.aten_fijo = 5.0 # Minutos de atención
        self.d_max_min = d_max_min # Límite de 5 horas máximo (Restricción 14)
        
        # ElementwiseProblem configurado:
        # n_var = permutación de índices de [0... n_clientes-1]
        # n_obj = 1 (Minimizar F: distancia total * S)
        # n_ieq_constr = 1 (Sumatoria de todas las roturas hard en tiempo y capacidad)
        
        super().__init__(n_var=n_clientes, 
                         n_obj=1, 
                         n_ieq_constr=1, 
                         xl=0, 
                         xu=n_clientes - 1, 
                         vtype=int)

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
        
        vol_actual = 0.0
        peso_actual = 0.0
        t_actual = self.t_inicio
        nodo_previo = self.depot_id
        rutas_camiones = []
        ruta_act = []
        tiempos_llegada = {}
        detalle_nodos = {}
        detalle_camiones = []  # Métricas por camión
        
        # Contadores del camión actual
        cam_t_viaje = 0.0
        cam_t_espera = 0.0
        cam_t_servicio = 0.0
        cam_dist = 0.0
        cam_t_salida = self.t_inicio
        
        for cliente_id in ruta_candidata:
            vol_p = self.vol_dict[cliente_id]
            peso_p = self.peso_dict[cliente_id]
            
            # 1. Proyección de la ruta para prever Restricción 14 (Conducción d_max) incluyendo retorno
            dist_arco_tent = float(self.matriz_dist.loc[nodo_previo, cliente_id])
            t_viaj_tent = float(tau_ij_vec(np.array([dist_arco_tent]), np.array([t_actual]), self.dia_semana)[0])
            t_ini_tent = max(t_actual + t_viaj_tent, self.a_dict[cliente_id])
            t_fin_tent = t_ini_tent + self.aten_fijo
            
            dist_retorno_tent = float(self.matriz_dist.loc[cliente_id, self.depot_id])
            t_viaj_ret_tent = float(tau_ij_vec(np.array([dist_retorno_tent]), np.array([t_fin_tent]), self.dia_semana)[0])
            tiempo_conduccion_estimado = cam_t_viaje + t_viaj_tent + t_viaj_ret_tent
            
            # SPLIT CONDICIONAL (Activa regreso al depósito si se violan capacidades o turno máximo de conducción)
            if (vol_actual + vol_p > self.cap_vol_cm3) or (peso_actual + peso_p > self.cap_peso_g) or (tiempo_conduccion_estimado > self.d_max_min):
                # Regreso del camión actual al depósito
                dist_reg = float(self.matriz_dist.loc[nodo_previo, self.depot_id])
                d_ret = np.array([dist_reg])
                t_ret = np.array([t_actual])
                t_viaje_reg = float(tau_ij_vec(distancia_m=d_ret, t=t_ret, dia_semana=self.dia_semana)[0])
                
                cam_t_viaje += t_viaje_reg
                cam_dist += dist_reg
                dist_total_m += dist_reg
                detalle_camiones.append({
                    "t_viaje_efectivo_min": cam_t_viaje,
                    "t_espera_total_min": cam_t_espera,
                    "t_servicio_total_min": cam_t_servicio,
                    "dist_total_m": cam_dist,
                    "t_salida_deposito": cam_t_salida,
                    "t_retorno_deposito": t_actual + t_viaje_reg,
                    "n_clientes": len(ruta_act),
                    "dist_retorno_m": dist_reg,
                    "t_viaje_retorno_min": t_viaje_reg
                })
                
                rutas_camiones.append(ruta_act)
                
                # Reseteo camión
                vol_actual = 0.0
                peso_actual = 0.0
                t_actual = self.t_inicio
                nodo_previo = self.depot_id
                ruta_act = []
                cam_t_viaje = 0.0
                cam_t_espera = 0.0
                cam_t_servicio = 0.0
                cam_dist = 0.0
                cam_t_salida = self.t_inicio
        
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
            
            if t_llegada_real < a_p:
                t_espera = a_p - t_llegada_real
                t_inicio_servicio = a_p
            else:
                t_inicio_servicio = t_llegada_real
                
            if t_inicio_servicio > b_p:
                t_violacion = t_inicio_servicio - b_p
                restricciones_fail += t_violacion
            
            # Acumular tiempos del camión
            cam_t_viaje += t_viaje
            cam_t_espera += t_espera
            cam_t_servicio += self.aten_fijo
            cam_dist += dist_arco
            
            detalle_nodos[cliente_id] = {
                "t_salida_anterior": t_actual,
                "dist_arco_m": dist_arco,
                "t_viaje_min": t_viaje,
                "t_llegada_real": t_llegada_real,
                "a_ventana": a_p,
                "b_ventana": b_p,
                "t_espera_min": t_espera,
                "t_inicio_servicio": t_inicio_servicio,
                "t_servicio_min": self.aten_fijo,
                "volumen_cm3": vol_p,
                "peso_g": peso_p,
                "t_violacion_min": t_violacion,
                "cumple_ventana": t_violacion == 0.0
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
                "t_viaje_retorno_min": t_viaje_ret
            })
            
            rutas_camiones.append(ruta_act)
            
        # ASIGNACIÓN DE SALIDAS (PyMoo standard)
        # Solo F y G pueden ir en out — PyMoo apila TODAS las claves del dict
        # en un array numpy para la población completa, y las claves con shapes
        # variables (listas de rutas, dicts) provocan errores de forma inhomogénea.
        out["F"] = np.array([dist_total_m * self.factor_s])
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
