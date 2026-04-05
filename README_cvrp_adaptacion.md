# Adaptación a CVRP Clásico: Documentación Técnica

Este documento explica las premisas de diseño y los atajos operacionales adoptados para integrar instancias clásicas (TSPLIB, EUC_2D) como `A-n32-k5.vrp` utilizando el esquema operativo del proyecto que originalmente fue diseñado localmente para Santiago (esquema Cluster-First, Route-Second con tensores de tiempo).

## 1. Tratamiento del Clustering y Coordenadas
Al operar en un espacio "matemático puro" del CVRP, no existen Latitud y Longitud geográficas estructuradas según Haversine, sino coordenadas cartesianas abstractas ($x, y$). Sin embargo, para mantener integridad con el método original, **hemos retenido el algoritmo `DBSCAN` (vía `run_clustering_pipeline` del `grafo.clustering`)**.

- **¿Cómo interactúan?** Se inyectan temporalmente las coordenadas abstractas $(x)$ como si fuesen Latitud y $(y)$ como Longitud. El modelo normaliza estadísticamente estas componentes ($Z$-score) mediante la función `normalize_and_weight`, permitiendo que el DBSCAN seccione los sub-grafos cartesianos sin depender de los kilómetros de radio, y se usa una ventana dinámica asimilada a las 09:00 hrs.

## 2. Factor de Conversión Tensor y Manejo del Tiempo
La función que otorga tiempo dinámico asimétrico al modelo original es `tau_ij_vec`, la cual espera parámetros de **distancia en metros**. 
Las grillas del TSPLIB a menudo operan en unidades discretas muy pequeñas (ej. $D = 32$). Para evitar que el software confunda la distancia de dos nodos con "32 metros geográficos" (dando como resultado un tiempo de viaje irrealmente minúsculo que haría que todo se atendiera en tres minutos), hemos inyectado un **`dist_multiplier = 100.0`**.

- **Explicación del uso**: Tras extraer la distancia matricial de la grilla ($Euclidiana$), el número cruza al evaluador PyMoo, es **multiplicado por 100** y se introduce a la simulación `tau_ij_vec` como "metros cartesianos teóricos" asegurando que la asimetría temporal funcione. Cuando los tableros CSV finales exportan al exterior, se divide por `100` para retornar las exactas unidades sin procesar de la grilla teórica.
- **Día Fijo**: La velocidad asimétrica del tensor varía por día de la semana. Por estandarización de las pruebas académicas estáticas CVRP, hemos forzado el valor `dia_semana = 0` (Lunes) como semilla de velocidad predeterminada para que las varianzas dependan puramente del desempeño genético del algoritmo y no de caídas de tráfico de domingos.

## 3. Ventana Operacional y Flota
A diferencia de un CVRP tradicional que permite rutas de 20 minutos u 80 horas de corrido asumiendo "flota sin límite", hemos replicado el rigor de la estructura local:
- Las sub-rutas inician siempre en el parámetro `540` (09:00).
- Cada camión ($ID_x$) hereda estrictamente las plantillas K (K11, K21...). Cumcluido un turno, si regresa, el *mismo* $ID_x$ asume la sucesión física de rutas (Turno Tarde), simulando una jornada realista.
- Límite operacional (Hard Constraint): Todo camión, sin importar su nivel de llenado u holgura volumétrica, debe estar de regreso en las coordenadas del Depósito antes de las **21:00 HRS** (`t_llegada < 1260.0`). Esta regla global sustituye las ventanas microscópicas eliminadas de los clientes y restringe explosiones de ruta en sub-espacios densos.
