# 🚀 Pipeline Global de Optimización: Capstone Analytics TDVRPTW

Este repositorio soluciona en su totalidad el problema avanzado de optimismo geográfico de **Routing de Vehículos Dependiente del Tiempo, con Ventanas de Tiempo y Múltiples Restricciones de Capacidad**.

Este documento maestro (`PIPELINE_GLOBAL.md`) explica cómo el sistema de carpetas y arquitecturas está desacoplado y fluye desde los datos planos hacia asignaciones logísticas reales, combinándose bajo la premisa algorítmica de **"Cluster-First, Route-Second"**.

---

## Estructura Macro de Ejecución

Cuando el usuario gatilla `algoritmo/genetic_algorithm.py`, desencadena un efecto dominó que convoca lógicamente al resto del ecosistema:

### 1. Preparación Espacial (Módulo: `grafo/`)
Aquí se ubica la capa geo-matemática. **No existe PyMoo aquí**, pero prepara todas las matrices que lo harán posible.
- Traduce cada orden (`df_despacho.csv`) en un punto georeferenciado vía la API ArcGIS (`geocoder.py`).
- Usa clustering multivariable 3D (Latitud, Longitud, Inicio Ventana) mediante `DBSCAN` en el archivo `clustering.py`. Transforma un problema irresoluble globalmente en sub-agrupaciones manejables (Polígonos o "Clústers").
- Descarga y se conecta con el asfalto (Grafo dirigido OSMNX) de toda el Área Metropolitana en `network_builder.py`.
- Finalmente, se calculan todas las combinaciones reales posibles limitadas al entorno de esas agrupaciones pre-fijadas (`routing.py`), esquivando rutas imposibles o pasajes peatonales vía algoritmos tipo A* asimétrico.

### 2. Formulación Heurística (Módulo: `modelo/`)
Una vez el Grafo resolvió los *dónde* y *a cuántos metros de calle* están los destinos del respectivo clúster, le toca a la "Ciencia de Decisión".
- La clase residente `pymoo_problem.py` plantea el escenario: tenemos penalizaciones y factibilidades. Castigará (` Hard Constraints = G`) todo vehículo que llegue fuera del tiempo acordado. Aumentará artificialmente el costo (`Fitness function = F`) por cada camión extra que se vea obligado a usar para satisfacer masa(`g`) o volumen(`cm3`).
- Contiene además, subalgoritmos analíticos en `funciones/tiempos_viaje.py` parametrizados para inflar matemáticamente la duración en base a perfiles de hora punta de tráfico ($D_{ij} \times \text{Función}(\tau)$).

### 3. Solución (Módulo: `algoritmo/`)
- Intercepta el problema configurado de forma independiente y, usando la librería `PyMoo` sobre `genetic_algorithm.py`, hace divergir e iterar 50 cromosomas (rutas de clientes) a través de "selección de ruleta", y cruzas inteligentes sin duplicación de nodos.
- Luego de decenas de generaciones (mutando caminos locamente), extrae las topologías supremas y menos erráticas para el Clúster $K_i$.

### 4. Empaquetamiento Real (Módulo: `gestion_flota/`)
- A pesar de que la optimización se hace parceladamente en `PyMoo`, las empresas tienen una cantidad **Fija** y centralizada de vehículos.
- El archivo `gestor.py` asume esta última capa: toma los trayectos ganadores de cada clúster y los redistribuye a camiones unificados globales en forma de "Turnos".
- Ordena quién sale primero cronológicamente, detectando si un vehículo que atendió el bloque de Las Condes fue lo suficientemente rápido como para volver al CD e intervenir en la tarde para el sub-módulo de Santiago Centro.
- De requerir más transportes simultáneos, lo transparenta hacia variables huérfanas o transporte *Tercerizado*.

### 5. Artefactación (Módulo: `resultados/`)
- El pipeline imprime una versión limpia humana que recopila este último tramo del Gestor, emitiendo Tablas Analíticas de Control en `.md`, desglosando llegada, peso y tiempos en cola o paradas de cada nodo visitado.
- Asimismo, empuja al módulo abstracto de `visualizer.py` y lanza frentes `.html` interactivos para su validación manual (Folium), permitiendo encender visualizaciones físicas turno por vehículo.

---
**Inicio de Ruta Crítica Recomendado**: Ejecutar siempre desde `python algoritmo/genetic_algorithm.py`.
