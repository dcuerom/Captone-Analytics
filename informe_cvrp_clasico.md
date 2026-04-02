# Resumen de Implementación de CVRP Clásico

He implementado de forma paralela el pipeline para procesar archivos de instancias TSPLIB con distancias euclidianas tal como lo planteaste para mantener a salvo el modelo geográfico principal.

## Componentes Desarrollados

1. **Parser (`grafo/cvrp_parser.py`)**:
   Implementado para leer dinámicamente el `A-n32-k5.vrp` y cualquier otro archivo con el formato numérico TSPLIB EUC_2D estricto. Extrae la **Dimensión** y **Capacidad ($Q=100$)**, además estima la cantidad ideal de vehículos en base al nombre `-k5`.
2. **Clusterización (`grafo/cvrp_clustering.py`)**:
   Se modificó la lógica para usar un modelo Euclidiano (puro $X, Y$) descartando Haversine, basado en `KMeans` para garantizar N clusters iguales a la cantidad teórica de camiones (`k=5`). Esto permite retener el paso de "Clustering" del pipeline original, pero ahora en el plano real del archivo.
3. **Grafos y Matemática (`grafo/cvrp_grafo.py`)**:
   En lugar recurrir al costoso A* de calles reales, inyectamos una función que calcula la matriz estricta usando $Distancia = \sqrt{(x_1-x_2)^2 + (y_1-y_2)^2}$ resguardando cada flotante sin trucar o redondear iterativamente.
4. **Modelo PyMoo Genético (`modelo/cvrp_pymoo_problem.py` y `algoritmo/cvrp_genetic.py`)**:
   - Reemplazado $D_{ij}$ asimétricos con la nueva matriz Euclidiana métrica.
   - Simplificada la asimetría temporal: Se erradicó la ventana de minutos; la penalización ("restricción dura") está unicamente dada por **peso total de clientes de la ruta vs. Capacidad $Q$ del vehículo**. Si el camión supera el peso actual, el algoritmo modela y cobra computacionalmente un retorno al depósito despachando al siguiente camión.
   - El optimizador maximiza la pureza y limpieza de cada sub-viaje priorizando distancias totales óptimas.

## Resultados Obtenidos
Ejecuté la instancia de validación **`A-n32-k5.vrp`**. Nuestro algoritmo genético pudo crear grupos, asignar y retornar un Óptimo Local Consolidado de **$D_{ij} = \approx 912$** en menos de 10 segundos, asignándole los 5 camiones de capacidad de peso (100) estipulados de forma impecable.

### Archivos Finales Generados
El pipeline procesó exitosa y limpiamente la tabla requerida con los formatos y simulaciones temporales "ficticias". Te comparto la ubicación de los reportes por cada camión generados durante la prueba en tu espacio `.csv`:

**1. Resumen por Camión** (`resultados/cvrp/CVRP_Resumen_20260401_205901.csv`):
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Dist   | Clientes |
|---------|---------|-------|-----------|------------|----------------|--------|----------|
| 1       | K11     | Mañana| 09:00     | 18:00      | 3.97           | 158.69 | 9        |
| 2       | K11     | Mañana| 09:00     | 18:00      | 5.95           | 237.93 | 7        |
| ...     | ...     | ...   | ...       | ...        | ...            | ...    | ...      |

**2. Detalle de Nodos Visitados** (`resultados/cvrp/CVRP_Detalle_20260401_205901.csv`):
| Cluster | clase | nodo | coordenadas  | distancia | peso |
|---------|-------|------|--------------|-----------|------|
| 1       | K11   | 25   | (61.0, 62.0) | 62.59     | 24.0 |
| 1       | K11   | 15   | (61.0, 59.0) | 3.0       | 3.0  |
| 1       | K11   | 31   | (85.0, 60.0) | 24.02     | 14.0 |
| ...     | ...   | ...  | ...          | ...       | ...  |

Puedes iterar o usar nuevas instancias fácilmente ejecutando:
```bash
conda run -n capstone python algoritmo/cvrp_genetic.py "Instancias de Prueba VRP/tu_instancia.vrp"
```
