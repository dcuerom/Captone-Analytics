# README de `modelo_final.py`

Este archivo contiene la implementación del problema TD-VRPTW en PyMoo.

## Resumen

- Clase de datos: `TDVRPTWData`.
- Problema PyMoo: `TDVRPTWProblem`.
- Utilidad: `build_travel_time_tensor_from_distance(...)` para construir `T_tij` desde distancia usando `modelo/funciones` (Fleischmann).
- Generador de instancia: `build_toy_tdvrptw_data(...)`.

## Nota de integración

`travel_time_tij` puede:
- entregarse directamente, o
- derivarse desde `distance_ij` con `tau_ij_vec`.

## Historial breve

- 2026-03-25: integración con `modelo/funciones` y validaciones de consistencia.
