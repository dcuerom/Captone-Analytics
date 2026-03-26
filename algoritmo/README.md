# 🧠 Algoritmos Metaheurísticos

Esta carpeta alberga los optimizadores (Algoritmo Genético y Búsqueda Tabú) desarrollados para abordar la complejidad computacional NP-Hard del problema central **TDVRPTW**.

Ambos algoritmos asumen la misma interfaz de datos:
1. Son inyectados con un espacio de cluster (desde `grafo/main.py`).
2. Reciben coordenadas y demandas de una muestra del archivo base (`df_despacho.csv`).
3. Heredan una matriz calculada estrictamente en **metros**.
4. Cruzan las métricas con el tensor de tiempos `tiempos_viaje.py` definido en el `modelo.py`, utilizando capacidades estandarizadas en **g** y **cm3**.

---

## 🧬 Funcionamiento de `genetic_algorithm.py`

El archivo `genetic_algorithm.py` orquesta la resolución del ruteo utilizando la librería oficial **PyMoo** mediante un Algoritmo Genético (GA) configurado para permutaciones. Su ejecución consta de dos grandes fases:

### 1. Preparación de los Datos y Orquestación (`disparar_rutina_ga`)
Este es el bloque principal (pipeline) que provee la información al algoritmo de optimización y gestiona las salidas:
- **Lectura y Filtrado:** Lee el archivo base `df_despacho.csv` desde `/DatosSimulados`, extrayendo los pedidos filtrados para una fecha designada (por ejemplo, `2026-12-03`).
- **Limpieza y Armado de Nodos:** Genera un ID único (`id_nodo`) por cada cliente consolidando el ID de pedido y el RUT limpio, y normaliza nombres de columnas geográficas.
- **Extracción Espacial:** Invoca el core geométrico/vial (`execute_vrp_pipeline`) para obtener la matriz de distancias ruteables asimétricas por cada "cluster".
- **Generación de Entregables:** Al finalizar la optimización iterativa iterando por todos los clústers, genera automáticamente dos resultados clave listos para el negocio:
  1. Un detallado **Reporte en formato Markdown** (exportado en `resultados/rutas/`) describiendo los KPIs de asignaciones, tiempos de espera, llegadas a destino y violaciones a las ventanas.
  2. Un **Mapa Interactivo HTML** (exportado en `resultados/mapa_rutas/`) trazando las polilíneas finales apoyando ruteros A* de forma visual.

### 2. Optimización Metaheurística (`optimizar_pymoo_ga`)
Por cada cluster que reciba el pipeline, la rutina instancia y resuelve la optimización genética:
- **Modelo Subyacente (`TDVRPTWProblem`):** Inyecta la matriz y los clientes al esquema `ElementwiseProblem` construido con las capacidades y penalizaciones en `modelo/pymoo_problem.py`.
- **Configuración del Algoritmo Genético (`GA`):**
  - **Población (`pop_size`):** Base evolutiva de 50 cromosomas/individuos.
  - **Muestreo Inicial (`PermutationRandomSampling`):** Genera la población aleatoria con secuencias lícitas (permutando clientes en enjambre desde $0 \dots n-1$).
  - **Crossover (`OrderCrossover`):** Mecanismo de reproducción principal que hereda ordenamientos eficientes sin duplicar y sin perder posiciones contiguas de la ruta.
  - **Mutación (`InversionMutation`):** Invierte el orden de sub-arreglos de clientes para saltar fuera de los óptimos locales e inyectar diversidad agresiva.
  - **Evolución (`minimize`):** Funciona a lo largo de 100 iteraciones (`n_gen`) minimizando sistemáticamente la variable "F" (distancia recorrida $\times S$) siempre en favor de los individuos que cumplan el estricto requerimiento de restricción "G" temporal.

---

## Ejecutables
- `genetic_algorithm.py`: Orquesta la optimización genética PyMoo (`GA`) sobre el pipeline de datos espaciales y genera reportes detallados MD / Web.
- `tabu_search.py`: Implementa Búsqueda Tabú pura bajo una aproximación agresiva local, con lista cíclica basada en swap de nodos.

## Ejecución

Ambos scripts están preparados para invocarse de forma aislada e interactiva desde el nivel superior del proyecto:
```bash
python algoritmo/genetic_algorithm.py
python algoritmo/tabu_search.py
```
