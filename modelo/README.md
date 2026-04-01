# 🧊 Módulo `modelo/` — Formalización Computacional TDVRPTW

Este módulo contiene la implementación computacional rigurosa del **Modelo Matemático TDVRPTW** formalizado analíticamente (Time-Dependent Vehicle Routing Problem with Time Windows).

## Archivos y su Contribución al Pipeline

### `pymoo_problem.py`
**Rol:** Clase evaluadora (Fitness Evaluator) para la heurística.
**Funcionalidad Detallada:** 
Contiene la arquitectura pesada en la clase `TDVRPTWProblem` que hereda de `ElementwiseProblem` de la librería `pymoo`. Mientras que `genetic_algorithm.py` simplemente arroja secuencias permutadas (cromosomas), **este script ejerce de juez estricto**. Decodifica cada ruta en un arreglo lineal ($0 \to i \to j \to 0$), recomputando:
- Tiempos de servicio.
- Volumen total y peso total (Haciendo Split Dinámico de la ruta si se sobrepasa la métrica `cm3` o `g` configurada).
- Funciones objetivo (`out["F"]`), favoreciendo distancias mínimas en **metros**.
- Restricciones restrictivas (`out["G"]`): Cuantifica en minutos todo exceso de las ventanas de tiempo.

### `modelo.py`
**Rol:** Esquema estricto exacto (MIP).
**Funcionalidad Detallada:** 
En modelamiento original (abstracto matemático exacto resuelto mediante librerías como `pyomo`). Plantea todas las variables $X_{ijk}$ booleanas. Como la naturaleza combinatoria explota en tiempos computacionales inmanejables (NP-Hard), este archivo actúa más como un testamento/referencia para que el algoritmo genético lo emule en aproximación.

### `vrp_pymoo.py`
**Rol:** Script base/laboratorio.
**Funcionalidad Detallada:** 
Contiene prototipos más básicos de la problemática VRP que los inyectados en producción, usualmente sin la capa $t$-dependiente (Tráfico) de los tiempos de viaje.

### `funciones/` (Subdirectorio)
**Rol:** Funciones matemáticas utilitarias independientes.
**Funcionalidad Detallada:**
Posee scripts como `test_tiempos_viaje.py` o convertidores de "Distancia a Tiempo Físico", como `tiempos_viaje.py`, que albergan ecuaciones de velocidad paramétricas (e.g. Función $\tau_{ij}(t)$ de curva de tráfico en hora punta). Contribuye siendo el engranaje que da el realismo a las velocidades de llegada dentro de `pymoo_problem.py`.
