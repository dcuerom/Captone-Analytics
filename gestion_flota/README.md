# Gestión de Flota Fija Global (Gestor Multi-Cluster)

Este directorio conforma la capa arquitectónica de nivel superior (Orquestador) que se encarga de asignar **Físicamente** los trayectos teóricos generados por el algoritmo de optimización interno (PyMoo / Búsqueda Tabú).

## Propósito

El modelo matemático fundamental de nuestro proyecto (`pymoo_problem.py`) resuelve el *Vehicle Routing Problem with Time Windows* (VRPTW) para cada clúster de forma separada por motivos algorítmicos. Sin embargo, en la vida real, una empresa posee un pool global de `N` camiones estacionados en la base (Centro de Distribución), los cuales proveen servicio transversal por toda la región Metropolitana.

El **Gestor de Flota** cierra esta brecha. Toma la resolución "Intra-Cluster" de PyMoo (que crea iterativamente vehículos para satisfacer las demandas locales) y re-empaqueta estos turnos en una **Capacidad de Flota Global Estática**.

## ¿Cómo Opera `gestor.py`?

1. **Recolección:** Espera a que el `genetic_algorithm.py` termine de iterar por todos los clusters geográficos (Conchalí, Maipú, Las Condes, etc). Recibe un compendio masivo `dict_out` que incluye todos los trayectos teóricos calculados (Bloques o Subrutas).
2. **Conversión a Bloques Atómicos:** Desvincula el "camión" abstracto que usó PyMoo para crear la ruta y encapsula cada ruta en un `BloqueRuta` puro. Este bloque define exactamente:
   - Su hora de salida del CD (ej: 09:00).
   - Su hora de retorno de regreso al CD (ej: 14:20).
   - A qué clúster pertenece.
3. **Ordenamiento Temporal Compartido (`Earliest Departure First`):** Aplana todos los bloques independientemente de la geografía, ordenándolos por quién tiene que salir primero a la calle.
4. **Emparejamiento (`Greedy Multi-Turno`):** 
   - Toma el `Vehículo 1` y le entrega la primera ruta disponible en la madrugada (ej: Turno Mañana $K_{11}$ clúster A).
   - El Vehículo 1 queda "ocupado" hasta las 14:20, hora en que vuelve al CD.
   - Tan pronto como vuelve, se le da un tiempo de descarga/preparación en base (`t_preparacion_deposito` = 15 minutos).
   - A las 14:35, el Vehículo 1 vuelve a quedar "libre" computacionalmente, de modo que es capaz de tomar un bloque Tarde ($K_{12}$ clúster C).
5. **Detección de Sub-Floteo (Infactibilidad Física):** El gestor cuenta los vehículos simultáneos que se han visto obligados a salir a la calle para evitar choques en el horario límite. Si se usa el total de `MAX_CAMIONES_GLOBALES` y sobraron bloques que requieren un turno de mañana al mismo que otros, los marca como de requerimiento **excedido (bloques huérfanos o a despachar por servicios tercerizados)**.

## Salida y Reportabilidad

Cambia drásticamente el reporte anterior:
- **Agrupación Fuerte por Camión**: Ahora todo el reporte `ruta_flotaglobal_{algoritmo}_{fecha}.md` tiene una estructura jerárquica con encabezados `## Vehículo Físico GLOBAL X`.
- **Atributos de Tránsito Inter-Cluster**: Las tablas internas agregan la fila `Cluster` bajo cada parada. El usuario/supervisor ve la bitácora perfecta y unificada de por dónde tuvo que viajar ese chofer y chasis específico en la mañana y después en la tarde, abarcando así un verdadero y escalable "Turno Completo" transmutado entre localizaciones del mapa.
