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
   - 2.4 [Metaheurística: Algoritmo Genético Híbrido](#24-metaheurística-algoritmo-genético-híbrido)
   - 2.5 [Modelamiento de Tiempos de Viaje Variables](#25-modelamiento-de-tiempos-de-viaje-variables)
   - 2.6 [Gestión Global de Flota Fija](#26-gestión-global-de-flota-fija)
3. [Estructura Modular del Sistema](#3-estructura-modular-del-sistema)
4. [Principales Aciertos del Planteamiento](#4-principales-aciertos-del-planteamiento)
5. [Principales Desaciertos del Planteamiento](#5-principales-desaciertos-del-planteamiento)
6. [Conclusiones](#6-conclusiones)

---

## 1. Introducción y Formulación del Problema

El presente informe documenta la construcción de un pipeline computacional para resolver el **Problema de Ruteo de Vehículos Dependiente del Tiempo con Ventanas de Tiempo** (TDVRPTW, por sus siglas en inglés). Este problema extiende el clásico VRP al incorporar dos dimensiones adicionales de complejidad: la variación temporal de las velocidades de tránsito y la presencia de restricciones de entrega en intervalos horarios definidos por cada cliente.

El escenario operativo modela la distribución logística de última milla en el Área Metropolitana de Santiago, Chile. La flota es heterogénea en turnos pero homogénea en capacidades físicas, y opera desde un depósito central ubicado en la comuna de San Miguel.

### 1.1 Formulación Matemática

Sea $G = (V, A)$ un grafo dirigido donde $V = \{0, 1, \ldots, n\}$ es el conjunto de nodos ($0$ representa el depósito central) y $A \subseteq V \times V$ es el conjunto de arcos. Se dispone de una flota homogénea de $m$ vehículos, cada uno con capacidad volumétrica $Q^v$ y capacidad de peso $Q^w$.

#### Parámetros del modelo

| Parámetro   | Descripción                                                | Valor          |
| ------------ | ----------------------------------------------------------- | -------------- |
| $Q^v$      | Capacidad volumétrica máxima por vehículo y turno        | 3.750.000 cm³ |
| $Q^w$      | Capacidad de peso máxima por vehículo y turno             | 803.333 g      |
| $T^{\max}$ | Duración máxima de turno operativo                        | 240 min        |
| $\delta$   | Holgura de ventana de tiempo suave (por extremo)            | 15 min         |
| $\Delta$   | Tiempo mínimo de descanso entre turnos del mismo vehículo | 120 min        |

#### Variables de decisión

Sea $x_{ij}^k \in \{0,1\}$ la variable binaria que toma valor $1$ si el vehículo $k$ transita por el arco $(i,j)$, y $0$ en caso contrario. Sea $s_i^k \geq 0$ el tiempo de inicio de servicio del vehículo $k$ en el nodo $i$.

#### Función objetivo

El modelo minimiza el costo total compuesto:

$$
\min \quad Z = \underbrace{\alpha_d \sum_{k} \sum_{(i,j) \in A} d_{ij} \cdot x_{ij}^k}_{\text{costo de distancia}} + \underbrace{\alpha_c \sum_{k} \mathbb{1}[\text{vehículo } k \text{ es utilizado}]}_{\text{costo fijo de flota}} + \underbrace{\alpha_w \sum_{k} \sum_{i \in V} w_i^k}_{\text{penalización por espera}}
$$

donde $d_{ij}$ es la distancia del arco $(i,j)$ en metros, $w_i^k$ es el tiempo de espera del vehículo $k$ en el nodo $i$ (tiempo ocioso antes de que abra la ventana de entrega), y los coeficientes $\alpha_d, \alpha_c, \alpha_w > 0$ son parámetros de ponderación del costo.

#### Restricciones

**Restricciones de flujo:**

$$
\sum_{j \in V} x_{0j}^k = \sum_{j \in V} x_{j0}^k = 1, \quad \forall k
$$

$$
\sum_{j \in V} x_{ij}^k = \sum_{j \in V} x_{ji}^k, \quad \forall i \in V \setminus \{0\}, \; \forall k
$$

**Restricciones de capacidad:**

$$
\sum_{i \in V \setminus \{0\}} q_i^v \cdot \sum_{j \in V} x_{ij}^k \leq Q^v, \quad \forall k
$$

$$
\sum_{i \in V \setminus \{0\}} q_i^w \cdot \sum_{j \in V} x_{ij}^k \leq Q^w, \quad \forall k
$$

**Restricciones de ventanas de tiempo suaves:**

Cada nodo $i \in V \setminus \{0\}$ tiene una ventana de tiempo $[a_i, b_i]$. Con holgura $\delta = 15$ minutos en cada extremo, la restricción impone una penalización —pero no una prohibición— ante el incumplimiento:

$$
s_i^k \geq a_i - \delta \quad \text{(llegada no antes del límite suave inferior)}
$$

$$
\text{Violación}_i^k = \max\left(0,\; s_i^k - (b_i + \delta)\right) \quad \text{(exceso sobre el límite suave superior)}
$$

La suma de violaciones $G = \sum_{k} \sum_{i} \text{Violación}_i^k$ actúa como restricción blanda en el modelo de optimización: solo se declaran factibles los cromosomas con $G = 0$.

**Restricción de continuidad temporal:**

$$
s_j^k \geq s_i^k + \text{serv}_i + \tau_{ij}(s_i^k + \text{serv}_i), \quad \forall (i,j) \in A, \; \forall k
$$

donde $\tau_{ij}(t)$ es el tiempo de viaje dependiente del tiempo desde $i$ hasta $j$ con partida en el instante $t$ (definido en la Sección 2.5), y $\text{serv}_i$ es el tiempo de servicio en el nodo $i$.

**Restricción de duración máxima de turno:**

$$
\sum_{(i,j) \in A} x_{ij}^k \cdot \left[ \tau_{ij}(t) + \text{serv}_i \right] \leq T^{\max}, \quad \forall k
$$

**Restricción de multi-turno:**

Si un vehículo físico $k$ opera en dos bloques de ruta $(B_1, B_2)$ en el mismo día, con horas de retorno $t^{\text{ret}}_1$ y de salida $t^{\text{sal}}_2$ respectivamente:

$$
t^{\text{sal}}_2 \geq t^{\text{ret}}_1 + \Delta, \quad \Delta = 120 \text{ min}
$$

---

## 2. Estrategia de Solución

### 2.1 Paradigma Cluster-First, Route-Second

El TDVRPTW es NP-duro en su forma general (Laporte, 2009; Toth y Vigo, 2014). Para instancias de escala real con $n > 100$ clientes y restricciones temporales acopladas, la búsqueda exacta resulta computacionalmente inviable. Se adopta el paradigma **Cluster-First, Route-Second** (Fisher y Jaikumar, 1981), que descompone el problema original en dos etapas:

1. **Etapa de partición:** Se construye una partición $\mathcal{C} = \{C_1, C_2, \ldots, C_K\}$ del conjunto de clientes $V \setminus \{0\}$ en $K$ subconjuntos disjuntos y exhaustivos, geográfica y temporalmente coherentes.
2. **Etapa de ruteo:** Cada subconjunto $C_k$ se resuelve como un subproblema VRP independiente de escala $|C_k| \ll n$.

Esta descomposición transforma un problema de complejidad $\mathcal{O}(n!)$ en $K$ subproblemas de complejidad $\mathcal{O}((n/K)!)$ aproximadamente, con una reducción factorial que crece exponencialmente con $K$. La viabilidad de la descomposición depende críticamente de que la partición sea geográfica y temporalmente coherente: clientes con ventanas de tiempo incompatibles no deben co-residir en el mismo clúster.

### 2.2 Clusterización Geo-Temporal con DBSCAN

La partición $\mathcal{C}$ se construye mediante el algoritmo **DBSCAN** (*Density-Based Spatial Clustering of Applications with Noise*, Ester et al., 1996). A diferencia de K-Means, DBSCAN no requiere especificar $K$ a priori, identifica automáticamente regiones de alta densidad en el espacio de características y clasifica como ruido los puntos aislados.

#### Espacio de características

Cada cliente $i$ se representa como un punto en un espacio tridimensional:

$$
\mathbf{x}_i = (\phi_i, \lambda_i, a_i) \in \mathbb{R}^3
$$

donde $\phi_i$ es la latitud, $\lambda_i$ la longitud y $a_i$ la hora de apertura de la ventana de tiempo (en minutos desde la medianoche).

#### Normalización y ponderación

Las tres dimensiones son heterogéneas en unidades. Se aplica estandarización z-score mediante:

$$
\tilde{x}_{i,f} = \frac{x_{i,f} - \mu_f}{\sigma_f}, \quad f \in \{\phi, \lambda, a\}
$$

Posteriormente se introduce un factor de ponderación diferencial $\alpha_{\text{time}} > 1$ sobre la dimensión temporal:

$$
\hat{x}_i = (\tilde{\phi}_i,\; \tilde{\lambda}_i,\; \alpha_{\text{time}} \cdot \tilde{a}_i), \quad \alpha_{\text{time}} = 7{,}0
$$

Este factor amplifica la cohesión temporal en detrimento de la cohesión geográfica, garantizando que clientes con ventanas de tiempo alejadas sean separados aunque estén próximos geográficamente. El valor $\alpha_{\text{time}} = 7{,}0$ fue calibrado empíricamente.

#### Criterio de vecindad DBSCAN

Dos puntos $\hat{x}_i$ y $\hat{x}_j$ son $\varepsilon$-vecinos si:

$$
\|\hat{x}_i - \hat{x}_j\|_2 \leq \varepsilon, \quad \varepsilon = 0{,}3
$$

Un punto $\hat{x}_i$ es un *core point* si tiene al menos $\text{min\_samples} = 3$ puntos en su vecindad $\varepsilon$. El algoritmo construye los clústeres como componentes conexas de core points y sus vecinos.

#### Gestión de outliers

Los puntos clasificados como ruido ($\text{etiqueta} = -1$) son reasignados al clúster cuyo centroide esté más próximo en el espacio normalizado ponderado, garantizando cobertura total de clientes cuando $\text{force\_rescue} = \text{True}$.

### 2.3 Heurística Constructiva de Ahorros (Clarke-Wright)

Antes de invocar el algoritmo metaheurístico, se construye una **solución inicial de alta calidad** mediante la heurística de Ahorros de Clarke y Wright (1964). Esta heurística greedy parte de la solución trivial —un vehículo exclusivo por cliente— y la compacta iterativamente mediante fusión de rutas.

#### Función de ahorro

Para un par de clientes $(i, j)$, el ahorro de consolidar sus rutas en una sola ruta continua depot $\to i \to j \to$ depot es:

$$
S(i,j) = d_{0i} + d_{j0} - d_{ij} \geq 0
$$

donde $d_{0i}$ es la distancia desde el depósito al cliente $i$. Un ahorro positivo indica que enlazar $j$ a continuación de $i$ es menos costoso que servir a $j$ desde el depósito de forma independiente.

#### Procedimiento de fusión

Se construye la lista de ahorros $\mathcal{L} = \{S(i,j) : i,j \in V \setminus \{0\}, i \neq j\}$, ordenada de mayor a menor. Para cada par $(i,j)$ en $\mathcal{L}$, se fusionan las rutas correspondientes si y solo si se cumplen simultáneamente:

1. $i$ es el último cliente de su ruta actual y $j$ es el primero de la suya (estructura de cadena).
2. La ruta resultante no excede la capacidad volumétrica: $\sum q^v \leq Q^v$.
3. La ruta resultante no excede la capacidad de peso: $\sum q^w \leq Q^w$.
4. La duración estimada de la ruta resultante no excede $T^{\max}$.
5. Las ventanas de tiempo de los clientes de la ruta resultante son temporalmente compatibles.

El resultado es una permutación de clientes $\sigma^* = (\sigma_1, \sigma_2, \ldots, \sigma_{|C_k|})$ que constituye la **solución semilla** del algoritmo genético. Al inyectar esta solución construida como individuo inicial de la población, se combina el poder de búsqueda local de la heurística greedy con la capacidad de exploración global del GA, conformando un **algoritmo memético** (Moscato, 1989).

### 2.4 Metaheurística: Algoritmo Genético Híbrido

El núcleo de la optimización por clúster es un **Algoritmo Genético (GA)** de permutaciones, formulado como un problema de optimización constreñido y resuelto mediante la biblioteca PyMoo (Blank y Deb, 2020).

#### Representación cromosómica

Cada individuo de la población es una permutación entera:

$$
\sigma = (\sigma_1, \sigma_2, \ldots, \sigma_{|C_k|}) \in \Pi_{|C_k|}
$$

donde $\Pi_n$ denota el conjunto de todas las permutaciones del conjunto $\{1, \ldots, n\}$. El cromosoma no contiene marcadores de separación de rutas: la asignación de clientes a sub-rutas (y por tanto la activación de nuevos vehículos) se reconstruye dinámicamente durante la evaluación, siguiendo un procedimiento de *split* por capacidad y duración de turno.

#### Evaluación de un individuo

Dado un cromosoma $\sigma$, el evaluador simula la ejecución de la ruta siguiendo el orden propuesto. Para el cliente en posición $p$ de la ruta, el tiempo de inicio de servicio se calcula recursivamente:

$$
s_{\sigma_p} = \max\!\left(a_{\sigma_p} - \delta,\; s_{\sigma_{p-1}} + \text{serv}_{\sigma_{p-1}} + \tau_{\sigma_{p-1}, \sigma_p}(s_{\sigma_{p-1}} + \text{serv}_{\sigma_{p-1}})\right)
$$

El término $\max(\cdot)$ captura el tiempo de **espera activa**: si el vehículo llega antes de la apertura suave de la ventana, aguarda hasta $a_i - \delta$.

Cuando se excede la capacidad o la duración máxima de turno, se activa un nuevo vehículo (*split*) reiniciando el reloj desde el depósito. El tiempo de salida del primer nodo de cada sub-ruta puede retrasarse mediante una lógica **JIT** (*Just-In-Time*): se calcula la salida más tardía posible que permita llegar a tiempo al primer cliente, reduciendo la espera ociosa.

#### Función objetivo y restricción

La función objetivo a minimizar es:

$$
F(\sigma) = \alpha_d \cdot D_{\text{total}}(\sigma) + \alpha_c \cdot m(\sigma) + \alpha_w \cdot W_{\text{total}}(\sigma)
$$

donde $D_{\text{total}}(\sigma)$ es la distancia total acumulada, $m(\sigma)$ el número de vehículos activados (resultado del *split*) y $W_{\text{total}}(\sigma)$ la espera total acumulada.

La restricción de factibilidad se formula como:

$$
G(\sigma) = \sum_{i \in C_k} \max\!\left(0,\; s_i - (b_i + \delta)\right) \leq 0
$$

Un cromosoma $\sigma$ es declarado **factible** si y solo si $G(\sigma) = 0$.

#### Operadores genéticos

- **Cruce (Order Crossover, OX):** Dado un par de padres $(\sigma^A, \sigma^B)$, se selecciona aleatoriamente un segmento $[\ell, r]$ del padre $A$ y se preserva en su posición original. Los genes restantes se rellenan con el orden relativo del padre $B$, omitiendo los ya presentes. OX es el operador canónico para problemas de permutación, pues garantiza que el hijo sea una permutación válida (Davis, 1985).
- **Mutación (Inversión):** Con probabilidad $p_m = 0{,}3$, se selecciona aleatoriamente un subsegmento $[\ell, r]$ del cromosoma y se invierte su orden:

$$
\sigma' = (\sigma_1, \ldots, \sigma_{\ell-1}, \sigma_r, \sigma_{r-1}, \ldots, \sigma_\ell, \sigma_{r+1}, \ldots, \sigma_n)
$$

La inversión es equivalente a aplicar un movimiento 2-opt local en el espacio de soluciones de la ruta, lo que le otorga una justificación estructural sólida para el TSP y sus variantes (Lin y Kernighan, 1973).

#### Criterio de terminación adaptativo

El GA no ejecuta un número fijo de generaciones. En su lugar, se emplea un criterio de terminación basado en la estabilización del valor de la función objetivo:

$$
\text{Terminar si} \quad \frac{|F^* - F^*_{\text{prev}}|}{|F^*_{\text{prev}}|} < f_{\text{tol}} = 10^{-3} \quad \text{durante} \quad p = 100 \text{ generaciones consecutivas}
$$

con un límite máximo de $n_{\max} \in \{500, 2000\}$ generaciones. Este criterio detecta convergencia prematura y libera recursos computacionales para clústeres que ya han alcanzado un óptimo estable.

#### Mecanismo de rescate ante infactibilidad

Si al concluir el GA no existe ningún individuo con $G(\sigma) = 0$ en la población final, el sistema extrae el individuo con menor violación:

$$
\sigma^{\text{rescue}} = \arg\min_{\sigma \in \mathcal{P}} G(\sigma)
$$

Este individuo se reporta explícitamente como infactible, garantizando cobertura total de clientes y visibilidad operacional sobre los clústeres problemáticos.

### 2.5 Modelamiento de Tiempos de Viaje Variables

El componente diferenciador frente a un VRP estándar es la función de tiempos de viaje dependiente del tiempo. Se implementa la formulación de **Fleischmann, Gietz y Gnutzmann (2004)**.

#### Perfil de velocidades

El horizonte de planificación $[t_0, t_f] = [09\text{h}00, 21\text{h}00]$ se divide en $K = 12$ intervalos de 60 minutos. Para cada intervalo $k \in \{1, \ldots, K\}$ y día de la semana $d \in \{0, \ldots, 6\}$, se define una velocidad media $v_{k,d}$ (en km/h), almacenada en la tabla $\mathbf{V} \in \mathbb{R}^{24 \times 7}$ que codifica los perfiles de tráfico urbano de Santiago.

El tiempo de viaje base para el arco $(i,j)$ durante el intervalo $k$ es:

$$
\tau_{ij}^k = \frac{d_{ij}}{v_{k,d} / 3{,}6} \quad \text{[segundos]}
$$

donde $d_{ij}$ es la distancia en metros y el factor $3{,}6$ convierte km/h a m/s.

#### Linealización en las fronteras de intervalo

Para garantizar la continuidad de $\tau_{ij}(t)$ en las fronteras entre intervalos y evitar discontinuidades que perturbarían la evaluación del GA, se implementa una zona de transición de ancho $2\delta_{\text{trans}}$ centrada en cada frontera $z_k$ (con $\delta_{\text{trans}} = 15$ min). La función de tiempo de viaje es:

$$
\tau_{ij}(t) = \begin{cases}
\tau_{ij}^k & \text{si } t \in [z_k + \delta_{\text{trans}},\; z_{k+1} - \delta_{\text{trans}}] \quad \text{(zona estable)} \\[4pt]
\tau_{ij}^k + (t - z_{k+1} + \delta_{\text{trans}}) \cdot s_{ij}^k & \text{si } t \in [z_{k+1} - \delta_{\text{trans}},\; z_{k+1}] \quad \text{(transición derecha)} \\[4pt]
\tau_{ij}^{k-1} + (t - z_k + \delta_{\text{trans}}) \cdot s_{ij}^{k-1} & \text{si } t \in [z_k,\; z_k + \delta_{\text{trans}}] \quad \text{(transición izquierda)}
\end{cases}
$$

donde la pendiente de transición en el intervalo $k$ es:

$$
s_{ij}^k = \frac{\tau_{ij}^{k+1} - \tau_{ij}^k}{2\,\delta_{\text{trans}}}
$$

Esta linealización garantiza que $\tau_{ij}(t)$ sea **continua por tramos** en todo el horizonte de planificación. La función se vectoriza sobre arrays de NumPy para operar eficientemente dentro del evaluador del GA, permitiendo calcular los tiempos de viaje de todos los arcos de una ruta en una sola operación matricial.

### 2.6 Gestión Global de Flota Fija

Una vez que el GA determina las rutas óptimas por clúster, el nivel superior de decisión asigna los bloques de ruta a los vehículos físicos disponibles.

#### Modelamiento de bloques de ruta

Cada bloque de ruta $B_\ell$ se representa como la tupla:

$$
B_\ell = (t_\ell^{\text{sal}},\; t_\ell^{\text{ret}},\; \pi_\ell,\; D_\ell)
$$

donde $t_\ell^{\text{sal}}$ es la hora de salida del depósito, $t_\ell^{\text{ret}}$ la hora de retorno, $\pi_\ell$ la plantilla de turno (K11, K12, K21, K22) y $D_\ell$ la duración total del bloque.

#### Algoritmo de asignación FFD (*First Fit Decreasing*)

Los bloques se ordenan en orden decreciente de duración: $D_{\sigma(1)} \geq D_{\sigma(2)} \geq \ldots \geq D_{\sigma(L)}$. Para cada bloque $B_{\sigma(\ell)}$, se recorre la flota disponible y se asigna al primer vehículo $k$ que satisfaga simultáneamente:

1. **Compatibilidad temporal:** $t_{\sigma(\ell)}^{\text{sal}} \geq t_{k,\text{prev}}^{\text{ret}} + \Delta$, donde $t_{k,\text{prev}}^{\text{ret}}$ es la hora de retorno del bloque previamente asignado al vehículo $k$.
2. **Homogeneidad de plantilla:** el vehículo $k$ no ha operado en una plantilla distinta a $\pi_{\sigma(\ell)}$.
3. **Unicidad de sub-turno:** el vehículo $k$ no ha operado previamente en el mismo sub-turno que $B_{\sigma(\ell)}$.

Si ningún vehículo de la flota puede absorber el bloque, este se registra como **huérfano** (candidato a tercerización).

La estrategia FFD es una heurística clásica para el *Bin Packing Problem* (Garey y Johnson, 1979). Al priorizar los bloques de mayor duración, se maximiza la utilización de cada vehículo antes de asignar los bloques cortos a los huecos residuales, minimizando el número de vehículos activos.

---

## 3. Estructura Modular del Sistema

El pipeline se organiza en módulos funcionales desacoplados, cada uno con responsabilidad única. La figura siguiente muestra la arquitectura de alto nivel y el flujo de datos entre módulos:

```
Captone-Analytics/
├── grafo/          → Capa geoespacial: geocodificación, clustering, matrices de distancia
├── modelo/         → Formulación matemática del TDVRPTW y función de tiempos de viaje
├── algoritmo/      → Heurística Clarke-Wright y orquestación del GA con PyMoo
├── gestion_flota/  → Asignación FFD de bloques de ruta a flota fija
├── resultados/     → Artefactos de salida: CSV, KPIs y mapas interactivos
└── pruebas_sensibilidad/ → Infraestructura de validación experimental
```

### 3.1 Módulo `grafo/` — Capa Geoespacial

Este módulo es la única interfaz entre los datos operativos crudos (direcciones textuales, coordenadas) y las estructuras matemáticas que consumen los módulos de optimización (matrices de distancia $\mathbf{D} \in \mathbb{R}^{n \times n}$).

**`grafo/geocoder.py`** — Traduce las direcciones textuales del dataset a coordenadas geográficas $(\phi_i, \lambda_i)$ mediante la API ArcGIS (librería `geopy`). Implementa un caché de coordenadas en memoria para minimizar llamadas externas durante la ejecución y un limitador de tasa (*rate limiter*) para respetar los umbrales de la API.

**`grafo/network_builder.py`** — Carga el grafo dirigido de la red vial de Santiago desde un archivo `.graphml` pre-descargado con OSMnx. El grafo $G = (V, A)$ contiene los arcos ponderados por longitud en metros (`weight='length'`) y es la estructura base sobre la que se calculan todas las rutas mínimas.

**`grafo/clustering.py`** — Implementa el pipeline completo de clusterización geo-temporal descrito en la Sección 2.2. Recibe el `DataFrame` de pedidos geocodificados y retorna el diccionario de clústeres $\mathcal{C} = \{C_1, \ldots, C_K\}$, los outliers reasignados y los pares origen-destino para la etapa de ruteo.

**`grafo/routing.py`** — Para cada clúster $C_k$, calcula la submatriz de distancias $\mathbf{D}^{(k)} \in \mathbb{R}^{(|C_k|+1) \times (|C_k|+1)}$ (incluyendo el depósito) sobre el grafo vial real. La optimización clave consiste en reemplazar $\mathcal{O}(|C_k|^2)$ búsquedas A\* independientes por $\mathcal{O}(|C_k|)$ expansiones Dijkstra radiales (`nx.single_source_dijkstra`) con consulta $\mathcal{O}(1)$ en tabla hash. Adicionalmente, solo se retienen en memoria los resultados hacia los nodos del clúster particular, evitando el desbordamiento de memoria (OOM) que produciría conservar los diccionarios completos del grafo vial (~500.000 nodos) por expansión.

**`grafo/main.py`** — Orquestador de la capa geoespacial. Ejecuta los seis pasos de preparación en secuencia (carga, geocodificación de pedidos, geocodificación del depósito, clusterización, carga del grafo y ruteo por clúster) y paraleliza el cálculo de matrices mediante `ProcessPoolExecutor`, inyectando el grafo OSMnx en cada proceso worker mediante un inicializador (`_init_worker`) para evitar su serialización vía `pickle` —que resulta prohibitiva en tiempo y memoria para grafos de escala urbana.

**`grafo/visualizer.py`** — Genera mapas HTML interactivos con Folium, tanto para la etapa de clústeres (coloreados por grupo) como para las rutas finales asignadas por vehículo, incluyendo el estado de cumplimiento de ventanas de tiempo por nodo.

### 3.2 Módulo `modelo/` — Formulación Matemática

Este módulo contiene la definición formal del problema de optimización tal como lo entiende el solver metaheurístico.

**`modelo/pymoo_problem.py`** — Define la clase `TDVRPTWProblem`, que hereda de `ElementwiseProblem` de PyMoo. Esta clase encapsula la formulación matemática completa del TDVRPTW: inicializa los diccionarios de demandas (volumen, peso) y ventanas de tiempo $[a_i, b_i]$ para cada cliente del clúster, y expone el evaluador `_evaluate(x, out)` que, dado un cromosoma de permutación $\sigma$, simula la ejecución completa de la ruta y calcula los valores $(F(\sigma), G(\sigma))$ descritos en la Sección 2.4. La lógica de *split* por capacidad y duración de turno, la heurística JIT de salida tardía del depósito, y la gestión de plantillas de turno multi-viaje (K11, K12, K21, K22) residen íntegramente en este evaluador.

**`modelo/funciones/tiempos_viaje.py`** — Implementa la función $\tau_{ij}(t)$ de Fleischmann et al. (2004) en dos versiones: una escalar (`tau_ij`) para cálculos puntuales y una vectorizada sobre arrays NumPy (`tau_ij_vec`) para uso dentro del evaluador del GA. Contiene la tabla de velocidades $\mathbf{V} \in \mathbb{R}^{24 \times 7}$ con los perfiles de tráfico urbano de Santiago para cada hora del día y día de la semana, así como las funciones de conversión de matrices de distancia en matrices de tiempo de viaje (`distancia_a_tiempo_matrix`, `matrices_distancia_a_tiempo`). El horizonte de planificación está definido por $K = 13$ intervalos de 60 minutos en $[540, 1260]$ minutos (09:00–21:00), con parámetro de suavizado $\delta = 15$ min.

### 3.3 Módulo `algoritmo/` — Punto de Entrada del Pipeline de Optimización

Este módulo contiene la lógica de orquestación del algoritmo genético y actúa como punto de entrada principal del pipeline.

**`algoritmo/savings.py`** — Implementa la heurística constructiva de Clarke-Wright (Sección 2.3). Calcula la lista ordenada de ahorros $\mathcal{L}$ para todos los pares $(i,j)$ de clientes del clúster y ejecuta el procedimiento de fusión greedy bajo las restricciones de capacidad volumétrica, peso, duración de turno y compatibilidad de ventanas de tiempo (mediante la función de estimación `es_viable_ventanas`, que simula la progresión de la ruta con velocidad constante de 25 km/h). El módulo maneja explícitamente la asimetría de la matriz de distancias al considerar ambas orientaciones $(i \to j)$ y $(j \to i)$ en la construcción de la lista $\mathcal{L}$. El resultado es una permutación $\sigma^*$ que sirve como semilla para el GA.

**`algoritmo/genetic_algorithm.py`** — Contiene dos componentes principales. La clase `SavingsSeededSampling` es un operador de muestreo personalizado que inyecta la permutación de Clarke-Wright como primer individuo de la población inicial, generando el resto de forma aleatoria. La función `optimizar_pymoo_ga` instancia `TDVRPTWProblem`, configura el GA con los operadores Order Crossover (OX) e `InversionMutation` ($p_m = 0{,}3$), y ejecuta `pymoo.optimize.minimize` con el criterio de terminación adaptativo ($f_{\text{tol}} = 10^{-3}$, ventana de 200 generaciones). Ante infactibilidad, aplica el mecanismo de rescate detallado en la Sección 2.4. La función `disparar_rutina_ga` actúa como punto de entrada de alto nivel: filtra el dataset por fecha objetivo, invoca la capa geoespacial, distribuye los clústeres entre workers paralelos mediante `ProcessPoolExecutor` (limitado a la mitad de los núcleos disponibles), y delega la asignación de flota global al módulo `gestion_flota/`.

### 3.4 Módulo `gestion_flota/` — Asignación de Flota Fija

**`gestion_flota/gestor.py`** — Resuelve el problema de asignación de bloques de ruta a vehículos físicos mediante el algoritmo FFD descrito en la Sección 2.6. La abstracción central distingue entre `BloqueRuta` (una sub-ruta optimizada por el GA, con su horario de salida $t^{\text{sal}}$, retorno $t^{\text{ret}}$, plantilla de turno y métricas de ejecución) y `VehiculoGlobal` (un vehículo físico con su historial de bloques asignados). El método `puede_absorber(bloque)` verifica en $\mathcal{O}(|\text{bloques asignados}|)$ las tres reglas de compatibilidad: homogeneidad de plantilla de turno (K1 o K2), unicidad de sub-turno, y descanso mínimo $\Delta = 120$ min. Tras la asignación, el gestor calculaun conjunto completo de KPIs operacionales y los exporta en cuatro archivos CSV: resumen por camión, detalle de paradas, KPIs globales y clientes atendidos.

### 3.5 Módulo `resultados/`

Directorio de salida que almacena los artefactos generados por cada ejecución del pipeline, organizados en dos subdirectorios:

- **`rutas/`**: Archivos CSV con el detalle de paradas por vehículo (`detalle_paradas_*.csv`), resumen de turnos (`resumen_camiones_*.csv`), KPIs globales (`kpis_*.csv`) y cobertura de clientes (`clientes_atendidos_*.csv`). Los nombres de archivo incluyen el algoritmo y la fecha objetivo para facilitar la trazabilidad entre ejecuciones.
- **`mapa_rutas/`**: Mapas HTML interactivos generados con Folium, uno por clúster (etapa de clusterización) y uno global con la asignación de flota completa.

### 3.6 Módulo `pruebas_sensibilidad/` — Validación Experimental

**`pruebas_sensibilidad/ejecutor_instancias.py`** — Ejecuta el pipeline completo para un conjunto de fechas y configuraciones de hiperparámetros definidas en una cuadrícula (*grid*). Los parámetros variables incluyen la holgura de ventana de tiempo ($\delta$), el tamaño de población del GA ($p$), el número máximo de generaciones ($n_{\max}$), el número máximo de vehículos y el multiplicador de capacidad. Para cada combinación y fecha, invoca `disparar_rutina_ga` y captura los KPIs resultantes (función objetivo, porcentaje de entregas a tiempo, vehículos usados, tardanza promedio) en un archivo CSV acumulativo.

**`pruebas_sensibilidad/analisis_sensibilidad.py`** — Consolida los resultados de todas las ejecuciones y genera el reporte comparativo `reporte_sensibilidad.md`, identificando las configuraciones factibles (100% de entregas dentro de ventana) y ordenándolas por valor de función objetivo.

**`pruebas_sensibilidad/escenarios_prueba.md`** — Documenta los escenarios de prueba definidos (cuatro fechas de despacho del dataset simulado: 2026-12-04 a 2026-12-07), con sus objetivos de validación y la configuración base de referencia.

---

## 4. Principales Aciertos del Planteamiento

### 4.1 Paradigma híbrido memético (constructiva + metaheurística)

La integración de Clarke-Wright como mecanismo de warm-start para el GA es el acierto metodológico más relevante del diseño. Las heurísticas constructivas generan soluciones factibles en tiempo polinomial pero quedan atrapadas en óptimos locales; los GA escapan de óptimos locales mediante variación estocástica pero sin buena inicialización convergen lentamente a soluciones de baja calidad. La combinación sinérgica de ambos enfoques constituye un **algoritmo memético** que hereda lo mejor de cada paradigma: la factibilidad y calidad constructiva de Clarke-Wright, más la capacidad de mejora global del GA.

### 4.2 Modelamiento de tiempos de viaje dependientes del tiempo

La implementación de Fleischmann et al. (2004) con linealización en las fronteras de intervalo es técnicamente rigurosa. La continuidad de $\tau_{ij}(t)$ elimina discontinuidades que podrían inducir evaluaciones inconsistentes del GA cuando dos individuos difieren únicamente en el tiempo de inicio de ruta. La vectorización de la función sobre arrays NumPy mantiene la eficiencia computacional al nivel de operaciones matriciales.

### 4.3 Clusterización tridimensional geo-temporal

La incorporación de la hora de apertura de ventana de tiempo $a_i$ como tercera dimensión del espacio de clusterización es una decisión de diseño que incrementa directamente la probabilidad de factibilidad de las rutas intra-clúster. El factor de amplificación $\alpha_{\text{time}} = 7{,}0$ en la dimensión temporal garantiza que la cohesión temporal domine sobre la cohesión geográfica cuando ambas entran en conflicto, produciendo clústeres internamente factibles.

### 4.4 Criterio de terminación adaptativo del GA

El criterio de terminación basado en la estabilización del fitness ($f_{\text{tol}} = 10^{-3}$ en una ventana de 100 generaciones) es más eficiente que un límite fijo de generaciones, pues permite al algoritmo invertir más tiempo en clústeres difíciles y terminar anticipadamente en clústeres que convergen rápidamente. Esto es especialmente relevante en la ejecución paralela, donde el *makespan* global está determinado por el clúster más lento.

### 4.5 Mecanismo de rescate ante infactibilidad

El rescate del mejor individuo infactible ($\sigma^{\text{rescue}} = \arg\min G$) garantiza que el pipeline no falle silenciosamente ante clústeres cuyas restricciones de ventanas de tiempo son incompatibles con la capacidad vehicular. La visibilidad operacional sobre infactibilidades permite al operador logístico intervenir selectivamente sin invalidar las soluciones del resto de los clústeres.

### 4.6 Optimización del cálculo de matrices de distancia

El reemplazo de $n^2$ búsquedas A* por $n$ expansiones Dijkstra radiales con lookup $\mathcal{O}(1)$ reduce la complejidad computacional de la etapa geoespacial de $\mathcal{O}(n^2 \cdot |E| \log |V|)$ a $\mathcal{O}(n \cdot |E| \log |V|)$, donde $|E|$ y $|V|$ son el número de aristas y vértices del grafo vial, respectivamente.

### 4.7 Gestión de flota con lógica de multi-turno y tercerización

La abstracción entre **bloques de ruta** (unidades lógicas de trabajo optimizado) y **vehículos físicos** (unidades de capital fijo) refleja correctamente la estructura del problema: un vehículo puede operar múltiples turnos siempre que se respete el descanso mínimo $\Delta$. Los bloques no asignables se reportan como candidatos a tercerización, lo que es coherente con la práctica operativa de la industria logística de última milla.

---

## 5. Principales Desaciertos del Planteamiento

### 5.1 Hiperparámetros de DBSCAN no calibrados automáticamente

Los parámetros $\varepsilon = 0{,}3$ y $\text{min\_samples} = 3$ de DBSCAN fueron calibrados empíricamente para el dataset de referencia. No existe ningún mecanismo automático de selección óptima —como el método del codo sobre la curva $k$-distancia o una búsqueda en cuadrícula con criterio de silhouette— que los ajuste cuando la densidad de pedidos o la distribución geográfica varía entre días. En días con demanda baja, DBSCAN puede degenerarse en un único clúster masivo o en un exceso de outliers, comprometiendo la calidad de la descomposición.

### 5.2 Representación cromosómica sin estructura de rutas múltiples

El cromosoma es una permutación plana sin marcadores de separación entre sub-rutas. La asignación de clientes a vehículos (el *split*) se reconstruye dinámicamente en el evaluador. Esto implica que los operadores genéticos (OX, inversión) operan sobre la permutación global sin conocimiento de la estructura de rutas subyacente, pudiendo generar cruces y mutaciones que violan la coherencia de los bloques de ruta. Una representación alternativa con cromosomas de dos niveles —permutación de clientes más vector de partición— preservaría la estructura de rutas y reduciría la frecuencia de evaluaciones infactibles.

### 5.3 Función de tiempos de viaje sin distinción por tipo de arco

La tabla $\mathbf{V} \in \mathbb{R}^{24 \times 7}$ es homogénea para toda la red vial: aplica la misma velocidad $v_{k,d}$ a autopistas, avenidas principales y calles secundarias. Un modelo más preciso incorporaría la velocidad diferenciada por tipo de vía mediante:

$$
v_{ij,k,d} = v_{k,d} \cdot \rho_{\text{highway}(i,j)}
$$

donde $\rho_h$ es un factor de corrección por tipo de vía $h$ (atributo `highway` del grafo OSMnx). La simplificación actual introduce sesgo sistemático en las estimaciones de tiempo de viaje en sectores con mezcla de tipos de vía.

### 5.4 Algoritmo greedy de asignación de flota sin optimalidad garantizada

El algoritmo FFD es una heurística sin garantía de optimalidad para el problema de asignación de bloques de ruta. En el Bin Packing unidimensional, FFD tiene una razón de aproximación de $\frac{11}{9} \text{OPT} + 6/9$ (Johnson, 1974), lo que implica que puede requerir hasta un 22% más de vehículos que el óptimo en el peor caso. Una formulación como problema de programación entera mixta (MIP) modelaría la asignación de forma exacta, aunque a un costo computacional significativamente mayor para instancias grandes.

### 5.5 Ausencia de validación de factibilidad inter-clúster

El pipeline garantiza la factibilidad de las rutas dentro de cada clúster de forma independiente, pero no verifica que la solución global (unión de todas las rutas) satisfaga la demanda total del día con la flota disponible. Si el número de vehículos $m$ es insuficiente para absorber todos los bloques de ruta, los bloques huérfanos se reportan pero no se triggerea una reasignación de la partición $\mathcal{C}$ para reducirlos. Un mecanismo de retroalimentación entre la etapa de asignación y la etapa de clusterización eliminaría esta incoherencia.

### 5.6 Geocodificación sin persistencia entre ejecuciones

El caché de coordenadas geográficas existe en memoria durante la ejecución actual, pero no se persiste en disco entre ejecuciones. Cada nueva ejecución vuelve a consultar vía API las coordenadas de las direcciones previamente geocodificadas, generando latencia innecesaria y costos de API redundantes para instancias que comparten ubicaciones recurrentes.

---

## 6. Conclusiones

El pipeline construido constituye una solución técnica completa y funcional para el TDVRPTW en el contexto de la distribución de última milla en Santiago. La estrategia de descomposición Cluster-First, Route-Second, combinada con el enfoque híbrido memético (Clarke-Wright + GA PyMoo), permite abordar instancias de escala real con tiempos de cómputo razonables y con garantías de cobertura total de clientes.

Los mayores méritos del planteamiento residen en la rigurosidad del modelamiento matemático —en particular la implementación de la función de tiempos de viaje de Fleischmann et al. (2004) con linealización de continuidad— y en la naturaleza memética del algoritmo, que combina la calidad constructiva de Clarke-Wright con la capacidad de exploración global del GA mediante operadores OX e inversión formalmente justificados para problemas de permutación.

Las principales oportunidades de mejora están concentradas en dos frentes: (1) la calibración automática de los hiperparámetros de DBSCAN mediante criterios de validez interna del clustering (silhouette, Davies-Bouldin), y (2) el reemplazo del algoritmo greedy FFD de asignación de flota por una formulación MIP compacta que garantice la optimalidad de la asignación bajo la restricción de flota fija.

La estructura modular del sistema facilita la incorporación de estas mejoras de forma iterativa sin necesidad de refactorizaciones globales, lo que representa una ventaja metodológica significativa para el desarrollo continuo del pipeline.

---

## Referencias

- Blank, J. y Deb, K. (2020). Pymoo: Multi-objective optimization in Python. *IEEE Access*, 8, 89497-89509.
- Clarke, G. y Wright, J. W. (1964). Scheduling of vehicles from a central depot to a number of delivery points. *Operations Research*, 12(4), 568-581.
- Davis, L. (1985). Applying adaptive algorithms to epistatic domains. *Proceedings of the 9th International Joint Conference on Artificial Intelligence*, 162-164.
- Ester, M., Kriegel, H.-P., Sander, J. y Xu, X. (1996). A density-based algorithm for discovering clusters in large spatial databases with noise. *Proceedings of the 2nd International Conference on Knowledge Discovery and Data Mining (KDD-96)*, 226-231.
- Fisher, M. L. y Jaikumar, R. (1981). A generalized assignment heuristic for vehicle routing. *Networks*, 11(2), 109-124.
- Fleischmann, B., Gietz, M. y Gnutzmann, S. (2004). Time-varying travel times in vehicle routing. *Transportation Science*, 38(2), 160-173.
- Garey, M. R. y Johnson, D. S. (1979). *Computers and Intractability: A Guide to the Theory of NP-Completeness*. W. H. Freeman.
- Johnson, D. S. (1974). Fast algorithms for bin packing. *Journal of Computer and System Sciences*, 8(3), 272-314.
- Laporte, G. (2009). Fifty years of vehicle routing. *Transportation Science*, 43(4), 408-416.
- Lin, S. y Kernighan, B. W. (1973). An effective heuristic algorithm for the traveling-salesman problem. *Operations Research*, 21(2), 498-516.
- Moscato, P. (1989). On evolution, search, optimization, genetic algorithms and martial arts: Towards memetic algorithms. *Caltech Concurrent Computation Program*, Technical Report 826.
- Toth, P. y Vigo, D. (Eds.). (2014). *Vehicle Routing: Problems, Methods, and Applications* (2nd ed.). SIAM.
