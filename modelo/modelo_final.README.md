# README de modelo_final.py

`modelo_final.py` contiene la formulacion TD-VRPTW y su evaluacion en PyMoo.

## Componentes

- `TDVRPTWData`: estructura de parametros y validaciones.
- `TDVRPTWProblem`: definicion de objetivo y restricciones.
- `build_travel_time_tensor_from_distance(...)`: construye `T_tij` desde distancias usando `modelo/funciones` (Fleischmann).
- `build_toy_tdvrptw_data(...)`: instancia de prueba sintetica.

## Cambios relevantes actuales

- Soporte para `z_t` iniciando en 0 o en 1 al construir `T_tij`.
- Restricciones de capacidad opcionales mediante `enforce_capacity`.
- Restriccion temporal sin servicio variable: se usa `s_i=0` y solo `service_fixed`.
- Tiempo fijo de atencion actual: `service_fixed = 7` minutos.
- `service_var_i` se fuerza a cero en `validate()` para asegurar que `S_i` no afecte el modelo.
- Bootstrap defensivo de dependencias:
  - valida `/.pydeps` antes de activarlo en `sys.path`;
  - evita sombrear un NumPy/PyMoo valido cuando `/.pydeps` esta incompleto;
  - detecta instalaciones incompletas tipicas de `numpy` y `pandas` en Windows.
- Manejo de camiones repetidos en subconjuntos `K11/K12/K21/K22`:
  - se colapsan camiones asignados,
  - target de salida por camion se fija al mas temprano.
- Conteo de restricciones consistente con el modo de capacidades activas/inactivas.
- Evaluacion de restricciones vectorizada para reducir tiempo por evaluacion en PyMoo.
- Sanitizacion de `travel_time_tij` para evitar NaN/Inf en `G` y `CV`.
- Instancia `toy` mas realista:
  - ventanas de clientes distribuidas en toda la jornada,
  - compatible con turnos manana/tarde.

## Supuestos de unidades

- Distancia: km.
- Tiempo interno del modelo: minutos.
- `tau_ij_vec` retorna horas, por lo que se multiplica por 60 para `travel_time_tij`.

## Historial

- 2026-03-26: se elimino `s_i` de la restriccion temporal (equivalente a fijar `s_i=0`) y se fijo `aten=7` min.
- 2026-03-26: agregado `enforce_capacity` y manejo robusto de subconjuntos de camiones repetidos.
- 2026-03-26: ajuste de construccion de `T_tij` para indices de intervalo `z_t` base-0 o base-1.
- 2026-03-26: fix de bootstrap para prevenir error `numpy._core._multiarray_umath` causado por `/.pydeps` incompleto.
- 2026-03-26: extension del fix para prevenir error `pandas._libs.pandas_parser` por `/.pydeps` incompleto.
- 2026-03-26: ajuste de generacion `toy` para evitar infactibilidad artificial por turnos.
- 2026-03-26: vectorizacion de `_evaluate` para mitigar bloqueos por tiempo (`KeyboardInterrupt`).
- 2026-03-26: forzado de `S_i=0` y sanitizacion de `T_tij` no finito.
- 2026-03-25: integracion inicial con `modelo/funciones` y validaciones.

