# Modelado

Definición del grafo

---

### Conjuntos y Sub-Conjuntos

$K: \text{Camiones} \space k$

$T: \text{Intervalos de partición (tiempo)} \space t$

$I: \text{Conjunto de nodos clientes } i \in \{1, \dots, |I|\}$

$0: \text{Nodo Depósito Central (CD)}$

$K_{11}: \text{Subconjunto de camiones designados para el turno 1 y para la ruta 1 (Mañana)}$

$K_{12}: \text{Subconjunto de camiones designados para el turno 1 y para la ruta 2 (Tarde)}$

$K_{21}: \text{Subconjunto de camiones designados para el turno 2 y para la ruta 1 (Mañana)}$

$K_{22}: \text{Subconjunto de camiones designados para el turno 2 y para la ruta 2 (Tarde)}$

---

### Parametros

- $C^v: \text{Capacidad volumetrica real del camión} \space k \space [m^3]$
- $C^{m}: \text{Capacidad del peso del camión} \space k \space [kg]$
- $VP_{i}: \text{Volumen del pedido del cliente} \space i \space [m^3]$
- $PP_{i}: \text{Masa del pedido del cliente} \space i \space [kg]$
- $T_{ijt}: \text{Tiempo requerido para recorrer el arco }(i,j) \space [min]$
- $C_{ij}: \text{Costo de emplear el arco }(i,j)$
  - $C_{ij}= D_{ij}*S$
    - S = Cociente entre Costo de combustible y el rendimiento del vehiculo.
- $Z_t: \text{Valor numérico asociado a la partición de tiempo }t \text{ (ej. hora)}$
- $a_i: \text{Limite inferior de la ventana de tiempo del cliente i} \ [min]$
- $b_i: \text{Limite superior de la ventana de tiempo del cliente i} \ [min]$
- $aten: \text {Tiempo de atención fijo para clientes} \ [min]$
- $s_i: \text{Tiempo de atención variable para el cliente i} \ [min]$
- $s_0: \text{Tiempo de atención/servicio inicial en el CD} \ [min]$
- $d_{max}: \text{Duración máxima que puede tener una ruta}$
- $M: \text{Número positivo suficientemente grande (Big-M)}$
- $\alpha_w: \text{Peso de penalización por tiempo de espera en la función objetivo}$

---

### Variables

$X_{(i,t)jk} = \text{1 si }k \text{ utiliza el arco } ((i,t),j) \space | \space 0 \text{ En otro caso}$

$ts_{ik} =  \text{Tiempo de arribo del camión }k \text{ al cliente }i$

$W_{ik} = \max(0, \ a_i - ts_{ik}): \text{Tiempo de espera del camión } k \text{ en el cliente } i \text{ (antes de apertura de ventana)}$

---

### Función Objetivo

$$
\min: \underbrace{\sum_{i=1}^{I} \sum_{j=1}^{I} \sum_{t=1}^{T} \sum_{k=1}^K X_{(i,t),j,k} \cdot C_{i,j}}_{\text{Costo de transporte}} + \underbrace{\alpha_w \cdot \sum_{i \in I} \sum_{k \in K} W_{ik}}_{\text{Penalización por espera}}
$$

Donde $W_{ik} = \max(0, \ a_i - ts_{ik})$ captura el tiempo improductivo que experimenta el camión $k$ al llegar antes de la apertura de ventana del cliente $i$. El parámetro $\alpha_w$ controla la importancia relativa de minimizar la espera frente al costo de transporte.

---

### Restricciones

$$
\text{1. Cada camión debe llevar una carga inferior a la capacidad en volumen:}\\

\sum_{i=1}^{I} \sum_{j=0}^{I} \sum_{t=1}^{T} X_{(i,t),j,k}\ VP_i 

\leq C^v*0,8,\ \forall k \in K
$$

$$
\text{2. Cada camión debe llevar una carga inferior a la capacidad en masa:}\\ \sum_{i=1}^{I} \sum_{j=0}^{I} \sum_{t=1}^{T} X_{(i,t),j,k}\, PP_i \leq C^m,\ \forall k \in K
$$

$$
\text{3. Cada camión que llega a un cliente debe retirarse del mismo:}\\ 

\sum_{j=1}^{I} \sum_{t=1}^{T} X_{(i,t),j,k} - \sum_{j=1}^{I} \sum_{t=1}^{T} X_{(j,t),i,k} = 0,

\ \forall k \in K,\ \forall i \in I
$$

$$
\text{4. A cada cliente llega un único camión:}\\
\sum_{t=1}^{T}\sum_{k=1}^{K}\sum_{i=1}^{I}
X_{(i,t),j,k} = 1\ ,\ \ 
\forall j\in I
$$

$$
\text{5. Desde cada cliente sale un único camión:}\\

\sum_{t=1}^{T}\sum_{k=1}^{K}\sum_{j=1}^{I} X_{(i,t),j,k} = 1 \ , \ \ \forall i \in I
$$

$$
\text{6. Eliminación de subtours y actualización de tiempos (con TD):}\\

ts_{j,k} \geq
ts_{i,k} + s_i + aten + \sum_{t=1}^{T} (X_{(i,t),j,k} \cdot T_{ij,t}) - M(1-\sum_{t=1}^{T} X_{(i,t),j,k})
\ , \ \ \forall j \in I
, \ \ \forall i \in I \cup \{0\}
, \ \ \forall k \in K
$$

$$
\text{7. Ventanas de tiempo :}\\

\sum_{k=1}^{K} ts_{i,k} 

\geq
a_i \ , \ \ \forall i \in I
\\ \ \\
\sum_{k=1}^{K} ts_{i,k} 

\leq
b_i \ , \ \ \forall i \in I
$$

$$
\text{8. Tiempo de atención en el intervalo:}\\

-(1-\sum_{i=0}^{I} X_{(i,t),j,k})M
+ 480 + 60Z_t 
\leq 
ts_{j,k} 

\ ,\ \forall j \in I ,\ \forall t \in T ,\ \forall k \in K

\\ \ \\

ts_{j,k} 
\leq
540 + 60Z_t + (1-\sum_{i=0}^{I} X_{(i,t),j,k})M

\ ,\ \forall j \in I ,\ \forall t \in T ,\ \forall k \in K
$$

$$
\text{9. Nodo sin atención no tiene tiempos de atención:}\\

ts_{i,k} 
\leq
\sum_{j=1}^{I}\sum_{t=1}^{T} (X_{(j,t),i,k})M

\ , \ \forall k \in K, \ \forall i \in I
$$

$$
\text{10. Salida del CD - Turno 1 - Ruta 1:}\\

ts_{0,k} + s_0 = 540 
 \ \ \forall k \in K_{11}
$$

$$
\text{11. Salida del CD - Turno 1 - Ruta 2:}\\

ts_{0,k} + s_0 = 900
 \ \ \forall k \in K_{12}
$$

$$
\text{12. Salida del CD - Turno 2 - Ruta 1:}\\

\\
ts_{0,k} + s_0 = 660 

 \ \ \forall k \in K_{21}
$$

$$
\text{13. Salida del CD - Turno 2 - Ruta 2:}\\

\\
ts_{0,k} + s_0 = 1020

 \ \ \forall k \in K_{22}
$$

$$
\text{14. Descansos:}\\

\sum_{t=1}^{T}\sum_{j=1}^{I}\sum_{i=1}^{I} X_{(i,t),j,k}*T_{i,t,j}

\leq
d_{max} \ , \ \ \forall k \in K
$$

$$
\text{15. Vuelta CD - Turno 1 - Ruta 1:}\\
\sum_{t=1}^T \sum_{i=1}^I
X_{(i,t),0,k} \leq 1
 \ \ \forall k \in K_{11}
$$

$$
\text{16. Vuelta CD - Turno 1 - Ruta 2:}\\
\sum_{t=1}^T \sum_{i=1}^I
X_{(i,t),0,k} \leq 1
 \ \ \forall k \in K_{12}
$$

$$
\text{17. Vuelta CD - Turno 2 - Ruta 1:}
\\
\sum_{t=1}^T \sum_{i=1}^I
X_{(i,t),0,k} \leq 1
 \ \ \forall k \in K_{21}
$$

$$
\text{18. Vuelta CD - Turno 2 - Ruta 2:}
\\
\sum_{t=1}^T \sum_{i=1}^I
X_{(i,t),0,k} \leq 1
 \ \ \forall k \in K_{22}
$$

$$
\text{19. Naturaleza de las variables} 
\\

X_{(i,t),j,k} \in \{0, 1\} \ , 

\forall i,j \in I \cup \{0\} \ , \ 
\forall k \in K \  , \
\forall t \in T \ 

\\ \ \\

ts_{i,k} \geq 0 \ , 

\forall i \in I \cup \{0\} \ , \ 
\forall k \in K
$$

## Restricciones Inter-Cluster (Gestor de Flota Global)

Dado que las ecuaciones matemáticas base del sistema VRP se ejecutan particionadas a nivel geográfico por cada subconjunto de nodos (Clúster o $c \in C$), se introduce un modelo de emparejamiento post-optimización que exige que el límite físico de Vehículos Base instalados $N_{total}$ no sea quebrantado en un momento de tiempo simultáneo para el conjunto general.

Llamemos $K_c$ al conjunto de rutas matemáticas construidas y asignadas dentro del clúster $c$. 

$$
\text{20. Límite de Vehículos Homogéneos Instalados en Transporte Activo:} \\
\\ \ \\

| \bigcup_{c \in C} \{ \text{Camiones Físicos Activos en el instante } t \} | \le N_{total} \quad \forall t \in \text{Horizonte}
$$
