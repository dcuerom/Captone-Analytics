# Informe Técnico: Construcción del Pipeline de Optimización para el Problema de Ruteo de Vehículos Dependiente del Tiempo con Ventanas de Tiempo (TDVRPTW)

**Proyecto:** Capstone Analytics  
**Repositorio:** `Captone-Analytics`  
**Fecha:** Abril 2026  

---

## Tabla de Contenidos

1. [Introducción y Formulación del Problema](#1-introducción-y-formulación-del-problema)
2. [Estrategia de Solución](#2-estrategia-de-solución)
   - 2.1 [Paradigma Cluster-First, Route-Second](#21-paradigma-cluster-first-route-second)
   - 2.2 [Clusterización Geo-Temporal con DBSCAN](#22-clusterización-geo-temporal-con-dbscan)
   - 2.3 [Heurística Constructiva de Ahorros (Clarke-Wright)](#23-heurística-constructiva-de-ahorros-clarke-wright)
   - 2.4 [Metaheurística: Algoritmo Genético Híbrido (PyMoo)](#24-metaheurística-algoritmo-genético-híbrido-pymoo)
   - 2.5 [Modelamiento de Tiempos de Viaje Variables](#25-modelamiento-de-tiempos-de-viaje-variables)
   - 2.6 [Gestión Global de Flota Fija](#26-gestión-global-de-flota-fija)
3. [Estructura del Código: Módulos y Composición](#3-estructura-del-código-módulos-y-composición)
   - 3.1 [Módulo `grafo/`](#31-módulo-grafo)
   - 3.2 [Módulo `modelo/`](#32-módulo-modelo)
   - 3.3 [Módulo `algoritmo/`](#33-módulo-algoritmo)
   - 3.4 [Módulo `gestion_flota/`](#34-módulo-gestion_flota)
   - 3.5 [Módulo `resultados/`](#35-módulo-resultados)
   - 3.6 [Módulo `pruebas_sensibilidad/`](#36-módulo-pruebas_sensibilidad)
4. [Principales Aciertos del Planteamiento](#4-principales-aciertos-del-planteamiento)
5. [Principales Desaciertos del Planteamiento](#5-principales-desaciertos-del-planteamiento)
6. [Conclusiones](#6-conclusiones)

---

## 1. Introducción y Formulación del Problema

El presente informe documenta la construcción de un pipeline computacional para resolver el **Problema de Ruteo de Vehículos Dependiente del Tiempo con Ventanas de Tiempo** (TDVRPTW, por sus siglas en inglés). Este problema extiende el clásico VRP al incorporar dos dimensiones adicionales de complejidad: la variación temporal de las velocidades de tránsito y la presencia de restricciones de entrega en intervalos horarios definidos (ventanas de tiempo) por cada cliente.

El escenario operativo modela la distribución logística de última milla en el Área Metropolitana de Santiago, Chile. Los pedidos provienen del archivo `DatosSimulados/df_despacho.csv`, que contiene información de clientes, volúmenes, pesos y ventanas de tiempo. La flota es heterogénea en turnos pero homogénea en capacidades físicas, y opera desde un depósito central ubicado en la comuna de San Miguel.

### Restricciones formales del problema

El pipeline resuelve de manera integrada las siguientes restricciones:

- **Restricciones de capacidad:** Cada vehículo tiene límites estrictos de volumen (3.750.000 cm³) y peso (803.333 g) por turno de operación.
- **Ventanas de tiempo suaves:** Cada cliente tiene una ventana `[a_i, b_i]` con una holgura de ±15 minutos en ambos extremos, penalizando pero no forzando el incumplimiento en la función objetivo.
- **Duración máxima de turno:** Ningún camión puede operar más de 240 minutos por jornada (turno).
- **Tiempos de viaje variables:** El tiempo de tránsito entre nodos se calcula en función de la hora de salida y el día de la semana, siguiendo el modelo de Fleischmann et al. (2004).
- **Flota fija global:** El número de vehículos disponibles es un parámetro configurable. Los bloques de ruta que excedan esta capacidad se reportan como demanda tercerizable.
- **Multi-turno:** Un mismo vehículo físico puede operar en un turno matutino y uno vespertino, con al menos 120 minutos de descanso entre ellos.

---

## 2. Estrategia de Solución

### 2.1 Paradigma Cluster-First, Route-Second

La estrategia fundamental adoptada es el paradigma **Cluster-First, Route-Second**, ampliamente estudiado en la literatura de VRP (Fisher y Jaikumar, 1981). Este enfoque descompone el problema original —que es NP-duro en su forma general— en dos etapas secuenciales de menor complejidad:

1. **Etapa de clusterización:** Se agrupan los clientes en subconjuntos geográfica y temporalmente coherentes, de modo que cada subconjunto pueda ser resuelto de forma independiente.
2. **Etapa de ruteo:** Cada subconjunto (clúster) se resuelve como un subproblema VRP de escala reducida mediante un algoritmo genético.

Esta descomposición transforma un problema de escala global con N clientes en K subproblemas de escala local con N/K clientes aproximadamente, reduciendo la explosión combinatoria de forma sustancial.

### 2.2 Clusterización Geo-Temporal con DBSCAN

La etapa de clusterización emplea el algoritmo **DBSCAN** (Density-Based Spatial Clustering of Applications with Noise), implementado en el módulo `grafo/clustering.py`. A diferencia de K-Means, DBSCAN no requiere especificar el número de clústers a priori, identifica automáticamente regiones de alta densidad y trata los puntos aislados como ruido (outliers).

La dimensión del espacio de agrupación es tridimensional: latitud, longitud y hora de inicio de la ventana de tiempo del cliente (`a_ventana`, expresada en minutos desde la medianoche). Esta tercera dimensión temporal es clave: clientes geográficamente cercanos pero con ventanas de tiempo incompatibles no deben pertenecer al mismo clúster, pues forzarían esperas excesivas al vehículo.

El proceso sigue el siguiente flujo interno:

1. **Construcción de la matriz de características** (`build_feature_matrix`): Se genera una matriz N×3 con [Latitud, Longitud, Tiempo_Ventana].
2. **Normalización y ponderación** (`normalize_and_weight`): Se aplica `StandardScaler` para estandarizar las unidades. La dimensión temporal se pondera con factor `alpha_time = 7.0`, reforzando la cohesión temporal sobre la espacial.
3. **Ejecución de DBSCAN** (`run_dbscan`): Con parámetros `eps = 0.3` y `min_samples = 3`.
4. **Gestión de ruido** (`manage_clusters_and_noise`): Los outliers se reasignan al clúster más cercano en el espacio normalizado. Si `force_rescue = True`, ningún cliente queda sin asignación.
5. **Generación de pares para A*** (`generate_astar_inputs`): Se construyen todos los pares origen-destino dentro de cada clúster para el posterior cálculo de matrices de distancia.

### 2.3 Heurística Constructiva de Ahorros (Clarke-Wright)

Antes de ejecutar el algoritmo genético, se genera una **solución inicial de alta calidad** mediante la heurística de Ahorros de Clarke y Wright (1964), implementada en `algoritmo/savings.py`. Esta es una heurística constructiva que parte de la solución trivial (un vehículo por cliente) y la mejora iterativamente fusionando rutas cuando el ahorro en distancia así lo justifica.

El ahorro de fusionar los clientes i y j se define como:

```
S(i, j) = D(depot, i) + D(j, depot) - D(i, j)
```

Los pares se ordenan de mayor a menor ahorro y se fusionan si no violan las restricciones de capacidad volumétrica, de peso y de duración máxima del turno. El resultado es una permutación de clientes que constituye la **semilla inicial** del cromosoma del algoritmo genético.

El rol de esta heurística en el pipeline es estratégico: al incrustar una solución constructiva factible en la primera posición de la población inicial del GA, se acelera la convergencia y se reduce el riesgo de infactibilidad en clústeres con ventanas de tiempo restrictivas.

### 2.4 Metaheurística: Algoritmo Genético Híbrido (PyMoo)

El núcleo de la resolución por clúster es un **Algoritmo Genético (GA)** de permutaciones, orquestado mediante la librería `PyMoo` (Blank y Deb, 2020). El diseño es el de un **algoritmo memético**: la heurística constructiva de Clarke-Wright actúa como mecanismo de inicialización inteligente, y el GA itera sobre esa base para mejorar la solución.

Las componentes del GA implementado son:

- **Representación:** Cromosoma de permutación entera de longitud N (número de clientes del clúster), donde cada gen es el índice del cliente en la secuencia de visitas.
- **Inicialización:** Clase `SavingsSeededSampling`, que inyecta la permutación de Clarke-Wright como primer individuo de la población. El resto se genera aleatoriamente.
- **Operador de cruce:** `OrderCrossover` (OX), preserva el orden relativo de un subconjunto de genes del primer padre y rellena con el orden del segundo.
- **Operador de mutación:** `InversionMutation` con probabilidad 0.3, invierte subsegmentos aleatorios de la permutación.
- **Tamaño de población:** Configurable (por defecto 200 individuos).
- **Criterio de terminación:** Número fijo de generaciones (por defecto 500).

El problema se formula como `ElementwiseProblem` de PyMoo:
- **Función objetivo F:** Minimización del costo total compuesto = distancia total acumulada × factor servicio + costo fijo por vehículo utilizado + penalización por tiempo de espera.
- **Restricción G:** Suma de minutos de violación de ventana de tiempo en todos los clientes del clúster. El GA solo acepta como factibles las soluciones con G ≤ 0.

En caso de no encontrar ninguna solución factible en el número de generaciones asignado, el sistema ejecuta un **mecanismo de rescate**: extrae el individuo con menor violación de restricciones de la población final y lo reporta explícitamente como infactible, evitando que el clúster quede sin resolver.

La ejecución de los clústeres es **paralela** mediante `ProcessPoolExecutor`, utilizando como máximo la mitad de los núcleos disponibles del sistema para mantener estabilidad de memoria.

### 2.5 Modelamiento de Tiempos de Viaje Variables

El componente diferenciador del modelo frente a un VRP estándar es la función de tiempos de viaje dependiente del tiempo. Se implementa la formulación matemática de **Fleischmann, Gietz y Gnutzmann (2004)**, especificada en el módulo `modelo/funciones/tiempos_viaje.py`.

El horizonte de planificación es `[09:00, 21:00]`, dividido en K = 13 intervalos de 60 minutos. Para cada intervalo k y día de la semana d, se define una velocidad media `v_{k,d}` en km/h, almacenada en la tabla `SPEED_TABLE_KMH` (24 filas × 7 columnas).

El tiempo de viaje para un arco de distancia `d_ij` metros con partida en el instante `t` se calcula como:

```
tau_ij(t) = tau_ijk                                    (zona estable del intervalo k)
tau_ij(t) = tau_ijk + (t - z_k + delta) * s_ijk        (zona de transición derecha)
tau_ij(t) = tau_{ij,k-1} + (t - z_{k-1} + delta) * s_{ij,k-1}  (zona de transición izquierda)
```

donde `delta = 15 min` es el parámetro de suavizado en las fronteras entre intervalos y `s_ijk` es la pendiente de transición. Esta linealización garantiza la continuidad de la función y evita discontinuidades que perturbarían la evaluación del GA.

La función vectorizada `tau_ij_vec` opera directamente sobre arrays de NumPy, siendo la versión utilizada dentro del evaluador del GA para mantener eficiencia computacional.

### 2.6 Gestión Global de Flota Fija

Una vez que el GA entrega las rutas óptimas por clúster, existe un nivel superior de decisión que el módulo `gestion_flota/gestor.py` resuelve mediante un **algoritmo greedy de empaquetamiento**:

Los bloques de ruta (sub-rutas con su horario de salida y retorno) se ordenan cronológicamente y se asignan a los vehículos de la flota fija siguiendo las siguientes reglas:
1. Un vehículo solo absorbe un bloque si su turno no se superpone con el bloque previo asignado a ese vehículo (respetando 120 minutos de descanso).
2. Un vehículo no puede mezclar plantillas de turno (K1: mañana-tarde fijo, K2: media mañana - noche).
3. No puede repetir el mismo sub-turno (p.ej., dos turnos K11 en el mismo vehículo).

Los bloques que no pueden ser absorbidos por la flota fija se registran como **huérfanos** (candidatos a tercerización).

---

## 3. Estructura del Código: Módulos y Composición

El repositorio está organizado en módulos funcionales desacoplados, cada uno con responsabilidades claramente delimitadas. La estructura general es la siguiente:

```
Captone-Analytics/
├── algoritmo/
│   ├── genetic_algorithm.py
│   └── savings.py
├── grafo/
│   ├── main.py
│   ├── clustering.py
│   ├── geocoder.py
│   ├── network_builder.py
│   ├── routing.py
│   └── visualizer.py
├── modelo/
│   ├── pymoo_problem.py
│   ├── modelo.py
│   ├── vrp_pymoo.py
│   └── funciones/
│       └── tiempos_viaje.py
├── gestion_flota/
│   └── gestor.py
├── resultados/
│   ├── rutas/
│   └── mapa_rutas/
├── pruebas_sensibilidad/
│   ├── ejecutor_instancias.py
│   ├── analisis_sensibilidad.py
│   └── escenarios_prueba.md
└── DatosSimulados/
    └── df_despacho.csv
```

### 3.1 Módulo `grafo/`

Este módulo constituye la **capa geo-matemática** del pipeline. Es el único responsable de transformar direcciones textuales en métricas de distancia reales sobre la red vial de Santiago.

#### `grafo/main.py` — Orquestador de la Capa Geográfica

Función principal: `execute_vrp_pipeline(input_file, depot_address, sample_size)`

Ejecuta en secuencia los seis pasos de preparación espacial:
1. Carga y normalización del archivo de pedidos.
2. Geocodificación de pedidos.
3. Geocodificación del depósito.
4. Clustering Cluster-First.
5. Carga del grafo de red vial.
6. Cálculo de matrices de distancia por clúster en paralelo.

Retorna: `(matrices_por_cluster, rutas_por_cluster, G, depot_coords)`

#### `grafo/geocoder.py` — Geocodificación de Direcciones

Funciones: `geocode_orders(df)`, `geocode_depot(address)`

Traduce las direcciones textuales del CSV a coordenadas geográficas (latitud, longitud) mediante la API ArcGIS a través de la librería `geopy`. Implementa un sistema de caché por dirección única para minimizar el número de llamadas externas y un `RateLimiter` para respetar los límites de la API.

#### `grafo/network_builder.py` — Carga del Grafo Vial

Responsable de cargar el grafo dirigido de la red de calles de Santiago desde un archivo `.graphml` pre-descargado con OSMnx. El grafo contiene los pesos de los arcos en metros (`weight='length'`).

#### `grafo/clustering.py` — Agrupación Geo-Temporal

Funciones principales: `run_clustering_pipeline(df, depot_id, ...)`

Implementa el pipeline completo de DBSCAN en cinco etapas internas (construcción de características, normalización, DBSCAN, gestión de ruido y generación de pares para A*). Cada etapa es una función independiente y testeable.

#### `grafo/routing.py` — Matrices de Distancia con A*

Función: `calculate_routing_for_day(df_day, G)`

Para cada clúster, calcula la matriz N×N de distancias en metros mediante Dijkstra radial desde cada nodo único de origen. El paso clave de optimización es que **no se ejecuta A* para cada par O-D individualmente**, sino una expansión Dijkstra completa desde cada nodo fuente, filtrando únicamente los destinos pertenecientes al clúster. Esto reduce la complejidad de O(N²) llamadas a A* a O(N) expansiones Dijkstra con lookup O(1).

#### `grafo/visualizer.py` — Visualización Interactiva

Genera mapas HTML interactivos con Folium mostrando los clústeres resultantes y, posteriormente, las rutas asignadas por vehículo con el detalle de ventanas de tiempo y estados de cumplimiento.

---

### 3.2 Módulo `modelo/`

Este módulo define la **formulación matemática del problema** de optimización tal como lo entiende PyMoo.

#### `modelo/pymoo_problem.py` — Definición del Problema TDVRPTW

Clase: `TDVRPTWProblem(ElementwiseProblem)`

Es el núcleo analítico del pipeline. Hereda de `ElementwiseProblem` de PyMoo, lo que implica que el evaluador `_evaluate(x, out)` es llamado individuo por individuo durante la evolución del GA.

**Constructor:** Inicializa los diccionarios de demandas (volumen, peso) y ventanas de tiempo (`a_dict`, `b_dict`) a partir del DataFrame del clúster. Configura los parámetros del problema: capacidades, duración máxima del turno, factor de servicio y parámetros de penalización.

**Evaluador `_evaluate`:** Recibe un cromosoma de permutación `x`, simula la ejecución de la ruta completa siguiendo el orden propuesto y calcula:
- La distancia total recorrida.
- El tiempo de llegada a cada cliente usando `tau_ij_vec`.
- La espera acumulada si el vehículo llega antes de la apertura de la ventana.
- La violación de ventana si el inicio de servicio excede el cierre relajado `b_i + 15 min`.
- La activación de nuevos vehículos ante violaciones de capacidad o duración de turno (lógica de split).
- La lógica JIT (Just-In-Time): retrasa la salida del depósito si llegar demasiado temprano generaría espera en el primer nodo.

**Función objetivo F:**
```
F = (distancia_total × factor_s) + (num_camiones × costo_fijo) + (alpha_espera × espera_total)
```

**Restricción G:**
```
G = suma de minutos de violación de ventana de tiempo en todos los clientes
```

**Lógica de ventanas suaves:** Se aplica una holgura de 15 minutos en ambos extremos de cada ventana de cliente, conforme a la política operativa del negocio.

**Plantillas de turno multi-viaje (K11, K12, K21, K22):** El modelo permite que un mismo vehículo físico realice un segundo turno de entregas dentro del mismo día, con un descanso mínimo de 120 minutos entre el retorno del primer turno y la salida del segundo.

#### `modelo/funciones/tiempos_viaje.py` — Tiempos de Viaje Dependientes del Tiempo

Implementa la función de tiempo de viaje de Fleischmann et al. (2004) en dos versiones:
- `tau_ij(distancia_m, t, dia_semana)`: versión escalar para cálculos puntuales.
- `tau_ij_vec(distancia_m, t, dia_semana)`: versión vectorizada sobre arrays NumPy, utilizada en el evaluador del GA.

Contiene además la tabla de velocidades `SPEED_TABLE_KMH` (24 horas × 7 días), que codifica los perfiles de tráfico urbano de Santiago para cada hora del día y día de la semana. También incluye las funciones `distancia_a_tiempo_matrix` y `matrices_distancia_a_tiempo` para convertir matrices de distancia en matrices de tiempo de viaje para un instante y día dados.

---

### 3.3 Módulo `algoritmo/`

Este módulo es el **punto de entrada principal** del pipeline de optimización y contiene la lógica de orquestación del algoritmo genético.

#### `algoritmo/savings.py` — Heurística de Clarke-Wright

Funciones: `calcular_ahorros(df_cluster, matriz_dist, depot_id)`, `clarke_wright_savings(...)`

Implementa la heurística constructiva de ahorros completa. Parte de la estructura de una ruta por cliente, calcula la matriz de ahorros para todos los pares (i, j) y fusiona rutas en orden decreciente de ahorro, validando en cada paso las restricciones de volumen, peso y duración estimada de turno.

El resultado es una lista ordenada de clientes (permutación) que representa la mejor solución constructiva encontrada por la heurística greedy.

#### `algoritmo/genetic_algorithm.py` — Orquestador del GA y del Pipeline

Clases: `SavingsSeededSampling(Sampling)`  
Funciones: `optimizar_pymoo_ga(...)`, `disparar_rutina_ga(...)`

**`SavingsSeededSampling`:** Operador de muestreo personalizado para PyMoo que inyecta la permutación de Clarke-Wright como primer individuo de la población, generando el resto aleatoriamente.

**`optimizar_pymoo_ga`:** Para un clúster dado, instancia el `TDVRPTWProblem`, ejecuta Clarke-Wright para obtener la semilla, configura el GA con los operadores OX e InversionMutation, y llama a `pymoo.optimize.minimize`. En caso de infactibilidad, aplica el mecanismo de rescate descrito en la sección 2.4.

**`disparar_rutina_ga`:** Función de alto nivel que actúa como punto de entrada. Filtra el dataset por fecha objetivo, llama al pipeline geográfico (`execute_vrp_pipeline`), distribuye los clústeres entre los workers paralelos mediante `ProcessPoolExecutor`, y finalmente llama al gestor de flota global (`asignar_y_reportar`).

---

### 3.4 Módulo `gestion_flota/`

Este módulo resuelve el **problema de asignación de bloques de ruta a una flota fija**.

#### `gestion_flota/gestor.py` — Gestor de Flota Global

Clases: `BloqueRuta`, `VehiculoGlobal`  
Función principal: `asignar_y_reportar(...)`

**`BloqueRuta`:** Encapsula una sub-ruta optimizada por el GA junto con sus metadatos temporales (hora de salida, hora de retorno, plantilla de turno).

**`VehiculoGlobal`:** Representa un vehículo físico con su historial de bloques asignados. El método `puede_absorber(bloque)` implementa las tres reglas de asignación: homogeneidad de plantilla de turno, unicidad de sub-turno y separación temporal mínima de 120 minutos.

**`asignar_y_reportar`:** Orquesta todo el flujo de post-procesamiento:
1. Recolección de bloques de ruta desde todos los clústeres.
2. Ordenamiento por hora de salida (Earliest Departure First).
3. Asignación greedy a vehículos de la flota fija.
4. Generación de cuatro archivos CSV de salida: resumen por camión, detalle de paradas, KPIs globales y clientes atendidos.
5. Generación del mapa HTML interactivo global.

Los KPIs calculados incluyen: función objetivo total, distancia total, porcentaje de entregas a tiempo, utilización de capacidad (volumen y peso), emisiones estimadas de CO2, tiempo de cómputo y tasa de desocupación, entre otros.

---

### 3.5 Módulo `resultados/`

Directorio de salida que almacena los artefactos generados por cada ejecución del pipeline:
- `rutas/`: Archivos CSV con el detalle de rutas (`detalle_paradas_*.csv`), resumen por camión (`resumen_camiones_*.csv`), KPIs (`kpis_*.csv`) y clientes atendidos (`clientes_atendidos_*.csv`).
- `mapa_rutas/`: Mapas HTML interactivos generados con Folium para visualización geográfica de clústeres y rutas asignadas.

---

### 3.6 Módulo `pruebas_sensibilidad/`

Contiene la infraestructura para validación experimental del pipeline bajo distintos escenarios de estrés logístico.

#### `pruebas_sensibilidad/ejecutor_instancias.py`

Ejecuta el pipeline completo para cuatro fechas distintas del dataset, variando la distribución de ventanas de tiempo para evaluar la robustez del sistema bajo condiciones de alta demanda matutina, distribución uniforme, alta demanda vespertina y mezcla estocástica.

#### `pruebas_sensibilidad/analisis_sensibilidad.py`

Consolida los resultados de las distintas ejecuciones y genera el reporte comparativo `reporte_sensibilidad.md`.

#### `pruebas_sensibilidad/escenarios_prueba.md`

Documenta los cuatro escenarios de prueba definidos, con sus fechas objetivo, configuraciones de ventanas de tiempo y objetivos de validación.

---

## 4. Principales Aciertos del Planteamiento

### 4.1 Descomposición modular con responsabilidades únicas

La organización del código en módulos con responsabilidades claramente delimitadas (`grafo/`, `modelo/`, `algoritmo/`, `gestion_flota/`) es quizás el acierto arquitectónico más relevante del proyecto. Cada módulo puede ser entendido, modificado y probado de forma independiente. Esta separación respeta el principio de responsabilidad única (SRP) y facilita la mantenibilidad del sistema a largo plazo.

### 4.2 Separación entre datos y lógica

Los datos operativos (pedidos, coordenadas) residen exclusivamente en `DatosSimulados/df_despacho.csv` y son inyectados al pipeline como parámetro. Los parámetros de configuración del algoritmo (tamaño de población, número de generaciones, capacidades de flota, holgura de ventanas) se pasan como argumentos de función, no están embebidos en la lógica del evaluador. Esto permite realizar análisis de sensibilidad sin modificar código fuente.

### 4.3 Paradigma híbrido memético (constructiva + metaheurística)

La integración de Clarke-Wright como mecanismo de warm-start para el algoritmo genético representa un acierto metodológico significativo. Las heurísticas constructivas generan soluciones factibles rápidamente pero quedan atrapadas en óptimos locales; los algoritmos genéticos escapan de óptimos locales pero sin buena inicialización convergen lentamente. La combinación de ambos aprovecha las fortalezas de cada enfoque.

### 4.4 Modelamiento de tiempos de viaje dependientes del tiempo

La implementación de la función de Fleischmann et al. (2004) con linealización en las fronteras de intervalos es técnicamente rigurosa. La función `tau_ij_vec` vectorizada permite evaluar miles de individuos del GA con eficiencia computacional comparable a la de operaciones matriciales en NumPy.

### 4.5 Clusterización tridimensional geo-temporal

La incorporación de la hora de apertura de ventana de tiempo como tercera dimensión del espacio de clustering es una decisión de diseño acertada. Garantiza que los clientes agrupados en un mismo clúster sean compatibles no solo en términos de proximidad geográfica, sino también en términos de compatibilidad temporal, lo que incrementa la probabilidad de factibilidad de las rutas generadas.

### 4.6 Optimización del cálculo de matrices de distancia

El reemplazo de N² llamadas a A* por N expansiones Dijkstra radiales con lookup O(1) en tabla hash reduce de manera significativa el tiempo de procesamiento de la capa geográfica. El filtrado de los resultados Dijkstra para retener únicamente los destinos del clúster (en lugar del grafo completo) previene desbordamientos de memoria (OOM) en instancias de gran escala.

### 4.7 Paralelización a nivel de clúster

La ejecución paralela de los clústeres mediante `ProcessPoolExecutor` con control de número de workers (limitado a la mitad de los núcleos disponibles) es un acierto tanto en eficiencia como en estabilidad del sistema. La inicialización del grafo OSMnx en cada proceso worker mediante `initializer=_init_worker` evita la serialización del objeto NetworkX a través de `pickle`, que resulta prohibitiva en tiempo y memoria.

### 4.8 Mecanismo de rescate ante infactibilidad

Cuando el GA no encuentra ningún individuo factible en el número de generaciones asignado, el sistema no falla silenciosamente ni detiene la ejecución. En su lugar, extrae el mejor individuo infactible de la población final (aquel con menor violación de restricciones) y lo reporta explícitamente. Este mecanismo garantiza que todos los clientes sean atendidos y que el operador logístico tenga visibilidad sobre qué clústers presentaron infactibilidades.

### 4.9 Gestión de flota con lógica de multi-turno y tercerización

La distinción entre bloques de ruta y vehículos físicos en el módulo `gestion_flota/` es una abstracción correcta del problema real. Un vehículo físico puede operar en múltiples bloques (turnos) durante el día, y el algoritmo greedy de asignación respeta las restricciones operacionales de descanso y unicidad de turno. Los bloques no asignables se reportan como candidatos a tercerización, lo que es coherente con la realidad operativa de la industria.

---

## 5. Principales Desaciertos del Planteamiento

### 5.1 Hiperparámetros de DBSCAN no calibrados automáticamente

Los parámetros `eps = 0.3` y `min_samples = 3` de DBSCAN están fijados manualmente en el código de `run_clustering_pipeline`. Estos valores fueron calibrados empíricamente para el dataset de prueba, pero no existe ningún mecanismo automático de selección (como el método del codo o la búsqueda en cuadrícula) que los ajuste cuando la densidad de pedidos o la distribución geográfica del día varía. En días con baja demanda, DBSCAN puede generar un único clúster masivo o numerosos outliers.

### 5.2 Ausencia de una representación de solución que preserve rutas múltiples

El cromosoma del GA es una permutación de todos los clientes del clúster, sin marcadores que separen sub-rutas (viajes distintos de un mismo vehículo). La asignación a sub-rutas se reconstruye dinámicamente en `_evaluate` siguiendo reglas de split por capacidad y duración. Esto implica que el operador de cruce OX no tiene información estructural sobre los límites de ruta, lo que puede generar soluciones infactibles frecuentes cuando hay muchos clientes con ventanas incompatibles en un mismo clúster.

### 5.3 Función de tiempo de viaje sin distinción por tipo de arco

La tabla de velocidades `SPEED_TABLE_KMH` es homogénea para toda la red vial: aplica la misma velocidad a autopistas, avenidas principales y calles secundarias. En un modelo más preciso, la función `tau_ij` debería incorporar el tipo de vía (atributo `highway` del grafo OSMnx) para calcular velocidades diferenciadas. Esta simplificación introduce sesgo en las estimaciones de tiempo de viaje en sectores con mezcla de tipos de vía.

### 5.4 Heurística de ahorros sin validación de ventanas de tiempo

La implementación de Clarke-Wright en `savings.py` valida restricciones de capacidad (volumen, peso) y duración total estimada del turno, pero **no evalúa la factibilidad de las ventanas de tiempo** al fusionar rutas. La complejidad de simular tiempos de llegada en la heurística constructiva justifica esta simplificación, pero implica que la semilla inicial puede ser infactible en clústeres con ventanas de tiempo muy restrictivas, lo que reduce su valor como warm-start para el GA.

### 5.5 Gestión greedy de flota sin optimización de la asignación

El algoritmo de asignación de bloques de ruta a vehículos físicos en `gestor.py` es estrictamente greedy: asigna cada bloque al primer vehículo disponible (en orden de ID). Este enfoque no garantiza la asignación óptima en cuanto a minimización del número de vehículos usados o maximización de la utilización de capacidad. Heurísticas como First-Fit Decreasing o formulaciones de bin-packing podrían reducir el número de vehículos necesarios.

### 5.6 Geocodificación sin mecanismo de persistencia entre ejecuciones

El módulo `geocoder.py` implementa un caché de coordenadas en memoria durante la ejecución actual, pero no persiste los resultados entre ejecuciones. Cada vez que se ejecuta el pipeline para una fecha nueva con pedidos que comparten direcciones con ejecuciones anteriores, se vuelven a consultar las coordenadas vía API. Un caché persistente en disco (por ejemplo, en la base de datos de `database/`) reduciría el tiempo de inicialización y los costos de API.

### 5.7 Criterio de terminación del GA fijo e independiente del tamaño del clúster

El número de generaciones del GA (por defecto 500) es un parámetro fijo que se aplica uniformemente a todos los clústeres, independientemente de su tamaño. Un clúster de 3 clientes requiere menos generaciones para converger que uno de 30 clientes. La ausencia de un criterio de terminación adaptativo (como la convergencia por estancamiento del fitness) resulta en tiempo de cómputo desigual entre clústeres y puede generar tanto convergencia prematura como sobreoptimización en clústeres pequeños.

### 5.8 Ausencia de validación de factibilidad inter-clúster

El pipeline garantiza factibilidad dentro de cada clúster de forma independiente, pero no verifica que la asignación global de bloques de ruta a vehículos sea factible en cuanto al cumplimiento de la demanda total diaria. Si el número de vehículos disponibles es insuficiente para absorber todos los bloques, los bloques huérfanos se reportan pero no se reoptimiza la asignación para minimizarlos.

---

## 6. Conclusiones

El pipeline construido constituye una solución técnicamente completa y funcional para el TDVRPTW en el contexto de la distribución de última milla en Santiago. La estrategia de descomposición Cluster-First, Route-Second, combinada con el enfoque híbrido memético (Clarke-Wright + GA PyMoo), permite abordar instancias de escala real con tiempos de cómputo razonables y con garantías de cobertura total de clientes.

Los mayores méritos del planteamiento residen en la rigurosidad del modelamiento matemático (función de tiempos de viaje de Fleischmann et al.), la correcta separación de responsabilidades entre módulos y la robustez operacional ante escenarios de infactibilidad. Las principales oportunidades de mejora están concentradas en la etapa de clusterización (calibración automática de hiperparámetros), la heurística constructiva (incorporación de validación de ventanas de tiempo) y el algoritmo de asignación de flota (reemplazo del enfoque greedy por una formulación de optimización).

La estructura modular del código facilita la incorporación de estas mejoras de forma iterativa sin necesidad de refactorizaciones globales, lo que representa una ventaja metodológica significativa para el desarrollo continuo del sistema.

---

## Referencias

- Blank, J. y Deb, K. (2020). Pymoo: Multi-objective optimization in Python. *IEEE Access*, 8, 89497-89509.
- Clarke, G. y Wright, J. W. (1964). Scheduling of vehicles from a central depot to a number of delivery points. *Operations Research*, 12(4), 568-581.
- Ester, M., Kriegel, H.-P., Sander, J. y Xu, X. (1996). A density-based algorithm for discovering clusters in large spatial databases with noise. *Proceedings of the 2nd International Conference on Knowledge Discovery and Data Mining (KDD-96)*, 226-231.
- Fisher, M. L. y Jaikumar, R. (1981). A generalized assignment heuristic for vehicle routing. *Networks*, 11(2), 109-124.
- Fleischmann, B., Gietz, M. y Gnutzmann, S. (2004). Time-varying travel times in vehicle routing. *Transportation Science*, 38(2), 160-173.
- Laporte, G. (2009). Fifty years of vehicle routing. *Transportation Science*, 43(4), 408-416.
- Toth, P. y Vigo, D. (Eds.). (2014). *Vehicle Routing: Problems, Methods, and Applications* (2nd ed.). SIAM.
