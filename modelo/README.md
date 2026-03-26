# 🧊 Módulo `modelo/` — Formalización Computacional TDVRPTW

Este módulo contiene la implementación computacional rigurosa del **Modelo Matemático TDVRPTW** descrito en `modelo.md`, mediante el uso de la librería **Pyomo**.

## Archivos Principales

*   `modelo.md`: Definición formal matemática del problema de optimización, incluyendo conjuntos ($C, 0, K, T$), parámetros ($S, VP_i, M, etc.$) y restricciones.
*   `modelo.py`: Transcripción de `modelo.md` hacia la programación orientada a restricciones usando `pyomo.environ.ConcreteModel`. Instancia los parámetros clave y variables de decisión exigidos para una posterior evaluación de aptitud (fitness) en heurísticas.

## Estandarización Físico-Métrica

Para evitar errores de conversión e inconsistencias lógicas entre submódulos, TODO parámetro introducido y calculado en `modelo.py` DEBE cumplir con las siguientes magnitudes:

1.  **Tiempo:** Se mide estrictamente en **Minutos** (`min`).
2.  **Volumen:** Se mide estrictamente en **Centímetros Cúbicos** (`cm3`).
3.  **Masa / Peso:** Se mide estrictamente en **Gramos** (`g`).
4.  **Distancia Espacial:** Se mide estrictamente en **Metros** (`m`).

## Uso Previsto

El archivo `modelo.py` define una función fabricadora de modelos: `crear_modelo_tdvrptw()`.
El flujo ideal desde las carpetas de negocio o de `algoritmo/` es instanciar la clase contenedora del modelo (`model`), inyectar en `$K$` la lista con la flota disponible para el día en análisis, rellenar los valores $Cv$, $Cm$, calcular la matriz transitoria en metros desde `grafo/` e inyectarlos localmente a Pyomo. 

*(Nota: debido a la altísima complejidad combinatoria de las variables $X_{itjk}$ , este modelo en lugar de ser resuelto con solvers ramificados formales (CBC, Gurobi) actuará como esquema base de fitness para el Algoritmo Genético y la Búsqueda Tabú)*.
