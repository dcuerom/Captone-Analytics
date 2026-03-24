# ⏱️ Funciones de Tiempo de Viaje (Fleischmann et al., 2004)

Este paquete (`modelo/funciones`) implementa la función de cálculo de tiempos de viaje con **variación temporal** (**Time-Varying Travel Times**). Fue modelada a partir de la metodología de:

> *Fleischmann, B., Gietz, M. y Gnutzmann, S. (2004). Time-Varying Travel Times in Vehicle Routing. Transportation Science, 38(2), 160-173.*

En Santiago, la velocidad del tráfico varía radicalmente dependiendo de la hora del día (hasta el doble de tiempo en hora punta respecto a la madrugada). Esta función **linealiza** estas transiciones para evitar saltos bruscos e inconsistentes en el modelo de optimización.

---

## 📐 Modelo Matemático (Ec. 2.2)

### Conceptos Clave

- $i, j$: Nodos origen y destino (clientes o depósito).
- $\tau_{ijk}$: Tiempo mínimo de viaje si se partiese desde $i$ en el intervalo $k$. Calculado como $d_{ij} / v_k$ (donde $d_{ij}$ es la distancia real sacada del sistema A* y $v_k$ es la velocidad del intervalo $k$).
- $Z_k$: Intervalos horarios del día. En este sistema **K=13** intervalos de 1 hora, cubriendo desde las **09:00 hasta las 21:00**.
- $t$: **Variable de decisión del modelo**, representando el *tiempo de partida* exacto desde el nodo $i$.
- $\delta$: Parámetro de suavizado (default: 0.25 horas = 15 minutos). Determina la longitud de la zona de "transición" entre un intervalo horario y el siguiente.

### La Función por Tramos

Para un tiempo de partida $t$ cualquiera dentro del horizonte, el tiempo real de viaje estimado $\tau_{ij}(t)$ se calcula así:

1. **Región Estable** (pleno intervalo horario $k$):

   $$
   \tau_{ij}(t) = \tau_{ijk} \quad \text{para } z_{k-1} + \delta \leq t \leq z_k - \delta
   $$
2. **Región de Transición** (Cerca de un cambio de hora $z_k$):

   $$
   \tau_{ij}(t) = \tau_{ijk} + (t - z_k + \delta) \cdot s_{ijk} \quad \text{para } z_k - \delta \leq t \leq z_k + \delta
   $$

   *Donde la pendiente es $s_{ijk} = (\tau_{ij,k+1} - \tau_{ijk}) / (2\delta)$.*

---

## 🛠️ Integración en PyMoo (VRP con Ventanas de Tiempo)

El mayor desafío técnico de implementar Fleischmann en un Algoritmo Genético es que la hora de partida $t_{ij}$ no es un valor final, sino que **se optimiza en tiempo de ejecución**.

### ¿Cómo opera el modelo?

1. **La Distancia es Estática**: Las matrices de distancia que obtuviste desde OpenStreetMap con A* en `grafo/routing.py` **no cambian**. Son constantes ingresadas al VRP.
2. **El Tiempo es Variable (Decisión)**: En PyMoo, tienes una variable de decisión continua `X` que albergará la secuencia de visitas (permutación) *y* el eventual tiempo de llegada/salida en cada nodo.

Por ejemplo, la propagación de tiempo funciona así:

$$
\text{Hora\_Llegada}_j = t_{ij} + \tau_{ij}(t_{ij})
$$

Luego, el camión debe esperar si llegó antes de la ventana, o será penalizado si llegó tarde:

$$
t_{jk} = \max(\text{Hora\_Llegada}_j, \, \text{Apertura\_Ventana}_j) + \text{Tiempo\_Servicio}_j
$$

### 🚀 Funciones Disponibles

El archivo provee dos versiones de la función, adaptadas a distintos contextos del proyecto:

#### 1. Consola o Reportes Rápidos (`tau_ij`)

Versión escalar clásica de Python. Recibe floats, devuelve un float. Útil para imprimir pruebas.

```python
from modelo.funciones import tau_ij

# Un arco de 12.5 km a las 17:30 de un Lunes (día=0)
tiempo_horas = tau_ij(distancia_km=12.5, t=17.5, dia_semana=0)
```

#### 2. Optimizador PyMoo (`tau_ij_vec`)

Cuando defines la clase `VRPModel(ElementwiseProblem)` o vectorize problem en PyMoo, la función `_evaluate` recibe docenas o miles de individuos (cromosomas) en masa. `tau_ij` no serviría porque PyMoo pasa **arrays de NumPy**. Evaluarlas con un *for loop* destruye el rendimiento.

Para esto existe **`tau_ij_vec`**, re-escrita pura en máscaras booleanas de NumPy para desempeño ultra-rápido:

```python
from modelo.funciones import tau_ij_vec

class VRPModel(ElementwiseProblem):
    def _evaluate(self, x, out, *args, **kwargs):
        # x[:, idx_t] es el numpy array (shape: pop_size) con TODAS las
        # horas de salida elegidas por el AG para un arco específico.
        tiempos_salida = x[:, idx_t]
      
        # Evaluamos para los 100~500 individuos en una sola operación matricial
        tiempos_viaje = tau_ij_vec(distancia_km=15.0, t=tiempos_salida, dia_semana=0)
      
        # Ahora `tiempos_viaje` es un array y sumamos
        llegada_j = tiempos_salida + tiempos_viaje
      
        # Penalizamos si llegada > 18.0 (6 PM)
        out["G"] = llegada_j - 18.0
```

---

## 📊 Matriz de Velocidades

Las velocidades ($v_k$) operan desde la tabla estática embebida en `tiempos_viaje.py`, donde las filas son la hora de inicio del intervalo (Ej. fila 14 = 14:00) y las columnas indican de Lunes a Domingo.

Si requieres probar un **escenario de alta congestión**, puedes usar el archivo `pruebas_sensibilidad/analisis_sensibilidad.py` para disminuir los coeficientes en esa matriz antes de inicializar a PyMoo.
