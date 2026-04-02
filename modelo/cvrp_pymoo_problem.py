import numpy as np
import pandas as pd
from pymoo.core.problem import ElementwiseProblem

class CVRPEuclideanProblem(ElementwiseProblem):
    def __init__(self, df_cluster: pd.DataFrame, matriz_dist: pd.DataFrame, depot_id: str, cap_peso: float):
        
        self.df_cluster = df_cluster.copy()
        
        # Guardaremos el array de IDs en orden, ignorando al depot_id
        self.clientes_ids = [c for c in matriz_dist.index if c != depot_id]
        n_clientes = len(self.clientes_ids)
        
        # Mapeados rápidos de demandas para acceso constante O(1)
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
        
        # Minimize (1 Objetivo), 0 Restricciones Desigualdad "Duras" 
        # (ya que penalizamos construyendo un viaje nuevo como fallback)
        super().__init__(n_var=n_clientes, 
                         n_obj=1, 
                         n_ieq_constr=0, 
                         xl=0, 
                         xu=max(0, n_clientes - 1), 
                         vtype=int)

    def _evaluate(self, x, out, *args, **kwargs):
        """
        x: Cromosoma Permutación de enteros (0..n-1), que mapean a self.clientes_ids.
        """
        # Extraer orden propuesto por X
        ruta_candidata = [self.clientes_ids[i] for i in x]
        
        dist_total = 0.0
        peso_actual = 0.0
        
        rutas_camiones = []
        ruta_act = []
        
        nodo_previo = self.depot_id
        
        detalle_nodos = {}
        detalle_camiones = []
        
        cam_dist = 0.0
        num_camiones = 1
        
        for cliente_id in ruta_candidata:
            peso_p = self.peso_dict[cliente_id]
            
            # SPLIT CONDICIONAL (Capacidad Vehicular)
            if peso_actual + peso_p > self.cap_peso:
                # Regreso del camión actual al depósito
                dist_reg = float(self.matriz_dist.loc[nodo_previo, self.depot_id])
                
                cam_dist += dist_reg
                dist_total += dist_reg
                
                detalle_camiones.append({
                    "id_camion": num_camiones,
                    "dist_total_m": cam_dist,
                    "peso_total": peso_actual,
                    "n_clientes": len(ruta_act)
                })
                rutas_camiones.append(ruta_act)
                
                # Siguiente camión
                num_camiones += 1
                peso_actual = 0.0
                nodo_previo = self.depot_id
                ruta_act = []
                cam_dist = 0.0
        
            # Tránsito hacia cliente
            dist_arco = float(self.matriz_dist.loc[nodo_previo, cliente_id])
            
            # Acumular
            cam_dist += dist_arco
            dist_total += dist_arco
            peso_actual += peso_p
            nodo_previo = cliente_id
            
            ruta_act.append(cliente_id)
            
            # Formato estándar solicitado por usuario
            detalle_nodos[cliente_id] = {
                "dist_arco_m": dist_arco,
                "peso_g": peso_p, # Nombre legado en pipeline, pero lleva la demanda genérica
                "peso_acumulado": peso_actual
            }
            
        # Regreso del último camión
        if ruta_act:
            dist_reg_final = float(self.matriz_dist.loc[nodo_previo, self.depot_id])
            cam_dist += dist_reg_final
            dist_total += dist_reg_final
            
            detalle_camiones.append({
                "id_camion": num_camiones,
                "dist_total_m": cam_dist,
                "peso_total": peso_actual,
                "n_clientes": len(ruta_act)
            })
            rutas_camiones.append(ruta_act)
            
        # Penalización lineal por exceso de camiones opcional (dejado implícito al maximizar eficiencia de peso)
        out["F"] = np.array([dist_total])
        
        # Guardar detalles exhaustivos simulando las ventanas temporales para no romper Gestor
        self.last_eval_details = {
            "rutas": rutas_camiones,
            "detalle_nodos": detalle_nodos,
            "detalle_camiones": detalle_camiones,
            "dist_total_m": dist_total,
            "costo_total": dist_total  # Distancia = Costo
        }
    
    def evaluar_completo(self, x):
        """Evalúa un cromosoma y retorna el dict completo de métricas."""
        out = {}
        self._evaluate(x, out)
        return self.last_eval_details.copy()
