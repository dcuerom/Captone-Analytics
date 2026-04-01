# 🧠 Módulo `algoritmo/` — Metaheurísticas VRP

Esta carpeta conforma la capa superior de orquestación y optimización metaheurística del proyecto. Su rol dentro del pipeline general es servir de "cerebro" para encontrar soluciones casi-óptimas al problema complejo NP-Hard del ruteo de vehículos (VRPTW).

## Archivos y su Contribución al Pipeline

### `genetic_algorithm.py`
**Rol:** Es el orquestador principal del proyecto y el punto real de entrada a todo el ecosistema.
**Contribución en detalle:**
1. **Punto de Inyección:** Carga los datos base crudos del negocio desde `DatosSimulados/df_despacho.csv`.
2. **Orquestador Espacial:** Llama internamente a `execute_vrp_pipeline()` del módulo abstracto `grafo/` para transformar las direcciones en coordenadas, agrupar a los clientes (DBSCAN) y obtener una matriz asimétrica calculada sobre las calles de Santiago.
3. **El Motor Genético:** Instancia y ejecuta un Algoritmo Genético (GA) mediante la librería `pymoo`. Utiliza cromosomas basados en permutación (`PermutationRandomSampling`, `OrderCrossover`) sobre poblaciones de individuos. Castiga penalizaciones fuertemente gracias a las funciones internas definidas en el módulo `modelo/`.
4. **Despacho Logístico:** Una vez resuelto a nivel de cluster, delega el rompecabezas de turnos al módulo `gestion_flota/` llamando a `asignar_y_reportar()`.

### `ga_vrp.py`
**Rol:** Esquema prototipo bi-objetivo (NSGA2).
**Contribución en detalle:**
Actúa como un artefacto semilla de investigación o Prueba de Concepto (POC) enfocado en optimizaciones multi-objetivo vía NSGA-II. Permite la instanciación de algoritmos genéticos más limpios, sin todo el acoplamiento logístico del archivo principal. Si bien actualmente todo está unificado en `genetic_algorithm.py`, este archivo sirve para experimentación pura con operadores de cruce (SBX) y mutación (PM).

---

## Flujo de Trabajo (Resumen)
El algoritmo contenido acá no calcula el asfalto (eso lo hace `grafo/`) ni impone restricciones matemáticas rígidas en abstracto (eso es trabajo de `modelo/`), simplemente "hace evolucionar" cientos de secuencias de viaje por iteraciones buscando aquella que tenga menores penalizaciones y menor distancia de calle acumulada, despachando su resultado final a la capa de `gestion_flota/`.
