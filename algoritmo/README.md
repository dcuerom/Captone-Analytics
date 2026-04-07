# Módulo `algoritmo/` — Enfoque Híbrido CW + GA para CVRP

## Resumen

Este módulo resuelve el **Capacitated Vehicle Routing Problem (CVRP)** bajo un enfoque **híbrido memético**: combina una **heurística de construcción** (Clarke & Wright Savings) con un **Algoritmo Genético evolutivo** (GA via PyMoo). El objetivo es encontrar rutas de distribución de calidad superior en menos tiempo de cómputo que un GA puro.

---

## Archivos del Módulo

| Archivo | Rol |
|---|---|
| `cvrp_genetic.py` | Orquestador principal: parsea instancias, llama a la heurística, configura y ejecuta el GA híbrido, genera informes. |
| `heuristica_construccion.py` | Implementación del algoritmo de **Clarke & Wright Savings**. Genera la semilla inicial de alta calidad para el GA. |
| `genetic_algorithm.py` | Algoritmo genético original (pipeline real de despacho con datos geográficos). |
| `ga_vrp.py` | Variante auxiliar del GA para pruebas de sensibilidad. |

---

## Arquitectura del Enfoque Híbrido

```
┌──────────────────────────────────────────────────────────────────┐
│               disparar_rutina_cvrp_clasico()                     │
│                    (cvrp_genetic.py)                             │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
         parse_cvrp_instance()   →   df_nodos, depot_id, k_trucks, cap_peso
                        │
                        ▼
         calculate_euclidean_routing()  →  matriz_dist (32×32)
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│              resolver_cluster_cvrp()                          │
│                                                               │
│  ① Heurística [heuristica_construccion.py]                    │
│     clarke_wright_savings()  →  permutación semilla           │
│                                                               │
│  ② HeuristicSampling (PyMoo Custom Sampling)                  │
│     Individuo 0  : permutación de C&W  (alta calidad)         │
│     Individuos 1…49: permutaciones aleatorias (diversidad)    │
│                                                               │
│  ③ GA PyMoo                                                   │
│     · Crossover : OrderCrossover (OX)                         │
│     · Mutación  : InversionMutation                           │
│     · 200 generaciones, pop_size=50                           │
│                                                               │
│  ④ CVRPEuclideanProblem._evaluate()                           │
│     Decodifica permutación → rutas por camión                 │
│     Aplica restricciones: cap_peso, k_trucks, 21:00 hr        │
│     Fitness = Distancia total (con penalización de flota)     │
└───────────────────────────────────────────────────────────────┘
                        │
                        ▼
         generar_informes()  →  CSV Resumen + CSV Detalle
```

---

## ① Heurística de Construcción: Clarke & Wright Savings

**Archivo:** `heuristica_construccion.py`

### ¿Qué es?

El algoritmo de **Ahorros de Clarke & Wright (1964)** es una heurística clásica y altamente confiable para el CVRP. Construye rutas eficientes en tiempo polinomial, sin necesidad de búsqueda exhaustiva.

### Paso a Paso

**1. Rutas triviales de partida:**
Cada cliente $i$ comienza con su propia ruta dedicada:
$$\text{Depósito} \to i \to \text{Depósito}$$

**2. Cálculo del ahorro `saving(i, j)`:**
Si fusionamos las rutas de los clientes $i$ y $j$:
$$s(i,j) = d(\text{depot}, i) + d(\text{depot}, j) - d(i, j)$$

Un ahorro positivo significa que visitar $i$ y $j$ en una misma ruta es más eficiente que hacer dos viajes separados.

**3. Ordenar por ahorro descendente:**
Se priorizan las fusiones que generan mayor reducción de distancia.

**4. Fusión iterativa con restricción de capacidad:**
Se fusionan rutas mientras:
- Los clientes $i$ (final de su ruta) y $j$ (inicio de su ruta) están en rutas distintas.
- La carga combinada $\leq$ `cap_peso`.

**5. Resultado:** Una permutación de clientes que representa el orden de visita en todas las rutas, lista para ser entregada al GA.

---

## ② Sampler Híbrido: `HeuristicSampling`

**Definido en:** `cvrp_genetic.py`

```python
class HeuristicSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        X[0, :] = semilla_clarke_wright   # Warm start
        X[1:, :] = permutaciones_random   # Diversidad genética
```

Esta clase reemplaza al `PermutationRandomSampling` estándar de PyMoo. La clave es que **el primer individuo ya es una solución buena**, no una aleatoria. El resto de la población aún es aleatoria para mantener **diversidad genética** y evitar convergencia prematura.

---

## ③ Algoritmo Genético (PyMoo GA)

| Componente | Elección | Justificación |
|---|---|---|
| `OrderCrossover (OX)` | Crossover | Preserva sub-secuencias de visita (ideal para problemas de permutación tipo TSP/VRP) |
| `InversionMutation` | Mutación | Invierte segmentos aleatorios → exploración eficiente del espacio de rutas |
| `pop_size=50` | Población | Balance entre diversidad y costo computacional |
| `n_gen=200` | Generaciones | Suficiente para convergencia después del warm start |

---

## ④ Decodificador: `CVRPEuclideanProblem`

**Archivo:** `modelo/cvrp_pymoo_problem.py`

El GA opera sobre **permutaciones de índices** (ej. `[3, 0, 7, 1, ...]`). El decodificador convierte esa permutación en rutas reales mediante la siguiente lógica secuencial:

1. Sigue la permutación asignando clientes al camión activo.
2. Si agregar el cliente siguiente **excede la capacidad** o el **retorno llegaría después de las 21:00 hrs** → el camión vuelve al depósito y se abre una nueva ruta.
3. Cada ruta asignada a un camión físico respeta los **turnos operativos** (`K11`, `K12`, `K21`, `K22`).
4. El **fitness** del individuo es la distancia total acumulada en todas las rutas (penalizada si se usan más de `k_trucks` camiones).

---

## Ventajas del Enfoque Híbrido vs. GA Puro

| Criterio | GA Puro | Híbrido CW + GA |
|---|---|---|
| **Calidad inicial** | Aleatoria, generalmente muy mala | Alta — C&W garantiza factibilidad de capacidad |
| **Velocidad de convergencia** | Lenta (muchas generaciones para "aprender lo básico") | Rápida — parte desde una solución ~80% óptima |
| **Riesgo de infactibilidad inicial** | Alto (penalizaciones dominan las primeras generaciones) | Bajo (al menos 1 individuo es factible desde gen 0) |
| **Diversidad** | Alta (pero con individuos poco útiles) | Alta (resto de la población sigue siendo aleatoria) |
| **Estabilidad entre corridas** | Variable | Más estable (misma semilla C&W fija el punto de partida) |

---

## Cómo Ejecutar

```bash
# Desde la raíz del proyecto con el entorno virtual activo:
python algoritmo/cvrp_genetic.py "Instancias de Prueba VRP/A/A-n32-k5.vrp"
```

### Salida esperada:
```
=== INICIANDO CVRP CLÁSICO (TSPLIB, Operativa Constreñida) ===
Instancia: A-n32-k5
Dimensión: 32, Capacidad QA: 100, Vehículos Meta: 5
Generada matriz Euclidiana exacta para 32 nodos.
      [Heurística] Ejecutando Clarke & Wright Savings para warm start...
      [PyMoo] Optimizando Cluster Global (31 clientes) [Híbrido CW + GA]...
      PyMoo Terminado. Distancia Óptima Aproximada = XXXX.XX

>>>> Optimo Encontrado CVRP Consolidado (Total Distancia Grilla): XXXX.XX
>>>> Tiempo de Cómputo Total: XX.XX segundos

[Éxito] Reportes Exportados:
 -> resultados/cvrp/CVRP_A-n32-k5_Resumen_YYYYMMDD_HHMMSS.csv
 -> resultados/cvrp/CVRP_A-n32-k5_Detalle_YYYYMMDD_HHMMSS.csv
```

---

## Referencias

- Clarke, G. & Wright, J.W. (1964). *Scheduling of Vehicles from a Central Depot to a Number of Delivery Points*. Operations Research, 12(4), 568–581.
- Blank, J. & Deb, K. (2020). *pymoo: Multi-Objective Optimization in Python*. IEEE Access.
- Laporte, G. (1992). *The Vehicle Routing Problem: An overview of exact and approximate algorithms*. European Journal of Operational Research.
