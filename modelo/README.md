# Modelo VRPTW en PyMoo

Este README documenta los modulos de `modelo/` y se actualiza en cada nueva peticion.

## Archivos principales

- `modelo_final.py`: formulacion TD-VRPTW y evaluacion de restricciones en PyMoo.
- `datos_diarios.py`: construccion de instancia diaria desde `DatosSimulados/df_despacho.csv`.
- `heuristica_savings.py`: semilla heuristica Clarke & Wright (Savings).
- `prueba.py`: runner principal para ejecutar pruebas.
- `pruebas.py`: wrapper de compatibilidad que llama a `prueba.py`.
- `funciones/`: funciones de tiempo de viaje tipo Fleischmann.

## Flujo actual de prueba diaria

1. Se toma un dia especifico de `DatosSimulados/df_despacho.csv` (`--fecha YYYY-MM-DD`).
2. Se construye matriz de distancias con `grafo/routing.py` si el grafo esta disponible.
3. Si no se puede usar `grafo` (por ejemplo, falta graphml o dependencias), se usa fallback Haversine para no bloquear pruebas.
4. Se construye costo con:
   - `C_ij = Distancia_ij[km] * 130`.
5. Se crea el problema TD-VRPTW y se corre GA de PyMoo, inyectando semilla Savings (opcional).
6. Bootstrap defensivo de dependencias:
   - valida `/.pydeps` antes de usarlo,
   - si detecta paquetes incompletos (por ejemplo, `numpy._core._multiarray_umath` o `pandas._libs.pandas_parser` faltantes), lo saca de `sys.path` para no romper imports.
7. Inicializacion y evolucion mejoradas:
   - multiples semillas Clarke & Wright (`--n-heuristic-seeds`),
   - operador de reparacion de `ts` y auto-arcos para bajar CV,
   - mutacion configurable (evita probabilidad demasiado baja en alta dimension).

## Supuestos de esta etapa

- Capacidad de camiones no es limitante aun:
  - `enforce_capacity=False`.
- Tiempo de atencion:
  - `s_i = 0` para todo nodo (se fuerza en validacion).
  - `aten = 7` minutos (tiempo fijo).
- Flota para pruebas:
  - `n_trucks=20`.
  - `K11 = K12 = {0..9}` (mismos camiones de turno 1).
  - `K21 = K22 = {10..19}` (mismos camiones de turno 2).
- El nodo deposito se fuerza como indice 0 del modelo.

## Ejecucion recomendada

Desde la raiz del proyecto:

```powershell
python modelo/prueba.py --fecha 2026-12-03 --max-orders 40 --n-trucks 20 --cost-per-km 130 --pop-size 60 --n-gen 80
```

Corrida rapida:

```powershell
python modelo/prueba.py --fecha 2026-12-03 --max-orders 8 --n-trucks 20 --cost-per-km 130 --pop-size 20 --n-gen 20 --n-heuristic-seeds 4
```

Usar datos toy:

```powershell
python modelo/prueba.py --use-toy-data --pop-size 80 --n-gen 120 --n-heuristic-seeds 6 --mutation-prob 0.05
```

Nota `toy`:

- ahora usa `n_intervals=13` (09:00-21:00) para ser consistente con turnos de tarde.

Corrida recomendada para mejorar factibilidad (datos reales):

```powershell
python modelo/prueba.py --fecha 2026-12-03 --max-orders 40 --n-trucks 20 --cost-per-km 130 --pop-size 120 --n-gen 250 --n-heuristic-seeds 8 --mutation-prob 0.05 --mutation-eta 20
```

## Diagnostico rapido del error de NumPy

Si aparece un error como:

- `No module named 'numpy._core._multiarray_umath'`
- `No module named 'pandas._libs.pandas_parser'`

la causa tipica es una carpeta `/.pydeps` incompleta que pisa un entorno Python valido.

Desde `2026-03-26`, el modelo evita ese sombreado automaticamente:

- `prueba.py`, `modelo_final.py` y `datos_diarios.py` validan `/.pydeps`;
- si esta incompleto, no lo usan.

## Salida de consola relevante

- Tabla por generacion:
  - `n_gen`, `n_eval`, `cv_min`, `cv_avg`, `f_avg`, `f_min`.
- Resumen final:
  - mejor objetivo,
  - CV,
  - cantidad de arcos activos,
  - rutas por camion en texto.

## Historial de cambios

### 2026-03-26

- Se agrego construccion diaria desde `df_despacho.csv` en `datos_diarios.py`.
- Se dejo configuracion de camiones segun subconjuntos solicitados (20 camiones, 10+10).
- Se fijo costo como `distancia_km * 130`.
- Se descarto `s_i` en restriccion temporal (se fija `s_i=0`) y se fijo `aten=7` minutos.
- Se desactivo capacidad como restriccion activa para esta fase.
- Se incorporo fallback geodesico (Haversine) cuando `grafo` no esta disponible en runtime.
- Se forzo deposito como nodo 0 para evitar inconsistencias de rutas.
- Se agrego bootstrap de dependencias locales (`.pydeps`) para ejecucion de scripts.
- Se corrigio bootstrap para evitar sombreado por `/.pydeps` incompleto (fix del error `numpy._core._multiarray_umath`).
- Se amplio el fix para detectar tambien `pandas` incompleto (`pandas._libs.pandas_parser`).
- Se mejoro el arranque del GA con multiples semillas de ahorro y reparacion de individuos (`ts`/auto-arcos).
- Se agregaron parametros de exploracion del GA (`mutation_prob`, `mutation_eta`, `crossover_prob`, `crossover_eta`).
- Se mejoro la asignacion de rutas heuristicas a camiones considerando violacion temporal aproximada.
- Se ajusto el modo `toy` para usar 13 intervalos y ventanas distribuidas en toda la jornada.
- Se vectorizo la evaluacion de restricciones en `modelo_final.py` para reducir tiempos de corrida y evitar `KeyboardInterrupt`.
- Se agrego sanitizacion de `T_tij` (NaN/Inf -> valores finitos) para evitar `CV = inf`.
- Se reforzo explicitamente que `S_i` se desprecia (solo `service_fixed=7`).

### 2026-03-25

- Integracion inicial de modelo + prueba + heuristica Savings.
- Impresion de rutas por camion.
- Documentacion de columnas de iteracion de PyMoo.
