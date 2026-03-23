import pandas as pd

def probar_escenarios_sensibilidad():
    """
    Script para ejecutar pruebas de sensibilidad cambiando parámetros 
    del modelo y del algoritmo (ej. aumento de flota, cambios de demanda, rangos horarios).
    """
    escenarios = [
        {"nombre": "Escenario Base", "parametros_modelo": {}},
        {"nombre": "Restricciones Horarias Más Estrictas", "parametros_modelo": {"ventana_tiempo": "estricta"}},
        {"nombre": "Flota Limitada", "parametros_modelo": {"vehiculos_max": 5}},
    ]

    resultados = []

    for un_escenario in escenarios:
        print(f"--- Evaluando {un_escenario['nombre']} ---")
        
        # 1. Instanciar el modelo con variaciones en sus parámetros
        # problem = VRPModel(**un_escenario['parametros_modelo'])
        
        # 2. Ejecutar el AG
        # res = ejecutar_algoritmo_genetico(problem, n_gen=50)
        
        # 3. Guardar las métricas de interés
        # resultados.append({
        #     "Escenario": un_escenario['nombre'],
        #     "Mejor F1 (Distancia)": res.F[0] if res.F is not None else None,
        #     "Mejor F2 (Vehículos)": res.F[1] if res.F is not None else None
        # })
        pass

    # df_res = pd.DataFrame(resultados)
    # print("\nTabla Resumen Sensibilidad:")
    # print(df_res)
    # df_res.to_csv("../resultados/sensibilidad_resultados.csv", index=False)

if __name__ == "__main__":
    probar_escenarios_sensibilidad()
