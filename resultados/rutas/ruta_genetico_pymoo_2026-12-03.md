# Reporte GA (PyMoo Problem) - 2026-12-03

## Cluster 0

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 97,131.3 m (97.13 km) |
| Costo Ruta (F = dist × S) | 116,557.56 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 20:29 |
| Duración Total | 11h 29min |
| Vehículos Asignados | 2 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 14/14 |
| Clientes con espera (llegada anticipada) | 6 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 954.4 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 19:41 | 157.1 min | 384.5 min | 100.0 min | 62.22 km | 10 |
| 2 | 09:00 | 20:29 | 80.1 min | 569.9 min | 40.0 min | 34.91 km | 4 |

### Camión 1 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000082_198569524 | 09:32 | [09:00, 11:00] | 09:32 | — | — | ✅ |
| 2 | ORD-CL-202612-000177_19337908  6 | 09:44 | [09:00, 21:00] | 09:44 | — | — | ✅ |
| 3 | ORD-CL-202612-000139_162296701 | 09:56 | [09:00, 21:00] | 09:56 | — | — | ✅ |
| 4 | ORD-CL-202612-000133_55387737 | 10:13 | [11:00, 13:00] | 11:00 | 47 min | — | ⏳ |
| 5 | ORD-CL-202612-000222_64382296 | 11:32 | [13:00, 15:00] | 13:00 | 87 min | — | ⏳ |
| 6 | ORD-CL-202612-000187_5138738  6 | 13:12 | [13:00, 15:00] | 13:12 | — | — | ✅ |
| 7 | ORD-CL-202612-000163_215462173 | 13:29 | [15:00, 17:00] | 15:00 | 91 min | — | ⏳ |
| 8 | ORD-CL-202612-000020_10263868  8 | 15:20 | [15:00, 17:00] | 15:20 | — | — | ✅ |
| 9 | ORD-CL-202612-000006_207417262 | 15:42 | [17:00, 19:00] | 17:00 | 77 min | — | ⏳ |
| 10 | ORD-CL-202612-000135_153012165 | 17:37 | [19:00, 21:00] | 19:00 | 82 min | — | ⏳ |
| 11 | DEPOT_01_BASE | 20:29 | — | — | — | — | 🏠 |

### Camión 2 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000031_14317726  4 | 09:30 | [19:00, 21:00] | 19:00 | 570 min | — | ⏳ |
| 2 | ORD-CL-202612-000002_173134031 | 19:14 | [09:00, 21:00] | 19:14 | — | — | ✅ |
| 3 | ORD-CL-202612-000032_83953104 | 19:36 | [09:00, 21:00] | 19:36 | — | — | ✅ |
| 4 | ORD-CL-202612-000024_53351852 | 19:49 | [19:00, 21:00] | 19:49 | — | — | ✅ |
| 5 | DEPOT_01_BASE | 20:29 | — | — | — | — | 🏠 |


---
## Cluster 1

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 23,430.6 m (23.43 km) |
| Costo Ruta (F = dist × S) | 28,116.73 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 19:47 |
| Duración Total | 10h 47min |
| Vehículos Asignados | 1 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 6/6 |
| Clientes con espera (llegada anticipada) | 2 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 531.3 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 19:47 | 55.9 min | 531.3 min | 60.0 min | 23.43 km | 6 |

### Camión 1 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000091_79104971 | 09:18 | [11:00, 13:00] | 11:00 | 101 min | — | ⏳ |
| 2 | ORD-CL-202612-000055_203179717 | 11:28 | [09:00, 21:00] | 11:28 | — | — | ✅ |
| 3 | ORD-CL-202612-000004_183059669 | 11:40 | [09:00, 21:00] | 11:40 | — | — | ✅ |
| 4 | ORD-CL-202612-000062_7640094    3 | 11:50 | [19:00, 21:00] | 19:00 | 430 min | — | ⏳ |
| 5 | ORD-CL-202612-000115_198154752 | 19:10 | [19:00, 21:00] | 19:10 | — | — | ✅ |
| 6 | ORD-CL-202612-000044_145036177 | 19:24 | [09:00, 21:00] | 19:24 | — | — | ✅ |
| 7 | DEPOT_01_BASE | 19:47 | — | — | — | — | 🏠 |


---
## Cluster 2

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 44,245.5 m (44.25 km) |
| Costo Ruta (F = dist × S) | 53,094.55 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 17:38 |
| Duración Total | 8h 38min |
| Vehículos Asignados | 1 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 9/9 |
| Clientes con espera (llegada anticipada) | 4 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 314.8 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 17:38 | 113.8 min | 314.8 min | 90.0 min | 44.25 km | 9 |

### Camión 1 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000108_9272430  1 | 09:28 | [09:00, 11:00] | 09:28 | — | — | ✅ |
| 2 | ORD-CL-202612-000210_11704104  4 | 09:45 | [11:00, 13:00] | 11:00 | 75 min | — | ⏳ |
| 3 | ORD-CL-202612-000066_96822760 | 11:10 | [09:00, 21:00] | 11:10 | — | — | ✅ |
| 4 | ORD-CL-202612-000195_16543282  2 | 11:34 | [13:00, 15:00] | 13:00 | 85 min | — | ⏳ |
| 5 | ORD-CL-202612-000009_8823811  3 | 13:24 | [13:00, 15:00] | 13:24 | — | — | ✅ |
| 6 | ORD-CL-202612-000021_217856993 | 13:44 | [13:00, 15:00] | 13:44 | — | — | ✅ |
| 7 | ORD-CL-202612-000045_74983175 | 14:02 | [15:00, 17:00] | 15:00 | 58 min | — | ⏳ |
| 8 | ORD-CL-202612-000140_98108348 | 15:10 | [09:00, 21:00] | 15:10 | — | — | ✅ |
| 9 | ORD-CL-202612-000017_149456125 | 15:23 | [17:00, 19:00] | 17:00 | 97 min | — | ⏳ |
| 10 | DEPOT_01_BASE | 17:38 | — | — | — | — | 🏠 |


---
## Cluster 3

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 36,265.9 m (36.27 km) |
| Costo Ruta (F = dist × S) | 43,519.08 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 15:31 |
| Duración Total | 6h 31min |
| Vehículos Asignados | 1 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 5/5 |
| Clientes con espera (llegada anticipada) | 1 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 252.3 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 15:31 | 89.5 min | 252.3 min | 50.0 min | 36.27 km | 5 |

### Camión 1 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000010_62835725 | 09:32 | [09:00, 21:00] | 09:32 | — | — | ✅ |
| 2 | ORD-CL-202612-000096_52601895 | 09:46 | [09:00, 21:00] | 09:46 | — | — | ✅ |
| 3 | ORD-CL-202612-000144_210301989 | 10:07 | [09:00, 11:00] | 10:07 | — | — | ✅ |
| 4 | ORD-CL-202612-000178_6756635  4 | 10:28 | [09:00, 21:00] | 10:28 | — | — | ✅ |
| 5 | ORD-CL-202612-000122_51491954 | 10:47 | [15:00, 17:00] | 15:00 | 252 min | — | ⏳ |
| 6 | DEPOT_01_BASE | 15:31 | — | — | — | — | 🏠 |


---
## Cluster 4

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 21,723.2 m (21.72 km) |
| Costo Ruta (F = dist × S) | 26,067.85 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 19:22 |
| Duración Total | 10h 22min |
| Vehículos Asignados | 1 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 7/7 |
| Clientes con espera (llegada anticipada) | 2 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 498.6 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 19:22 | 53.7 min | 498.6 min | 70.0 min | 21.72 km | 7 |

### Camión 1 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000209_163993586 | 09:09 | [15:00, 17:00] | 15:00 | 350 min | — | ⏳ |
| 2 | ORD-CL-202612-000160_108505650 | 15:10 | [15:00, 17:00] | 15:10 | — | — | ✅ |
| 3 | ORD-CL-202612-000013_9933788  8 | 15:21 | [09:00, 21:00] | 15:21 | — | — | ✅ |
| 4 | ORD-CL-202612-000025_224766177 | 15:33 | [09:00, 21:00] | 15:33 | — | — | ✅ |
| 5 | ORD-CL-202612-000039_64956582 | 15:49 | [09:00, 21:00] | 15:49 | — | — | ✅ |
| 6 | ORD-CL-202612-000126_22556099  9 | 16:07 | [09:00, 21:00] | 16:07 | — | — | ✅ |
| 7 | ORD-CL-202612-000118_65054485 | 16:31 | [19:00, 21:00] | 19:00 | 148 min | — | ⏳ |
| 8 | DEPOT_01_BASE | 19:22 | — | — | — | — | 🏠 |


---
## Cluster 5

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 64,713.4 m (64.71 km) |
| Costo Ruta (F = dist × S) | 77,656.07 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 15:25 |
| Duración Total | 6h 25min |
| Vehículos Asignados | 2 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 11/11 |
| Clientes con espera (llegada anticipada) | 2 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 304.9 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 12:10 | 110.5 min | 0.0 min | 80.0 min | 44.12 km | 8 |
| 2 | 09:00 | 15:25 | 51.0 min | 304.9 min | 30.0 min | 20.59 km | 3 |

### Camión 1 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000141_140162225 | 09:54 | [09:00, 21:00] | 09:54 | — | — | ✅ |
| 2 | ORD-CL-202612-000111_5802113  4 | 10:18 | [09:00, 21:00] | 10:18 | — | — | ✅ |
| 3 | ORD-CL-202612-000208_107728946 | 10:31 | [09:00, 21:00] | 10:31 | — | — | ✅ |
| 4 | ORD-CL-202612-000022_169468917 | 10:56 | [09:00, 21:00] | 10:56 | — | — | ✅ |
| 5 | ORD-CL-202612-000087_17107764  6 | 11:11 | [11:00, 13:00] | 11:11 | — | — | ✅ |
| 6 | ORD-CL-202612-000121_102139227 | 11:26 | [09:00, 21:00] | 11:26 | — | — | ✅ |
| 7 | ORD-CL-202612-000143_14358394    1 | 11:36 | [09:00, 21:00] | 11:36 | — | — | ✅ |
| 8 | ORD-CL-202612-000015_93475810 | 11:46 | [09:00, 21:00] | 11:46 | — | — | ✅ |
| 9 | DEPOT_01_BASE | 15:25 | — | — | — | — | 🏠 |

### Camión 2 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000150_10411606  1 | 09:09 | [09:00, 21:00] | 09:09 | — | — | ✅ |
| 2 | ORD-CL-202612-000011_18195149  6 | 09:38 | [13:00, 15:00] | 13:00 | 202 min | — | ⏳ |
| 3 | ORD-CL-202612-000071_212196364 | 13:16 | [15:00, 17:00] | 15:00 | 103 min | — | ⏳ |
| 4 | DEPOT_01_BASE | 15:25 | — | — | — | — | 🏠 |


---
## Cluster 6

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 32,272.8 m (32.27 km) |
| Costo Ruta (F = dist × S) | 38,727.33 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 15:43 |
| Duración Total | 6h 43min |
| Vehículos Asignados | 1 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 4/4 |
| Clientes con espera (llegada anticipada) | 2 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 284.9 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 15:43 | 78.4 min | 284.9 min | 40.0 min | 32.27 km | 4 |

### Camión 1 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000049_111101253 | 09:29 | [13:00, 15:00] | 13:00 | 210 min | — | ⏳ |
| 2 | ORD-CL-202612-000060_199941644 | 13:20 | [09:00, 21:00] | 13:20 | — | — | ✅ |
| 3 | ORD-CL-202612-000019_156820915 | 13:33 | [09:00, 21:00] | 13:33 | — | — | ✅ |
| 4 | ORD-CL-202612-000092_162059956 | 13:45 | [15:00, 17:00] | 15:00 | 75 min | — | ⏳ |
| 5 | DEPOT_01_BASE | 15:43 | — | — | — | — | 🏠 |


---
## Cluster 7

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 24,570.7 m (24.57 km) |
| Costo Ruta (F = dist × S) | 29,484.83 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 11:23 |
| Duración Total | 2h 23min |
| Vehículos Asignados | 3 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 19/19 |
| Clientes con espera (llegada anticipada) | 6 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 916.5 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 19:48 | 28.4 min | 520.2 min | 100.0 min | 12.06 km | 10 |
| 2 | 09:00 | 15:13 | 24.8 min | 278.7 min | 70.0 min | 10.11 km | 7 |
| 3 | 09:00 | 11:23 | 5.9 min | 117.5 min | 20.0 min | 2.39 km | 2 |

### Camión 1 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000197_12172627  6 | 09:02 | [09:00, 11:00] | 09:02 | — | — | ✅ |
| 2 | ORD-CL-202612-000089_172068824 | 09:12 | [11:00, 13:00] | 11:00 | 107 min | — | ⏳ |
| 3 | ORD-CL-202612-000103_22242242  0 | 11:10 | [09:00, 21:00] | 11:10 | — | — | ✅ |
| 4 | ORD-CL-202612-000116_73802946 | 11:21 | [09:00, 21:00] | 11:21 | — | — | ✅ |
| 5 | ORD-CL-202612-000170_137256512 | 11:33 | [09:00, 21:00] | 11:33 | — | — | ✅ |
| 6 | ORD-CL-202612-000026_175731263 | 11:43 | [17:00, 19:00] | 17:00 | 316 min | — | ⏳ |
| 7 | ORD-CL-202612-000169_15815165  1 | 17:13 | [17:00, 19:00] | 17:13 | — | — | ✅ |
| 8 | ORD-CL-202612-000107_158151651 | 17:23 | [19:00, 21:00] | 19:00 | 97 min | — | ⏳ |
| 9 | ORD-CL-202612-000095_140053537 | 19:16 | [09:00, 21:00] | 19:16 | — | — | ✅ |
| 10 | ORD-CL-202612-000061_180518007 | 19:32 | [09:00, 21:00] | 19:32 | — | — | ✅ |
| 11 | DEPOT_01_BASE | 11:23 | — | — | — | — | 🏠 |

### Camión 2 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000088_79249631 | 09:02 | [09:00, 11:00] | 09:02 | — | — | ✅ |
| 2 | ORD-CL-202612-000155_22116046  1 | 09:12 | [09:00, 21:00] | 09:12 | — | — | ✅ |
| 3 | ORD-CL-202612-000093_134538869 | 09:26 | [09:00, 21:00] | 09:26 | — | — | ✅ |
| 4 | ORD-CL-202612-000027_7499276  7 | 09:38 | [11:00, 13:00] | 11:00 | 82 min | — | ⏳ |
| 5 | ORD-CL-202612-000188_146386625 | 11:12 | [09:00, 21:00] | 11:12 | — | — | ✅ |
| 6 | ORD-CL-202612-000196_204415159 | 11:28 | [09:00, 21:00] | 11:28 | — | — | ✅ |
| 7 | ORD-CL-202612-000184_21805102  0 | 11:43 | [15:00, 17:00] | 15:00 | 197 min | — | ⏳ |
| 8 | DEPOT_01_BASE | 11:23 | — | — | — | — | 🏠 |

### Camión 3 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000085_15236104    9 | 09:02 | [11:00, 13:00] | 11:00 | 118 min | — | ⏳ |
| 2 | ORD-CL-202612-000119_6466103  7 | 11:12 | [11:00, 13:00] | 11:12 | — | — | ✅ |
| 3 | DEPOT_01_BASE | 11:23 | — | — | — | — | 🏠 |


---
## Cluster 8

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 33,224.2 m (33.22 km) |
| Costo Ruta (F = dist × S) | 39,869.03 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 17:36 |
| Duración Total | 8h 36min |
| Vehículos Asignados | 1 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 10/10 |
| Clientes con espera (llegada anticipada) | 3 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 330.5 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 17:36 | 86.0 min | 330.5 min | 100.0 min | 33.22 km | 10 |

### Camión 1 — Detalle de Paradas
| # | Nodo | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000166_9709625  6 | 09:13 | [09:00, 11:00] | 09:13 | — | — | ✅ |
| 2 | ORD-CL-202612-000183_148999950 | 09:32 | [09:00, 11:00] | 09:32 | — | — | ✅ |
| 3 | ORD-CL-202612-000052_14976779    6 | 09:57 | [13:00, 15:00] | 13:00 | 182 min | — | ⏳ |
| 4 | ORD-CL-202612-000179_121067557 | 13:13 | [09:00, 21:00] | 13:13 | — | — | ✅ |
| 5 | ORD-CL-202612-000069_143319312 | 13:28 | [09:00, 21:00] | 13:28 | — | — | ✅ |
| 6 | ORD-CL-202612-000112_208275613 | 13:40 | [15:00, 17:00] | 15:00 | 80 min | — | ⏳ |
| 7 | ORD-CL-202612-000180_135550036 | 15:16 | [09:00, 21:00] | 15:16 | — | — | ✅ |
| 8 | ORD-CL-202612-000079_112922605 | 15:32 | [09:00, 21:00] | 15:32 | — | — | ✅ |
| 9 | ORD-CL-202612-000148_175474353 | 15:51 | [17:00, 19:00] | 17:00 | 68 min | — | ⏳ |
| 10 | ORD-CL-202612-000094_84473640 | 17:14 | [09:00, 21:00] | 17:14 | — | — | ✅ |
| 11 | DEPOT_01_BASE | 17:36 | — | — | — | — | 🏠 |


---
