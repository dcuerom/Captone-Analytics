# 🗺️ Módulo `grafo/` — Documentación Técnica

## Contexto del Problema: VRPTW

Este módulo resuelve el **Vehicle Routing Problem with Time Windows (VRPTW)**: dado un conjunto de clientes con coordenadas geográficas y ventanas horarias de entrega, ¿cómo asignar rutas óptimas a una flota de vehículos partiendo desde un depósito central?

El VRPTW es un problema NP-difícil. La estrategia adoptada para hacerlo computacionalmente tratable es **Cluster-First, Route-Second**:

> 1. **Cluster-First**: Agrupar clientes geográfica y temporalmente (DBSCAN) → reduce el espacio de búsqueda global.
> 2. **Route-Second**: Optimizar la secuencia de visita dentro de cada grupo con A* sobre un grafo vial real.

---

## 🏗️ Arquitectura del Pipeline

```
vrp_orders.xlsx
      │
      ▼
[main.py] execute_vrp_pipeline()
      │
      ├─► [geocoder.py]   Geocodificación de direcciones → (lat, lon)
      │
      ├─► [clustering.py] DBSCAN 3D (lat, lon, tiempo) → clusters + outliers
      │
      ├─► [network_builder.py] Carga grafo vial Santiago (OSMnx / Supabase)
      │
      ├─► [routing.py]    A* intra-cluster → Matrices NxN de distancia
      │
      └─► [visualizer.py] Mapa HTML interactivo (Folium)
```

---

## 📦 Módulos y Funciones

---

### `main.py` — Orquestador Principal

Punto de entrada del sistema. Ejecuta el pipeline completo de forma secuencial.

#### `clean_rut(rut) -> str`

Sanitiza el RUT del cliente eliminando puntos, guiones y espacios, y convirtiéndolo a mayúsculas. Produce llaves de identificación limpias para el grafo.

```python
clean_rut("12.345.678-9")  # → "123456789"
```

#### `execute_vrp_pipeline(input_file, depot_address, sample_size) -> (matrices, rutas, outliers)`

Macro-función que encadena los 6 pasos del sistema:

| Paso | Acción |
|------|--------|
| 1 | Carga y normalización del Excel de pedidos |
| 2 | Geocodificación de pedidos (`geocode_orders`) |
| 3 | Geocodificación del depósito (`geocode_depot`) |
| 4 | Clustering DBSCAN (`run_clustering_pipeline`) |
| 5 | Carga del grafo vial de Santiago (`get_santiago_graph`) |
| 6 | Ruteo A* por cluster (`calculate_routing_for_day`) |

**Parámetros importantes:**

| Parámetro | Por defecto | Descripción |
|-----------|-------------|-------------|
| `input_file` | `EDA/vrp_orders.xlsx` | Archivo Excel con los pedidos |
| `depot_address` | `"Plaza de Armas, Santiago, Chile"` | Dirección de la base de operaciones |
| `sample_size` | `None` | Límite de pedidos (útil para pruebas rápidas) |

**Columnas normalizadas automáticamente:**
- `"Número de Orden"` → `"Número de orden"`
- `"Fecha de despacho Solicitada"` → `"fecha de despacho"`
- `"volumen_total_m3"` → `"volumen total_m3"`

La columna `id_nodo` se construye como:
```
id_nodo = str(Número de orden) + "_" + rut_clean
```

**Retorna:**
- `matrices_por_cluster`: `{ cluster_id: DataFrame NxN de distancias km }`
- `rutas_por_cluster`: `{ cluster_id: dict con info de rutas A* }`
- `outliers`: DataFrame de clientes que no pudieron ser agrupados

---

### `geocoder.py` — Geocodificación de Direcciones

Convierte direcciones textuales en coordenadas GPS `(latitud, longitud)` usando la API de **ArcGIS** a través de la librería `geopy`.

> **¿Por qué ArcGIS y no Nominatim?**  
> ArcGIS ofrece mayor tolerancia a direcciones mal escritas y no requiere autenticación, siendo más estable para producción en Chile.

#### `geocode_depot(address) -> (lat, lon)`

Geocodifica la dirección del depósito. Lanza `ValueError` si no se encuentra la dirección.

#### `geocode_orders(df, address_col) -> DataFrame`

Geocodifica masivamente los pedidos del DataFrame con dos optimizaciones clave:

1. **Caché por dirección única**: Si 50 pedidos tienen la misma dirección, solo se hace 1 llamada a la API.
2. **Rate limiting**: `RateLimiter` con `min_delay_seconds=0.2` para respetar los límites de la API.
3. **Pre-carga de coordenadas existentes**: Si el DataFrame ya viene con `latitud`/`longitud`, no las sobreescribe.
4. **Tolerancia a fallos**: Captura excepciones por pedido y asigna `(None, None)`, con pausa de 1s en errores de conexión.

#### SSL y Certificados

```python
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
```

Se deshabilita la verificación SSL para compatibilidad con entornos corporativos con proxies o certificados autofirmados.

#### `process_and_save_geocoded_data(input_path, output_path)`

Función de utilidad standalone: lee un Excel, geocodifica y guarda el resultado en un nuevo Excel. Útil para pre-procesar y cachear coordenadas antes de ejecutar el pipeline completo.

---

### `clustering.py` — Clustering Multidimensional (Cluster-First)

Implementa el primer paso del paradigma **Cluster-First**. Agrupa clientes en un espacio tridimensional `(latitud, longitud, tiempo)` usando DBSCAN.

#### ¿Por qué DBSCAN?

| Característica | K-Means | DBSCAN |
|---|---|---|
| Número de clusters | Fijo (k) | Automático |
| Manejo de outliers | No | Sí (label -1) |
| Forma de clusters | Solo esférica | Arbitraria |
| Robustez geográfica | Baja | Alta |

DBSCAN es ideal para clientes en una ciudad: forma grupos de *densidad real* sin asumir geometría.

#### `build_feature_matrix(df, time_column, default_window_start_hour) -> (X, df_clean)`

Construye la matriz `N × 3 = [latitud, longitud, tiempo_minutos]`.

- Acepta columnas `latitud`/`Latitud` y `longitud`/`Longitud`.
- Descarta filas sin coordenadas (`dropna`).
- **Dimensión temporal**: Si existe `time_column`, la usa (convirtiéndola con `pd.to_numeric`). Si no, usa `default_window_start_hour * 60` (ej. 9h → 540 min).

> **Formato esperado de `time_column`**: entero o float en **minutos desde medianoche**.  
> Ejemplo: 09:30 AM → `570`

#### `normalize_and_weight(X, alpha_time) -> (X_scaled, scaler)`

Aplica `StandardScaler` (media=0, varianza=1) para que lat, lon y tiempo sean comparables. Luego multiplica la columna de tiempo por `alpha_time`:

- `alpha_time > 1.0` → El tiempo pesa más; clientes con horarios similares se agrupan aunque estén geográficamente más dispersos.
- `alpha_time < 1.0` → El tiempo pesa menos; predomina la proximidad geográfica.
- `alpha_time = 1.0` → Equilibrio (valor por defecto en el pipeline).

#### `run_dbscan(X_scaled, eps, min_samples) -> labels`

Ejecuta `sklearn.cluster.DBSCAN` y retorna los labels de cluster. Los puntos con label `-1` son **ruido** (outliers).

> ⚠️ `eps=0.3` y `min_samples=3` son los hiperparámetros de producción actuales.  
> Requieren re-calibración si cambia la densidad de cobertura geográfica.

#### `manage_clusters_and_noise(df, labels, X_scaled, rescue_threshold, force_rescue) -> (clusters_dict, outliers)`

Gestiona los outliers con una **heurística de rescate**:

1. Calcula el centroide de cada cluster válido en el espacio normalizado.
2. Para cada outlier, calcula la distancia euclidiana a todos los centroides.
3. Si `distancia_mínima ≤ rescue_threshold` **o** `force_rescue=True` → lo reasigna al cluster más cercano.

Con `force_rescue=True` (activado en el pipeline principal), se garantizan **0 outliers** en la salida: todos los clientes son asignados a algún cluster.

#### `generate_astar_inputs(clusters_dict, depot_node_id, id_column) -> Dict[int, List[Tuple]]`

Inyecta el nodo depósito en cada cluster y genera todas las permutaciones dirigidas `(origen, destino)` intra-cluster usando `itertools.permutations`.

```
Cluster 0: [A, B, C, DEPOT] → [(A,B), (A,C), (A,DEPOT), (B,A), (B,C), ...]
```

Esto transforma el problema de ruteo global O(N!) en múltiples sub-problemas O(k!) donde `k << N`.

#### `run_clustering_pipeline(df, depot_id, id_column, force_outlier_rescue, time_column) -> (clusters_dict, outliers, pairs_for_astar)`

**Orquestador del módulo**. Encadena los 4 pasos anteriores con los hiperparámetros de producción:

```python
eps=0.3, min_samples=3, alpha_time=1.0, rescue_threshold=0.8
```

---

### `visualizer.py` — Visualización Interactiva

Genera mapas web interactivos en HTML usando **Folium** con fondo cartográfico **CartoDB Positron**.

#### `plot_cluster_results(clusters_dict, outliers, filepath)`

Visualiza el resultado del clustering DBSCAN:

- **Cada cluster** → color único asignado de una paleta de 14 colores.
- **Depósito** → marcador especial con ícono `fa-home`.
- **Outliers** → puntos negros con opacidad 0.7.
- Cada marcador incluye un `tooltip` con el número de orden.

#### `plot_network_and_routes(G, info_rutas, filepath)`

Renderiza las rutas A* calculadas sobre el grafo vial:

- Extrae la **geometría real de las calles** (no líneas rectas) desde los datos de arista del grafo OSMnx.
- Dibuja `PolyLine` por ruta con colores diferenciados.
- Marca el inicio (marcador por defecto) y fin (marcador verde) de cada ruta.
- Si no hay rutas, genera un mapa base centrado en el grafo.

---

## 📋 Formato del Archivo de Entrada

### Columnas Obligatorias

| Columna | Descripción |
|---------|-------------|
| `Número de orden` | ID único del pedido |
| `RUT` | RUT del cliente (con o sin puntos/guiones) |
| `direccion_ruteo` | Dirección textual completa para geocodificación |

> **Ejemplo de dirección ideal**: `"Avenida Libertador Bernardo O'Higgins 1058, Santiago, Chile"`

### Columnas Opcionales

| Columna | Descripción |
|---------|-------------|
| `latitud` / `longitud` | Coordenadas pre-calculadas (evita llamadas a la API) |
| `ventana_tiempo_minutos` | Minutos desde medianoche del inicio de ventana de entrega |
| `volumen total_m3` | Volumen del pedido (para restricciones de capacidad) |
| `peso_total_kg` | Peso del pedido |
| `fecha de despacho` | Fecha del despacho |

---

## 🔧 Dependencias y Herramientas

| Librería | Uso |
|----------|-----|
| `pandas` | Manipulación de DataFrames |
| `numpy` | Operaciones matriciales |
| `scikit-learn` | DBSCAN, StandardScaler |
| `geopy` | Geocodificación (ArcGIS) |
| `osmnx` | Descarga y manipulación del grafo vial de Santiago |
| `networkx` | Representación del grafo dirigido y A* |
| `folium` | Generación de mapas HTML interactivos |
| `itertools` | Generación de permutaciones para pares A* |

---

## 💻 Uso desde otro módulo

```python
from grafo.main import execute_vrp_pipeline

matrices, rutas, outliers = execute_vrp_pipeline(
    input_file="EDA/vrp_orders.xlsx",
    depot_address="Avenida Providencia 2000, Providencia, Chile",
    sample_size=100  # None para ejecutar todos los pedidos
)

# matrices: { cluster_id: DataFrame NxN de distancias }
# rutas:    { cluster_id: { par_nodos: info_ruta_astar } }
# outliers: DataFrame con clientes no asignados a ningún cluster
```

---

## ⚠️ Consideraciones de Diseño

### Ventanas de tiempo en clustering vs. routing

El clustering usa **solo la hora de apertura** de la ventana como tercera dimensión. La restricción de cierre y apertura suavizada (suavizamiento de 15 min en ambos extremos) es responsabilidad del modelo evaluador en el Algoritmo Genético. Esta separación es una simplificación deliberada: el clustering es heurístico y su objetivo es reducir el espacio de búsqueda, no garantizar factibilidad de ventanas.

### Grafo vial y Supabase

El archivo `santiago_routing_graph.graphml` se comprime con **GZIP** para eludir el límite de 50 MB de Supabase Storage. El módulo `network_builder.py` gestiona su descarga, descompresión y caché local automáticamente.

### Escalabilidad

El parámetro `sample_size` en `execute_vrp_pipeline` permite reducir el conjunto de pedidos para pruebas rápidas. A* sobre grafos viales reales es costoso: para 1000+ clientes sin clustering, el tiempo de cómputo se vuelve inviable. El Cluster-First lo hace lineal en el número de clusters.

---

## 🔍 Estructura de Salida: Una Ruta A*

El diccionario `rutas_por_cluster` retornado por `execute_vrp_pipeline` mapea cada par origen→destino a su información de ruta. Cada entrada tiene la siguiente forma:

```python
'DEPOT_01_BASE->ORD-CL-202612-001037_6283572    5': {
    'distancia_km': 12.289,
    'ruta_nodos_osmnx': [11057674695, 11057674694, 6956627860, ...]
}
```

### Anatomía de la clave

```
DEPOT_01_BASE  ->  ORD-CL-202612-001037_6283572    5
     │          │            │                  │
  Origen     Flecha       id_nodo            Índice de
 (Depósito)  Dirigida     cliente            permutación
```

| Parte | Ejemplo | Origen |
|---|---|---|
| Nodo origen | `DEPOT_01_BASE` | `depot_id` definido en `main.py` |
| `->` | literal | Indica arista **dirigida** en el grafo |
| Número de orden | `ORD-CL-202612-001037` | Columna `Número de orden` del Excel |
| RUT limpio | `_6283572` | Resultado de `clean_rut()` |
| Índice | `5` | Posición en la lista de `permutations()` del cluster |

El `id_nodo` se construye en `main.py` como:
```python
id_nodo = f"{Número_de_orden}_{rut_clean}"
```

### Campo `distancia_km`

Distancia **real en kilómetros** calculada por A* sobre el grafo vial de Santiago. No es distancia euclidiana: respeta sentidos de circulación, restricciones viales y la topología real de las calles.

### Campo `ruta_nodos_osmnx`

Lista ordenada de **IDs de nodos OSMnx** (enteros), que representan intersecciones reales del mapa de OpenStreetMap. Define la secuencia exacta de intersecciones que A* atravesó desde el origen hasta el destino:

```
[11057674695] → [11057674694] → [6956627860] → ... → [2355936038]
   Partida                                              Llegada
  (próximo al                                         (próximo al
    depósito)                                           cliente)
```

> Una ruta de ~12 km en zona urbana de Santiago puede involucrar **~190 nodos intermedios** dada la alta densidad de intersecciones.

`plot_network_and_routes` en `visualizer.py` consume esta lista para extraer la geometría real de cada segmento de calle y dibujar la `PolyLine` en el mapa HTML interactivo.

### Rol dentro del pipeline

```
generate_astar_inputs()
    └── permutations([DEPOT, A, B, C])
            → (DEPOT→A), (DEPOT→B), (A→DEPOT), ...

calculate_routing_for_day()
    └── Para cada par → corre A* en el grafo G
            → { "DEPOT→A": { distancia_km, ruta_nodos_osmnx }, ... }
```

El conjunto de todas estas entradas conforma la **matriz de adyacencia real** del cluster, donde cada celda representa el costo verdadero (en km de calle) de ir de un nodo a otro. Esta matriz es el insumo para resolver el ordenamiento óptimo de visitas (TSP/VRP) dentro de cada grupo.
