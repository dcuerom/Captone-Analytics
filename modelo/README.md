# 🧊 Módulo `modelo/` — Formalización Computacional TDVRPTW

Este módulo contiene la implementación computacional rigurosa del **Modelo Matemático TDVRPTW** formalizado en `modelo.md`. Originalmente concebido con Pyomo (`modelo.py`), el enfoque principal actual es la resolución metaheurística utilizando Algoritmos Genéticos a través de la librería **PyMoo** (`pymoo_problem.py`).

## 🧬 Traspaso Lógico de `modelo.md` a `pymoo_problem.py`

Debido a la altísima complejidad combinatoria del ruteo de vehículos dependiente del tiempo con ventanas de tiempo (TDVRPTW), el modelo matemático estricto fue adaptado a una estructura de evaluación heurística en la clase `TDVRPTWProblem` heredada de `ElementwiseProblem` en PyMoo.

A continuación se detalla cómo se representaron los elementos teóricos de `modelo.md` en el código de evaluación:

### 1. Variables de Decisión (Enrutamiento)
- **Modelo Matemático:** Uso de extensa matriz binaria $X_{(i,t)jk}$ para rastrear de, hacia, y con qué camión y en qué momento puntual se viaja.
- **PyMoo (`x`):** Se simplificó utilizando un **Cromosoma de Permutación** de enteros (de $0$ a $n-1$). Cada gen representa el ID de un cliente a visitar (mapeado en `clientes_ids`). El orden de los genes dicta la ruta subyacente de visitas. Con esta simple permutación, las **restricciones espaciales estrictas de conservación de flujo y prohibición de sub-tours** (Restricciones 3, 4, 5 y 6) **quedan implícitamente satisfechas** (cada cliente es visitado una sola vez y no hay ciclos aislados).

### 2. Función Objetivo (Costo)
- **Modelo Matemático:** $\text{min: } \sum X_{(i,t),j,k}C_{i,j}$ (minimizar el costo de ruta iterativo en función de $D_{ij} \times S$).
- **PyMoo (`out["F"]`):** El programa decodifica la ruta, calcula la distancia secuencial completa (`dist_total_m`) considerando tanto los tramos hacia clientes como los retornos al depósito, y se multiplica por el factor de rendimiento (`factor_s`). El resultado de aptitud final a MINIMIZAR es inyectado en `out["F"]` siguiendo el estándar funcional de PyMoo.

### 3. Restricciones de Capacidad: Volumen y Masa (Restricciones 1 y 2)
- **Modelo Matemático:** Restringe estrictamente que la carga en un camión deba ser $\leq C^v$ y $\leq C^m$.
- **PyMoo (Split Dinámico):** Para favorecer una búsqueda en el espacio de soluciones sin descartar inmensas cantidades de individuos infactibles, las capacidades NO son "Hard Constraints" que invaliden al individuo. En su lugar, el algoritmo lee secuencialmente el cromosoma acumulando el volumen (`vol_actual`) y peso (`peso_actual`). **Si visitar el siguiente cliente excede `cap_vol_cm3` o `cap_peso_g`, se desencadena un "Split Dinámico"**: se simula que el camión actual cierra viaje regresando al depósito (`depot_id`), y sale un SEGUNDO camión a la misma hora desde el depósito a visitar a ese cliente. El castigo al "fitness" se refleja como **mayor distancia total** por los múltiples regresos y partidas superpuestas.

### 4. Ventanas de Tiempo y Tráfico dependiente del tiempo (Restricciones 7 y 8)
- **Modelo Matemático:** Precisa acotar matemáticamente variables $ts$ bajo los paramétros [$a_i$, $b_i$].
- **PyMoo (Penalizaciones explícitas `out["G"]`):** 
  - El tiempo de trayecto asimétrico y variante con el tráfico se deduce mediante la función vectorial `tau_ij_vec(distancia, tiempo, dia_semana)`. 
  - **Llegada Temprana ($t\_llegada\_real < a_i$):** El camión se detiene a la espera obligatoria hasta que inicie el bloque de ventana temporal del cliente (`t_espera`).
  - **Llegada Tardía ($t\_inicio\_servicio > b_i$):** Implica un incumplimiento de plazos con el cliente. Siendo un aspecto muy crítico, todo tiempo excedido se suma exhaustivamente en `t_violacion`.
  - **Infactibilidad:** Toda la sumatoria de incumplimientos de plazos de un cromosoma entero se deposita bajo la variable de restricción `out["G"]`. En la arquitectura PyMoo, si un individuo posee un `out["G"] > 0` será marcado como **Infactible** (Hard Constraint), promoviendo que las cruzas prioricen a los camiones que siempre llegan a tiempo.

### 5. Tiempos de Servicio
- **Modelo Matemático:** Constante aditiva que influye en los arcos de partida.
- **PyMoo:** Simulado insertando 10 minutos empíricos (`self.aten_fijo`) sumados al $t\_inicio\_servicio$ antes de transitar al próximo cliente, empujando la hora del reloj `t_actual` lógicamente.

---

## Estandarización Físico-Métrica

Para evitar errores de conversión e inconsistencias lógicas entre submódulos, TODO parámetro introducido y calculado en los archivos del modelo DEBE cumplir con las siguientes magnitudes absolutas:

1.  **Tiempo:** Se mide estrictamente en **Minutos** (`min`).
2.  **Volumen:** Se mide estrictamente en **Centímetros Cúbicos** (`cm3`).
3.  **Masa / Peso:** Se mide estrictamente en **Gramos** (`g`).
4.  **Distancia Espacial:** Se mide estrictamente en **Metros** (`m`).
