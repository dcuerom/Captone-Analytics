# Modelo VRPTW en PyMoo

Este README documenta los archivos principales del modelo en `modelo/`:

- `modelo_final.py`: formulación TD-VRPTW (con intervalos de tiempo) en PyMoo.
- `heuristica_savings.py`: construcción de solución inicial con Clarke & Wright (Savings).
- `prueba.py`: script de prueba para ejecutar una instancia sintética y validar integración.
- `pruebas.py`: wrapper de compatibilidad que llama a `prueba.py`.

Este documento se irá actualizando en cada nueva petición de desarrollo sobre este módulo.

## 1) `modelo_final.py`

### Qué contiene

- `TDVRPTWData`:
  - Estructura de datos del problema (costos, capacidades, ventanas, servicio, subsets de camiones, etc.).
  - Valida dimensiones y consistencia de parámetros.
  - Permite dos modos para tiempos de viaje:
    - Entregar `travel_time_tij` directamente.
    - Entregar `distance_ij` y construir `travel_time_tij` automáticamente usando `modelo/funciones` (Fleischmann).

- `build_travel_time_tensor_from_distance(...)`:
  - Usa `tau_ij_vec` de `modelo/funciones/tiempos_viaje.py`.
  - Convierte matriz de distancias (km) a tensor `T_tij` en minutos para cada intervalo `t`.

- `TDVRPTWProblem(ElementwiseProblem)`:
  - Variables:
    - `x_(i,t,j),k` (codificadas en el cromosoma y umbralizadas a binario con `>=0.5`).
    - `ts_i,k` (tiempo de servicio/llegada por camión y nodo).
  - Objetivo:
    - Minimiza costo total por arcos activos.
  - Restricciones:
    - Capacidad volumen y masa.
    - Conservación de flujo.
    - Entrada/salida única por cliente.
    - Coherencia temporal/subtours (Big-M).
    - Ventanas de tiempo.
    - Acoplamiento de servicio a intervalo.
    - Salida/retorno al CD por subconjuntos `K11, K12, K21, K22`.
    - Duración máxima de ruta.

- `build_toy_tdvrptw_data(...)`:
  - Crea instancia sintética de prueba.
  - Construye tiempos usando Fleischmann desde distancias.

### Supuesto de unidades

- El modelo interno trabaja en **minutos** para tiempos.
- Las funciones de `modelo/funciones` retornan horas, por lo que en la construcción de `T_tij` se convierten a minutos multiplicando por `60`.

## 2) `prueba.py`

### Qué hace

- Construye una instancia sintética con `build_toy_tdvrptw_data`.
- Instancia `TDVRPTWProblem`.
- Construye una semilla heurística con Clarke & Wright (Savings) e inyecta esa solución a la población inicial (opcional).
- Ejecuta GA de PyMoo.
- Imprime:
  - Mejor costo.
  - Violación total de restricciones (CV).
  - Cantidad de arcos activos.
  - Rango de tiempos `ts`.
  - Rutas por camión (texto).

### Ejecución

Desde la raíz del proyecto:

```powershell
python modelo/prueba.py
```

o como módulo:

```powershell
python -m modelo.prueba
```

Con parámetros (ejemplo rápido):

```powershell
python modelo/prueba.py --pop-size 20 --n-gen 5 --seed 1
```

Sin semilla heurística:

```powershell
python modelo/prueba.py --pop-size 20 --n-gen 5 --seed 1 --no-heuristic-seed
```

### Flujo recomendado (híbrido)

- Paso 1: construir solución inicial con Clarke & Wright (rápida y estructurada).
- Paso 2: usar GA de PyMoo para mejorar esa base (exploración y refinamiento).
- Ventaja: se reduce el tiempo en poblaciones totalmente inviables y mejora la convergencia inicial.

### Interpretación de la tabla de iteraciones (PyMoo)

Durante la ejecución aparece una tabla como:

`n_gen | n_eval | cv_min | cv_avg | f_avg | f_min`

Significado:

- `n_gen`: generación actual del algoritmo genético.
- `n_eval`: número acumulado de evaluaciones de la función objetivo/restricciones.
- `cv_min`: menor violación total de restricciones encontrada en la población de esa generación.
- `cv_avg`: violación total promedio de restricciones en la población de esa generación.
- `f_avg`: valor promedio de la función objetivo entre soluciones factibles de esa generación.
- `f_min`: mejor (mínimo) valor objetivo entre soluciones factibles de esa generación.

Notas útiles:

- Si no hay factibles en una generación, `f_avg` y `f_min` pueden mostrarse como `-`.
- En ese caso, la señal de progreso principal es que `cv_min` vaya bajando.

### ¿Se puede imprimir la ruta de cada camión?

Sí. Ya está implementado en `prueba.py`.

Qué imprime:

- Camiones usados (solo camiones con al menos un arco activo).
- Arcos activos por camión, incluyendo intervalo `t`:
  - Formato: `tX:ORIGEN->DESTINO`.
- Ruta principal reconstruida en texto desde `DEPOT`.
- Subrutas residuales (si el individuo tiene estructura no conectada o infeasible).

Nota:

- En corridas cortas o infeasibles, la reconstrucción puede mostrar subrutas residuales; eso ayuda a diagnosticar por qué no se alcanza factibilidad.

## 3) Historial de cambios

### 2026-03-25

- Se integró `modelo_final.py` con `modelo/funciones`:
  - Ahora soporta construir `travel_time_tij` desde `distance_ij` usando `tau_ij_vec`.
- Se creó `prueba.py` como entrada principal de test.
- `pruebas.py` quedó como wrapper de compatibilidad.
- Se añadió este README para mantener documentación viva del módulo.
- Se mejoró `prueba.py` para reportar también el mejor individuo infeasible cuando no aparece factibilidad en corridas cortas.
- Se añadieron argumentos CLI en `prueba.py` (`--pop-size`, `--n-gen`, `--seed`).
- Se documentó la interpretación de columnas de iteración (`n_gen`, `n_eval`, `cv_min`, `cv_avg`, `f_avg`, `f_min`).
- Se implementó impresión de rutas por camión en `prueba.py` (ruta principal + subrutas residuales).
- Se implementó inyección de semilla heurística Clarke & Wright antes de correr GA.
