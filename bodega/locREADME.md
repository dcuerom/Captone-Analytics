# Cambios implementados en `localizacion.ipynb`

Se dejo el notebook con el flujo completo para:

1. construir `vrp_orders_agrupado`,
2. calcular el centro de gravedad,
3. medir distancia a cada bodega de RM,
4. ordenar todas las bodegas por cercania,
5. obtener automaticamente la bodega mas cercana.

## Archivos usados

- `../EDA/vrp_orders.xlsx`
- `bodegas_rm_geocoded.csv`
- `../grafo/geocoder.py` (`geocode_orders`)
- `vrp_orders_localizacion.xlsx` (salida intermedia final de pedidos)

## Flujo del notebook

### 1) Preparacion de pedidos y geocodificacion

- Se cargan pedidos y bodegas.
- Se filtran columnas de pedidos:
  - `Nombre cliente`
  - `direccion_ruteo`
  - `Monto Pedido`
  - `peso_total_kg`
- Se renombran columnas:
  - `Nombre cliente` -> `nombre_cliente`
  - `Monto Pedido` -> `monto_pedido`
- Se ejecuta `geocode_orders(...)` para agregar `latitud` y `longitud` a pedidos.
- Se agrupa por:
  - `nombre_cliente`
  - `direccion_ruteo`
  - `latitud`
  - `longitud`
- Se calculan sumas:
  - `monto_pedido`
  - `peso_total_kg`
- Se crea `monto_por_kg = monto_pedido / peso_total_kg` (con `NA` si peso es 0).
- Se exporta a `bodega/vrp_orders_localizacion.xlsx`.

### 2) Centro de gravedad

Se calcula sobre `vrp_orders_agrupado` con ponderador `monto_por_kg`:

- `latitud_centro_gravedad = sum(latitud * monto_por_kg) / sum(monto_por_kg)`
- `longitud_centro_gravedad = sum(longitud * monto_por_kg) / sum(monto_por_kg)`

Variables de salida:

- `latitud_centro_gravedad`
- `longitud_centro_gravedad`
- `centro_gravedad` (DataFrame con ambas coordenadas)

### 3) Distancia a bodegas y seleccion de la mejor

- Se usa `bodegas_rm_geocoded.csv`.
- Se convierten `Latitud` y `Longitud` a numerico.
- Se elimina cualquier fila sin coordenadas.
- Se calcula `distancia_centro_km` con formula Haversine para cada bodega:
  - punto A: centro de gravedad
  - punto B: coordenadas de cada bodega
- Se ordena ascendente en `bodegas_ordenadas`.
- Se extrae la primera fila como `bodega_mas_cercana`.

El notebook muestra:

- `bodegas_ordenadas` (todas las bodegas en orden de cercania)
- `bodega_mas_cercana` (mejor candidata)

## Resultado actual (con datos vigentes)

- Centro de gravedad:
  - `latitud_centro_gravedad = -33.4670579685123`
  - `longitud_centro_gravedad = -70.62792757517515`
- Bodega mas cercana:
  - `id = MLC1781381141`
  - `Comuna = Santiago`
  - `distancia_centro_km = 0.2339990275`
