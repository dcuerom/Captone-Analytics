# casoBase_res - Resultados Heuristica TSP Caso Base

Este directorio contiene salidas generadas desde:

- `casoBase/run_caso_base_tsp.py`

## Ejecucion registrada

- Run label: `2026-12-07`
- Fecha: `2026-12-07`
- Depot address: `SANTA ELENA 840 SANTIAGO`
- Depot final: `(-33.452746, -70.631992)`
- Metodo depot: `geocoded_exact_address`
- Modo distancia: `road`
- Capacidad camion (g): `803333`
- Capacidad camion (cm3): `3750000`
- Velocidad promedio: `25.0` km/h
- Costo transporte KPI: `1200.0` $/km
- Rendimiento diesel KPI: `6.5` km/L
- Factor CO2 KPI: `2.68` kg/L
- N camiones: `20`

## Artefactos

- `mapa_rutas_tsp_2026-12-07.html`: mapa interactivo por camion.
- `rutas_tsp_2026-12-07.md`: resumen y detalle de paradas por camion/ruta.
- `paradas_tsp_2026-12-07.csv`: detalle tabular de cada parada.
- `no_asignados_tsp_2026-12-07.csv`: pedidos no asignados/no entregados.

## Resumen

- Rutas totales: `42`
- Paradas entregadas: `115`
- Distancia total: `1266.23 km`
- Pedidos no asignados: `0`

## Nota metodologica

No se aplico clusterizacion para asignar clientes a rutas.
No se aplico DBSCAN para ajustar el depot: se usa la geocodificacion exacta de --depot-address.
El mapa HTML muestra la numeracion de visita por camion en cada parada.
El popup del depot incluye la hora de llegada por camion/ruta.
El markdown de rutas incluye KPIs calculados para costo de transporte, diesel y emisiones.
Costos fijos y penalizacion por espera quedan en blanco hasta definir su regla.
KPI actuales: costo transporte=1200.0 $/km, rendimiento=6.5 km/L, factor emisiones=2.68 kgCO2/L.
Las distancias de ruteo se calcularon sobre red vial real de Santiago.