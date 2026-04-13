# Anexo: Documentación de Uso de Inteligencia Artificial

## Prompts y Respuestas — Proyecto Capstone Analytics

**Proyecto:** Optimización Logística con Algoritmo Genético (TDVRPTW)
**Equipo:** Ingeniería Industrial — UDD
**Herramienta IA utilizada:** Antigravity (Google DeepMind) — Asistente de código IA
**Período documentado:** Abril 2026

---

> **Nota sobre el uso de IA en este proyecto:**Conforme al marco académico establecido, el uso de IA en este proyecto tuvo dos propósitos fundamentales:
>
> 1. **Generación de código Python**: Los integrantes del equipo actuaron como ingenieros industriales que definieron las especificaciones funcionales del sistema (qué debía hacer el código), mientras que la IA generó la implementación técnica. Cada pieza de código fue revisada y validada por el equipo.
> 2. **Tratamiento de datos**: La IA asistió en el procesamiento y análisis de grandes volúmenes de datos, siempre bajo las instrucciones y supervisión del equipo.
>
> Todo el contenido de este anexo es el registro fiel de las conversaciones sostenidas con la herramienta de IA.

---

---

## SECCIÓN I: MODELAMIENTO MATEMÁTICO Y EVALUACIÓN DEL MODELO TDVRPTW

**Conversación de referencia:** *"Evaluating TDVRPTW Mathematical Model"*
**Fecha:** Abril 2026
**Propósito:** Generar el modelo matemático formal del problema TDVRPTW y su integración con el evaluador PyMoo.

---

### Prompt 1.1 — Solicitud de implementación del modelo híbrido Pyomo + PyMoo

**Contexto previo:** El equipo ya contaba con una estructura Pyomo (`modelo/modelo.py`) y necesitaba incorporar un evaluador de alta performance para el Algoritmo Genético.

**Prompt del usuario:**

> Necesito que implementes el modelo de optimización híbrido integrando Pyomo con PyMoo. El modelo debe:
>
> - Mantener la estructura formal de Pyomo como referencia algebraica del negocio
> - Crear un nuevo archivo `modelo/pymoo_problem.py` que implemente `TDVRPTWProblem(Problem)`
> - El evaluador debe usar `tau_ij_vec()` para vectorizar los cálculos de tiempo de viaje
> - Las restricciones de capacidad y ventanas de tiempo deben implementarse como hard constraints en `out["G"]`
> - La función objetivo `out["F"]` debe minimizar la distancia total (en metros) × factor S

**Respuesta del asistente IA:**

El asistente propuso el siguiente plan de implementación:

**Plan de Implementación: Integración Híbrida Pyomo + PyMoo**

**1. Dualidad del Planteamiento (`modelo/`)**

- **Mantener Pyomo**: El archivo actual `modelo/modelo.py` conserva su estructura formal `ConcreteModel` exacta, proveyendo un esqueleto de referencia de negocio.
- **[NUEVO] `modelo/pymoo_problem.py`**:
  - Implementará `TDVRPTWProblem(Problem)`. Se usará `Problem` (Vectorizado) en vez de `ElementwiseProblem` para aprovechar masivamente `tau_ij_vec()`.
  - **Uso de `tau_ij_vec`**: El método `_evaluate(self, x, out)` iterará sobre los tramos del recorrido, pero procesará a *toda la población (cientos de individuos) en paralelo matriz a matriz*.
  - **Restricciones Hard**:
    - Las violaciones de capacidad o impuntualidades de ventana (pasado el límite `b`) dictarán penalizaciones físicas en `out["G"]`, obligando al Algoritmo a rechazar individuos infactibles usando las reglas de dominancia de Deb.
    - `out["F"]` permanecerá dictaminando puramente la sumatoria minimizada de la distancia en metros × factor S.

**2. Refactorización en `algoritmo/`**

- **[MODIFY] `algoritmo/genetic_algorithm.py`**: Se orquestará usando la librería oficial `from pymoo.algorithms.soo.nonconvex.ga import GA`, inyectando la matriz de clientes y la configuración a `TDVRPTWProblem`, y generando los cruces empleando `OrderCrossover()` nativo de PyMoo.
- **[MODIFY] `algoritmo/tabu_search.py`**: Se mantendrá su ciclo nativo, pero al requerir ponderar la bondad de un vecino, invocará centralizadamente al simulador inyectando el cromosoma al vector de `TDVRPTWProblem().evaluate([cromosoma])`. Esto asegura consistencia 1:1 en las penalizaciones de ambos mundos.

**3. Generación de Reportes**

Ambos procesos dictarán los resultados usando sus mejores subproductos factibles, vaciando el flujo en `resultados/rutas/` de manera legible.

---

### Prompt 1.2 — Solicitud de penalización por espera, salida flexible y exportación CSV

**Contexto previo:** Tras las primeras ejecuciones, el equipo detectó que algunos camiones acumulaban hasta 463 minutos de espera (Vehículo 16) por tener hora de salida fija del depósito, lo que representaba una ineficiencia operacional importante.

**Prompt del usuario:**

> Quiero implementar 3 cambios en el modelo:
>
> 1. **Penalización por tiempo de espera**: Si un camión llega antes de que abra la ventana del cliente, ese tiempo de espera debe penalizar la función objetivo con un parámetro configurable `alpha_espera`.
> 2. **Salida flexible desde el depósito**: En vez de forzar a todos los camiones K11 a salir exactamente a las 09:00, quiero que la hora de salida sea flexible dentro del intervalo del turno, usando una heurística JIT (Just-In-Time).
> 3. **Exportación a CSV**: Los reportes deben dejar de generarse en `.md` y pasar a dos archivos `.csv` separados: uno de resumen de camiones y otro de detalle de paradas.

**Respuesta del asistente IA:**

La IA generó un plan de implementación en tres partes:

**Cambio 1 — Nueva Función Objetivo con Penalización por Espera:**

Redefinición matemática:

```
min: ΣΣ X_(i,t),j,k · C_ij  +  α_w · ΣΣ W_ik
```

Donde `W_ik = max(0, a_i - ts_ik)` es el tiempo de espera del camión `k` en el cliente `i`, y `α_w` es un peso de penalización configurable.

Cambios en `pymoo_problem.py`:

- Agregar parámetro `alpha_espera` al constructor (default: `1.0`)
- Acumular el total de espera en el bucle `_evaluate`
- Sumar a `out["F"]`: `F = (dist_total * S) + costo_vehiculos + (alpha_espera * espera_total)`

**Cambio 2 — Salida Flexible (Restricciones 10'-13'):**

Las restricciones de salida fija pasan a ser desigualdades de intervalo:

```
K11: 540 ≤ ts_0,k + s_0 ≤ 900   (09:00 – 15:00)
K12: 900 ≤ ts_0,k + s_0 ≤ 1260  (15:00 – 21:00)
K21: 660 ≤ ts_0,k + s_0 ≤ 1020  (11:00 – 17:00)
K22: 1020 ≤ ts_0,k + s_0 ≤ 1380 (17:00 – 23:00)
```

Implementación: Nueva función `_calcular_salida_optima(ruta_clientes, turno_intervalo)` que busca la ventana de apertura más temprana entre todos los clientes asignados al turno, resta el tiempo de viaje estimado desde el depósito hasta el primer cliente, y clampa el resultado al intervalo del turno `[lb, ub]`.

**Cambio 3 — Exportación a dos archivos CSV:**

- `gestor.py` reemplaza la generación de Markdown por la construcción de dos DataFrames de Pandas.
- Se exportan `resumen_camiones_*.csv` y `detalle_paradas_*.csv`.

**Archivos modificados:**

| Archivo                            | Tipo de cambio                                                 |
| ---------------------------------- | -------------------------------------------------------------- |
| `modelo/modelo.md`               | MODIFY — Nueva F.O., restricciones 10'-13'                    |
| `modelo/pymoo_problem.py`        | MODIFY — alpha_espera, intervalos de turno, salida óptima    |
| `algoritmo/genetic_algorithm.py` | MODIFY — Pasar alpha_espera al constructor                    |
| `gestion_flota/gestor.py`        | MODIFY — Reemplazar generación Markdown por DataFrames + CSV |

**Validación realizada:**

```bash
python3 -m py_compile modelo/pymoo_problem.py  # ✅
python3 -m py_compile algoritmo/genetic_algorithm.py  # ✅
python3 -m py_compile gestion_flota/gestor.py  # ✅
```

---

### Resumen de lo construido en esta sesión

El asistente IA generó e implementó:

1. La clase `TDVRPTWProblem` heredando de `ElementwiseProblem` (PyMoo) con vectorización mediante `tau_ij_vec()` y hard constraints configurables.
2. La integración del GA de PyMoo con `OrderCrossover`, mutación por inversión y muestreo permutacional.
3. La penalización por tiempo de espera en la función objetivo y la lógica de salida flexible JIT.
4. El sistema de exportación a CSV organizado en resumen y detalle de paradas.

---

---

## SECCIÓN II: ANÁLISIS DE OPERACIONES DE FLOTA — ASIGNACIÓN DINÁMICA DE TURNOS

**Conversación de referencia:** *"Analyzing Fleet Management Operations"*
**Fecha:** 13 de Abril, 2026
**Propósito:** Eliminar la asignación forzada de turnos de mañana (K11) para entregas de tarde, implementando una selección dinámica del turno según las ventanas del primer cliente de cada ruta.

---

### Prompt 2.1 — Corrección de asignación de turno forzada

**Contexto previo:** Al revisar los resultados del algoritmo genético, el equipo detectó que el sistema asignaba el turno K11 (mañana) a rutas cuyo primer cliente tenía ventanas de tiempo en la tarde (ej. 14:00 hrs). Esto generaba tiempos de espera excesivos e incoherencia operacional.

**Prompt del usuario:**

> El algoritmo está asignando el turno K11 (mañana, salida 09:00) a rutas que deberían pertenecer al turno de tarde (K21 o K22). El problema es que la lógica actual siempre inicia en K11 independientemente de cuándo abren los clientes. Necesito que el algoritmo determine dinámicamente el turno óptimo de inicio (K11, K12, K21, o K22) mirando la ventana de tiempo del primer cliente de cada ruta para minimizar el tiempo ocioso y que la asignación sea coherente con los horarios reales de entrega.

**Respuesta del asistente IA:**

La IA analizó el código e identificó que en `pymoo_problem.py` la lógica de evaluación siempre iniciaba asignando el primer turno disponible de forma secuencial sin considerar cuándo debía atenderse el primer cliente. La solución propuesta fue:e

**Heurística de Selección Dinámica de Turno:**

```python
def _seleccionar_turno_inicial(self, primer_cliente_ventana_apertura):
    """
    Selecciona el turno de despacho más adecuado en función de
    la ventana de apertura del primer cliente de la ruta.
  
    Retorna el índice de plantilla de turno (turno_tipo, ruta_idx)
    que minimiza el tiempo de espera del camión al llegar.
    """
    mejor_turno = None
    menor_espera = float('inf')
  
    for tipo_idx, rutas in enumerate(self.plantillas_turnos):
        for ruta_idx, (lb, ub) in enumerate(rutas):
            # Tiempo de salida óptimo dentro del intervalo
            t_salida = max(lb, primer_cliente_ventana_apertura - t_viaje_estimado)
            t_salida = min(t_salida, ub)
            espera = max(0, primer_cliente_ventana_apertura - (t_salida + t_viaje_estimado))
            if espera < menor_espera:
                menor_espera = espera
                mejor_turno = (tipo_idx, ruta_idx)
  
    return mejor_turno
```

**Resultado:** La lógica de evaluación ahora selecciona dinámicamente el turno que minimiza el tiempo de espera inicial, asignando automáticamente turnos de tarde (K21/K22) a rutas con clientes vespertinos.

**Archivos modificados:** `modelo/pymoo_problem.py`, `algoritmo/genetic_algorithm.py`

---

---

## SECCIÓN III: OPTIMIZACIÓN HÍBRIDA Y PARALELIZACIÓN

**Conversación de referencia:** *"Hybrid Optimization And Parallelization"*
**Fecha:** Abril 2026
**Propósito:** Migrar de un Algoritmo Genético puro (población aleatoria) a un paradigma híbrido que usa el Algoritmo de Ahorros de Clarke-Wright como solución semilla, y paralelizar la optimización de clústeres usando multi-procesamiento.

---

### Prompt 3.1 — Implementación del paradigma híbrido Savings + GA

**Contexto previo:** El equipo observó que el Algoritmo Genético, al partir de poblaciones completamente aleatorias, tardaba demasiado en converger y en ocasiones no encontraba soluciones factibles. Se buscaba una estrategia constructiva que sirviera como punto de partida de alta calidad.

**Prompt del usuario:**

> Quiero mejorar el rendimiento del GA implementando un paradigma híbrido de dos fases:
>
> 1. **Fase Constructiva**: Implementar el Algoritmo de Ahorros de Clarke-Wright adaptado al TDVRPTW que genere una solución inicial factible respetando capacidades de peso, volumen y duración máxima de ruta.
> 2. **Fase de Mejora**: Usar esa solución como la "semilla" (primer individuo) de la población inicial del GA.
> 3. **Paralelización**: Reemplazar el bucle secuencial de clústeres por procesamiento paralelo usando todos los cores disponibles de la CPU.
>
> Para el algoritmo de ahorros, calcula `s(i,j) = d(depot,i) + d(depot,j) - d(i,j)` para todo par de clientes. Ordena descendente y fusiona rutas respetando capacidades.

**Respuesta del asistente IA:**

La IA propuso e implementó el siguiente plan, con dos preguntas de revisión importantes:

> ⚠️ **Revisión requerida — Hard constraints en savings**: El Algoritmo de Ahorros (Clarke-Wright) producirá una solución constructiva que respeta las restricciones de capacidad y duración máxima de ruta. Las ventanas de tiempo se verifican pero NO se validan como hard-constraint en la fase de savings (eso lo maneja el GA posterior). ¿Es aceptable este enfoque?
>
> ⚠️ **Revisión requerida — Workers**: Para la paralelización se usará `concurrent.futures.ProcessPoolExecutor`. La cantidad de workers será `os.cpu_count()` (todos los cores disponibles). ¿Deseas limitar la cantidad máxima de workers?

**Módulos propuestos e implementados:**

**`algoritmo/savings.py` (NUEVO):**

```python
def clarke_wright_savings(df_cluster, matriz_dist, depot_id, 
                          cap_vol_cm3, cap_peso_g, d_max_min):
    """
    Algoritmo de Ahorros de Clarke-Wright adaptado al TDVRPTW.
  
    1. Calcula matriz de ahorros: s(i,j) = d(depot,i) + d(depot,j) - d(i,j)
    2. Ordena pares por savings descendente
    3. Fusiona rutas iterativamente respetando:
       - Capacidad de volumen (cap_vol_cm3)
       - Capacidad de peso (cap_peso_g)
       - Duración máxima de ruta (d_max_min)
       - Solo fusiona extremos de ruta (primer o último cliente)
    4. Retorna lista de rutas convertida en permutación para el GA
    """
```

**`algoritmo/genetic_algorithm.py` (MODIFICADO):**

```python
class SavingsSeededSampling(Sampling):
    """
    Muestreo personalizado para PyMoo que inyecta la solución
    del algoritmo de ahorros como primer individuo de la población.
    """
    def __init__(self, savings_permutation):
        super().__init__()
        self.savings_perm = savings_permutation
  
    def _do(self, problem, n_samples, **kwargs):
        X = np.full((n_samples, problem.n_var), 0, dtype=int)
        # Primer individuo: solución de savings
        X[0] = self.savings_perm
        # Resto: permutaciones aleatorias
        for i in range(1, n_samples):
            X[i] = np.random.permutation(problem.n_var)
        return X

# Paralelización con ProcessPoolExecutor
with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
    futures = {
        executor.submit(resolver_cluster, cluster_id, df_c, params): cluster_id
        for cluster_id, df_c in clusters.items()
    }
    for future in as_completed(futures):
        resultado = future.result()
        resultados.append(resultado)
```

**Resultados verificados en prueba (muestra 20 pedidos):**

| KPI                     | Valor      |
| ----------------------- | ---------- |
| Función Objetivo Total | 211,433.41 |
| % Entregas a Tiempo     | 100.0%     |
| Distancia Total         | 224.53 km  |
| Vehículos Usados       | 4          |

**Archivos creados/modificados:**

| Archivo                            | Acción                                          |
| ---------------------------------- | ------------------------------------------------ |
| `algoritmo/savings.py`           | NUEVO — Implementación Clarke-Wright           |
| `algoritmo/genetic_algorithm.py` | MODIFICADO — Semilla savings + paralelismo      |
| `PIPELINE_GLOBAL.md`             | MODIFICADO — Documentación del nuevo paradigma |

---

---

## SECCIÓN IV: RELAJACIÓN DE RESTRICCIONES DE VENTANA DE TIEMPO

**Conversación de referencia:** *"Relaxing Time Window Constraints"*
**Fecha:** 8 de Abril, 2026
**Propósito:** Implementar una tolerancia de 30 minutos en el cierre de las ventanas de tiempo de los clientes, y luego migrar de restricción de "tiempo de conducción" a "duración total del turno" para evitar el problema de Shift Spanning.

---

### Prompt 4.1 — Relajación de 30 minutos en ventanas de tiempo

**Contexto previo:** Al ejecutar el algoritmo con los datos reales, se observaba que muchas entregas eran marcadas como violaciones de ventana por llegar pocos minutos tarde (1-10 minutos). El equipo consideró que una tolerancia de 30 minutos era operacionalmente razonable.

**Prompt del usuario:**

> Necesito relajar las ventanas de tiempo de los clientes en 30 minutos adicionales en el cierre. Es decir, si la ventana de un cliente es [09:00, 10:00], ahora se debe considerar como [09:00, 10:30]. Esto debe:
>
> 1. Actualizarse en la documentación del modelo (`modelo.md`) en la Restricción 7
> 2. Implementarse en el evaluador `pymoo_problem.py` modificando el cálculo de `t_violacion`
> 3. Reflejarse en el reporte de diagnóstico de `genetic_algorithm.py` mostrando claramente la ventana relajada

**Respuesta del asistente IA:**

**Cambios implementados:**

**1. `modelo/modelo.md` — Restricción 7 actualizada:**
La documentación matemática ahora refleja explícitamente el término `+ 30` en el límite superior de la ventana:

```
Restricción 7: ts_ik + s_i ≤ b_i + 30  ∀ i ∈ I, k ∈ K
```

**2. `modelo/pymoo_problem.py` — Evaluación con tolerancia:**

```python
# ANTES
if t_inicio_servicio > b_p:
    t_violacion = t_inicio_servicio - b_p

# DESPUÉS
if t_inicio_servicio > (b_p + 30.0):
    t_violacion = t_inicio_servicio - (b_p + 30.0)
```

Adicionalmente, el diccionario `detalle_nodos` ahora incluye la clave `b_ventana_relaxed` para trazabilidad (`b_ventana_relaxed = b_p + 30.0`).

**3. `algoritmo/genetic_algorithm.py` — Diagnóstico mejorado:**

```python
# ANTES
print(f"        - {nid}: Servicio a las {h_lleg} | Cierre ventana: {h_cierre} | Exceso: {viola:.0f} min")

# DESPUÉS
print(f"        - {nid}: Servicio a las {h_lleg} | Cierre (+30m): {h_cierre_rel} | Exceso: {viola:.0f} min")
```

---

### Prompt 4.2 — Corrección del problema de Shift Spanning (turno que se extiende)

**Contexto previo:** Tras las ejecuciones iniciales, el equipo detectó un comportamiento anómalo: camiones clasificados como K11 (mañana) realizaban entregas vespertinas porque la restricción solo medía tiempo de conducción (trayecto A→B) y no incluía tiempos de espera. Un camión podía salir a las 09:00, esperar 5 horas frente a un cliente, atenderlo en la tarde y seguir siendo K11.

**Prompt del usuario:**

> El algoritmo tiene un problema que llamo "shift spanning": un camión de turno K11 (09:00) puede estar esperando fuera de un cliente hasta las 15:00 y el sistema lo sigue catalogando como K11 porque solo mide el tiempo de conducción, no el tiempo total del turno.
>
> Necesito cambiar la restricción de control de duración de "tiempo máximo de conducción" a "duración máxima del turno completo" (incluyendo tiempos de espera). Si duración total (desde salida hasta regreso estimado al depósito) > 5 horas (300 min), el camión debe cerrar esa ruta y comenzar una nueva con el siguiente turno disponible.

**Respuesta del asistente IA:**

**Diagnóstico del problema:**

> En `pymoo_problem.py`, la condición que fuerza a un camión a regresar al depósito y "cerrar" su ruta K11 es:
> `if (vol_actual + vol_p > self.cap_vol_cm3) o (tiempo_conduccion_estimado > self.d_max_min):`
>
> El problema es que `tiempo_conduccion_estimado` **solo suma los tiempos de viaje (viajar de A a B)**. Un camión puede salir a las 09:00, viajar 10 minutos, quedarse esperando 5 horas parado afuera de un cliente de la tarde, atenderlo, y volver a las 15:00. Para el código de ese entonces, ese camión solo "trabajó/condujo" 20 minutos, así que no rompe la regla de los 300 minutos y el algoritmo lo sigue catalogando bajo su etiqueta original: K11.

**Cambio propuesto en `pymoo_problem.py`:**

```python
# ANTES: Solo mide tiempo de conducción
if (vol_actual + vol_p > self.cap_vol_cm3) or \
   (tiempo_conduccion_estimado > self.d_max_min):
    # cierra ruta y abre nueva

# DESPUÉS: Mide duración total del turno
t_retorno_estimado = t_fin_tent + t_viaj_ret_tent
duracion_turno_estimada = t_retorno_estimado - cam_t_salida

if (vol_actual + vol_p > self.cap_vol) or \
   (duracion_turno_estimada > self.d_max_min):
    # cierra ruta y abre nueva
```

**Impacto documentado en `modelo.md` — Restricción 14:**

La restricción matemática se actualizó para reflejar que la diferencia entre la salida del depósito y el retorno estimado (incluyendo esperas) debe ser ≤ `d_max`:

```
Restricción 14 (actualizada): 
ts_fin_k - ts_inicio_k ≤ d_max   ∀ k ∈ K
(donde ts_fin_k incluye el tiempo de regreso al depósito)
```

**Aviso importante planteado por la IA:**

> ⚠️ Si la ventana máxima de un turno (ej. `d_max_min` = 300 min / 5 horas) se vuelve estricta, el algoritmo creará rutas más fragmentadas y utilizará más saltos a "K12" u otros camiones, ya que la espera cuenta como tiempo del turno. ¿Te parece correcto que limitaremos toda la duración de la salida a 300 minutos?

El equipo confirmó que esto era correcto y alineado con la realidad operacional.

---

---

## SECCIÓN V: SCRAPING DE DATOS — PORTAL INMOBILIARIO (BODEGAS)

**Conversación de referencia:** *"Scraping Portal Inmobiliario Data"*
**Fecha:** Abril 2026
**Propósito:** Extraer datos de bodegas en venta en la Región Metropolitana desde Portal Inmobiliario para su análisis como potenciales centros de distribución. Este es un caso de uso de IA para **tratamiento de datos**.

---

### Prompt 5.1 — Desarrollo del scraper con Playwright

**Contexto previo:** El equipo necesitaba recopilar información georreferenciada de bodegas disponibles en la RM para alimentar el análisis de ubicación del centro de distribución. Los métodos directos (requests/BeautifulSoup) fueron bloqueados por el sistema anti-bot del portal.

**Prompt del usuario:**

> Necesito un scraper para Portal Inmobiliario que extraiga información de bodegas en venta en la Región Metropolitana. El scraper debe:
>
> 1. Usar Playwright con Chromium para evitar bloqueos anti-bot
> 2. Navegar a la URL de búsqueda de bodegas
> 3. Identificar y visitar uno por uno cada enlace de bodega listado
> 4. Extraer por cada bodega: ID, Dirección, Latitud, Longitud, Precio de venta, Dimensiones (superficie)
> 5. Guardar todo en un archivo `bodegas_rm.csv` usando pandas
>
> Crea un entorno virtual en `/home/dacmxo/Desktop/udd/bodega/` e instala las dependencias necesarias.

**Respuesta del asistente IA:**

La IA propuso el siguiente plan y ejecutó la implementación:

**Entorno y Dependencias:**

```bash
# Crear entorno virtual
python3 -m venv /home/dacmxo/Desktop/udd/bodega/venv

# Instalar dependencias
./venv/bin/pip install playwright pandas

# Instalar navegador Chromium
./venv/bin/playwright install chromium
```

**Script `scraper.py` generado:**

El script implementa:

1. Apertura de navegador Chromium en modo headless con Playwright
2. Navegación a la URL de búsqueda de Portal Inmobiliario
3. Identificación de todos los links individuales de bodegas listadas
4. Visita secuencial de cada enlace para extraer: ID, Dirección, Precio, Superficie, Coordenadas
5. Almacenamiento progresivo en `bodegas_rm.csv` via pandas

**Desafío encontrado:** Portal Inmobiliario oculta las coordenadas exactas y entrega puntos predeterminados (coordenadas centroidales de la dirección, no exactas).

**Solución implementada por la IA:** Se creó un script adicional `process_geocoder.py` que:

- Lee cada dirección extraída del CSV
- La pasa al motor de geocodificación de ArcGIS (via `geocode_orders` de `Captone-Analytics/grafo/geocoder.py`)
- Reasigna las coordenadas reales georeferenciadas
- Agrega una columna nueva de `Comuna` parseada desde la dirección

---

### Prompt 5.2 — Geocodificación y enriquecimiento del dataset

**Prompt del usuario:**

> Las coordenadas que extrae el scraper son centroidales (Portal Inmobiliario las oculta). Necesitas usar el geocoder que ya tenemos en el proyecto (`Captone-Analytics/grafo/geocoder.py`) para geocodificar cada una de las 230 direcciones extraídas y reemplazar las coordenadas del CSV con las coordenadas reales. También agrega una columna de "Comuna" parseada de la dirección.

**Respuesta del asistente IA:**

La IA generó el script `process_geocoder.py`:

```python
from Captone-Analytics.grafo.geocoder import geocode_orders
import pandas as pd

df = pd.read_csv('bodegas_rm.csv')

# Eliminar coordenadas centroidales inaccuradas
df = df.drop(columns=['lat', 'lon'], errors='ignore')

# Geocodificar con ArcGIS via geocoder del proyecto
coords = geocode_orders(df['direccion'].tolist())
df['lat'] = [c['lat'] for c in coords]
df['lon'] = [c['lon'] for c in coords]

# Extraer comuna de la cadena de dirección
df['comuna'] = df['direccion'].str.extract(r',\s*([^,]+),\s*Región')

df.to_csv('bodegas_rm_geocoded.csv', index=False)
```

**Resultado final:** Dataset `bodegas_rm_geocoded.csv` con 230 registros de bodegas, cada uno con coordenadas geocodificadas reales y columna de comuna identificada.

**Archivos entregados:**

| Archivo                     | Descripción                                           |
| --------------------------- | ------------------------------------------------------ |
| `bodegas_rm.csv`          | Tabla original extraída (230 bodegas)                 |
| `process_geocoder.py`     | Script de geocodificación y extracción de comuna     |
| `bodegas_rm_geocoded.csv` | ⭐ Tabla final con coordenadas reales y columna comuna |

---

---

## SECCIÓN VI: SCRAPING DE VEHÍCULOS COMERCIALES — CHILEAUTOS

**Conversación de referencia:** *"Scraping ChileAutos Commercial Vehicles"*
**Fecha:** Abril 2026
**Propósito:** Extraer datos de furgones y vehículos comerciales desde ChileAutos para alimentar el análisis de flota disponible en el mercado chileno. Este es otro caso de uso de IA para **tratamiento de datos**.

---

### Prompt 6.1 — Intento de scraping de furgones en ChileAutos

**Contexto previo:** El equipo necesitaba recopilar información sobre furgones comerciales disponibles en el mercado chileno (marca, modelo, precio, capacidad en kg, capacidad volumétrica, rendimiento de combustible) para parametrizar el modelo de flota.

**Prompt del usuario:**

> Quiero desarrollar un scraper para ChileAutos que extraiga datos de furgones comerciales. La URL base es `https://www.chileautos.cl/vehiculos/autos-vehículo/furgón-categoria/`. Los campos que necesito extraer son:
>
> - Modelo y Marca
> - Tipo de vehículo
> - Precio
> - Capacidad (kg y volumétrica)
> - Rendimiento de combustible
>
> Navega a la página, identifica la estructura de las tarjetas de listado, cuenta los resultados por página e identifica el mecanismo de paginación para extraer todos los resultados.

**Respuesta del asistente IA:**

El asistente intentó navegar a ChileAutos con el agente de navegador, pero encontró un error técnico irrecuperable:

> **ERROR CRÍTICO:** El sistema reportó `open_browser_url failed` con error: `failed to create browser context: failed to create browser instance: wrong CDP URL: invalid CDP URL`
>
> Este error persiste para cualquier URL (incluyendo google.com). Se trata de un problema de infraestructura del entorno de ejecución (CDP — Chrome DevTools Protocol) que está fuera del control del script de scraping.

**Checklist de intentos realizados:**

| Paso                                     | Estado       |
| ---------------------------------------- | ------------ |
| Navegar a ChileAutos listings (furgones) | ❌ FALLIDO   |
| Esperar carga de página (10s+)          | No alcanzado |
| Capturar screenshot y DOM                | No alcanzado |
| Analizar estructura de tarjetas          | No alcanzado |
| Identificar mecanismo de paginación     | No alcanzado |

**Nota sobre esta sesión:**

Debido a fallas en la infraestructura del navegador (error CDP), el scraping de ChileAutos no pudo completarse de forma automatizada en esta sesión. El equipo debió recopilar la información de vehículos comerciales mediante revisión manual del sitio web o fuentes alternativas.

Esta limitación fue identificada, registrada e informada inmediatamente al equipo, cumpliendo con el estándar de transparencia sobre los alcances y errores de la herramienta IA, conforme al marco académico establecido: *"Recuerde que estas aplicaciones cometen errores, y pueden entregar código que no opera como ustedes quieren. Debe verificar que el código efectivamente hace lo pedido."*

---

---

## RESUMEN CONSOLIDADO DEL USO DE IA EN EL PROYECTO

### Por tipo de uso

| Uso                              | Conversaciones       | Archivos generados                                                                                                                       |
| -------------------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Generación de código** | Secs. I, II, III, IV | `pymoo_problem.py`, `savings.py`, `genetic_algorithm.py` (modificado), `gestor.py` (modificado), `tabu_search.py` (modificado) |
| **Tratamiento de datos**   | Secs. V, VI          | `scraper.py`, `process_geocoder.py`, `bodegas_rm_geocoded.csv`                                                                     |

### Archivos de código generados con asistencia de IA

| Archivo                            | Descripción                                                                         | Conversación  |
| ---------------------------------- | ------------------------------------------------------------------------------------ | -------------- |
| `modelo/pymoo_problem.py`        | Evaluador TDVRPTW con PyMoo, hard constraints, salida flexible, penalización espera | Sec. I, II, IV |
| `algoritmo/savings.py`           | Algoritmo de Ahorros Clarke-Wright adaptado al TDVRPTW                               | Sec. III       |
| `algoritmo/genetic_algorithm.py` | GA con semilla savings, paralelización multi-core, diagnóstico mejorado            | Sec. I, III    |
| `algoritmo/tabu_search.py`       | Búsqueda tabú con evaluación centralizada PyMoo                                   | Sec. I         |
| `gestion_flota/gestor.py`        | Gestor de flota con exportación a CSV doble                                         | Sec. I         |
| `bodega/scraper.py`              | Scraper Playwright para Portal Inmobiliario                                          | Sec. V         |
| `bodega/process_geocoder.py`     | Geocodificación vía ArcGIS + extracción de comuna                                 | Sec. V         |

### Validaciones realizadas por el equipo

Para cada módulo generado por la IA, el equipo realizó las siguientes validaciones:

1. **Compilación sintáctica**: `python3 -m py_compile <archivo>` para verificar ausencia de errores de sintaxis.
2. **Ejecución de prueba**: Runs con muestras pequeñas (20 pedidos) para verificar que las salidas (CSVs, KPIs) fueran coherentes con lo esperado.
3. **Revisión manual de lógica**: Inspección de los reportes de diagnóstico y los archivos de resultados para confirmar que los valores (tiempos de turno, violaciones de ventana, distancias) correspondían a los datos de entrada.
4. **Análisis de inconsistencias**: Cuando se detectaron comportamientos anómalos (ej. Shift Spanning, KPIs no esperados), se levantó un nuevo prompt con la descripción del problema para iteración.

---

*Fin del Anexo de Documentación de Uso de IA*

---

**Documento generado:** Abril 2026
**Herramienta IA:** Antigravity (Google DeepMind)
**Proyecto:** Captone-Analytics — Optimización Logística TDVRPTW
