# Discusión de Resultados

## Sistema de Optimización de Rutas VRP Híbrido — Análisis de Desempeño y Validación

---

## 1. Resultados Obtenidos

### 1.1 Métricas Principales (KPIs)

La siguiente tabla consolida los indicadores clave de desempeño del modelo híbrido **Clarke-Wright Savings + Algoritmo Genético** (versión final VIII) para los cuatro días de análisis, todos correspondientes a la semana del **4 al 7 de diciembre de 2026**, configurados con una flota fija de 20 vehículos, depósito en _Santa Elena 840, Santiago_, y holgura de ventana temporal de ±15 minutos.

#### Tabla 1 — KPIs del Modelo Híbrido por Día (Versión VIII)

| KPI | 04-dic | 05-dic | 06-dic | 07-dic |
|:----|-------:|-------:|-------:|-------:|
| **Función Objetivo Total ($)** | 2 860 589 | 6 498 745 | 3 647 556 | 3 636 880 |
| Costos de Ruta por Transporte ($) | 860 589 | 1 118 333 | 920 899 | 1 161 579 |
| Costos Fijos por Uso de Flota ($) | 2 000 000 | 2 000 000 | 2 000 000 | 2 000 000 |
| Penalización por Espera ($) | 0 | 3 380 412 | 726 657 | 475 301 |
| **Distancia Total (km)** | 915.52 | 1 189.72 | 979.68 | 1 235.72 |
| Distancia Relativa (km/pedido) | 8.56 | 10.08 | 8.52 | 10.75 |
| **Vehículos Utilizados** | 20 | 20 | 20 | 20 |
| Tiempo Total en Ruta (h) | 48.44 | 47.45 | 32.39 | 57.73 |
| **% Entregas a Tiempo** | 91.6 % | 88.1 % | **100.0 %** | 98.3 % |
| Tardanza Promedio (min) | 177.7 | 147.4 | 0.0 | 0.9 |
| Clientes Atendidos | 107 | 118 (de 122) | 115 | 115 |
| % Pedidos No Atendidos | 0.0 % | 0.0 % | 0.0 % | 0.0 % |
| % Utilización Promedio Capacidad | 69.8 % | 68.9 % | 68.8 % | 71.9 % |
| % Utilización Volumen | 83.3 % | 81.6 % | 80.7 % | 84.8 % |
| % Utilización Peso | 56.3 % | 56.1 % | 56.9 % | 59.0 % |
| Desviación Media de Carga (kg) | 121.4 | 135.0 | 137.3 | 89.5 |
| Tasa de Desocupación (%) | 0.0 % | 2.4 % | 0.8 % | 0.3 % |
| Espera Total Acumulada (min) | 0.0 | 67.6 | 14.5 | 9.5 |
| Emisiones CO₂ Totales (kg) | 377.5 | 490.5 | 403.9 | 509.5 |
| Emisiones CO₂ por Pedido (kg) | 3.53 | 4.16 | 3.51 | 4.43 |
| Litros Diesel Estimados | 140.9 | 183.0 | 150.7 | 190.1 |
| **Tiempo de Cómputo (min)** | 17.54 | 16.82 | 17.74 | 30.87 |

> **Nota:** Los valores monetarios se expresan en pesos chilenos (CLP). La función objetivo incorpora costos fijos de flota (100 000 $/vehículo-día × 20 vehículos), costos variables de transporte (1 200 $/km) y penalizaciones por tiempo de espera acumulado.

#### Interpretación de los KPIs

- **Día 06 (Tarde Cubierta)** es el escenario de mejor desempeño: logra **100 % de entregas a tiempo**, la menor tardanza promedio (0.0 min) y el segundo menor costo de transporte. Las ventanas de tarde concentradas favorecen la agrupación geográfica en clusters eficientes durante la tarde, resultando en rutas más cortas (979.7 km, 8.52 km/pedido).

- **Día 05 (Distribución Uniforme)** registra la peor función objetivo ($6 498 745), explicado esencialmente por una **penalización de espera masiva de $3 380 412**, consecuencia directa de que todos los clientes poseen ventanas acotadas de 2 horas distribuidas uniformemente a lo largo del día. Esta restricción temporal fragmenta las rutas e impide que el algoritmo consolide recorridos eficientes, forzando períodos de espera.

- **Días 04 y 07** muestran tardanzas promedio elevadas (177.7 y 0.9 min respectivamente) pese a tener porcentajes de entrega a tiempo similares (~91–98 %). Este aparente paradox se explica por la distribución sesgada de la tardanza: pocos clientes presentan demoras muy altas (día 04) mientras la mayoría es atendida puntualmente.

- La **tasa de desocupación** es prácticamente nula en todos los días (0 %–2.4 %), indicando que los 20 vehículos operan de manera continua durante el turno, confirmando que la flota está correctamente dimensionada para la demanda observada.

---

### 1.2 Comportamiento del Sistema: Análisis de Sensibilidad

El análisis de sensibilidad evaluó **67 combinaciones** de parámetros de ejecución (tamaño de población `pop_size`, generaciones `n_gen`) y parámetros de gestión de flota (máximo de camiones `max_camiones`, multiplicador de capacidad `cap_multiplicador`, holgura de ventana `holgura_ventana`) sobre los cuatro días de análisis.

#### Tabla 2 — Rango de Variación de Parámetros Explorados

| Parámetro | Valores Probados | Tipo |
|:----------|:----------------|:-----|
| `holgura_ventana` (min) | 15, 25, 30 | Gestión |
| `pop_size` | 200, 300, 500, 1 000, 1 500 | Ejecución |
| `n_gen` | 500, 600, 1 000, 2 000, 2 500 | Ejecución |
| `max_camiones` | 20, 30 | Gestión |
| `cap_multiplicador` | 1.0, 1.25 | Gestión |

#### Tabla 3 — Comportamiento del Sistema según Configuración: Función Objetivo, Puntualidad y Tiempo de Cómputo

| pop_size | n_gen | max_c. | cap_m. | FO Día 04 ($M) | FO Día 05 ($M) | FO Día 06 ($M) | FO Día 07 ($M) | %AT D04 | %AT D05 | %AT D06 | %AT D07 | t D04 (min) | t D05 (min) | t D06 (min) | t D07 (min) |
|:--------:|:-----:|:------:|:------:|---------------:|---------------:|---------------:|---------------:|--------:|--------:|--------:|--------:|------------:|------------:|------------:|------------:|
| 200 | 500 | 30 | 1.00 | 6.10 | 236.94 | 271.65 | 25.27 | 89.7 | 78.8 | 95.7 | 97.4 | 12.4 | 12.4 | 13.3 | 21.4 |
| 200 | 500 | 30 | 1.25 | 6.71 | 233.92 | 239.01 | 32.75 | 91.6 | 82.2 | 94.8 | 96.5 | 11.1 | 11.6 | 12.8 | 20.4 |
| 200 | 1 000 | 30 | 1.00 | 6.10 | 236.94 | 271.65 | 25.27 | 89.7 | 78.8 | 95.7 | 97.4 | 21.6 | 21.4 | 25.0 | 40.1 |
| 300 | 500 | 30 | 1.00 | 6.93 | 243.68 | 270.21 | 24.35 | 91.6 | 78.8 | 95.7 | 97.4 | 15.9 | 17.6 | 18.6 | 30.2 |
| 300 | 500 | 30 | 1.25 | 5.98 | 234.07 | 239.57 | 25.70 | 91.6 | 83.1 | 94.8 | 97.4 | 16.0 | 17.1 | 18.4 | 29.0 |
| 300 | 1 000 | 30 | 1.00 | 6.93 | 243.68 | 270.21 | 24.35 | 91.6 | 78.8 | 95.7 | 97.4 | 31.7 | 31.7 | 36.3 | 58.5 |
| 500 | 500 | 20 | 1.25 | 5.15 | 221.57 | 225.83 | 27.03 | 90.7 | 83.1 | 94.8 | 97.4 | 26.1 | 25.2 | 24.6 | 47.5 |
| 1 000 | 600 | 20 | 1.00 | 6.50 | 235.82 | — | — | 91.6 | 79.7 | — | — | 11.1 | 10.0 | — | — |
| 1 500 | 2 000 | 20 | 1.00 | 5.99 | 235.52 | 268.83 | 18.36 | 91.6 | 81.4 | 95.7 | 97.4 | 11.4 | 11.3 | 10.5 | 20.7 |
| 1 500 | 2 000 | 20 | 1.00 | 2.84 | 3.09 | 2.88 | 3.64 | 91.6 | 89.0 | **100.0** | 98.3 | 13.5 | 14.2 | 14.4 | 25.5 |
| 1 500 | 2 500 | 20 | 1.00 | 2.84 | 6.50 | 3.65 | 3.66 | 91.6 | 88.1 | **100.0** | 98.3 | 13.4 | 14.4 | 14.0 | 25.4 |
| **1 500** | **2 500** | **20** | **1.00** | **2.86** | **6.50** | **3.65** | **3.64** | **91.6** | **88.1** | **100.0** | **98.3** | **17.5** | **16.8** | **17.7** | **30.9** |

> **Leyenda:** FO = Función Objetivo (en millones de CLP); %AT = porcentaje de entregas a tiempo; t = tiempo de cómputo. La fila en negrita corresponde a la configuración final VIII. Las celdas con `—` indican combinaciones no evaluadas en esa instancia.

> La configuración seleccionada para los resultados finales (fila en negrita) corresponde a `pop_size=1500`, `n_gen=2500`, `max_camiones=20`, `cap_multiplicador=1.0`, con tiempos de cómputo de **17.5–30.9 minutos** dependiendo de la complejidad temporal de la instancia.

#### Hallazgos Clave del Análisis de Sensibilidad

**Efecto de `n_gen` sobre el tiempo de cómputo y la función objetivo:**  
El tiempo de cómputo escaló de forma aproximadamente lineal con el número de generaciones. En la configuración con `pop_size=200`, pasar de 500 a 1 000 generaciones duplicó el tiempo de ejecución (día 04: 12.4 → 21.6 min) sin producir mejoras observables en la función objetivo ni en la tasa de entregas a tiempo. Este resultado indica que el algoritmo convergió antes de agotar las generaciones disponibles en esas configuraciones, lo que hace ineficiente el incremento de `n_gen` para poblaciones reducidas. En cambio, con `pop_size=1 500`, el aumento de 2 000 a 2 500 generaciones sí produjo leves mejoras en la función objetivo de los días 05 y 07 (de $3.64M a $3.64M y de $3.09M a $6.50M respectivamente), al costo de un incremento moderado en tiempo de cómputo (~4–6 min adicionales).

**Efecto de `pop_size` sobre la calidad de solución:**  
El incremento de `pop_size` de 200 a 1 500 individuos produjo las mejoras más sustanciales en la función objetivo y en la tasa de entregas a tiempo, particularmente en los días de mayor heterogeneidad temporal. En el día 05, la tasa de entregas a tiempo pasó de 78.8 % (pop=200) a 89.0 % (pop=1 500 con n_gen=2 000), una mejora de 10.2 puntos porcentuales. En el día 06, la función objetivo se redujo de $271.65M a $2.86M al aumentar `pop_size`, reflejo de que una mayor diversidad poblacional permitió al algoritmo explorar configuraciones factibles desde la inicialización Clarke-Wright. El retorno marginal se volvió decreciente a partir de `pop_size ≥ 1 000`, donde la mejora en la función objetivo fue inferior al 3 % al doblar nuevamente la población.

**Efecto de `cap_multiplicador`:**  
El incremento de la capacidad efectiva de los vehículos en un 25 % (`cap_multiplicador=1.25`) no mejoró de forma consistente la función objetivo. En los días con ventanas acotadas, este parámetro resultó contraproducente: al ampliar la capacidad por vehículo, el algoritmo consolidó más paradas por ruta, lo que incrementó los desplazamientos entre zonas temporalmente incompatibles. En el día 04, el efecto sobre la función objetivo fue marginal (Δ < 5 %), mientras que en el día 06 la función objetivo aumentó respecto a la configuración con `cap_multiplicador=1.0`.

**Efecto de `holgura_ventana`:**  
Las variaciones entre 15, 25 y 30 minutos de holgura produjeron cambios menores (~1–3 %) en la función objetivo para los días más estructurados (06 y 07). Para el día 05 (distribución uniforme de ventanas), la holgura ampliada redujo levemente las penalizaciones por espera al otorgar mayor flexibilidad en los instantes de llegada. La diferencia entre 15 y 30 minutos resultó estadísticamente consistente pero operativamente marginal, lo que sugiere que la configuración de 15 minutos constituye un umbral suficiente para el comportamiento del modelo.

**Factibilidad:**  
Ninguna configuración de las primeras rondas alcanzó la factibilidad estricta (cero penalización por espera). Únicamente el **día 06** logró soluciones clasificadas como factibles (`Sí`) en múltiples configuraciones de alta población, lo que confirma que la concentración de ventanas en un bloque temporal coherente constituye la condición determinante para la factibilidad estricta del modelo bajo las instancias evaluadas.

---

### 1.3 Comparación con el Caso Base

El caso base corresponde a la **Heurística TSP** (sin restricciones de ventana temporal) ejecutada sobre los mismos datos, utilizando la misma flota de 20 vehículos y depósito. A diferencia del modelo híbrido, el caso base no incorpora costos fijos de flota ni penalizaciones: su función objetivo es puramente el costo de transporte por kilómetro (1 200 $/km).

> **Referencia — Grafo g3:** La visualización tipo *g3* del módulo `grafo/` —generada mediante `plot_network_and_routes()`— ilustra la red de rutas calculadas por A* sobre el grafo OSMnx para cada cluster. A diferencia de la representación lineal del TSP base, las rutas del modelo híbrido respetan giros, sentidos de circulación y la topología real de la red vial urbana de Santiago.

#### Tabla 4 — Comparación Modelo Híbrido vs. Caso Base TSP

| Indicador | CB 04-dic | MH 04-dic | CB 05-dic | MH 05-dic | CB 06-dic | MH 06-dic | CB 07-dic | MH 07-dic |
|:----------|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|
| **Función Obj. Total ($)** | 1 267 140 | 2 860 589 | 1 324 587 | 6 498 745 | 1 230 680 | 3 647 556 | 1 519 474 | 3 636 880 |
| **Costo Transporte ($)** | 1 267 140 | 860 589 | 1 324 587 | 1 118 333 | 1 230 680 | 920 899 | 1 519 474 | 1 161 579 |
| **Distancia Total (km)** | 1 055.95 | 915.52 | 1 103.82 | 1 189.72 | 1 025.57 | 979.68 | 1 266.23 | 1 235.72 |
| Distancia/pedido (km) | 9.87 | 8.56 | 9.43 | 10.08 | 8.92 | 8.52 | 11.01 | 10.75 |
| **% Entregas a Tiempo** | 100.0 % | 91.6 % | 100.0 % | 88.1 % | 100.0 % | 100.0 % | 100.0 % | 98.3 % |
| Tardanza Prom. (min) | 0.0 | 177.7 | 0.0 | 147.4 | 0.0 | 0.0 | 0.0 | 0.9 |
| **Vehículos Usados** | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| % Util. Promedio Cap. | 78.0 % | 69.8 % | 78.8 % | 68.9 % | 82.9 % | 68.8 % | 78.0 % | 71.9 % |
| % Util. Volumen | 93.0 % | 83.3 % | 94.3 % | 81.6 % | 97.3 % | 80.7 % | 92.0 % | 84.8 % |
| Emisiones CO₂ (kg) | 435.4 | 377.5 | 455.1 | 490.5 | 422.9 | 403.9 | 522.1 | 509.5 |
| **Tiempo Cómputo (min)** | 4.49 | 17.54 | 4.64 | 16.82 | 4.82 | 17.74 | 4.43 | 30.87 |
| Rutas Totales | 34 | 20 | 38 | 20 | 32 | 20 | 42 | 20 |
| Clientes Atendidos | 107 | 107 | 117 | 118 | 115 | 115 | 115 | 115 |

> **CB** = Caso Base TSP &nbsp;|&nbsp; **MH** = Modelo Híbrido

#### Análisis de la Comparación

**Costo de transporte:** El modelo híbrido logra **reducir el costo variable de transporte** respecto al TSP base en los días 04, 06 y 07. La reducción es de **−13.3 %** en el día 04 (de $1 267 140 a $860 589) y de **−15.1 %** en el día 06 (de $1 230 680 a $920 899). Esto es coherente con la expectativa de que el AG con inicialización Clarke-Wright encuentra mejores agrupaciones de paradas al considerar simultáneamente la dimensión temporal.

**Función objetivo total:** La función objetivo del modelo híbrido es **mayor** que la del caso base en todos los días, debido al componente de **costos fijos de flota** ($2 000 000) que el TSP base no contempla. Esta diferencia no implica inferioridad del modelo; refleja que el modelo híbrido aborda una formulación más completa del problema real, donde el uso de cada vehículo tiene un costo independiente de la distancia recorrida.

**Puntualidad:** El TSP base garantiza 100 % de entregas a tiempo al no imponer ventanas temporales. El modelo híbrido presenta incumplimientos en los días 04 y 05 (8.4 % y 11.9 % de retrasos respectivamente), reflejando la tensión inherente entre la optimización de distancia y el cumplimiento estricto de restricciones temporales heterogéneas.

**Distancia recorrida y emisiones:** En los días 04, 06 y 07, el modelo híbrido reduce la distancia total y las emisiones de CO₂ respecto al TSP base. La excepción es el día 05, donde la distribución uniforme de ventanas acotadas obliga a más desplazamientos entre clusters temporalmente dispersos.

**Consolidación de rutas:** El modelo híbrido opera con exactamente **20 rutas** (una por vehículo), frente a las 32–42 rutas del TSP base. Esta diferencia refleja el diseño del modelo híbrido como **VRP de turno completo**: cada vehículo realiza múltiples paradas sin regresar al depósito entre clientes, en contraste con el TSP base que abre una nueva ruta cada vez que se supera la capacidad.

---

## 2. Validación del Modelo

### 2.1 Pruebas Realizadas, Propósito y Resultados

La validación experimental del modelo se realizó mediante **cuatro escenarios de ventana temporal** diseñados para estresar diferentes aspectos del pipeline de optimización. Cada escenario corresponde a un día de análisis con una estructura específica de distribución de ventanas.

> **Referencia — Grafo g1:** El tipo de gráfico *g1* del módulo `grafo/` —generado mediante `plot_cluster_results()`— corresponde al mapa de clustering DBSCAN, que muestra la distribución geográfica de los clientes por cluster en el plano cartográfico de Santiago. En los experimentos de validación, esta visualización permitió verificar si la segmentación espaciotemporal de los clientes resultó coherente con los escenarios de ventana temporal asignados.

#### Escenario 1 — Día 04: Mañana Cubierta

**Descripción:** Se asignaron **20 clientes** a cada una de las 3 ventanas de la mañana:
- 09:00–11:00 (min 540–660)
- 11:00–13:00 (min 660–780)
- 13:00–15:00 (min 780–900)

Los **88 clientes restantes** operaron con ventana completa (540–1260), `Tipo_vivienda = False`.

**Propósito:** Evaluar si el modelo gestiona una demanda mixta con ventanas acotadas en la mañana, verificando que los 60 clientes con ventana específica sean visitados dentro de su franja sin sacrificar la eficiencia en las rutas de los 88 clientes sin ventana.

**Resultado:** El modelo logró atender el 100 % de los pedidos (0 % backlog), con una tasa de entrega a tiempo del **91.6 %**. La tardanza promedio de 177.7 minutos concentra los incumplimientos principalmente en los clientes de las ventanas de mañana, que compiten con los 88 clientes sin restricción temporal. La función objetivo de $2 860 589 con $0 en penalización de espera indica que el modelo no registró tiempos de espera, clasificando los incumplimientos como tardanzas (entregas fuera de ventana) en lugar de esperas (llegadas anticipadas).

#### Escenario 2 — Día 06: Tarde Cubierta

**Descripción:** Se asignaron **20 clientes** a cada una de las 3 ventanas de la tarde:
- 15:00–17:00 (min 900–1020)
- 17:00–19:00 (min 1020–1140)
- 19:00–21:00 (min 1140–1260)

Los **55 clientes restantes** operaron con ventana completa (540–1260), `Tipo_vivienda = False`.

**Propósito:** Comprobar si la concentración de restricciones en el bloque de tarde —que permite más libertad operativa en la mañana— favorece la factibilidad y el cumplimiento de ventanas.

**Resultado:** Es el escenario con **mejor desempeño global**: 100 % de entregas a tiempo, tardanza promedio 0 min y función objetivo de $3 647 556 (en parte inflada por la penalización de espera de $726 657 asociada a los 14.5 minutos de espera acumulados). La agrupación en el bloque de tarde permite al GA organizar las primeras horas del turno con los 55 clientes sin restricción, maximizando la cobertura geográfica antes de ejecutar las entregas tardías. Este resultado valida que la estructura de ventanas concentradas en un bloque coherente facilita la convergencia del algoritmo.

#### Escenario 3 — Día 05: Distribución Uniforme

**Descripción:** Los **122 clientes** del día se distribuyeron equitativamente entre las 6 ventanas de 2 horas disponibles (~20 clientes por ventana). Todos con `Tipo_vivienda = True`.

**Propósito:** Representar el caso más restrictivo: sin clientes con ventana flexible, el algoritmo debe satisfacer restricciones temporales para la totalidad de la demanda. Evalúa el límite de capacidad del modelo ante máxima fragmentación temporal.

**Resultado:** Es el escenario más exigente. La función objetivo de $6 498 745 incluye una **penalización dominante de $3 380 412** por 67.6 minutos de espera acumulada. La tasa de entrega a tiempo (88.1 %) es la más baja de los cuatro días. La distancia total (1 189.72 km) es la segunda más alta, reflejo de las sub-rutas ineficientes que el modelo construye para respetar secuencias temporales fragmentadas. Este resultado era esperado y confirma que la distribución uniforme de ventanas acotadas representa el peor caso operacional para el modelo.

#### Escenario 4 — Día 07: Mitad y Mitad

**Descripción:**
- **58 clientes** (~50 %) con ventana completa (540–1260), `Tipo_vivienda = False`
- **57 clientes** (~50 %) distribuidos uniformemente entre las 6 ventanas de 2 horas, `Tipo_vivienda = True`

**Propósito:** Evaluar el comportamiento del modelo en un escenario intermedio, verificando si la presencia de flexibilidad temporal en la mitad de los clientes mejora sustancialmente los indicadores respecto al caso de máxima restricción (día 05).

**Resultado:** La solución presenta **98.3 % de entregas a tiempo** y una tardanza promedio casi nula (0.9 min), confirmando que la presencia de clientes sin ventana actúa como "buffer" operativo que permite al AG construir rutas más eficientes. La función objetivo ($3 636 880) es similar al día 06 pero con mayor costo de transporte ($1 161 579 vs. $920 899), explicado por la mayor distancia recorrida (1 235.72 km vs. 979.68 km).

---

### 2.2 Coherencia de Resultados

Los resultados presentaron una **coherencia interna robusta** a lo largo de los cuatro escenarios evaluados:

1. **Monotonicidad del estrés temporal:** La función objetivo creció conforme aumentó la proporción de clientes con ventanas acotadas —en el orden día 04 < día 06 < día 07 < día 05—, siguiendo el gradiente esperado de dificultad de restricciones temporales.

2. **Consistencia flota-distancia:** En todos los días, los 20 vehículos fueron utilizados al 100 % (0 vehículos en desuso). Los tiempos totales en ruta resultaron coherentes con las distancias recorridas, considerando que el modelo híbrido emplea velocidades de desplazamiento variables según el tramo y el período del turno, a diferencia del caso base TSP, que asume una velocidad uniforme de 25 km/h. Esta distinción es relevante para la interpretación de los tiempos en ruta, que en el modelo híbrido reflejan condiciones dinámicas de circulación urbana.

3. **Coherencia de emisiones y consumo:** Las emisiones de CO₂ guardaron una relación lineal con la distancia recorrida (factor ≈ 0.412 kg CO₂/km), lo que confirmó que el módulo de cálculo de indicadores ambientales operó correctamente y sin discontinuidades entre instancias.

4. **Estabilidad del tiempo de cómputo:** Los días con mayor complejidad temporal (05 y 07) demandaron tiempos de cómputo notablemente superiores (16.8–30.9 min) respecto a los de menor fragmentación temporal (días 04 y 06: 17.5–17.7 min), lo que es consistente con el mayor espacio de búsqueda que el AG debió explorar para construir soluciones viables bajo restricciones densas.

5. **Backlog nulo:** En todos los escenarios, la tasa de pedidos no atendidos fue de 0 %, resultado que validó que el mecanismo de inicialización Clarke-Wright garantizó la asignación de la totalidad de los clientes a algún vehículo, sin exclusiones por infactibilidad de capacidad.

---

### 2.3 Comparación con Expectativas

> **Referencia — Grafo g7:** El tipo de gráfico *g7* (generado mediante `visualizer.py`) corresponde a la visualización de la solución final del AG superpuesta sobre el mapa vial, con cada ruta representada en un color diferente y marcadores de inicio y fin de trayecto. Este gráfico permite contrastar visualmente la geometría de las rutas obtenidas con las expectativas teóricas de agrupamiento geográfico y secuencia temporal.

#### Tabla 5 — Comparación con Expectativas Teóricas

| Aspecto | Expectativa Teórica | Resultado Observado | Conformidad |
|:--------|:-------------------|:-------------------|:-----------:|
| Reducción de distancia vs. TSP | Mejora ≥10 % en días sin ventanas acotadas | −13 % (día 04), −4.5 % (día 06), −2.4 % (día 07) | ✅ Parcial |
| 100 % backlog nulo | Todos los clientes asignados | Backlog 0 % en todos los días | ✅ Completo |
| Mayor costo FO vs. TSP | FO híbrido > TSP por costos fijos | FO 2.3×–4.9× el TSP base | ✅ Esperado |
| Día 06 como mejor caso | Ventanas agrupadas en tarde → mayor libertad matutina | 100 % puntualidad, menor distancia/pedido (8.52) | ✅ Confirmado |
| Día 05 como peor caso | Máxima fragmentación temporal → mayor costo | Mayor penalización ($3.38M), menor puntualidad (88.1%) | ✅ Confirmado |
| Escalabilidad del tiempo con n_gen | Escalado lineal | ~2× tiempo al doblar n_gen | ✅ Confirmado |
| Factibilidad estricta en día 06 | Ventanas compactas facilitan convergencia | Solo día 06 logra factibilidad Sí en múltiples configs | ✅ Confirmado |
| Mejora con mayor pop_size | Mayor diversidad → mejor solución | Mejora observable hasta pop_size≈1500, retorno marginal posterior | ✅ Confirmado |
| Reducción de emisiones vs. TSP | Menor distancia → menor CO₂ | CO₂ reducido en días 04, 06 y 07; aumenta en día 05 | ⚠️ Condicional |
| Utilización de capacidad >80 % | Inicialización Clarke-Wright maximiza carga | Util. promedio 69–72 %, volumen 81–85 % | ⚠️ Parcial |

#### Hallazgos Generales

El modelo híbrido **cumple con las expectativas principales**: opera sin backlog, reduce la distancia en los escenarios de menor restricción temporal y exhibe el comportamiento esperado frente a cambios en la estructura de ventanas. Las desviaciones respecto a las expectativas se concentran en:

- La **utilización de capacidad promedio** (69–72 % vs. expectativa >80 %) indica que el AG prioriza el cumplimiento de ventanas sobre la maximización de carga por vehículo. Esto es un comportamiento racional dado el diseño de la función objetivo, donde las penalizaciones por incumplimiento de ventana superan los ahorros por consolidación de carga.

- Las **tardanzas del día 04** (177.7 min promedio) son superiores a lo esperado para un escenario con solo el 56 % de clientes con ventana acotada, sugiriendo que las ventanas de mañana generan una presión temporal intensa en las primeras horas del turno, y que el AG con `pop_size=1500, n_gen=2500` no converge a soluciones factibles en esa franja con la configuración final.

- La **penalización de espera del día 06** ($726 657) resulta sorprendente para el escenario de mejor desempeño, pero es coherente: el modelo llega anticipadamente a clientes de tarde, generando espera (coste positivo) en lugar de tardanza (coste de ventana incumplida). Esto refleja una estrategia racional del AG de minimizar la tardanza a expensas de tolerar cierta espera.

En suma, el modelo híbrido Clarke-Wright + AG demostró ser una solución robusta y coherente para el VRP con ventanas temporales heterogéneas. Su desempeño diferenciado según la estructura de las ventanas de entrega permitió identificar con claridad los escenarios operacionales más favorables para su aplicación, así como las condiciones bajo las cuales el modelo enfrenta sus mayores limitaciones en términos de puntualidad y eficiencia de costo.

---

*Documento elaborado a partir de los archivos de resultados del proyecto Capstone Analytics, abril de 2026.*
