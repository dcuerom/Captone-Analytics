# README de `prueba.py`

Este archivo ejecuta una prueba de humo del modelo TD-VRPTW en PyMoo.

## Qué valida

- Construcción de datos sintéticos.
- Construcción del problema (`TDVRPTWProblem`).
- Inyección opcional de semilla heurística Clarke & Wright (Savings).
- Ejecución de GA con PyMoo.
- Reporte de resultado factible o, si no existe, mejor solución por CV.
- Impresión de rutas por camión en texto (camiones usados, arcos activos, ruta principal y subrutas residuales).

## Ejecución

```powershell
python modelo/prueba.py
```

o

```powershell
python -m modelo.prueba
```

Ejemplo rápido:

```powershell
python modelo/prueba.py --pop-size 20 --n-gen 5 --seed 1
```

Sin semilla heurística:

```powershell
python modelo/prueba.py --pop-size 20 --n-gen 5 --seed 1 --no-heuristic-seed
```

## Historial breve

- 2026-03-25: creado para validar integración con `modelo_final.py`.
- 2026-03-25: agregado reporte de mejor infeasible cuando no hay factibles.
- 2026-03-25: agregados argumentos CLI (`--pop-size`, `--n-gen`, `--seed`).
- 2026-03-25: agregada impresión de rutas por camión en salida de consola.
- 2026-03-25: agregada inyección de semilla heurística Clarke & Wright antes del GA.
