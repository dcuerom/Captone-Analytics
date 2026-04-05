# Condiciones de Operación y Supuestos del Modelo CVRP Clásico

La adaptación del pipeline generador de mallas operativas (TDVRPTW originalmente estructurado para cuadrantes urbanos dinámicos) para permitir la resolución y mapeo en entornos teóricos del **CVRP TSPLIB (Plano Euclidiano Puro)** conllevó las siguientes parametrizaciones e interpretaciones:

## 1. Condiciones de Operación

1. **Clústering Operacional**
2. **Jornada y Límite Global de Operación (Ventana de 9 a 9)**

   - Se erradicaron las ventanas temporales asimétricas para cada cliente; todos nacen disponibles. Sin embargo, el universo de la simulación impone que ninguna flota puede nacer antes de las **09:00 a.m.** (`540 min`), y toda unidad *debe* tener terminada físicamente su faena regresando al origen a las **09:00 p.m.** (`1260 min`).
3. **Limitante Unidimensional Estricto de Carga**

   - El vehículo solo audita un umbral `Q` referenciado como *peso*. Se descartan volumetrías CBM, cajas estáticas, perfiles de mercadería térmica y anchos de vía en favor de obedecer netamente la variable declarada en las cabeceras `CAPACITY` de la instancia.
4. **Multi-Turnos Re-Operativos (Gestión K)**

   - Si un camión físico alcanza su límite de carga a las `11:00 a.m.`, es obligado a retornar al **Depósito**. En lugar de caducar u obligar la contratación de otro ID logístico, el software utiliza ese mismo camión físico (asignándole el segundo turno programado, ej. `K12`), ahorrando flota física limitando el cruce al techo impuesto de `$K_{max}$`.

---

## 2. Supuestos Considerados en la Adaptación

1. **El Supuesto de Metrológico y Congestión Escalar (`Factor 100`)**

   - **Situación:** Una topología plana tradicional de TSPLIB se concentra en grillas abstractas $[0, 100]$, lo que el algoritmo interpretaría llanamente como *metros urbanos*. 100 metros serían transitados en menos de un minuto real, inhabilitando la función matemática temporal.
   - **Supuesto:** Se asume y multiplica un factor de `x 100.0` en todas las lecturas de los arcos Euclidianos cuando entran al conversor de tiempo. Esto expande ficticiamente la grilla del problema hacia magnitudes comparables a avenidas reales sin alterar los polígonos, dándole la oportunidad al Tensor Operativo (`tau_ij_vec`) de frenar o acelerar los tiempos lógicos al simular horas reales.
2. **Homogeneidad Atmosférica y de Tránsito (Virtualidad del "Lunes")**

   - **Situación:** En el proyecto oficial, los tiempos de tránsitos ($C_{ij}$) sufren asimetrías pesadas si son recorridos un Fin de Semana versus un Miércoles a las `08:00 A.M`. Las pruebas paramétricas de escritorio exigen estabilidad.
   - **Supuesto:** Se congela arbitrariamente toda iteración al `"Día de la semana = 0"` (Lunes constante). Cualquier retardo, caída de la asimetría temporal de rutas, o tapón simulado del algoritmo reacciona universalmente como el día lunes, aislando el comportamiento para comparar la eficacia del ruteo independientemente del tráfico externo.
3. **Demora Fija de Operación (Tiempo de Servicio)**

   - **Situación:** Numerosas instancias clásicas TSPLIB no declaran el `Service Delay` de descargar cajas, provocando que los modelos asuman recolección y servicio cronométrico inmediato sin detención aparente (Tiempo cero en nodo).
   - **Supuesto:** La adaptabilidad exige un retraso operacional estándar. Cada llegada a nodo estipula congelar al Algoritmo durante `5.0 min` en el servidor independientemente de la instancia testeada. Ese tiempo suma contra el reloj de cierre global de jornada a las `21:00hrs`.
4. **Sincronía Geográfica de Flota (Sectorización Aglomerativa = K Vehículos)**

   - **Situación:** Con una flota pre-declarada pequeña ($K=5$ o $K=10$), los enfoques basados estrictamente en densidad (DBSCAN) o volumetría pura generarían disparidades (ej: dejar un único clúster geográfico al que los 10 camiones deban viajar juntos empalmándose en la zona).
   - **Supuesto:** Se asume que el territorio plano **debe** estar sectorizado a priori en exactamente la misma cantidad de macro-zonas que vehículos disponibles posee la empresa ($N\_clusters = K\_trucks$). Empleando *Clustering Aglomerativo*, el sistema garantiza particionar los clientes en la misma cantidad de camiones. Esto asegura matemáticamente que en la teoría de despacho ideal, a cada sector geográfico se le apunte el esfuerzo primario de al menos *un* camión exclusivo.
