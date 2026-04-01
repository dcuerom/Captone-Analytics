# 🗺️ Módulo `grafo/` — Red Vial, Distancias y Clustering

Este módulo es el **motor geoespacial** de la herramienta. Responde a preguntas vitales para el ecosistema: *¿Dónde están los clientes?*, *¿Cómo se agrupan en proximidad?* y *¿Cuántos kilómetros y peajes hay en un camino desde el punto A al punto B usando calles reales?*

Su lógica principal sigue un esquema secuencial de preprocesamiento, conocido típicamente como **Cluster-First**. Extrae hiper-matrices de navegación requeridas luego por el `algoritmo/`.

## Archivos y su Contribución al Pipeline

### `main.py`
**Rol:** Enrutador de llamadas y creador formal de los inputs.
**Funcionalidad:** Posee la función central `execute_vrp_pipeline()`. Convoca metódicamente a la geocodificación, el clustering, y finalmente la matriz final, inyectando el Centro de Distribución. Este archivo es el nexo para evitar que el algoritmo genético deba lidiar con los procesos espaciales subyacentes.

### `geocoder.py`
**Rol:** Traductor Texto -> GPS.
**Funcionalidad:** Invoca la API de ArcGIS (via `geopy`) para convertir "Dirección real X, comuna Y" a tuplas `(Latitud, Longitud)`. Incluye mecanismos anti-saturación de recargas (Rate Limiters) y optimización vía caché de "direcciones únicas".

### `clustering.py`
**Rol:** Agrupador tridimensional algorítmico.
**Funcionalidad:** Extrae subgrafos utilizando `scikit-learn` a través de **DBSCAN**. Mapea a los clientes basándose en su densidad lat/lon y sus límites temporales. Emite "clusters" separados, permitiendo dividir un problema gigantesco y costoso (miles de nodos de todo Santiago) en micromundos paralelos computacionalmente tratables. Contiene además heurísticas de rescate de *outliers*.

### `network_builder.py`
**Rol:** Creador la infraestructura cartográfica asfáltica.
**Funcionalidad:** Utiliza `osmnx` para conectarse a plataformas como Supabase y OpenStreetMap, recuperando el gigantesco grafo subyacente de la ciudad (`santiago_routing_graph.graphml`). Extrae un grafo `MultiDiGraph` dirigido que soporta sentidos de calle, carreteras no transitables, y puentes reales.

### `routing.py`
**Rol:** Calculador de Distancias sobre asfalto.
**Funcionalidad:** Olvida la ingenua distancia Euclidiana mediante el cómputo de ruteadores como **A*** o **Dijkstra** (Single-Source). Por cada cluster, halla todos los caminos óptimos posibles entre todos los pares (Matriz Completa NxN). Su salida da fe precisa y estricta en "Metros" requerida por el optimizador.

### `visualizer.py`
**Rol:** Generador de mapas y frentes de usuario.
**Funcionalidad:** Renderiza artefactos `.html` de la familia `Folium`. Utilizando tooltips informativos y capas activables (`FeatureGroups`), permite previsualizar la separación de DBSCAN de las comunas (`plot_cluster_results`) o las rutas físicas trazadas por el gestor de flota a nivel macroscópico (`plot_global_flota_interactive`).
