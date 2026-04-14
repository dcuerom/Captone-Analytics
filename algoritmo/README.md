# 🧠 Módulo `algoritmo/` — Metaheurísticas VRP

Esta carpeta conforma la capa superior de orquestación y optimización metaheurística del proyecto. Su rol dentro del pipeline general es servir de "cerebro" para encontrar soluciones casi-óptimas al problema complejo NP-Hard del ruteo de vehículos con ventanas de tiempo dependientes del tiempo (TDVRPTW).

## Arquitectura de la Solución

La lógica de resolución no se basa en un simple algoritmo, sino en una arquitectura híbrida de varias capas:

### 1. Inicialización Heurística (Semilla)
Antes de iniciar la evolución, el sistema utiliza la **Heurística de Ahorros de Clarke-Wright** (`savings.py`). Esto genera una solución inicial razonable basada en la cercanía y ahorro de distancia, la cual se inyecta en la población inicial del Algoritmo Genético para acelerar la convergencia hacia zonas de alta calidad.

### 2. Motor de Evolución (Algoritmo Genético)
Utilizamos la librería **PyMoo** para ejecutar un GA basado en permutaciones:
- **Cromosoma:** Una secuencia de IDs de clientes.
- **Sampling:** `SavingsSeededSampling` (Mezcla de semilla Clarke-Wright + aleatoriedad).
- **Cruce (Crossover):** `OrderCrossover (OX)`, diseñado para mantener la estructura de secuencias en problemas de ruteo.
- **Mutación:** `InversionMutation`, que invierte sub-secuencias para explorar nuevas rutas.

### 3. Decodificador Greedy Split (Evaluación)
Para transformar una secuencia de clientes en métricas reales (`F` y `G` de PyMoo), el evaluador en `modelo/pymoo_problem.py` realiza un recorrido voraz:
- **Agrupación en Rutas:** Lee los clientes uno por uno y los asigna a un camión. Si se supera la capacidad volumétrica, de peso, o el tiempo máximo de conducción (300 min), el camión retorna a la base y se inicia una nueva ruta.
- **Dependencia del Tiempo:** Cada traslado calcula su duración asimétrica basándose en la hora exacta de salida mediante el módulo de tráfico.

### 4. Optimización Dinámica de Salida (Novedad)
A diferencia de modelos rígidos donde los camiones salen a una hora fija, este motor incluye **Elección Dinámica del Tiempo de Salida**:
- Al cerrar cada ruta, el evaluador realiza un muestreo de salida cada 15 minutos dentro de la ventana permitida del turno (ej. [09:00 - 12:00]).
- Se selecciona automáticamente el minuto de salida que minimice el costo combinado de combustible y penalización por tiempo de espera del conductor.

### 5. Procesamiento Paralelo
Dado que Santiago se divide en múltiples clústeres, el sistema utiliza un `ProcessPoolExecutor` para lanzar optimizaciones independientes en todos los núcleos del procesador disponibles, permitiendo resolver toda la ciudad en minutos.

---

## Archivos Principales

- **`genetic_algorithm.py`**: El orquestador que une la geocodificación, el clustering, las matrices A* y el GA.
- **`savings.py`**: Implementación de la heurística de ahorros para seeding.
- **`ga_vrp.py`**: Entorno de experimentación para modelos multi-objetivo (NSGA-II).

---

## Flujo de Trabajo (Resumen)
1. **Datos:** Carga de pedidos y geocodificación.
2. **Espacio:** Generación de matriz de distancias real sobre grafo vial.
3. **Evolución:** El GA genera permutaciones.
4. **Rescate:** `_optimizar_salida_ruta` ajusta los tiempos de salida de cada camión.
5. **Reporte:** El `Gestor Flota` consolida los viajes en vehículos físicos reales.
