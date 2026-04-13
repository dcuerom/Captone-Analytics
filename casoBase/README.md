# casoBase - Pipeline Heuristica TSP/VRP Simplificada

Esta carpeta implementa un **caso base operativo** para reparto diario usando una heuristica tipo vecino mas cercano (TSP/VRP), con enfoque practico:

- sin ventanas de tiempo activas (se fuerza ventana global `[540, 1260]`)
- sin clusterizacion de clientes para rutear
- con capacidad configurable con **dos hiperparametros simultaneos**:
  - peso en gramos (`g`)
  - volumen en centimetros cubicos (`cm3`)
- con cantidad de camiones configurable
- con fecha de salida configurable (`yyyy-mm-dd`)
- con modo de distancia configurable (`road` o `haversine`)
- con velocidad promedio configurable (por defecto `25 km/h`)
- con factores KPI configurables (costo, rendimiento diesel y factor CO2)

## Archivo principal

- [`run_caso_base_tsp.py`](/C:/Users/gmari/udd_tech/CA/Captone-Analytics/casoBase/run_caso_base_tsp.py)

## Fuentes de datos utilizadas

- `EDA/vrp_orders.xlsx`
- `EDA/df_despacho.csv`

El script fusiona ambas fuentes por `id_pedido` / `Numero de Orden` para conservar:

- coordenadas de despacho y fecha/dia (`df_despacho`)
- metadata comercial/direccion y medidas (`vrp_orders`)

## Pipeline del script

1. **Carga y fusion**
- lee `vrp_orders.xlsx` y `df_despacho.csv`
- filtra por `--day` en formato `yyyy-mm-dd`
- merge por pedido
- normaliza columnas y crea `id_nodo`

2. **Normalizacion de negocio**
- fija todas las ventanas a:
  - `a_ventana = 540`
  - `b_ventana = 1260`
- convierte demanda a:
  - `demand_g`
  - `demand_cm3`
- agrega columnas auxiliares para lectura humana:
  - `demand_kg`
  - `demand_m3`

3. **Depot configurable por direccion exacta**
- intenta geocodificar `--depot-address` usando `grafo.geocoder`
- usa ese punto geocodificado directamente como depot final (sin snap)
- si no geocodifica, usa fallback al centroide global de pedidos del dia

4. **Ruteo heuristico (round-robin por camion)**
- usa vecino mas cercano con restriccion de capacidad
- cada camion puede hacer multiples rutas en un turno unico
- no se usa clusterizacion de clientes para asignar rutas
- si `--distance-mode road`, usa la matriz de distancias de red vial real
  calculada con `grafo/network_builder.py` + `grafo/routing.py`

5. **Salidas**
- markdown detallado de rutas por camion
- tabla de KPIs en markdown (ya calcula costo transporte, litros diesel y emisiones CO2;
  costos fijos y penalizacion quedan en blanco hasta definir su regla)
- csv de paradas
- csv de no asignados
- mapa html interactivo por camion con numero de visita visible en cada parada
  y hora estimada de llegada por cliente/depot
- README resumen en `casoBase_res`

## Ejecucion

Ejemplo base:

```powershell
.\capstone\Scripts\python.exe .\casoBase\run_caso_base_tsp.py `
  --depot-address "SANTA ELENA 840 SANTIAGO" `
  --distance-mode road `
  --truck-capacity-g 803333330 `
  --truck-capacity-cm3 3750000 `
  --num-trucks 4 `
  --avg-speed-kmh 25 `
  --cost-per-km 1200 `
  --diesel-km-per-liter 6.5 `
  --co2-kg-per-liter 2.68 `
  --day 2026-12-03
```

## Hiperparametros clave

- `--depot-address`: direccion del depot (default `SANTA ELENA 840 SANTIAGO`).
- `--distance-mode`: `road` (grafo real) o `haversine` (aproximacion).
- `--graph-path`: ruta al `santiago_routing_graph.graphml`.
- `--truck-capacity-g`: capacidad de peso por camion en gramos (default `803333330`, equivalente a `803333.33 kg`).
- `--truck-capacity-cm3`: capacidad de volumen por camion en cm3 (default `3750000`).
- `--num-trucks`: cantidad de camiones disponibles.
- `--day`: fecha de salida (`yyyy-mm-dd`).
- `--service-minutes`: tiempo de servicio por parada (default `5` minutos).
- `--avg-speed-kmh`: velocidad promedio para ETA (default `25`).
- `--cost-per-km`: costo por km para KPI (default `1200`).
- `--diesel-km-per-liter`: rendimiento diesel para KPI (default `6.5`).
- `--co2-kg-per-liter`: factor de emisiones para KPI (default `2.68`).
- `--start-minute`: minuto de inicio de turno.

## Nota metodologica

En este caso base, la clusterizacion **no** participa en el ruteo de clientes.  
Tampoco se aplica DBSCAN para ajustar el depot: se usa la geocodificacion exacta
de `--depot-address` (con fallback al centroide de pedidos solo si falla geocode).

## KPI: factores (hiperparametros)

- Costo de transporte (default): `1200 $/km`
- Rendimiento diesel (default): `6.5 km/L`
- Factor emisiones (default): `2.68 kgCO2/L`
- Conversion aplicada: `CO2/km = co2_kg_per_liter / diesel_km_per_liter`


