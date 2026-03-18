# Módulo de Ruteo y Generación de Grafos Dirigidos

Este módulo (`grafo/`) es el corazón del ruteo logístico del VRP (Vehicle Routing Problem). Implementa una arquitectura moderna de computación espacial conocida como **"Cluster-First, Route-Second"**. Su objetivo es procesar pedidos brutos, agruparlos geográficamente para reducir la complejidad computacional y generar matrices matemáticas de distancia real basadas en topología de calles (OSMnx/NetworkX) de la ciudad de Santiago.

## 🚀 Flujo de Funcionamiento del Pipeline

El pipeline se ejecuta secuencialmente mediante la macro-instancia principal `execute_vrp_pipeline()` alojada en **`main.py`**.

El proceso se divide en las siguientes de 6 capas:

1. **Carga y Normalización (`main.py`)**:
   - Lee el dataset de input y estandariza los nombres de sus columnas principales.
   - Limpia IDs del cliente eliminando caracteres especiales para producir las llaves del grafo `id_nodo` (que se forman uniendo `Número de orden` y `RUT`).

2. **Geocodificación (`geocoder.py`)**:
   - Asigna coordenadas GPS (Latitud, Longitud) llamando a la API de *Nominatim*, a partir del texto crudo encontrado en la `direccion_ruteo`.
   - Resuelve independientemente la ubicación del "Depósito" o Base de operaciones.

3. **Clustering Multi-dimensional (`clustering.py` | *Cluster-First*)**:
   - Extrae las dimensiones de latitud, longitud y una ventana de tiempo predefinida (por default 9 a 21 hrs).
   - Utiliza **DBSCAN** para aislar pedidos aglomerados. Aquellos lejanos y no viables se separan como ruido u *Outliers*, previniendo camiones sub-utilizados o rutas irreales.

4. **Motor de Red Vial (`network_builder.py` e Integración Supabase)**:
   - Recupera el grafo pre-procesado (`santiago_routing_graph.graphml`).
   - El sistema es escalable y descargará en memoria caché local este mapeo desde tu **Supabase Storage**, empleando algoritmos de compresión `GZIP` para violar el límite restrictivo de 50MB que usualmente trunca despliegues en la nube.

5. **El Algoritmo A* (`routing.py` | *Route-Second*)**:
   - Toma cada clúster agrupado e *inyecta* temporalmente el Depósito central como si fuese una orden más.
   - Crea una Matriz de Distancia $N \times N$, midiendo el kilometraje exhaustivamente dentro del grafo dirigido vehicular respetando sentidos de vía y restricciones viales mediante el motor *A-Star*.

6. **Visualización Interactiva (`visualizer.py`)**:
   - Rinde el documento mapa web interactivo en la raíz del proyecto local que pinta a los nodos diferenciándolos visualmente en Folium según los clusters correspondientes al cálculo del día.

---

## 📋 Formato de los Datos de Entrada

Para invocar la mega-instancia y ejecutar la formación del grafo, es **estrictamente necesario** proveer un DataFrame (o archivo Excel) con los siguientes requerimientos de columna base:

### Obligatorias (Limpiadas automáticamente si varían en formato)

- **`Número de orden`** (*o "Número de Orden"*): Identificador único transaccional de la hoja de ruta en tu sistema.
- **`RUT`** (*o "Rut", "rut"*): RUN/RUT del cliente, puede contener puntos o guiones, la lógica `clean_rut` lo saneará.
- **`direccion_ruteo`**: Texto legible de dirección usado para la geocodificación.
   > **Nota:** La dirección textual debe ser lo más específica posible en el estándar OS.  
   > *Ejemplo deseado*: `"Avenida Libertador Bernardo O'Higgins 1058, Santiago, Chile"`

### Opcionales Recomendadas (Si se saltan, se deducen o se omiten en optimización)

- **`latitud` y `longitud`**: Coordenadas *float*. Si las puedes proveer directamente desde tu BD como un cache previo, acelerará enormemente el proceso eximiéndote del throttling de la API pública de Nominatim.
- **`volumen total_m3` y `peso_total_kg`**: Requerido para resolver despachos limitados a restricciones restrictivas de vehículo
- **`fecha de despacho`**: Fecha base del ruteo.

---

## 💻 Uso en Scripts

Puedes requerir todo el proceso matemático desde otro módulo instanciando:

```python
from grafo.main import execute_vrp_pipeline

# Recibe por default Plaza de Armas como Depot
# Para testing masivo y evitar esperar latencias A* de toda la red comercial del año, puedes setear "sample_size" a 100.
matrices, rutas, outliers = execute_vrp_pipeline(
    input_file="EDA/vrp_orders.xlsx", 
    depot_address="Avenida Providencia 2000, Providencia, Chile", # Opcional
    sample_size=None
)
```
