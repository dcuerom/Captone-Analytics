# 📊 Resultados y Visualizaciones TDVRPTW

Acá se albergan las salidas analíticas tras correr exitosamente cualquier heurística de agrupamiento y travesía. 

### Directorios Destacados:

- **`mapa_rutas/`**: Capa visual. Genera archivos HTML y renderizaciones (como Folium). Estos muestran las nubes de clústeres espaciales obtenidos vía DBSCAN junto al enhebrado de rutas A* trazadas directamente sobre la cartografía real de Santiago (respetando manzanas, y avenidas).
- **`rutas/`**: Compilación secuencial detallada (*logs heurísticos*). Los archivos markdown `.md` listan la secuencia matemática del reparto por cada grupo ($0 \to i \to j \to 0$), exponiendo tiempos tentativos de llegada y fitness computado.

> **Reglas de Unidad**: Al leer los reportes de `rutas/*.md`, recuerda que los tiempos de llegada son presentados en minutos respecto a las ventanas de tiempo operativas (ej. $540 \implies 09:00 \text{ AM}$).
