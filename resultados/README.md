# 📊 Resultados y Visualizaciones TDVRPTW

Acá se albergan las salidas analíticas y artefactos finales tras correr exitosamente cualquier tubería heurística y de gestión. El pipeline se asegura de no sobrescribir, sino fechar y empaquetar de forma inteligente los recursos para el usuario final (El Supervisor Logístico de turno).

## Archivos y su Contribución al Pipeline

### `mapa_rutas/`
**Rol:** Contenedor de Front-End Cartográfico.
**Funcionalidad Detallada:**
- Alberga los mapas iterativos en `HTML`.
- Producidos por `grafo/visualizer.py` a lo largo del proceso. Permiten a nivel gerencial pre-aprobar el esquema de clustering generado por `DBSCAN` (Ej: ver que las direcciones lejanas periféricas tienen color propio).
- Adicionalmente, genera la malla visible del "Grafo Físico Vehicular"; pudiendo alternar capas (FeatureGroups) sobre qué chofer/cluster dibujó cuáles trayectorias asfálticas por sector la ciudad entera.

### `rutas/`
**Rol:** Compilaciones y Diarios MD (Logs Analíticos MD).
**Funcionalidad Detallada:**
- Conserva el resultado en limpio extraído desde `gestion_flota/gestor.py`.
- En este subdirectorio reposan reportes cruzados que listan rigurosamente por vehículo asignado (`Vehículo 1`, `Vehículo 2`), cada iteración que deben despachar, la calle exacta de llegada pre-medida, tiempos tentativos, e inflacionarios por tiempos de espera o faltas a la hora de cierre. Todo se compila dentro de tablas legibles por GitHub/Markdown.
