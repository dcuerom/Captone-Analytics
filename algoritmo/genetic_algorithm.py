"""
algoritmo/genetic_algorithm.py

Orquestación híbrida Savings + GA (PyMoo) para TDVRPTW.
"""

import os
import sys
import time
import concurrent.futures
from typing import Callable, Optional

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gestion_flota.gestor import asignar_y_reportar
from grafo.main import execute_vrp_pipeline, clean_rut
from modelo.pymoo_problem import TDVRPTWProblem
from algoritmo.config import DEFAULT_OPTIMIZATION_CONFIG
from algoritmo.savings import clarke_wright_savings

from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.optimize import minimize
from pymoo.core.sampling import Sampling
from pymoo.termination.default import DefaultSingleObjectiveTermination

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)


class SavingsSeededSampling(Sampling):
    def __init__(self, savings_seed: Optional[np.ndarray], n_clientes: int):
        super().__init__()
        self.savings_seed = savings_seed
        self.n_clientes = n_clientes

    def _do(self, problem, n_samples, **kwargs):
        X = np.array([np.random.permutation(self.n_clientes) for _ in range(n_samples)])
        if self.savings_seed is not None and len(self.savings_seed) == self.n_clientes:
            X[0] = self.savings_seed
        return X


def _merge_config(config: Optional[dict]) -> dict:
    out = DEFAULT_OPTIMIZATION_CONFIG.copy()
    if isinstance(config, dict):
        out.update({k: v for k, v in config.items() if v is not None})
    return out


def _load_input_dataframe(input_csv_path: Optional[str]) -> tuple[pd.DataFrame, str]:
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


def _notify_progress(
    progress_callback: Optional[Callable[..., None]],
    stage: str,
    message: str,
    progress_pct: float,
    current_step: Optional[int] = None,
    total_steps: Optional[int] = None,
) -> None:
    if not callable(progress_callback):
        return
    try:
        progress_callback(
            stage=stage,
            message=message,
            progress_pct=progress_pct,
            current_step=current_step,
            total_steps=total_steps,
        )
    except Exception:
        # El progreso no debe detener el pipeline de optimización.
        pass


def optimizar_pymoo_ga(
    cluster_idx,
    df_cluster,
    matriz_dist,
    depot_id,
    dia_semana=0,
    config: Optional[dict] = None,
):
    """Ejecuta Savings + GA de PyMoo sobre un clúster."""
    clientes = [id_n for id_n in matriz_dist.index if id_n != depot_id]
    n_clientes = len(clientes)
    cfg = _merge_config(config)

    problem = TDVRPTWProblem(
        df_cluster=df_cluster,
        matriz_dist_m=matriz_dist,
        depot_id=depot_id,
        t_inicio=float(cfg["t_inicio"]),
        cap_vol_cm3=float(cfg["cap_vol_cm3"]),
        cap_peso_g=float(cfg["cap_peso_g"]),
        factor_s=float(cfg["factor_s"]),
        dia_semana=dia_semana,
        alpha_espera=float(cfg["alpha_espera"]),
        d_max_min=float(cfg["d_max_min"]),
    )
    problem.costo_fijo_camion = float(cfg.get("costo_fijo_camion", 0.0))

    if n_clientes == 0:
        return {
            "F": 0.0,
            "G": 0.0,
            "rutas": [],
            "tiempos_llegada": {},
            "dist_total_m": 0.0,
            "costo_total": 0.0,
            "t_inicio": float(cfg["t_inicio"]),
            "t_fin": float(cfg["t_inicio"]),
            "duracion_min": 0.0,
        }
    if n_clientes == 1:
        return problem.evaluar_completo([0])

    # Semilla Clarke-Wright
    savings_route_ids = clarke_wright_savings(
        df_cluster,
        matriz_dist,
        depot_id,
        cap_vol_cm3=float(cfg["cap_vol_cm3"]),
        cap_peso_g=float(cfg["cap_peso_g"]),
        d_max_min=float(cfg["d_max_min"]),
        speed_kmh=25.0,
    )
    id_to_idx = {cid: i for i, cid in enumerate(clientes)}
    savings_route_idx = (
        np.array([id_to_idx[cid] for cid in savings_route_ids if cid in id_to_idx])
        if savings_route_ids
        else None
    )

    algorithm = GA(
        pop_size=int(cfg["ga_pop_size"]),
        sampling=SavingsSeededSampling(savings_seed=savings_route_idx, n_clientes=n_clientes),
        crossover=OrderCrossover(),
        mutation=InversionMutation(prob=0.3),
        eliminate_duplicates=False,
    )

    terminacion_adaptativa = DefaultSingleObjectiveTermination(
        ftol=1e-3,
        period=200,
        n_max_gen=int(cfg["ga_n_gen"]),
    )

    res = minimize(
        problem,
        algorithm,
        termination=terminacion_adaptativa,
        seed=int(cfg["ga_seed"]),
        verbose=False,
        save_history=False,
    )

    if res.X is None:
        pop = res.pop
        if pop is not None and len(pop) > 0:
            cv_arr = pop.get("CV").flatten()
            best_idx = cv_arr.argmin()
            best_x = pop.get("X")[best_idx]
            return problem.evaluar_completo(best_x)
        raise ValueError(f"El GA no generó población válida para clúster {cluster_idx}.")

    return problem.evaluar_completo(res.X)


def disparar_rutina_ga(
    input_csv_path: Optional[str] = None,
    fecha_target: Optional[str] = None,
    max_vehiculos_globales: Optional[int] = 20,
    config: Optional[dict] = None,
    progress_callback: Optional[Callable[..., None]] = None,
):
    print("=== INICIANDO TDVRPTW - HIBRIDO SAVINGS + GA ===")
    t0 = time.time()
    cfg = _merge_config(config)
    _notify_progress(progress_callback, "preparing", "Validando datos de entrada...", 5.0)

    df, data_path = _load_input_dataframe(input_csv_path)
    if df.empty:
        raise ValueError(f"La fuente de datos está vacía: {data_path}. Carga un CSV con pedidos antes de optimizar.")

    if fecha_target is None:
        if 'fecha_entrega' in df.columns and not df['fecha_entrega'].dropna().empty:
            normalized_dates = _normalize_date_series(df['fecha_entrega']).dropna()
            fecha_target = str(sorted(normalized_dates.unique())[-1]) if not normalized_dates.empty else pd.Timestamp.now().strftime('%Y-%m-%d')
        else:
            fecha_target = pd.Timestamp.now().strftime('%Y-%m-%d')

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
    _notify_progress(progress_callback, "preparing", f"Pedidos listos para {fecha_target}.", 15.0)

    if 'id_cliente' in df_filtro.columns and 'id_pedido' in df_filtro.columns:
        df_filtro['rut_clean'] = df_filtro['id_cliente'].apply(clean_rut)
        df_filtro['id_nodo'] = df_filtro['id_pedido'].astype(str).str.strip() + "_" + df_filtro['rut_clean']

    df_filtro.rename(columns={'Latitud': 'latitud', 'Longitud': 'longitud', 'Dirección': 'direccion_ruteo'}, inplace=True)

    temp_csv_path = os.path.join(base_dir, 'EDA', 'df_despacho.csv')
    os.makedirs(os.path.dirname(temp_csv_path), exist_ok=True)
    df_filtro.to_csv(temp_csv_path, index=False)

    _notify_progress(progress_callback, "clustering_routing", "Ejecutando clustering y matriz vial...", 25.0)
    matrices_km_o_m, rutas_dict, G, depot_coords = execute_vrp_pipeline(
        input_file=temp_csv_path,
        clustering_time_column=str(cfg["clustering_time_column"]),
        clustering_default_window_start_hour=int(cfg["clustering_default_window_start_hour"]),
        clustering_alpha_time=float(cfg["clustering_alpha_time"]),
        clustering_eps=float(cfg["clustering_eps"]),
        clustering_min_samples=int(cfg["clustering_min_samples"]),
        clustering_rescue_threshold=float(cfg["clustering_rescue_threshold"]),
        force_outlier_rescue=bool(cfg["force_outlier_rescue"]),
    )
    _notify_progress(progress_callback, "clustering_routing", "Clustering y ruteo vial completados.", 55.0)

    out_dir = os.path.join(base_dir, 'resultados', 'rutas')
    mapa_dir = os.path.join(base_dir, 'resultados', 'mapa_rutas')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(mapa_dir, exist_ok=True)
    depot_id = "DEPOT_01_BASE"

    max_camiones = int(max_vehiculos_globales if max_vehiculos_globales is not None else cfg["max_vehiculos_globales"])

    tasks = [
        (cluster_id, df_filtro, matriz_dist, depot_id, dia_semana_target, cfg)
        for cluster_id, matriz_dist in matrices_km_o_m.items()
    ]
    total_clusters = len(tasks)

    resultados_globales = {}
    max_w = max(1, (os.cpu_count() or 2) // 2)
    print(f"[PyMoo] Procesamiento paralelo de clústeres con {max_w} workers...")
    _notify_progress(
        progress_callback,
        "optimizing_clusters",
        "Optimizando clústeres con GA...",
        60.0,
        current_step=0,
        total_steps=total_clusters,
    )

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_w) as executor:
        future_to_cluster = {
            executor.submit(optimizar_pymoo_ga, *task): task[0]
            for task in tasks
        }
        completed_clusters = 0
        for future in concurrent.futures.as_completed(future_to_cluster):
            cluster_id = future_to_cluster[future]
            try:
                resultados_globales[cluster_id] = future.result()
                print(f"[PyMoo] Cluster {cluster_id} finalizado.")
            except Exception as e:
                print(f"Error procesando {cluster_id}: {e}")
            completed_clusters += 1
            progress_pct = 60.0 + (30.0 * completed_clusters / max(1, total_clusters))
            _notify_progress(
                progress_callback,
                "optimizing_clusters",
                f"Clústeres optimizados: {completed_clusters}/{total_clusters}",
                progress_pct,
                current_step=completed_clusters,
                total_steps=total_clusters,
            )

    _notify_progress(progress_callback, "assigning_fleet", "Asignando rutas a la flota global...", 92.0)

    tiempo_total_min = (time.time() - t0) / 60.0

    asignar_y_reportar(
        resultados_clusters=resultados_globales,
        max_vehiculos=max_camiones,
        df_filtro=df_filtro,
        depot_id=depot_id,
        fecha_target=fecha_target,
        tipo_algoritmo="Hibrido Savings GA",
        out_dir=out_dir,
        rutas_dict_global=rutas_dict,
        G=G,
        mapa_dir=mapa_dir,
        depot_coords=depot_coords,
        tiempo_computo_min=tiempo_total_min,
    )
    _notify_progress(progress_callback, "exporting", "Exportando reportes y mapa...", 97.0)
    _notify_progress(progress_callback, "completed", "Optimización completada.", 100.0)

    print("[Éxito] Optimización y Asignación de Flota finalizada.")
    return {
        "fecha_target": fecha_target,
        "dia_semana_target": int(dia_semana_target),
        "clusters_optimizados": int(len(resultados_globales)),
        "max_vehiculos_globales": int(max_camiones),
        "source_csv": data_path,
        "config_applied": cfg,
    }


if __name__ == "__main__":
    disparar_rutina_ga()
