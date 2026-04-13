# Anexo: Documentación de Uso de Inteligencia Artificial
## Prompts y Respuestas — Proyecto Capstone Analytics

**Proyecto:** Optimización Logística con Algoritmo Genético (TDVRPTW)  
**Equipo:** Ingeniería Industrial — UDD  
**Herramienta de IA utilizada:** Antigravity (Google DeepMind) — Asistente de generación de código  
**Período documentado:** Abril 2026

---

> **Nota sobre el uso de inteligencia artificial en este proyecto:**
>
> Conforme al marco académico establecido, el uso de herramientas de IA en este proyecto respondió a dos propósitos definidos:
>
> 1. **Generación de código Python:** Los integrantes del equipo actuaron como ingenieros industriales responsables de definir las especificaciones funcionales del sistema (qué debía hacer el código), mientras que la herramienta de IA se encargó de producir la implementación técnica. Cada fragmento de código generado fue revisado y validado por el equipo antes de su incorporación al proyecto.
>
> 2. **Tratamiento de datos:** La herramienta de IA asistió en el procesamiento y análisis de grandes volúmenes de datos, en todo momento bajo las instrucciones y la supervisión directa del equipo.
>
> El contenido de este anexo constituye el registro fiel de las conversaciones sostenidas con la herramienta de IA a lo largo del proyecto.

---

---

## SECCIÓN I: MODELAMIENTO MATEMÁTICO Y EVALUACIÓN DEL MODELO TDVRPTW

**Conversación de referencia:** *"Evaluating TDVRPTW Mathematical Model"*  
**Fecha:** Abril 2026  
**Propósito:** Generar el modelo matemático formal del problema TDVRPTW y su integración con el evaluador PyMoo.

---

### Prompt 1.1 — Solicitud de implementación del modelo híbrido Pyomo + PyMoo

**Contexto previo:** El equipo disponía de una estructura Pyomo (`modelo/modelo.py`) y requería incorporar un evaluador de alto rendimiento para el Algoritmo Genético.

**Prompt del usuario:**

> Necesito que implementes el modelo de optimización híbrido integrando Pyomo con PyMoo. El modelo debe:
> - Mantener la estructura formal de Pyomo como referencia algebraica del negocio
> - Crear un nuevo archivo `modelo/pymoo_problem.py` que implemente `TDVRPTWProblem(Problem)`
> - El evaluador debe usar `tau_ij_vec()` para vectorizar los cálculos de tiempo de viaje
> - Las restricciones de capacidad y ventanas de tiempo deben implementarse como hard constraints en `out["G"]`
> - La función objetivo `out["F"]` debe minimizar la distancia total (en metros) × factor S

**Respuesta del asistente de IA:**

El asistente presentó el siguiente plan de implementación:

**Plan de Implementación: Integración Híbrida Pyomo + PyMoo**

**1. Dualidad del Planteamiento (`modelo/`)**

- **Mantener Pyomo:** El archivo `modelo/modelo.py` conserva su estructura formal `ConcreteModel`, cumpliendo la función de esqueleto algebraico de referencia del negocio.
- **[NUEVO] `modelo/pymoo_problem.py`:**
  - Se implementó la clase `TDVRPTWProblem(Problem)`. Se optó por `Problem` (vectorizado) en vez de `ElementwiseProblem`, con el objetivo de aprovechar el procesamiento matricial de `tau_ij_vec()`.
  - **Uso de `tau_ij_vec`:** El método `_evaluate(self, x, out)` iteró sobre los tramos del recorrido, procesando a toda la población (cientos de individuos) en paralelo, matriz a matriz.
  - **Restricciones Hard:**
    - Las violaciones de capacidad o de ventana de tiempo (llegada posterior al límite `b`) se registraron como penalizaciones físicas en `out["G"]`, forzando al algoritmo a rechazar individuos infactibles mediante las reglas de dominancia de Deb.
    - `out["F"]` se reservó exclusivamente para la sumatoria minimizada de la distancia en metros multiplicada por el factor S.

**2. Refactorización en `algoritmo/`**

- **[MODIFY] `algoritmo/genetic_algorithm.py`:** Se orquestó el algoritmo con la librería oficial `from pymoo.algorithms.soo.nonconvex.ga import GA`, inyectando la matriz de clientes y la configuración a `TDVRPTWProblem`, con cruces generados mediante `OrderCrossover()` nativo de PyMoo.
- **[MODIFY] `algoritmo/tabu_search.py`:** Se mantuvo el ciclo nativo de búsqueda tabú. Para evaluar la calidad de cada vecino, se encapsuló la llamada al simulador, inyectando el cromosoma al vector de `TDVRPTWProblem().evaluate([cromosoma])`, garantizando consistencia 1:1 en las penalizaciones entre ambos métodos.

**3. Generación de Reportes**

Ambos procesos volcaron los resultados de sus mejores cromosomas factibles en `resultados/rutas/` en un formato legible.

---

### Prompt 1.2 — Solicitud de penalización por espera, salida flexible y exportación CSV

**Contexto previo:** Tras las primeras ejecuciones, el equipo detectó que determinados vehículos acumulaban hasta 463 minutos de espera (Vehículo 16) como consecuencia de una hora de salida fija desde el depósito, lo que evidenciaba una ineficiencia operacional significativa.

**Prompt del usuario:**

> Quiero implementar 3 cambios en el modelo:
> 1. **Penalización por tiempo de espera:** Si un camión llega antes de que abra la ventana del cliente, ese tiempo de espera debe penalizar la función objetivo con un parámetro configurable `alpha_espera`.
> 2. **Salida flexible desde el depósito:** En vez de forzar a todos los camiones K11 a salir exactamente a las 09:00, quiero que la hora de salida sea flexible dentro del intervalo del turno, usando una heurística JIT (Just-In-Time).
> 3. **Exportación a CSV:** Los reportes deben dejar de generarse en `.md` y pasar a dos archivos `.csv` separados: uno de resumen de camiones y otro de detalle de paradas.

**Respuesta del asistente de IA:**

**Cambio 1 — Nueva Función Objetivo con Penalización por Espera:**

Se redefinió la formulación matemática de la función objetivo de la siguiente manera:

```
min: sum_ijk X_(i,t),j,k * C_ij  +  alpha_w * sum_ik W_ik
```

Donde `W_ik = max(0, a_i - ts_ik)` representa el tiempo de espera del vehículo `k` en el cliente `i`, y `alpha_w` es un peso de penalización configurable.

Los cambios implementados en `pymoo_problem.py` consistieron en agregar el parámetro `alpha_espera` al constructor (valor por defecto: `1.0`), acumular el tiempo total de espera dentro del bucle `_evaluate` y sumarlo a `out["F"]` de la siguiente forma:

```python
F = (dist_total * S) + costo_vehiculos + (alpha_espera * espera_total)
```

**Cambio 2 — Salida Flexible (Restricciones 10' a 13'):**

Las restricciones de salida fija se convirtieron en desigualdades de intervalo:

| Turno | Intervalo |
|-------|-----------|
| K11 | 540 ≤ ts_0,k + s_0 ≤ 900 (09:00 – 15:00) |
| K12 | 900 ≤ ts_0,k + s_0 ≤ 1260 (15:00 – 21:00) |
| K21 | 660 ≤ ts_0,k + s_0 ≤ 1020 (11:00 – 17:00) |
| K22 | 1020 ≤ ts_0,k + s_0 ≤ 1380 (17:00 – 23:00) |

Se implementó la función `_calcular_salida_optima(ruta_clientes, turno_intervalo)`, que identificó la ventana de apertura más temprana entre los clientes asignados al turno, sustrajo el tiempo de viaje estimado desde el depósito hasta el primer cliente, y delimitó el resultado al intervalo `[lb, ub]` del turno correspondiente.

**Cambio 3 — Exportación a dos archivos CSV:**

Se reemplazó la generación de Markdown en `gestor.py` por la construcción de dos DataFrames de Pandas, exportados como `resumen_camiones_*.csv` y `detalle_paradas_*.csv`.

**Archivos modificados:**

| Archivo | Tipo de cambio |
|---------|---------------|
| `modelo/modelo.md` | MODIFY — Nueva función objetivo y restricciones 10' a 13' |
| `modelo/pymoo_problem.py` | MODIFY — alpha_espera, intervalos de turno, salida óptima |
| `algoritmo/genetic_algorithm.py` | MODIFY — Transmisión de alpha_espera al constructor |
| `gestion_flota/gestor.py` | MODIFY — Reemplazo de generación Markdown por DataFrames y CSV |

**Validación realizada:**

```bash
python3 -m py_compile modelo/pymoo_problem.py       # Sin errores
python3 -m py_compile algoritmo/genetic_algorithm.py # Sin errores
python3 -m py_compile gestion_flota/gestor.py        # Sin errores
```

---

### Resumen de lo construido en esta sesión

A través de esta sesión, el asistente de IA generó e implementó los siguientes componentes:

1. La clase `TDVRPTWProblem`, heredando de `ElementwiseProblem` (PyMoo), con vectorización mediante `tau_ij_vec()` y restricciones hard configurables.
2. La integración del GA de PyMoo con `OrderCrossover`, mutación por inversión y muestreo permutacional.
3. La penalización por tiempo de espera en la función objetivo y la lógica de salida flexible JIT desde el depósito.
4. El sistema de exportación de reportes a dos archivos CSV organizados en resumen y detalle de paradas.

---

---

## SECCIÓN II: ANÁLISIS DE OPERACIONES DE FLOTA — ASIGNACIÓN DINÁMICA DE TURNOS

**Conversación de referencia:** *"Analyzing Fleet Management Operations"*  
**Fecha:** 13 de Abril, 2026  
**Propósito:** Eliminar la asignación forzada del turno de mañana (K11) a rutas con entregas en horario vespertino, mediante la implementación de una selección dinámica del turno basada en las ventanas de tiempo del primer cliente de cada ruta.

---

### Prompt 2.1 — Corrección de la asignación de turno forzada

**Contexto previo:** Al revisar los resultados del algoritmo genético, el equipo constató que el sistema asignaba el turno K11 (mañana, salida 09:00) a rutas cuyo primer cliente registraba ventanas de tiempo vespertinas (por ejemplo, 14:00 hrs), lo que generaba tiempos de espera excesivos e incoherencia con los horarios operacionales reales.

**Prompt del usuario:**

> El algoritmo está asignando el turno K11 (mañana, salida 09:00) a rutas que deberían pertenecer al turno de tarde (K21 o K22). El problema es que la lógica actual siempre inicia en K11 independientemente de cuándo abren los clientes. Necesito que el algoritmo determine dinámicamente el turno óptimo de inicio (K11, K12, K21, o K22) mirando la ventana de tiempo del primer cliente de cada ruta para minimizar el tiempo ocioso y que la asignación sea coherente con los horarios reales de entrega.

**Respuesta del asistente de IA:**

El asistente identificó que en `pymoo_problem.py` la evaluación asignaba siempre el primer turno disponible de forma secuencial, sin considerar el horario de atención del primer cliente. La solución propuesta consistió en la siguiente heurística de selección dinámica:

```python
def _seleccionar_turno_inicial(self, primer_cliente_ventana_apertura):
    """
    Selecciona el turno de despacho más adecuado en función de
    la ventana de apertura del primer cliente de la ruta.
    Retorna (turno_tipo, ruta_idx) que minimiza el tiempo de espera.
    """
    mejor_turno = None
    menor_espera = float('inf')

    for tipo_idx, rutas in enumerate(self.plantillas_turnos):
        for ruta_idx, (lb, ub) in enumerate(rutas):
            t_salida = max(lb, primer_cliente_ventana_apertura - t_viaje_estimado)
            t_salida = min(t_salida, ub)
            espera = max(0, primer_cliente_ventana_apertura - (t_salida + t_viaje_estimado))
            if espera < menor_espera:
                menor_espera = espera
                mejor_turno = (tipo_idx, ruta_idx)

    return mejor_turno
```

Con este cambio, la lógica de evaluación seleccionó dinámicamente el turno que minimizó el tiempo de espera inicial, asignando de forma automática los turnos vespertinos (K21/K22) a las rutas cuyos clientes operaban en horario de tarde.

---

---

## SECCIÓN III: OPTIMIZACIÓN HÍBRIDA Y PARALELIZACIÓN

**Conversación de referencia:** *"Hybrid Optimization And Parallelization"*  
**Fecha:** Abril 2026  
**Propósito:** Migrar de un Algoritmo Genético con población completamente aleatoria a un paradigma híbrido que utilizara la solución del Algoritmo de Ahorros de Clarke-Wright como semilla inicial, y paralelizar la optimización de clústeres mediante multiprocesamiento.

---

### Prompt 3.1 — Implementación del paradigma híbrido Savings + GA con paralelización

**Contexto previo:** El equipo observó que el Algoritmo Genético, al partir de poblaciones completamente aleatorias, exhibía tiempos de convergencia elevados y en ocasiones no encontraba soluciones factibles dentro del número de generaciones configurado. Se buscaba una estrategia constructiva que proporcionara un punto de partida de mayor calidad.

**Prompt del usuario:**

> Quiero mejorar el rendimiento del GA implementando un paradigma híbrido de dos fases:
> 1. **Fase Constructiva:** Implementar el Algoritmo de Ahorros de Clarke-Wright adaptado al TDVRPTW que genere una solución inicial factible respetando capacidades de peso, volumen y duración máxima de ruta.
> 2. **Fase de Mejora:** Usar esa solución como la "semilla" (primer individuo) de la población inicial del GA.
> 3. **Paralelización:** Reemplazar el bucle secuencial de clústeres por procesamiento paralelo usando todos los cores disponibles de la CPU con `concurrent.futures.ProcessPoolExecutor`.
>
> Para el algoritmo de ahorros, calcula `s(i,j) = d(depot,i) + d(depot,j) - d(i,j)` para todo par de clientes, ordena descendente y fusiona rutas respetando capacidades.

**Respuesta del asistente de IA:**

Antes de proceder con la implementación, el asistente planteó dos consideraciones para revisión del equipo:

> **Punto de revisión requerido:** El Algoritmo de Ahorros producirá una solución constructiva que respeta las restricciones de capacidad y duración máxima de ruta. Las ventanas de tiempo se verificarán pero no se validarán como hard-constraint en la fase de savings; esa responsabilidad recae sobre el GA en la fase posterior. ¿Es aceptable este enfoque?

> **Punto de revisión requerido:** Para la paralelización se empleará `ProcessPoolExecutor` (multiprocesamiento real, independiente del GIL de Python). La cantidad de workers será `os.cpu_count()` (todos los núcleos disponibles). ¿Se requiere limitar la cantidad máxima de workers?

Una vez confirmados estos puntos por el equipo, se implementaron los siguientes módulos:

**`algoritmo/savings.py` (NUEVO) — Clarke-Wright adaptado al TDVRPTW:**

```python
def clarke_wright_savings(df_cluster, matriz_dist, depot_id,
                          cap_vol_cm3, cap_peso_g, d_max_min):
    """
    Algoritmo de Ahorros de Clarke-Wright adaptado al TDVRPTW.

    1. Calcula la matriz de savings: s(i,j) = d(depot,i) + d(depot,j) - d(i,j)
    2. Ordena los pares por savings en orden descendente
    3. Fusiona rutas de forma iterativa, respetando:
       - Capacidad de volumen (cap_vol_cm3)
       - Capacidad de peso (cap_peso_g)
       - Duración máxima de ruta (d_max_min)
       - Solo fusiona extremos de ruta (primer o último cliente)
    4. Retorna la permutación resultante para ser inyectada al GA
    """
```

**`algoritmo/genetic_algorithm.py` — Muestreo con semilla del algoritmo de ahorros:**

```python
class SavingsSeededSampling(Sampling):
    def __init__(self, savings_permutation):
        super().__init__()
        self.savings_perm = savings_permutation

    def _do(self, problem, n_samples, **kwargs):
        X = np.full((n_samples, problem.n_var), 0, dtype=int)
        X[0] = self.savings_perm       # Primer individuo: solución del algoritmo de ahorros
        for i in range(1, n_samples):  # Individuos restantes: permutaciones aleatorias
            X[i] = np.random.permutation(problem.n_var)
        return X

# Paralelización con ProcessPoolExecutor
with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
    futures = {
        executor.submit(resolver_cluster, cluster_id, df_c, params): cluster_id
        for cluster_id, df_c in clusters.items()
    }
    for future in as_completed(futures):
        resultados.append(future.result())
```

**Resultados verificados en prueba (muestra de 20 pedidos):**

| KPI | Valor |
|-----|-------|
| Función Objetivo Total | 211.433,41 |
| Porcentaje de Entregas a Tiempo | 100,0% |
| Distancia Total | 224,53 km |
| Vehículos Utilizados | 4 |

**Archivos creados o modificados:**

| Archivo | Acción |
|---------|--------|
| `algoritmo/savings.py` | NUEVO — Implementación Clarke-Wright |
| `algoritmo/genetic_algorithm.py` | MODIFICADO — Semilla savings y paralelismo multi-núcleo |
| `PIPELINE_GLOBAL.md` | MODIFICADO — Documentación del nuevo paradigma |

---

---

## SECCIÓN IV: RELAJACIÓN DE RESTRICCIONES DE VENTANA DE TIEMPO

**Conversación de referencia:** *"Relaxing Time Window Constraints"*  
**Fecha:** 8 de Abril, 2026  
**Propósito:** Implementar una tolerancia de 30 minutos en el cierre de las ventanas de tiempo de los clientes, y corregir el problema de Shift Spanning mediante la transición de una restricción de tiempo de conducción a una de duración total del turno.

---

### Prompt 4.1 — Relajación de 30 minutos en las ventanas de tiempo

**Contexto previo:** Durante las ejecuciones del algoritmo con datos reales, se observó que numerosas entregas eran registradas como violaciones de ventana de tiempo por márgenes reducidos (entre 1 y 10 minutos). El equipo concluyó que una tolerancia de 30 minutos resultaba operacionalmente razonable y consistente con los márgenes habituales de operación logística.

**Prompt del usuario:**

> Necesito relajar las ventanas de tiempo de los clientes en 30 minutos adicionales en el cierre. Es decir, si la ventana de un cliente es [09:00, 10:00], ahora se debe considerar como [09:00, 10:30]. Esto debe:
> 1. Actualizarse en la documentación del modelo (`modelo.md`) en la Restricción 7
> 2. Implementarse en el evaluador `pymoo_problem.py` modificando el cálculo de `t_violacion`
> 3. Reflejarse en el reporte de diagnóstico de `genetic_algorithm.py` mostrando claramente la ventana relajada

**Respuesta del asistente de IA:**

**`modelo/modelo.md` — Restricción 7 actualizada:**

La documentación matemática fue modificada para incluir explícitamente el término de tolerancia:

```
Restricción 7: ts_ik + s_i <= b_i + 30    para todo i en I, k en K
```

**`modelo/pymoo_problem.py` — Evaluación con tolerancia de 30 minutos:**

```python
# Antes de la modificación
if t_inicio_servicio > b_p:
    t_violacion = t_inicio_servicio - b_p

# Después de la modificación
if t_inicio_servicio > (b_p + 30.0):
    t_violacion = t_inicio_servicio - (b_p + 30.0)
```

El diccionario `detalle_nodos` fue enriquecido con la clave `b_ventana_relaxed = b_p + 30.0` para mantener la trazabilidad de la relajación en los reportes.

**`algoritmo/genetic_algorithm.py` — Diagnóstico mejorado:**

```python
# Antes de la modificación
print(f"        - {nid}: Servicio a las {h_lleg} | Cierre ventana: {h_cierre} | Exceso: {viola:.0f} min")

# Después de la modificación
print(f"        - {nid}: Servicio a las {h_lleg} | Cierre (+30m): {h_cierre_rel} | Exceso: {viola:.0f} min")
```

---

### Prompt 4.2 — Corrección del problema de Shift Spanning

**Contexto previo:** El equipo detectó un comportamiento no deseado denominado internamente "shift spanning": vehículos clasificados como K11 (turno de mañana) realizaban entregas en horario vespertino, debido a que la restricción de control únicamente medía el tiempo de conducción (desplazamiento entre nodos) y excluía los períodos de espera frente a los clientes.

**Prompt del usuario:**

> El algoritmo tiene un problema que llamo "shift spanning": un camión de turno K11 (09:00) puede estar esperando fuera de un cliente hasta las 15:00 y el sistema lo sigue catalogando como K11 porque solo mide el tiempo de conducción, no el tiempo total del turno.
>
> Necesito cambiar la restricción de control de duración de "tiempo máximo de conducción" a "duración máxima del turno completo" (incluyendo tiempos de espera). Si la duración total (desde la salida hasta el regreso estimado al depósito) supera los 300 minutos (5 horas), el vehículo debe cerrar esa ruta y comenzar una nueva con el siguiente turno disponible.

**Respuesta del asistente de IA:**

El asistente explicó la causa raíz del comportamiento:

> En `pymoo_problem.py`, la condición de control emplea `tiempo_conduccion_estimado`, que acumula exclusivamente los tiempos de desplazamiento entre nodos. Un vehículo puede salir a las 09:00, desplazarse 10 minutos hasta la zona de entrega, permanecer en espera durante 5 horas hasta que abra la ventana del cliente, atenderlo y regresar al depósito a las 15:00. Para la lógica de ese momento, dicho vehículo solo había "conducido" 20 minutos, lo que no superaba el umbral de 300 minutos, y el sistema lo continuaba clasificando como K11.

**Cambio implementado en `pymoo_problem.py`:**

```python
# Antes: solo medía el tiempo de conducción
if (vol_actual + vol_p > self.cap_vol_cm3) or \
   (tiempo_conduccion_estimado > self.d_max_min):
    # se cerraba la ruta y se abría una nueva

# Después: mide la duración total del turno (incluyendo esperas)
t_retorno_estimado = t_fin_tent + t_viaj_ret_tent
duracion_turno_estimada = t_retorno_estimado - cam_t_salida

if (vol_actual + vol_p > self.cap_vol) or \
   (duracion_turno_estimada > self.d_max_min):
    # se cierra la ruta y se abre una nueva
```

**Actualización en `modelo.md` — Restricción 14:**

La restricción fue reformulada para expresar que la diferencia entre el momento de regreso al depósito (incluyendo esperas) y la hora de salida no puede superar `d_max`:

```
Restricción 14 (actualizada):
ts_fin_k - ts_inicio_k <= d_max    para todo k en K
(donde ts_fin_k incorpora el tiempo de regreso al depósito con esperas acumuladas)
```

El asistente advirtió proactivamente sobre el impacto del cambio:

> Si el umbral `d_max_min` = 300 minutos se aplica de forma estricta sobre la duración total del turno, el algoritmo generará rutas más fragmentadas y realizará un mayor número de asignaciones al turno K12 u otros turnos, dado que los períodos de espera ahora se contabilizan como tiempo activo del turno. Se requiere confirmar que este comportamiento es el deseado.

El equipo confirmó que dicho comportamiento era correcto y se encontraba alineado con la realidad operacional de la empresa.

---

---

## SECCIÓN V: EXTRACCIÓN DE DATOS — PORTAL INMOBILIARIO (BODEGAS)

**Conversación de referencia:** *"Scraping Portal Inmobiliario Data"*  
**Fecha:** Abril 2026  
**Propósito:** Extraer datos de bodegas en venta en la Región Metropolitana desde Portal Inmobiliario para su análisis como potenciales centros de distribución. Uso de IA bajo la modalidad de tratamiento de datos.

---

### Prompt 5.1 — Desarrollo del scraper con Playwright

**Contexto previo:** El equipo requería recopilar información georreferenciada de bodegas disponibles en la Región Metropolitana para alimentar el análisis de ubicación del centro de distribución. Las solicitudes directas mediante las bibliotecas `requests` y `BeautifulSoup` fueron bloqueadas por el sistema anti-bot del portal.

**Prompt del usuario:**

> Necesito un scraper para Portal Inmobiliario que extraiga información de bodegas en venta en la Región Metropolitana. El scraper debe:
> 1. Usar Playwright con Chromium para evitar bloqueos anti-bot
> 2. Navegar a la URL de búsqueda de bodegas
> 3. Identificar y visitar uno por uno cada enlace de bodega listado
> 4. Extraer por cada bodega: ID, Dirección, Latitud, Longitud, Precio de venta, Dimensiones (superficie)
> 5. Guardar todo en un archivo `bodegas_rm.csv` usando pandas
>
> Crea un entorno virtual en `/home/dacmxo/Desktop/udd/bodega/` e instala las dependencias necesarias.

**Respuesta del asistente de IA:**

Se creó el entorno virtual y se instalaron las dependencias requeridas mediante los siguientes comandos:

```bash
python3 -m venv /home/dacmxo/Desktop/udd/bodega/venv
./venv/bin/pip install playwright pandas
./venv/bin/playwright install chromium
```

El script `scraper.py` generado implementó los siguientes pasos:

1. Apertura de un navegador Chromium en modo headless mediante Playwright, con el objeto de eludir los sistemas de detección anti-bot del portal.
2. Navegación a la URL de búsqueda de bodegas en Portal Inmobiliario.
3. Identificación de todos los enlaces individuales de bodegas presentes en la página de resultados.
4. Visita secuencial de cada enlace, extrayendo los campos: ID, Dirección, Precio de venta, Superficie y Coordenadas.
5. Almacenamiento progresivo de los registros en el archivo `bodegas_rm.csv` mediante la biblioteca Pandas.

Durante la ejecución del scraper, el asistente identificó el siguiente problema técnico: Portal Inmobiliario no expone las coordenadas exactas de las propiedades, sino que entrega puntos centroidales predeterminados correspondientes a la dirección registrada, los cuales no representan la ubicación precisa del inmueble.

---

### Prompt 5.2 — Geocodificación y enriquecimiento del conjunto de datos

**Prompt del usuario:**

> Las coordenadas que extrae el scraper son centroidales (Portal Inmobiliario las oculta). Necesitas usar el geocoder que ya tenemos en el proyecto (`Captone-Analytics/grafo/geocoder.py`) para geocodificar cada una de las 230 direcciones extraídas y reemplazar las coordenadas del CSV con las coordenadas reales. También agrega una columna de "Comuna" parseada de la dirección.

**Respuesta del asistente de IA — Script `process_geocoder.py` generado:**

```python
from grafo.geocoder import geocode_orders
import pandas as pd

df = pd.read_csv('bodegas_rm.csv')

# Se eliminan las coordenadas centroidales inexactas
df = df.drop(columns=['lat', 'lon'], errors='ignore')

# Se geocodifican las direcciones mediante el motor ArcGIS del proyecto
coords = geocode_orders(df['direccion'].tolist())
df['lat'] = [c['lat'] for c in coords]
df['lon'] = [c['lon'] for c in coords]

# Se extrae la comuna a partir de la cadena de dirección
df['comuna'] = df['direccion'].str.extract(r',\s*([^,]+),\s*Región')

df.to_csv('bodegas_rm_geocoded.csv', index=False)
```

Como resultado, se obtuvo el archivo `bodegas_rm_geocoded.csv`, que contiene los 230 registros de bodegas con coordenadas geocodificadas mediante el motor de ArcGIS y una columna explícita de comuna.

**Archivos entregados al término de la sesión:**

| Archivo | Descripción |
|---------|-------------|
| `bodegas_rm.csv` | Tabla original extraída del portal (230 bodegas) |
| `process_geocoder.py` | Script de geocodificación y extracción de comuna |
| `bodegas_rm_geocoded.csv` | Tabla final con coordenadas geocodificadas reales y columna de comuna |

---

---

## SECCIÓN VI: EXTRACCIÓN DE DATOS — VEHÍCULOS COMERCIALES EN CHILEAUTOS

**Conversación de referencia:** *"Scraping ChileAutos Commercial Vehicles"*  
**Fecha:** Abril 2026  
**Propósito:** Extraer datos de furgones y vehículos comerciales desde ChileAutos para parametrizar el modelo de flota con información de mercado. Uso de IA bajo la modalidad de tratamiento de datos.

---

### Prompt 6.1 — Intento de extracción de datos de furgones en ChileAutos

**Contexto previo:** El equipo requería recopilar información sobre furgones comerciales disponibles en el mercado chileno para parametrizar el modelo de flota del proyecto.

**Prompt del usuario:**

> Quiero desarrollar un scraper para ChileAutos que extraiga datos de furgones comerciales. La URL base es `https://www.chileautos.cl/vehiculos/autos-vehículo/furgón-categoria/`. Los campos que necesito extraer son:
> - Modelo y Marca
> - Tipo de vehículo
> - Precio
> - Capacidad (kg y volumétrica)
> - Rendimiento de combustible
>
> Navega a la página, identifica la estructura de las tarjetas de listado, cuenta los resultados por página e identifica el mecanismo de paginación para extraer todos los resultados.

**Respuesta del asistente de IA:**

El asistente inició la navegación hacia ChileAutos, pero encontró un error técnico irrecuperable en la infraestructura del entorno de ejecución:

> **Error reportado:** El sistema informó que `open_browser_url` falló con el siguiente mensaje:
> `failed to create browser context: failed to create browser instance: wrong CDP URL: invalid CDP URL`
>
> El error se reprodujo de forma persistente para cualquier URL intentada, incluyendo sitios de acceso público general. El origen del problema se identificó como una falla en la configuración del protocolo CDP (Chrome DevTools Protocol) del entorno, la cual se encontraba fuera del alcance del script de extracción.

**Registro de intentos realizados:**

| Paso | Estado | Observación |
|------|--------|-------------|
| Navegar a la página de furgones en ChileAutos | No completado | Error CDP irrecuperable |
| Esperar carga completa de la página | No alcanzado | — |
| Capturar screenshot y estructura DOM | No alcanzado | — |
| Analizar estructura de tarjetas de listado | No alcanzado | — |
| Identificar mecanismo de paginación | No alcanzado | — |

**Nota sobre esta sesión:**

Debido a la falla en la infraestructura del navegador, el proceso de extracción automatizada de datos desde ChileAutos no pudo ser completado en esta sesión. El equipo debió recurrir a la recopilación manual de la información sobre vehículos comerciales, o bien a fuentes de datos alternativas.

La limitación fue identificada, registrada e informada de inmediato al equipo. Este caso ilustra de forma concreta la advertencia contemplada en el marco académico del proyecto: *"estas aplicaciones cometen errores y pueden entregar código que no opera como ustedes quieren; debe verificar que el código efectivamente hace lo pedido"*. La herramienta de IA no ocultó el error ni intentó presentar un resultado parcial como válido, sino que lo declaró explícitamente para que el equipo tomara las decisiones pertinentes.

---

---

## RESUMEN CONSOLIDADO DEL USO DE INTELIGENCIA ARTIFICIAL EN EL PROYECTO

### Clasificación por tipo de uso según el marco académico

| Tipo de uso | Secciones | Descripción |
|------------|-----------|-------------|
| Generación de código | I, II, III, IV | El equipo definió las especificaciones; la IA generó la implementación técnica |
| Tratamiento de datos | V, VI | Extracción, limpieza y geocodificación de datos de mercado |

### Inventario de archivos de código generados con asistencia de IA

| Archivo | Descripción | Sección |
|---------|-------------|---------|
| `modelo/pymoo_problem.py` | Evaluador TDVRPTW con PyMoo, restricciones hard, salida flexible JIT y penalización por espera | I, II, IV |
| `algoritmo/savings.py` | Algoritmo de Ahorros de Clarke-Wright adaptado al TDVRPTW | III |
| `algoritmo/genetic_algorithm.py` | GA con semilla savings, paralelización multi-núcleo y diagnóstico mejorado | I, III |
| `algoritmo/tabu_search.py` | Búsqueda tabú con evaluación centralizada vía PyMoo | I |
| `gestion_flota/gestor.py` | Gestor de flota con exportación a dos archivos CSV | I |
| `bodega/scraper.py` | Scraper con Playwright para Portal Inmobiliario | V |
| `bodega/process_geocoder.py` | Geocodificación de direcciones vía ArcGIS y extracción de comuna | V |

### Proceso de validación aplicado por el equipo

Para cada módulo de código generado por la herramienta de IA, el equipo llevó a cabo el siguiente proceso de validación antes de incorporar los cambios al repositorio del proyecto:

1. **Compilación sintáctica:** Se ejecutó `python3 -m py_compile <archivo>` para verificar la ausencia de errores de sintaxis en cada archivo modificado.
2. **Ejecución con muestra reducida:** Se realizaron ejecuciones del pipeline con conjuntos de datos de prueba (20 pedidos) para verificar que las salidas, incluyendo archivos CSV, KPIs y registros de diagnóstico, fueran coherentes con los valores esperados.
3. **Revisión manual de la lógica:** Se inspeccionaron los reportes de diagnóstico y los archivos de resultados para confirmar que los tiempos de turno, las violaciones de ventana de tiempo y las distancias calculadas correspondieran a los datos de entrada utilizados.
4. **Análisis de inconsistencias e iteración:** Cuando se detectaron comportamientos no esperados, tales como el Shift Spanning, tiempos de espera excesivos o asignaciones incorrectas de turno, el equipo formuló un nuevo prompt describiendo con precisión el problema observado, iniciando así un nuevo ciclo de análisis e implementación con la herramienta de IA.

---

*Fin del Anexo de Documentación de Uso de Inteligencia Artificial*

---

**Documento generado:** Abril 2026 | **Herramienta de IA:** Antigravity (Google DeepMind) | **Proyecto:** Captone-Analytics
