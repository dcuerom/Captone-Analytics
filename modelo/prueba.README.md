# README de prueba.py

`prueba.py` es el archivo principal para correr pruebas del modelo TD-VRPTW.

## Que hace

- Carga datos toy o datos diarios reales desde `DatosSimulados/df_despacho.csv`.
- Arma el problema con `TDVRPTWProblem`.
- Usa servicio variable desactivado (`s_i=0`) y tiempo fijo de atencion `aten=7` minutos.
- Inyecta una semilla heuristica Clarke & Wright (Savings) por defecto.
- Puede inyectar multiples semillas Clarke & Wright (`--n-heuristic-seeds`).
- Ejecuta GA de PyMoo.
- Aplica reparacion de individuos para fijar `ts` del deposito y limpiar auto-arcos.
- Imprime resultado final y rutas por camion.

## Cual archivo correr: prueba.py o pruebas.py

- Ejecutar recomendado: `prueba.py`.
- `pruebas.py` existe solo por compatibilidad y delega en `prueba.py`.

## Comandos

Ejecucion diaria (recomendada):

```powershell
python modelo/prueba.py --fecha 2026-12-03 --max-orders 40 --n-trucks 20 --cost-per-km 130 --pop-size 60 --n-gen 80
```

Corrida rapida:

```powershell
python modelo/prueba.py --fecha 2026-12-03 --max-orders 8 --pop-size 20 --n-gen 20 --n-heuristic-seeds 4
```

Compatibilidad antigua:

```powershell
python modelo/pruebas.py
```

En `--use-toy-data`, el script ahora usa `n_intervals=13` para alinear turnos manana/tarde.

## Bootstrap de dependencias

`prueba.py` ahora valida `/.pydeps` antes de usarlo:

- si `/.pydeps` esta sano, se habilita;
- si esta incompleto (caso comun: `numpy` namespace sin `__init__.py`), se ignora para evitar errores como
  `No module named 'numpy._core._multiarray_umath'` o
  `No module named 'pandas._libs.pandas_parser'`.

## Parametros CLI mas usados

- `--fecha`: fecha del despacho en formato `YYYY-MM-DD`.
- `--max-orders`: cantidad maxima de pedidos del dia para prueba.
- `--n-trucks`: cantidad de camiones.
- `--cost-per-km`: costo por km para `C_ij`.
- `--pop-size`: tamano de poblacion.
- `--n-gen`: generaciones.
- `--n-heuristic-seeds`: cantidad de semillas Savings.
- `--mutation-prob`: probabilidad de mutacion PM.
- `--mutation-eta`: eta de mutacion PM.
- `--crossover-prob`: probabilidad de crossover SBX.
- `--crossover-eta`: eta de crossover SBX.
- `--no-heuristic-seed`: desactiva la semilla Savings.
- `--use-toy-data`: usa instancia sintetica.

## Significado de columnas en iteraciones

`n_gen | n_eval | cv_min | cv_avg | f_avg | f_min`

- `n_gen`: generacion actual.
- `n_eval`: evaluaciones acumuladas.
- `cv_min`: menor violacion de restricciones en la poblacion.
- `cv_avg`: violacion promedio de restricciones.
- `f_avg`: promedio del objetivo en soluciones factibles.
- `f_min`: mejor objetivo en soluciones factibles.

Si no hay factibles en una generacion, `f_avg` y `f_min` pueden aparecer como `-`.

## Rutas por camion

La salida imprime, por camion usado:

- arcos activos por intervalo,
- ruta principal en texto,
- subrutas residuales (si aparecen).

Esto permite revisar rapido si la estructura de rutas tiene sentido.

## Historial

- 2026-03-26: ajustado a `s_i=0` y `aten=7` minutos para la restriccion temporal.
- 2026-03-26: integrado flujo diario desde CSV, costo km*130, e impresion de fuente de distancias usada.
- 2026-03-26: agregado soporte de dependencias locales en `.pydeps`.
- 2026-03-26: bootstrap robusto para no sombrear NumPy/PyMoo cuando `.pydeps` esta incompleto.
- 2026-03-26: bootstrap robusto tambien para instalaciones incompletas de pandas en `.pydeps`.
- 2026-03-26: agregado `TDVRPTWRepair` para reducir CV en GA.
- 2026-03-26: agregado soporte de multiples semillas heuristicas (`--n-heuristic-seeds`).
- 2026-03-26: expuestos parametros de crossover/mutacion por CLI.
- 2026-03-26: ajuste de `toy` a 13 intervalos para evitar infactibilidad artificial de turnos.
- 2026-03-26: evaluacion de restricciones vectorizada para reducir tiempos y evitar cortes por `KeyboardInterrupt`.
- 2026-03-26: `S_i` forzado a 0 y sanitizacion de `T_tij` no finito.
- 2026-03-25: agregado reporte de rutas y semilla heuristica Savings.

