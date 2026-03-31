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
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000082_198569524 | 12.32 | 32.1 m | 23.0 | 09:32 | [09:00,11:00] | 09:32 | 10.0 m | 481.1 L | 96.3 kg | — | — | ✅ |
| 2 | ORD-CL-202612-000177_19337908  6 | 1.09 | 2.8 m | 23.1 | 09:44 | [09:00,21:00] | 09:44 | 10.0 m | 905.8 L | 185.3 kg | — | — | ✅ |
| 3 | ORD-CL-202612-000139_162296701 | 0.45 | 1.1 m | 23.9 | 09:56 | [09:00,21:00] | 09:56 | 10.0 m | 614.9 L | 114.0 kg | — | — | ✅ |
| 4 | ORD-CL-202612-000133_55387737 | 2.91 | 7.1 m | 24.7 | 10:13 | [11:00,13:00] | 11:00 | 10.0 m | 379.5 L | 55.8 kg | 47 m | — | ⏳ |
| 5 | ORD-CL-202612-000222_64382296 | 9.42 | 22.6 m | 25.0 | 11:32 | [13:00,15:00] | 13:00 | 10.0 m | 1396.1 L | 158.3 kg | 87 m | — | ⏳ |
| 6 | ORD-CL-202612-000187_5138738  6 | 1.11 | 2.7 m | 25.0 | 13:12 | [13:00,15:00] | 13:12 | 10.0 m | 222.3 L | 37.4 kg | — | — | ✅ |
| 7 | ORD-CL-202612-000163_215462173 | 2.77 | 6.6 m | 25.0 | 13:29 | [15:00,17:00] | 15:00 | 10.0 m | 24.8 L | 9.3 kg | 91 m | — | ⏳ |
| 8 | ORD-CL-202612-000020_10263868  8 | 4.52 | 10.4 m | 26.0 | 15:20 | [15:00,17:00] | 15:20 | 10.0 m | 3905.5 L | 441.5 kg | — | — | ✅ |
| 9 | ORD-CL-202612-000006_207417262 | 5.26 | 12.4 m | 25.4 | 15:42 | [17:00,19:00] | 17:00 | 10.0 m | 639.5 L | 113.7 kg | 77 m | — | ⏳ |
| 10 | ORD-CL-202612-000135_153012165 | 9.31 | 27.6 m | 20.3 | 17:37 | [19:00,21:00] | 19:00 | 10.0 m | 644.2 L | 128.1 kg | 82 m | — | ⏳ |
| 11 | DEPOT_01_BASE | 13.06 | 31.6 m | 24.8 | 19:41 | — | — | — | — | — | — | — | 🏠 |

### Camión 2 — Detalle de Paradas
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000031_14317726  4 | 11.54 | 30.1 m | 23.0 | 09:30 | [19:00,21:00] | 19:00 | 10.0 m | 2786.0 L | 391.8 kg | 570 m | — | ⏳ |
| 2 | ORD-CL-202612-000002_173134031 | 1.91 | 4.6 m | 24.8 | 19:14 | [09:00,21:00] | 19:14 | 10.0 m | 4239.4 L | 505.6 kg | — | — | ✅ |
| 3 | ORD-CL-202612-000032_83953104 | 5.58 | 11.9 m | 28.0 | 19:36 | [09:00,21:00] | 19:36 | 10.0 m | 2217.2 L | 261.7 kg | — | — | ✅ |
| 4 | ORD-CL-202612-000024_53351852 | 1.20 | 2.6 m | 28.0 | 19:49 | [19:00,21:00] | 19:49 | 10.0 m | 168.8 L | 34.9 kg | — | — | ✅ |
| 5 | DEPOT_01_BASE | 14.69 | 30.8 m | 28.6 | 20:29 | — | — | — | — | — | — | — | 🏠 |


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
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000091_79104971 | 7.16 | 18.7 m | 23.0 | 09:18 | [11:00,13:00] | 11:00 | 10.0 m | 848.6 L | 167.5 kg | 101 m | — | ⏳ |
| 2 | ORD-CL-202612-000055_203179717 | 7.87 | 18.9 m | 25.0 | 11:28 | [09:00,21:00] | 11:28 | 10.0 m | 224.5 L | 56.1 kg | — | — | ✅ |
| 3 | ORD-CL-202612-000004_183059669 | 0.49 | 1.2 m | 25.0 | 11:40 | [09:00,21:00] | 11:40 | 10.0 m | 2514.1 L | 317.4 kg | — | — | ✅ |
| 4 | ORD-CL-202612-000062_7640094    3 | 0.00 | 0.0 m | 0.0 | 11:50 | [19:00,21:00] | 19:00 | 10.0 m | 634.5 L | 101.6 kg | 430 m | — | ⏳ |
| 5 | ORD-CL-202612-000115_198154752 | 0.13 | 0.3 m | 24.8 | 19:10 | [19:00,21:00] | 19:10 | 10.0 m | 371.8 L | 100.9 kg | — | — | ✅ |
| 6 | ORD-CL-202612-000044_145036177 | 1.77 | 3.9 m | 27.0 | 19:24 | [09:00,21:00] | 19:24 | 10.0 m | 855.7 L | 127.7 kg | — | — | ✅ |
| 7 | DEPOT_01_BASE | 6.02 | 12.9 m | 28.0 | 19:47 | — | — | — | — | — | — | — | 🏠 |


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
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000108_9272430  1 | 11.05 | 28.8 m | 23.0 | 09:28 | [09:00,11:00] | 09:28 | 10.0 m | 230.5 L | 31.4 kg | — | — | ✅ |
| 2 | ORD-CL-202612-000210_11704104  4 | 2.37 | 6.2 m | 23.0 | 09:45 | [11:00,13:00] | 11:00 | 10.0 m | 1707.5 L | 294.1 kg | 75 m | — | ⏳ |
| 3 | ORD-CL-202612-000066_96822760 | 0.00 | 0.0 m | 0.0 | 11:10 | [09:00,21:00] | 11:10 | 10.0 m | 1260.2 L | 220.9 kg | — | — | ✅ |
| 4 | ORD-CL-202612-000195_16543282  2 | 6.10 | 14.6 m | 25.0 | 11:34 | [13:00,15:00] | 13:00 | 10.0 m | 1450.2 L | 222.2 kg | 85 m | — | ⏳ |
| 5 | ORD-CL-202612-000009_8823811  3 | 6.01 | 14.4 m | 25.0 | 13:24 | [13:00,15:00] | 13:24 | 10.0 m | 2219.0 L | 256.8 kg | — | — | ✅ |
| 6 | ORD-CL-202612-000021_217856993 | 4.07 | 9.6 m | 25.4 | 13:44 | [13:00,15:00] | 13:44 | 10.0 m | 482.8 L | 56.6 kg | — | — | ✅ |
| 7 | ORD-CL-202612-000045_74983175 | 3.57 | 8.2 m | 26.0 | 14:02 | [15:00,17:00] | 15:00 | 10.0 m | 31.4 L | 10.2 kg | 58 m | — | ⏳ |
| 8 | ORD-CL-202612-000140_98108348 | 0.00 | 0.0 m | 0.0 | 15:10 | [09:00,21:00] | 15:10 | 10.0 m | 74.7 L | 16.7 kg | — | — | ✅ |
| 9 | ORD-CL-202612-000017_149456125 | 1.39 | 3.2 m | 25.7 | 15:23 | [17:00,19:00] | 17:00 | 10.0 m | 22.7 L | 6.4 kg | 97 m | — | ⏳ |
| 10 | DEPOT_01_BASE | 9.67 | 28.6 m | 20.3 | 17:38 | — | — | — | — | — | — | — | 🏠 |


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
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000010_62835725 | 12.29 | 32.1 m | 23.0 | 09:32 | [09:00,21:00] | 09:32 | 10.0 m | 894.1 L | 164.7 kg | — | — | ✅ |
| 2 | ORD-CL-202612-000096_52601895 | 1.63 | 4.2 m | 23.1 | 09:46 | [09:00,21:00] | 09:46 | 10.0 m | 1136.0 L | 188.5 kg | — | — | ✅ |
| 3 | ORD-CL-202612-000144_210301989 | 4.44 | 11.1 m | 24.0 | 10:07 | [09:00,11:00] | 10:07 | 10.0 m | 196.0 L | 24.5 kg | — | — | ✅ |
| 4 | ORD-CL-202612-000178_6756635  4 | 4.74 | 11.4 m | 25.0 | 10:28 | [09:00,21:00] | 10:28 | 10.0 m | 363.4 L | 89.2 kg | — | — | ✅ |
| 5 | ORD-CL-202612-000122_51491954 | 3.73 | 8.9 m | 25.0 | 10:47 | [15:00,17:00] | 15:00 | 10.0 m | 322.7 L | 73.9 kg | 252 m | — | ⏳ |
| 6 | DEPOT_01_BASE | 9.43 | 21.8 m | 26.0 | 15:31 | — | — | — | — | — | — | — | 🏠 |


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
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000209_163993586 | 3.75 | 9.8 m | 23.0 | 09:09 | [15:00,17:00] | 15:00 | 10.0 m | 276.9 L | 36.7 kg | 350 m | — | ⏳ |
| 2 | ORD-CL-202612-000160_108505650 | 0.00 | 0.0 m | 0.0 | 15:10 | [15:00,17:00] | 15:10 | 10.0 m | 245.4 L | 52.4 kg | — | — | ✅ |
| 3 | ORD-CL-202612-000013_9933788  8 | 0.47 | 1.1 m | 25.7 | 15:21 | [09:00,21:00] | 15:21 | 10.0 m | 262.6 L | 34.5 kg | — | — | ✅ |
| 4 | ORD-CL-202612-000025_224766177 | 1.00 | 2.4 m | 25.4 | 15:33 | [09:00,21:00] | 15:33 | 10.0 m | 1343.6 L | 132.4 kg | — | — | ✅ |
| 5 | ORD-CL-202612-000039_64956582 | 2.58 | 6.2 m | 25.0 | 15:49 | [09:00,21:00] | 15:49 | 10.0 m | 3005.7 L | 379.0 kg | — | — | ✅ |
| 6 | ORD-CL-202612-000126_22556099  9 | 3.19 | 7.6 m | 25.0 | 16:07 | [09:00,21:00] | 16:07 | 10.0 m | 866.8 L | 120.4 kg | — | — | ✅ |
| 7 | ORD-CL-202612-000118_65054485 | 5.62 | 14.3 m | 23.6 | 16:31 | [19:00,21:00] | 19:00 | 10.0 m | 1214.1 L | 215.7 kg | 148 m | — | ⏳ |
| 8 | DEPOT_01_BASE | 5.12 | 12.4 m | 24.8 | 19:22 | — | — | — | — | — | — | — | 🏠 |


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
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000141_140162225 | 20.74 | 54.1 m | 23.0 | 09:54 | [09:00,21:00] | 09:54 | 10.0 m | 84.7 L | 24.3 kg | — | — | ✅ |
| 2 | ORD-CL-202612-000111_5802113  4 | 6.01 | 14.7 m | 24.6 | 10:18 | [09:00,21:00] | 10:18 | 10.0 m | 2018.8 L | 255.6 kg | — | — | ✅ |
| 3 | ORD-CL-202612-000208_107728946 | 1.13 | 2.7 m | 25.0 | 10:31 | [09:00,21:00] | 10:31 | 10.0 m | 4894.5 L | 609.0 kg | — | — | ✅ |
| 4 | ORD-CL-202612-000022_169468917 | 6.07 | 14.6 m | 25.0 | 10:56 | [09:00,21:00] | 10:56 | 10.0 m | 929.9 L | 130.3 kg | — | — | ✅ |
| 5 | ORD-CL-202612-000087_17107764  6 | 2.46 | 5.9 m | 25.0 | 11:11 | [11:00,13:00] | 11:11 | 10.0 m | 237.6 L | 62.3 kg | — | — | ✅ |
| 6 | ORD-CL-202612-000121_102139227 | 1.78 | 4.3 m | 25.0 | 11:26 | [09:00,21:00] | 11:26 | 10.0 m | 1152.4 L | 159.0 kg | — | — | ✅ |
| 7 | ORD-CL-202612-000143_14358394    1 | 0.00 | 0.0 m | 0.0 | 11:36 | [09:00,21:00] | 11:36 | 10.0 m | 74.2 L | 18.0 kg | — | — | ✅ |
| 8 | ORD-CL-202612-000015_93475810 | 0.00 | 0.0 m | 0.0 | 11:46 | [09:00,21:00] | 11:46 | 10.0 m | 266.4 L | 74.4 kg | — | — | ✅ |
| 9 | DEPOT_01_BASE | 5.93 | 14.2 m | 25.0 | 12:10 | — | — | — | — | — | — | — | 🏠 |

### Camión 2 — Detalle de Paradas
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000150_10411606  1 | 3.64 | 9.5 m | 23.0 | 09:09 | [09:00,21:00] | 09:09 | 10.0 m | 1086.9 L | 173.4 kg | — | — | ✅ |
| 2 | ORD-CL-202612-000011_18195149  6 | 7.13 | 18.6 m | 23.0 | 09:38 | [13:00,15:00] | 13:00 | 10.0 m | 4252.7 L | 550.2 kg | 202 m | — | ⏳ |
| 3 | ORD-CL-202612-000071_212196364 | 2.92 | 7.0 m | 25.0 | 13:16 | [15:00,17:00] | 15:00 | 10.0 m | 1006.0 L | 197.4 kg | 103 m | — | ⏳ |
| 4 | DEPOT_01_BASE | 6.90 | 15.9 m | 26.0 | 15:25 | — | — | — | — | — | — | — | 🏠 |


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
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000049_111101253 | 11.40 | 29.7 m | 23.0 | 09:29 | [13:00,15:00] | 13:00 | 10.0 m | 3858.7 L | 488.3 kg | 210 m | — | ⏳ |
| 2 | ORD-CL-202612-000060_199941644 | 4.48 | 10.8 m | 25.0 | 13:20 | [09:00,21:00] | 13:20 | 10.0 m | 577.7 L | 83.3 kg | — | — | ✅ |
| 3 | ORD-CL-202612-000019_156820915 | 1.35 | 3.2 m | 25.3 | 13:33 | [09:00,21:00] | 13:33 | 10.0 m | 2163.4 L | 238.1 kg | — | — | ✅ |
| 4 | ORD-CL-202612-000092_162059956 | 0.62 | 1.4 m | 25.7 | 13:45 | [15:00,17:00] | 15:00 | 10.0 m | 892.8 L | 131.5 kg | 75 m | — | ⏳ |
| 5 | DEPOT_01_BASE | 14.42 | 33.3 m | 26.0 | 15:43 | — | — | — | — | — | — | — | 🏠 |


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
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000197_12172627  6 | 1.00 | 2.6 m | 23.0 | 09:02 | [09:00,11:00] | 09:02 | 10.0 m | 2704.0 L | 358.4 kg | — | — | ✅ |
| 2 | ORD-CL-202612-000089_172068824 | 0.00 | 0.0 m | 0.0 | 09:12 | [11:00,13:00] | 11:00 | 10.0 m | 653.9 L | 144.7 kg | 107 m | — | ⏳ |
| 3 | ORD-CL-202612-000103_22242242  0 | 0.29 | 0.7 m | 25.0 | 11:10 | [09:00,21:00] | 11:10 | 10.0 m | 208.2 L | 28.5 kg | — | — | ✅ |
| 4 | ORD-CL-202612-000116_73802946 | 0.38 | 0.9 m | 25.0 | 11:21 | [09:00,21:00] | 11:21 | 10.0 m | 409.0 L | 59.3 kg | — | — | ✅ |
| 5 | ORD-CL-202612-000170_137256512 | 0.95 | 2.3 m | 25.0 | 11:33 | [09:00,21:00] | 11:33 | 10.0 m | 776.8 L | 140.6 kg | — | — | ✅ |
| 6 | ORD-CL-202612-000026_175731263 | 0.00 | 0.0 m | 0.0 | 11:43 | [17:00,19:00] | 17:00 | 10.0 m | 1731.7 L | 205.5 kg | 316 m | — | ⏳ |
| 7 | ORD-CL-202612-000169_15815165  1 | 1.10 | 3.3 m | 20.3 | 17:13 | [17:00,19:00] | 17:13 | 10.0 m | 682.2 L | 97.5 kg | — | — | ✅ |
| 8 | ORD-CL-202612-000107_158151651 | 0.00 | 0.0 m | 0.0 | 17:23 | [19:00,21:00] | 19:00 | 10.0 m | 2219.2 L | 319.8 kg | 97 m | — | ⏳ |
| 9 | ORD-CL-202612-000095_140053537 | 2.66 | 6.4 m | 24.8 | 19:16 | [09:00,21:00] | 19:16 | 10.0 m | 76.0 L | 23.9 kg | — | — | ✅ |
| 10 | ORD-CL-202612-000061_180518007 | 2.94 | 6.3 m | 28.0 | 19:32 | [09:00,21:00] | 19:32 | 10.0 m | 25.7 L | 10.6 kg | — | — | ✅ |
| 11 | DEPOT_01_BASE | 2.74 | 5.9 m | 28.0 | 19:48 | — | — | — | — | — | — | — | 🏠 |

### Camión 2 — Detalle de Paradas
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000088_79249631 | 1.12 | 2.9 m | 23.0 | 09:02 | [09:00,11:00] | 09:02 | 10.0 m | 940.8 L | 161.2 kg | — | — | ✅ |
| 2 | ORD-CL-202612-000155_22116046  1 | 0.00 | 0.0 m | 0.0 | 09:12 | [09:00,21:00] | 09:12 | 10.0 m | 400.4 L | 60.1 kg | — | — | ✅ |
| 3 | ORD-CL-202612-000093_134538869 | 1.39 | 3.6 m | 23.0 | 09:26 | [09:00,21:00] | 09:26 | 10.0 m | 937.2 L | 124.3 kg | — | — | ✅ |
| 4 | ORD-CL-202612-000027_7499276  7 | 0.61 | 1.6 m | 23.0 | 09:38 | [11:00,13:00] | 11:00 | 10.0 m | 1718.7 L | 278.7 kg | 82 m | — | ⏳ |
| 5 | ORD-CL-202612-000188_146386625 | 1.21 | 2.9 m | 25.0 | 11:12 | [09:00,21:00] | 11:12 | 10.0 m | 3169.8 L | 425.3 kg | — | — | ✅ |
| 6 | ORD-CL-202612-000196_204415159 | 2.37 | 5.7 m | 25.0 | 11:28 | [09:00,21:00] | 11:28 | 10.0 m | 1895.3 L | 289.6 kg | — | — | ✅ |
| 7 | ORD-CL-202612-000184_21805102  0 | 1.90 | 4.6 m | 25.0 | 11:43 | [15:00,17:00] | 15:00 | 10.0 m | 226.3 L | 29.0 kg | 197 m | — | ⏳ |
| 8 | DEPOT_01_BASE | 1.53 | 3.5 m | 26.0 | 15:13 | — | — | — | — | — | — | — | 🏠 |

### Camión 3 — Detalle de Paradas
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000085_15236104    9 | 0.94 | 2.5 m | 23.0 | 09:02 | [11:00,13:00] | 11:00 | 10.0 m | 1445.3 L | 206.3 kg | 118 m | — | ⏳ |
| 2 | ORD-CL-202612-000119_6466103  7 | 1.19 | 2.8 m | 25.0 | 11:12 | [11:00,13:00] | 11:12 | 10.0 m | 728.8 L | 123.9 kg | — | — | ✅ |
| 3 | DEPOT_01_BASE | 0.27 | 0.6 m | 25.0 | 11:23 | — | — | — | — | — | — | — | 🏠 |


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
| # | Nodo | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | ORD-CL-202612-000166_9709625  6 | 5.14 | 13.4 m | 23.0 | 09:13 | [09:00,11:00] | 09:13 | 10.0 m | 1056.7 L | 190.9 kg | — | — | ✅ |
| 2 | ORD-CL-202612-000183_148999950 | 3.68 | 9.6 m | 23.0 | 09:32 | [09:00,11:00] | 09:32 | 10.0 m | 685.5 L | 100.8 kg | — | — | ✅ |
| 3 | ORD-CL-202612-000052_14976779    6 | 5.63 | 14.6 m | 23.2 | 09:57 | [13:00,15:00] | 13:00 | 10.0 m | 1652.6 L | 231.9 kg | 182 m | — | ⏳ |
| 4 | ORD-CL-202612-000179_121067557 | 1.55 | 3.7 m | 25.0 | 13:13 | [09:00,21:00] | 13:13 | 10.0 m | 716.4 L | 154.0 kg | — | — | ✅ |
| 5 | ORD-CL-202612-000069_143319312 | 1.91 | 4.6 m | 25.1 | 13:28 | [09:00,21:00] | 13:28 | 10.0 m | 400.4 L | 79.2 kg | — | — | ✅ |
| 6 | ORD-CL-202612-000112_208275613 | 0.90 | 2.1 m | 25.5 | 13:40 | [15:00,17:00] | 15:00 | 10.0 m | 1409.6 L | 246.7 kg | 80 m | — | ⏳ |
| 7 | ORD-CL-202612-000180_135550036 | 2.74 | 6.3 m | 26.0 | 15:16 | [09:00,21:00] | 15:16 | 10.0 m | 1259.6 L | 232.8 kg | — | — | ✅ |
| 8 | ORD-CL-202612-000079_112922605 | 2.45 | 5.8 m | 25.5 | 15:32 | [09:00,21:00] | 15:32 | 10.0 m | 201.8 L | 37.8 kg | — | — | ✅ |
| 9 | ORD-CL-202612-000148_175474353 | 3.93 | 9.4 m | 25.0 | 15:51 | [17:00,19:00] | 17:00 | 10.0 m | 75.1 L | 20.7 kg | 68 m | — | ⏳ |
| 10 | ORD-CL-202612-000094_84473640 | 1.51 | 4.5 m | 20.3 | 17:14 | [09:00,21:00] | 17:14 | 10.0 m | 745.5 L | 121.3 kg | — | — | ✅ |
| 11 | DEPOT_01_BASE | 3.78 | 12.1 m | 18.8 | 17:36 | — | — | — | — | — | — | — | 🏠 |


---
