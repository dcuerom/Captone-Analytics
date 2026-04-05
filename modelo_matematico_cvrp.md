# Modelo Matemático: CVRP con Ventana Operativa

El problema a resolver, adaptado de la lógica genérica original TDVRPTW pero enfocado bajo el dominio de distancias puras del `Classic VRP (TSPLIB)`, ha modificado el foco métrico desde Minimización de Costos Variables Financieros ($C_{ij}$) a Minimización de Metros Recorridos Puros, preservando la capacidad vehicular simple y una ventana extendida y global de recintos.

## Conjuntos y Parámetros
- $V = \{0, 1, ..., n\}$: Conjunto de Nodos, donde $0$ representa al depósito (CD) y $\{1, ..., n\}$ representan a los clientes pre-clusterizados de un clúster espacial $G$.
- $K$: Flota de vehículos homogéneos. Cada vehículo $k \in K$ opera bajo una ventana física general compartida.
- $D_{ij}$: Distancia Euclidiana exacta flotante en matriz entre el nodo $i$ y el nodo $j$, derivada a través de $D(i, j) = \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}$.
- $\tau(D_{ij}, t_{i}^{k})$: Función tensorial dinámica que calcula el tiempo asimétrico (en minutos) requerido para recorrer la distancia $D_{ij}$ asumiendo $dia=0$ (Lunes) y factor multiplicador de traslación $1000x$. 
- $Q$: Capacidad física máxima (en este caso de peso) compartida por toda la flota. Reemplaza el volumen y simplifica la restricción asimétrica.
- $demand_i$: Demanda paramétrica del peso exigida por el nodo cliente $i \in V$.
- $service_i$: Minutos fijos que demora la atención de descargar y certificar el pedido del cliente $i$ (estático en 5.0 min).
- $W_{max}$: Límite operativo dictatorial para el Sistema (21:00 hrs o 1260 minutos absolutos desde las 00:00). Todos los retornos deben ser previos a esto.

## Variables de Decisión
- $x_{ijk} \in \{0, 1\}$: 1 si el camión $k$ transita directamente desde el nodo $i$ al $j$, 0 en otro caso.
- $y_i^k$: Demanda acumulada contenida por el vehículo $k$ al momento de atender el nodo $i$.
- $t_{arr, i}^k$: Momento cronológico concreto de llegada del vehículo $k$ al nodo $i$.

## Función Objetivo
El objetivo primordial del sistema consiste en minimizar la sumatoria absoluta de la longitud topológica (los metros de arco exactos) recorridos por la totalidad de la matriz vehicular habilitada:

$$ 
\text{Minimizar } \quad Z = \sum_{k \in K} \sum_{i \in V} \sum_{j \in V} D_{ij} \cdot x_{ijk}
$$

## Restricciones

1. **Visita Única y Exhaustiva**:
Cada cliente en el sub-grupo debe ser ruteado por un camión, y solo uno.
$$ 
\sum_{k \in K} \sum_{j \in V} x_{ijk} = 1, \quad \forall i \in \{1, ..., n\} 
$$

2. **Continuidad del Flujo (Conservación de Nodos)**:
Si un vehículo llega a un nodo cliente, por obligación debe salir de dicho nodo cliente hacia alguna parte.
$$ 
\sum_{i \in V} x_{ihk} - \sum_{j \in V} x_{hjk} = 0, \quad \forall h \in \{1, ..., n\}, \forall k \in K 
$$

3. **Restricción de Capacidad Global (Pesos del Sub-viaje)**:
No es permitido acumular más peso que $Q$ a lo largo del segmento entre depósitos que ejecuta el camión en un ciclo de carga.
$$ 
y_j^k \ge y_i^k + demand_j \cdot x_{ijk} - Q(1 - x_{ijk}), \quad \forall i, j \in \{1, ..., n\}, i \neq j, \forall k \in K 
$$
$$ 
demand_i \le y_i^k \le Q, \quad \forall i \in \{1, ..., n\}, \forall k \in K 
$$

4. **Flujo Temporal Cronológico y Tensores de Tránsito**:
Los tiempos de las mallas deben avanzar sin permitir retrocesos sub-lumínicos. Se emplea $\tau()$. (No penalizados por límite $A$ ya que las ventanas individuales de clientes fueron erradicadas).
$$ 
t_{arr, j}^k \ge t_{arr, i}^k + service_i + \tau(D_{ij} \times 1000, t_{arr, i}^k) - M(1 - x_{ijk}), \quad \forall i, j \in V, \forall k \in K
$$

5. **Límite Operacional Máximo (Restricción Global de Ventana Cierre 9 a 9)**:
Cada cadena lineal del vehículo $k$ de turno tarde (Sub-ruta K2X final) **debe** recalar en el Depósito $(0)$ con su hora final de término menor o igual al cierre del bloque a las 21:00hrs.
$$ 
t_{arr, 0_{Final}}^k \le 1260.0 \quad (21:00 \text{ hrs}), \quad \forall k \in K
$$

6. **Límite de Flota Disponible Física (Flota Fija Nominal)**:
La cantidad computada e individualizada de vehículos de carga (descartando dobles turnos del mismo ID físico) jamás podrá sobrepasar a la constante proveída de vehículos de meta $K_{max}$ (proveniente de la instancia parametrizada, ej. `k=5`):
$$ 
|K| \le K_{max}
$$

*Nota técnica para el evaluador `ElementwiseProblem` (Pymoo)*:
El modelo genético asume en su matriz cromosoma el cumplimiento exacto de {1} y {2} por su arquitectura combinatoria transcrecida de PyMoo. Para proteger las métricas restrictivas de la Capacidad de Carga y la Ventana Cierre de Jornada, de no cumplirse se bifurca la visita enviando físicamente al camión de vuelta al almacén para arrancar un Nuevo Turno o un Nuevo Físico; y de existir una infracción al Límite Máximo de Vehículos Físicos {6}, se bloquea la solución genéticamente retornándola como vector matemáticamente **infactible** transversal para el GA (Restricción rígida $G$).
