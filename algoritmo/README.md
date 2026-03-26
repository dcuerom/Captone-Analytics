# 🧠 Algoritmos Metaheurísticos

Esta carpeta alberga los optimizadores (Algoritmo Genético y Búsqueda Tabú) desarrollados para abordar la complejidad computacional NP-Hard del problema central **TDVRPTW**.

Ambos algoritmos asumen la misma interfaz de datos:
1. Son inyectados con un espacio de cluster (desde `grafo/main.py`).
2. Reciben coordenadas y demandas de una muestra del archivo base (`df_despacho.csv`).
3. Heredan una matriz calculada estrictamente en **metros**.
4. Cruzan las métricas con el tensor de tiempos `tiempos_viaje.py` definido en el `modelo.py`, utilizando capacidades estandarizadas en **g** y **cm3**.

## Ejecutables
- `genetic_algorithm.py`: Implementa un GA evolutivo con cruce de orden y splits capacitados. Evalúa ventanas de tiempo iterativamente.
- `tabu_search.py`: Implementa Búsqueda Tabú bajo una aproximación agresiva local, con lista tabú cíclica basada en swap de nodos, esquivando óptimos locales.

## Ejecución

Ambos scripts están preparados para invocarse de forma aislada e interactiva:
```bash
python algoritmo/genetic_algorithm.py
python algoritmo/tabu_search.py
```
