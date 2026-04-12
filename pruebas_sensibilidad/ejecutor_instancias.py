import os
import sys
import pandas as pd
import time
import itertools
from datetime import datetime

# Añadir el raíz para poder importar algoritmos
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from algoritmo.genetic_algorithm import disparar_rutina_ga

def generar_reporte_md(csv_path, md_path):
    if not os.path.exists(csv_path):
        return
    df = pd.read_csv(csv_path)
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Reporte de Pruebas de Sensibilidad - TDVRPTW\n\n")
        f.write("Este documento resume los resultados obtenidos al evaluar distintas combinaciones ")
        f.write("de hiperparámetros sobre cada uno de los días de despacho registrados en `df_despacho.csv`.\n\n")
        
        f.write("## Resumen General\n")
        f.write(f"- Total de corridas ejecutadas: {len(df)}\n")
        
        factibles = df[df['Factible'] == "Sí"]
        f.write(f"- Pruebas Factibles (100% Entregas a Tiempo en ventanas de reloj): {len(factibles)} ({(len(factibles)/len(df)*100) if len(df)>0 else 0:.1f}%)\n")
        
        if not factibles.empty:
            f.write("\n### Mejores Configuraciones (Top 10 - Menor Función Objetivo)\n")
            top_configs = factibles.sort_values(by="Funcion_Objetivo").head(10)
            f.write(top_configs.to_markdown(index=False))
            f.write("\n\n")
            
        f.write("## Análisis sobre impacto de Hiperparámetros de Sensibilidad\n\n")
        f.write("A continuación se observan los distintos parámetros en la ejecución paralela y un log constante.\n")
        f.write("Consulte el archivo `resultados_combinaciones.csv` para la tabla completa al nivel granular.\n")


def ejecutar_pruebas():
    # 1. Leer dias disponibles
    data_path = os.path.join(base_dir, 'DatosSimulados', 'df_despacho.csv')
    df_data = pd.read_csv(data_path)
    if 'fecha_entrega' not in df_data.columns:
        print("El archivo no contiene 'fecha_entrega'.")
        sys.exit(1)
        
    dias_disponibles = sorted(df_data['fecha_entrega'].dropna().unique())
    print(f"Días a evaluar ({len(dias_disponibles)}): {dias_disponibles}")
    
    # 2. Definir Grid de Hiperparámetros (Según petición del usuario: capacidad, camiones, tiempo config)
    grid_params = {
        "holgura_ventana": [15.0],
        "pop_size": [100, 150],
        "n_gen": [2000, 3000],
        "max_camiones": [20, 30],        # Jugar con la cantidad de camiones max disponible
        "cap_multiplicador": [1.0, 1.25] # Jugar con la capacidad base (multiplicador)
    }
    
    cap_vol_base = 3750000.0
    cap_peso_base = 803333.33
    
    keys, values = zip(*grid_params.items())
    combinaciones = [dict(zip(keys, v)) for v in itertools.product(*values)]
    
    print(f"Total de configuraciones a probar: {len(combinaciones)}")
    print(f"Total de iteraciones globales esperadas: {len(combinaciones) * len(dias_disponibles)}")
    
    # 3. Preparar archivo de resultados CSV
    res_path = os.path.join(base_dir, 'pruebas_sensibilidad', 'resultados_combinaciones.csv')
    md_path = os.path.join(base_dir, 'pruebas_sensibilidad', 'reporte_sensibilidad.md')
    
    if not os.path.exists(res_path):
        headers = ["Fecha", "holgura_ventana", "pop_size", "n_gen", "max_camiones", "cap_multiplicador", 
                   "Funcion_Objetivo", "Entregas_A_Tiempo_Pct", "Vehiculos_Usados", "Tardanza_Promedio", "Factible", "Tiempo_Computo_Min",
                   "Clientes_Atendidos", "Clientes_No_Atendidos"]
        pd.DataFrame(columns=headers).to_csv(res_path, index=False)
    
    # 4. Iterar y Ejecutar
    for comb_idx, comb in enumerate(combinaciones):
        print(f"\n[{comb_idx+1}/{len(combinaciones)}] Probando combinación: {comb}")
        
        cap_v = cap_vol_base * comb["cap_multiplicador"]
        cap_p = cap_peso_base * comb["cap_multiplicador"]
        
        for dia_idx, fecha in enumerate(dias_disponibles):
            print(f"  -> Evaluando día: {fecha} ({dia_idx+1}/{len(dias_disponibles)})")
            try:
                # Ejecutar el algoritmo
                disparar_rutina_ga(
                    fecha_target=fecha,
                    holgura_ventana=comb["holgura_ventana"],
                    pop_size=comb["pop_size"],
                    n_gen=comb["n_gen"],
                    max_camiones=comb["max_camiones"],
                    cap_vol_cm3=cap_v,
                    cap_peso_g=cap_p
                )
                
                # Leer el CSV generado de KPIs para capturar resultados
                kpi_csv_path = os.path.join(base_dir, 'resultados', 'rutas', f'kpis_hibridosavingsga_{fecha}.csv')
                
                if os.path.exists(kpi_csv_path):
                    df_kpi = pd.read_csv(kpi_csv_path)
                    kpi_dict = dict(zip(df_kpi['KPI'], df_kpi['Valor']))
                    
                    fo = kpi_dict.get("Función Objetivo Total ($)", -1)
                    entregas_pct = kpi_dict.get("% Entregas a Tiempo", 0)
                    veh_usados = kpi_dict.get("Vehículos Utilizados", 0)
                    tardanza = kpi_dict.get("Tardanza Promedio (min)", -1)
                    tiempo_comp = kpi_dict.get("Tiempo de Cómputo (min)", 0)
                    
                    factible = "Sí" if entregas_pct == 100.0 else "No"
                    
                    # Calcular clientes atendidos vs no atendidos
                    cl_csv_path = os.path.join(base_dir, 'resultados', 'rutas', f'clientes_atendidos_hibridosavingsga_{fecha}.csv')
                    cl_atendidos = 0
                    cl_no_atendidos = kpi_dict.get("Pedidos No Atendidos (qty)", 0)
                    if os.path.exists(cl_csv_path):
                        df_cl = pd.read_csv(cl_csv_path)
                        cl_atendidos = len(df_cl[df_cl['Atendido'] == "Sí"])
                        cl_no_atendidos = len(df_cl[df_cl['Atendido'] == "No"])
                    
                    fila_res = {
                        "Fecha": fecha,
                        "holgura_ventana": comb["holgura_ventana"],
                        "pop_size": comb["pop_size"],
                        "n_gen": comb["n_gen"],
                        "max_camiones": comb["max_camiones"],
                        "cap_multiplicador": comb["cap_multiplicador"],
                        "Funcion_Objetivo": fo,
                        "Entregas_A_Tiempo_Pct": entregas_pct,
                        "Vehiculos_Usados": veh_usados,
                        "Tardanza_Promedio": tardanza,
                        "Factible": factible,
                        "Tiempo_Computo_Min": tiempo_comp,
                        "Clientes_Atendidos": cl_atendidos,
                        "Clientes_No_Atendidos": cl_no_atendidos
                    }
                    
                    # Append al csv final usando mode='a'
                    pd.DataFrame([fila_res]).to_csv(res_path, mode='a', header=False, index=False)
                    print(f"     [+] Éxito. FO: {fo} | Veh_Usados: {veh_usados} | Factible: {factible}")
                    
                    # Regenerar log markdown al terminar del dia
                    generar_reporte_md(res_path, md_path)

                else:
                    print(f"     [-] Advertencia: No se encontró el archivo de KPIs {kpi_csv_path}")

            except Exception as e:
                print(f"     [!] Error corriendo la iteración: {e}")
            
            import gc
            gc.collect()

    print("\n[+] Fin de las Pruebas de Sensibilidad. Revisar reporte markdown y csv.")

if __name__ == "__main__":
    ejecutar_pruebas()
