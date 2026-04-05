import numpy as np
import pandas as pd
from pymoo.core.problem import ElementwiseProblem
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from modelo.funciones.tiempos_viaje import tau_ij_vec

class CVRPEuclideanProblem(ElementwiseProblem):
    def __init__(self, df_cluster: pd.DataFrame, matriz_dist: pd.DataFrame, depot_id: str, cap_peso: float, k_trucks: int):
        
        self.df_cluster = df_cluster.copy()
        
        self.clientes_ids = [c for c in matriz_dist.index if c != depot_id]
        n_clientes = len(self.clientes_ids)
        
        self.peso_dict = {}
        df_idx = self.df_cluster.set_index('id_nodo')
        for cid in self.clientes_ids:
            if cid in df_idx.index:
                row = df_idx.loc[cid]
                if isinstance(row, pd.DataFrame):
                    row = row.iloc[0]
                self.peso_dict[cid] = float(row.get('demanda', 0.0))
            else:
                self.peso_dict[cid] = 0.0
                
        self.matriz_dist = matriz_dist
        self.depot_id = depot_id
        
        self.cap_peso = cap_peso
        self.k_trucks = k_trucks
        
        # Parámetros operativos y fijos para la versión clásica:
        self.dia_semana = 0 # Asumimos Lunes según retroalimentación
        self.aten_fijo = 5.0 # Minutos de atención por cliente
        self.dist_multiplier = 100.0 # Factor para que tau_ij_vec trate la grilla como metros
        
        # Límite global: Todo debe terminar antes de las 21:00 hrs (1260 minutos)
        # La ventana del cliente individual ya no existe (todos disponibles todo el día).
        # Turnos operacionales para respetar la simulación:
        self.plantillas_turnos = [
            [540.0, 900.0],   # K11 (09:00), K12 (15:00)
            [660.0, 1020.0]   # K21 (11:00), K22 (17:00)
        ]
        
        super().__init__(n_var=n_clientes, 
                         n_obj=1, 
                         n_ieq_constr=1, 
                         xl=0, 
                         xu=max(0, n_clientes - 1), 
                         vtype=int)

    def _evaluate(self, x, out, *args, **kwargs):
        ruta_candidata = [self.clientes_ids[i] for i in x]
        
        dist_total_m = 0.0
        peso_actual = 0.0
        
        rutas_camiones = []
        ruta_act = []
        tiempos_llegada = {}
        
        num_camiones_fisicos = 1
        plantilla_idx = 0
        turnos_actual = self.plantillas_turnos[plantilla_idx]
        turno_idx = 0
        cam_t_salida = turnos_actual[turno_idx]
        t_actual = cam_t_salida
        nodo_previo = self.depot_id
        
        detalle_nodos = {}
        detalle_camiones = []
        
        cam_t_viaje = 0.0
        cam_t_espera = 0.0
        cam_t_servicio = 0.0
        cam_dist = 0.0
        
        for cliente_id in ruta_candidata:
            peso_p = self.peso_dict[cliente_id]
            
            # Recuperar distancia Euclidiana plana de la matriz
            dist_arco_tent = float(self.matriz_dist.loc[nodo_previo, cliente_id]) * self.dist_multiplier
            t_viaj_tent = float(tau_ij_vec(np.array([dist_arco_tent]), np.array([t_actual]), self.dia_semana)[0])
            t_ini_tent = t_actual + t_viaj_tent # Sin a_ventana
            t_fin_tent = t_ini_tent + self.aten_fijo
            
            dist_retorno_tent = float(self.matriz_dist.loc[cliente_id, self.depot_id]) * self.dist_multiplier
            t_viaj_ret_tent = float(tau_ij_vec(np.array([dist_retorno_tent]), np.array([t_fin_tent]), self.dia_semana)[0])
            
            # En CVRP Clásico simulado: split condicional si excede capacidad O si el retorno excede las 21:00 hrs
            hora_retorno_estimada = t_fin_tent + t_viaj_ret_tent
            
            if (peso_actual + peso_p > self.cap_peso) or (hora_retorno_estimada > 1260.0):
                # Regresar camión
                dist_reg = float(self.matriz_dist.loc[nodo_previo, self.depot_id]) * self.dist_multiplier
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
                    "dist_total_m": cam_dist / self.dist_multiplier, # Revertir a unidades de grilla originales
                    "peso_total": peso_actual,
                    "t_salida_deposito": cam_t_salida,
                    "t_retorno_deposito": t_actual + t_viaje_reg,
                    "n_clientes": len(ruta_act),
                    "dist_retorno_m": dist_reg / self.dist_multiplier,
                    "t_viaje_retorno_min": t_viaje_reg,
                    "id_camion_fisico": num_camiones_fisicos,
                    "turno_operacion": "Mañana" if turno_idx == 0 else "Tarde",
                    "subconjunto_k": f"K{plantilla_idx+1}{turno_idx+1}"
                })
                
                rutas_camiones.append(ruta_act)
                
                # Multi-viaje / Nuevo Turno o Nuevo Físico
                turno_idx += 1
                if turno_idx < len(turnos_actual):
                    cam_t_salida = turnos_actual[turno_idx]
                else:
                    num_camiones_fisicos += 1
                    plantilla_idx = (plantilla_idx + 1) % len(self.plantillas_turnos)
                    turnos_actual = self.plantillas_turnos[plantilla_idx]
                    turno_idx = 0
                    cam_t_salida = turnos_actual[turno_idx]

                peso_actual = 0.0
                t_actual = cam_t_salida
                nodo_previo = self.depot_id
                ruta_act = []
                cam_t_viaje = 0.0
                cam_t_espera = 0.0
                cam_t_servicio = 0.0
                cam_dist = 0.0

            # Transito
            dist_arco = float(self.matriz_dist.loc[nodo_previo, cliente_id]) * self.dist_multiplier
            d_arr = np.array([dist_arco])
            t_arr = np.array([t_actual])
            
            t_viaje_arr = tau_ij_vec(distancia_m=d_arr, t=t_arr, dia_semana=self.dia_semana)
            t_viaje = float(t_viaje_arr[0])
            
            t_llegada_real = t_actual + t_viaje
            t_inicio_servicio = t_llegada_real # Sin tiempo muerto (wait=0)

            cam_t_viaje += t_viaje
            cam_t_servicio += self.aten_fijo
            cam_dist += dist_arco
            
            detalle_nodos[cliente_id] = {
                "t_salida_anterior": t_actual,
                "dist_arco_m": dist_arco / self.dist_multiplier,
                "t_viaje_min": t_viaje,
                "t_llegada_real": t_llegada_real,
                "t_inicio_servicio": t_inicio_servicio,
                "peso_g": peso_p
            }
                
            t_actual = t_inicio_servicio + self.aten_fijo
            dist_total_m += dist_arco
            peso_actual += peso_p
            nodo_previo = cliente_id
            
            ruta_act.append(cliente_id)
            tiempos_llegada[cliente_id] = t_inicio_servicio

        if ruta_act:
            dist_reg_final = float(self.matriz_dist.loc[nodo_previo, self.depot_id]) * self.dist_multiplier
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
                "dist_total_m": cam_dist / self.dist_multiplier,
                "peso_total": peso_actual,
                "t_salida_deposito": cam_t_salida,
                "t_retorno_deposito": t_retorno,
                "n_clientes": len(ruta_act),
                "dist_retorno_m": dist_reg_final / self.dist_multiplier,
                "t_viaje_retorno_min": t_viaje_ret,
                "id_camion_fisico": num_camiones_fisicos,
                "turno_operacion": "Mañana" if turno_idx == 0 else "Tarde",
                "subconjunto_k": f"K{plantilla_idx+1}{turno_idx+1}"
            })
            rutas_camiones.append(ruta_act)

        # Objetivo Puramente Distancial (El Costo = Distancia en metros "grilla")
        # Para empujar el algoritmo también penalizamos sutilmente los camiones usados (como en modelo real)
        out["F"] = np.array([(dist_total_m / self.dist_multiplier)])
        
        penalizacion_camiones = max(0, num_camiones_fisicos - self.k_trucks)
        out["G"] = np.array([penalizacion_camiones])
        
        self.last_eval_details = {
            "rutas": rutas_camiones,
            "tiempos_llegada": tiempos_llegada,
            "detalle_nodos": detalle_nodos,
            "detalle_camiones": detalle_camiones,
            "dist_total_m": dist_total_m / self.dist_multiplier,
            "costo_total": dist_total_m / self.dist_multiplier
        }
    
    def evaluar_completo(self, x):
        out = {}
        self._evaluate(x, out)
        return self.last_eval_details.copy()
