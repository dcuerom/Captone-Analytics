# Reporte GA (PyMoo Problem) - 2026-12-04

## Cluster 0

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 27,101.1 m (27.10 km) |
| Costo Ruta (F = dist × S) | 32,521.36 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 20:25 |
| Duración Total | 11h 25min |
| Vehículos Asignados | 1 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 7/7 |
| Clientes con espera (llegada anticipada) | 2 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 551.4 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 20:25 | 64.0 min | 551.4 min | 70.0 min | 27.10 km | 7 |

### Camión 1 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000003_7941056  6 | 22.3 min | 09:22 | [17:00, 19:00] | 17:00 | 458 min | — | ⏳ |
| 2 | ORD-CL-202612-000035_18489688    3 | 3.2 min | 17:13 | [17:00, 19:00] | 17:13 | — | — | ✅ |
| 3 | ORD-CL-202612-000137_11669766  7 | 3.2 min | 17:26 | [19:00, 21:00] | 19:00 | 94 min | — | ⏳ |
| 4 | ORD-CL-202612-000244_71172331 | 7.5 min | 19:17 | [09:00, 21:00] | 19:17 | — | — | ✅ |
| 5 | ORD-CL-202612-000386_173427377 | 0.0 min | 19:27 | [09:00, 21:00] | 19:27 | — | — | ✅ |
| 6 | ORD-CL-202612-000086_73835094 | 6.3 min | 19:43 | [09:00, 21:00] | 19:43 | — | — | ✅ |
| 7 | ORD-CL-202612-000335_17893629  2 | 8.3 min | 20:02 | [19:00, 21:00] | 20:02 | — | — | ✅ |
| 8 | DEPOT_01_BASE | — | 20:25 | — | — | — | — | 🏠 |


---
## Cluster 1

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 226,500.9 m (226.50 km) |
| Costo Ruta (F = dist × S) | 271,801.10 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 20:42 |
| Duración Total | 11h 42min |
| Vehículos Asignados | 5 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 47/47 |
| Clientes con espera (llegada anticipada) | 14 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 1595.6 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 18:23 | 128.6 min | 364.5 min | 70.0 min | 47.41 km | 7 |
| 2 | 09:00 | 19:28 | 143.2 min | 355.5 min | 130.0 min | 55.71 km | 13 |
| 3 | 09:00 | 15:04 | 137.4 min | 107.3 min | 120.0 min | 57.58 km | 12 |
| 4 | 09:00 | 15:13 | 60.1 min | 263.1 min | 50.0 min | 24.50 km | 5 |
| 5 | 09:00 | 20:42 | 97.6 min | 505.2 min | 100.0 min | 41.30 km | 10 |

### Camión 1 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000046_76867734 | 11.5 min | 09:11 | [09:00, 11:00] | 09:11 | — | — | ✅ |
| 2 | ORD-CL-202612-000037_138726383 | 13.2 min | 09:34 | [09:00, 11:00] | 09:34 | — | — | ✅ |
| 3 | ORD-CL-202612-000040_204734613 | 3.5 min | 09:48 | [11:00, 13:00] | 11:00 | 72 min | — | ⏳ |
| 4 | ORD-CL-202612-000274_133249077 | 17.7 min | 11:27 | [09:00, 21:00] | 11:27 | — | — | ✅ |
| 5 | ORD-CL-202612-000165_203287315 | 29.7 min | 12:07 | [17:00, 19:00] | 17:00 | 293 min | — | ⏳ |
| 6 | ORD-CL-202612-000007_177091525 | 17.4 min | 17:27 | [17:00, 19:00] | 17:27 | — | — | ✅ |
| 7 | ORD-CL-202612-000182_19246133  9 | 22.5 min | 17:59 | [09:00, 21:00] | 17:59 | — | — | ✅ |
| 8 | DEPOT_01_BASE | — | 20:42 | — | — | — | — | 🏠 |

### Camión 2 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000255_88760271 | 1.9 min | 09:01 | [09:00, 21:00] | 09:01 | — | — | ✅ |
| 2 | ORD-CL-202612-000110_161115011 | 5.2 min | 09:17 | [11:00, 13:00] | 11:00 | 103 min | — | ⏳ |
| 3 | ORD-CL-202612-000005_203293099 | 2.9 min | 11:12 | [13:00, 15:00] | 13:00 | 107 min | — | ⏳ |
| 4 | ORD-CL-202612-000247_196940954 | 10.3 min | 13:20 | [13:00, 15:00] | 13:20 | — | — | ✅ |
| 5 | ORD-CL-202612-000081_52073122 | 20.0 min | 13:50 | [15:00, 17:00] | 15:00 | 70 min | — | ⏳ |
| 6 | ORD-CL-202612-000038_151993937 | 13.4 min | 15:23 | [15:00, 17:00] | 15:23 | — | — | ✅ |
| 7 | ORD-CL-202612-000252_10595944  8 | 8.1 min | 15:41 | [09:00, 21:00] | 15:41 | — | — | ✅ |
| 8 | ORD-CL-202612-000173_93122655 | 4.9 min | 15:56 | [09:00, 21:00] | 15:56 | — | — | ✅ |
| 9 | ORD-CL-202612-000056_17709152  5 | 17.6 min | 16:23 | [15:00, 17:00] | 16:23 | — | — | ✅ |
| 10 | ORD-CL-202612-000253_71125181 | 13.9 min | 16:47 | [17:00, 19:00] | 17:00 | 12 min | — | ⏳ |
| 11 | ORD-CL-202612-000245_193984732 | 25.6 min | 17:35 | [17:00, 19:00] | 17:35 | — | — | ✅ |
| 12 | ORD-CL-202612-000030_20757511  0 | 10.7 min | 17:56 | [19:00, 21:00] | 19:00 | 64 min | — | ⏳ |
| 13 | ORD-CL-202612-000257_217834513 | 7.7 min | 19:17 | [19:00, 21:00] | 19:17 | — | — | ✅ |
| 14 | DEPOT_01_BASE | — | 20:42 | — | — | — | — | 🏠 |

### Camión 3 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000239_52073122 | 12.7 min | 09:12 | [11:00, 13:00] | 11:00 | 107 min | — | ⏳ |
| 2 | ORD-CL-202612-000125_13728526  8 | 15.2 min | 11:25 | [11:00, 13:00] | 11:25 | — | — | ✅ |
| 3 | ORD-CL-202612-000161_146386625 | 4.8 min | 11:40 | [09:00, 21:00] | 11:40 | — | — | ✅ |
| 4 | ORD-CL-202612-000375_7894878  8 | 10.2 min | 12:00 | [09:00, 21:00] | 12:00 | — | — | ✅ |
| 5 | ORD-CL-202612-000241_220312237 | 9.5 min | 12:19 | [09:00, 21:00] | 12:19 | — | — | ✅ |
| 6 | ORD-CL-202612-000250_51297436 | 10.2 min | 12:40 | [09:00, 21:00] | 12:40 | — | — | ✅ |
| 7 | ORD-CL-202612-000267_76488412 | 3.3 min | 12:53 | [09:00, 21:00] | 12:53 | — | — | ✅ |
| 8 | ORD-CL-202612-000251_16267073  3 | 0.7 min | 13:04 | [09:00, 21:00] | 13:04 | — | — | ✅ |
| 9 | ORD-CL-202612-000048_7062851  9 | 13.5 min | 13:27 | [09:00, 21:00] | 13:27 | — | — | ✅ |
| 10 | ORD-CL-202612-000134_165548003 | 22.5 min | 13:59 | [09:00, 21:00] | 13:59 | — | — | ✅ |
| 11 | ORD-CL-202612-000076_211884031 | 19.8 min | 14:29 | [13:00, 15:00] | 14:29 | — | — | ✅ |
| 12 | ORD-CL-202612-000012_115652150 | 6.3 min | 14:46 | [09:00, 21:00] | 14:46 | — | — | ✅ |
| 13 | DEPOT_01_BASE | — | 20:42 | — | — | — | — | 🏠 |

### Camión 4 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000053_177778086 | 17.7 min | 09:17 | [11:00, 13:00] | 11:00 | 102 min | — | ⏳ |
| 2 | ORD-CL-202612-000158_14233701  5 | 1.6 min | 11:11 | [09:00, 21:00] | 11:11 | — | — | ✅ |
| 3 | ORD-CL-202612-000281_11555733  9 | 2.2 min | 11:23 | [11:00, 13:00] | 11:23 | — | — | ✅ |
| 4 | ORD-CL-202612-000068_16822988  5 | 23.1 min | 11:56 | [13:00, 15:00] | 13:00 | 63 min | — | ⏳ |
| 5 | ORD-CL-202612-000029_221499706 | 12.4 min | 13:22 | [15:00, 17:00] | 15:00 | 98 min | — | ⏳ |
| 6 | DEPOT_01_BASE | — | 20:42 | — | — | — | — | 🏠 |

### Camión 5 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000156_225559170 | 2.2 min | 09:02 | [09:00, 21:00] | 09:02 | — | — | ✅ |
| 2 | ORD-CL-202612-000047_14175945    6 | 15.9 min | 09:28 | [09:00, 11:00] | 09:28 | — | — | ✅ |
| 3 | ORD-CL-202612-000008_83363320 | 25.8 min | 10:03 | [11:00, 13:00] | 11:00 | 56 min | — | ⏳ |
| 4 | ORD-CL-202612-000199_153064855 | 6.3 min | 11:16 | [17:00, 19:00] | 17:00 | 344 min | — | ⏳ |
| 5 | ORD-CL-202612-000216_52957852 | 4.5 min | 17:14 | [19:00, 21:00] | 19:00 | 105 min | — | ⏳ |
| 6 | ORD-CL-202612-000114_195137682 | 1.9 min | 19:11 | [19:00, 21:00] | 19:11 | — | — | ✅ |
| 7 | ORD-CL-202612-000227_6510437  1 | 1.8 min | 19:23 | [09:00, 21:00] | 19:23 | — | — | ✅ |
| 8 | ORD-CL-202612-000236_22813500  2 | 6.5 min | 19:40 | [09:00, 21:00] | 19:40 | — | — | ✅ |
| 9 | ORD-CL-202612-000254_88154490 | 19.9 min | 20:10 | [09:00, 21:00] | 20:10 | — | — | ✅ |
| 10 | ORD-CL-202612-000084_203258279 | 8.9 min | 20:28 | [19:00, 21:00] | 20:28 | — | — | ✅ |
| 11 | DEPOT_01_BASE | — | 20:42 | — | — | — | — | 🏠 |


---
## Cluster 2

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 43,834.9 m (43.83 km) |
| Costo Ruta (F = dist × S) | 52,601.84 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 17:57 |
| Duración Total | 8h 57min |
| Vehículos Asignados | 1 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 9/9 |
| Clientes con espera (llegada anticipada) | 4 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 329.9 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 17:57 | 117.5 min | 329.9 min | 90.0 min | 43.83 km | 9 |

### Camión 1 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000205_108843648 | 45.6 min | 09:45 | [09:00, 11:00] | 09:45 | — | — | ✅ |
| 2 | ORD-CL-202612-000278_58354112 | 2.1 min | 09:57 | [09:00, 21:00] | 09:57 | — | — | ✅ |
| 3 | ORD-CL-202612-000232_155950952 | 0.0 min | 10:07 | [11:00, 13:00] | 11:00 | 52 min | — | ⏳ |
| 4 | ORD-CL-202612-000285_75547549 | 6.6 min | 11:16 | [09:00, 21:00] | 11:16 | — | — | ✅ |
| 5 | ORD-CL-202612-000014_107947201 | 2.4 min | 11:29 | [13:00, 15:00] | 13:00 | 91 min | — | ⏳ |
| 6 | ORD-CL-202612-000305_185184001 | 0.0 min | 13:10 | [15:00, 17:00] | 15:00 | 110 min | — | ⏳ |
| 7 | ORD-CL-202612-000018_184841742 | 4.6 min | 15:14 | [09:00, 21:00] | 15:14 | — | — | ✅ |
| 8 | ORD-CL-202612-000083_104691534 | 8.6 min | 15:33 | [15:00, 17:00] | 15:33 | — | — | ✅ |
| 9 | ORD-CL-202612-000043_104691534 | 0.0 min | 15:43 | [17:00, 19:00] | 17:00 | 77 min | — | ⏳ |
| 10 | DEPOT_01_BASE | — | 17:57 | — | — | — | — | 🏠 |


---
## Cluster 3

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 50,540.4 m (50.54 km) |
| Costo Ruta (F = dist × S) | 60,648.48 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 20:03 |
| Duración Total | 11h 3min |
| Vehículos Asignados | 1 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 6/6 |
| Clientes con espera (llegada anticipada) | 2 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 476.8 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 20:03 | 126.2 min | 476.8 min | 60.0 min | 50.54 km | 6 |

### Camión 1 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000176_6031151  7 | 54.7 min | 09:54 | [09:00, 21:00] | 09:54 | — | — | ✅ |
| 2 | ORD-CL-202612-000204_142763322 | 6.9 min | 10:11 | [09:00, 21:00] | 10:11 | — | — | ✅ |
| 3 | ORD-CL-202612-000181_6219949  0 | 0.0 min | 10:21 | [09:00, 11:00] | 10:21 | — | — | ✅ |
| 4 | ORD-CL-202612-000023_154609167 | 4.3 min | 10:35 | [09:00, 21:00] | 10:35 | — | — | ✅ |
| 5 | ORD-CL-202612-000132_108142076 | 6.5 min | 10:52 | [11:00, 13:00] | 11:00 | 8 min | — | ⏳ |
| 6 | ORD-CL-202612-000067_12592663    1 | 0.9 min | 11:10 | [19:00, 21:00] | 19:00 | 469 min | — | ⏳ |
| 7 | DEPOT_01_BASE | — | 20:03 | — | — | — | — | 🏠 |


---
## Cluster 4

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 49,608.7 m (49.61 km) |
| Costo Ruta (F = dist × S) | 59,530.49 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 15:23 |
| Duración Total | 6h 23min |
| Vehículos Asignados | 2 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 7/7 |
| Clientes con espera (llegada anticipada) | 3 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 589.1 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 15:38 | 93.3 min | 255.0 min | 50.0 min | 37.51 km | 5 |
| 2 | 09:00 | 15:23 | 29.7 min | 334.1 min | 20.0 min | 12.10 km | 2 |

### Camión 1 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000057_199420292 | 30.1 min | 09:30 | [09:00, 21:00] | 09:30 | — | — | ✅ |
| 2 | ORD-CL-202612-000229_222906804 | 12.3 min | 09:52 | [09:00, 21:00] | 09:52 | — | — | ✅ |
| 3 | ORD-CL-202612-000152_58890293 | 17.6 min | 10:20 | [11:00, 13:00] | 11:00 | 40 min | — | ⏳ |
| 4 | ORD-CL-202612-000136_9255041  3 | 15.0 min | 11:25 | [15:00, 17:00] | 15:00 | 215 min | — | ⏳ |
| 5 | ORD-CL-202612-000036_58822448 | 4.2 min | 15:14 | [09:00, 21:00] | 15:14 | — | — | ✅ |
| 6 | DEPOT_01_BASE | — | 15:23 | — | — | — | — | 🏠 |

### Camión 2 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000063_94443217 | 15.6 min | 09:15 | [09:00, 21:00] | 09:15 | — | — | ✅ |
| 2 | ORD-CL-202612-000142_6304052  0 | 0.2 min | 09:25 | [15:00, 17:00] | 15:00 | 334 min | — | ⏳ |
| 3 | DEPOT_01_BASE | — | 15:23 | — | — | — | — | 🏠 |


---
## Cluster 5

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 105,498.0 m (105.50 km) |
| Costo Ruta (F = dist × S) | 126,597.55 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 17:56 |
| Duración Total | 8h 56min |
| Vehículos Asignados | 3 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 20/20 |
| Clientes con espera (llegada anticipada) | 7 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 1107.1 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 15:35 | 83.6 min | 252.3 min | 60.0 min | 33.89 km | 6 |
| 2 | 09:00 | 19:47 | 98.4 min | 459.3 min | 90.0 min | 38.82 km | 9 |
| 3 | 09:00 | 17:56 | 91.2 min | 395.5 min | 50.0 min | 32.79 km | 5 |

### Camión 1 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000172_21961796  1 | 36.5 min | 09:36 | [09:00, 11:00] | 09:36 | — | — | ✅ |
| 2 | ORD-CL-202612-000200_7995605  2 | 7.3 min | 09:53 | [11:00, 13:00] | 11:00 | 66 min | — | ⏳ |
| 3 | ORD-CL-202612-000074_71332179 | 3.7 min | 11:13 | [13:00, 15:00] | 13:00 | 106 min | — | ⏳ |
| 4 | ORD-CL-202612-000198_130854087 | 3.8 min | 13:13 | [13:00, 15:00] | 13:13 | — | — | ✅ |
| 5 | ORD-CL-202612-000185_83399781 | 3.7 min | 13:27 | [09:00, 21:00] | 13:27 | — | — | ✅ |
| 6 | ORD-CL-202612-000164_135946728 | 2.8 min | 13:40 | [15:00, 17:00] | 15:00 | 80 min | — | ⏳ |
| 7 | DEPOT_01_BASE | — | 17:56 | — | — | — | — | 🏠 |

### Camión 2 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000145_17328690  8 | 24.9 min | 09:24 | [09:00, 21:00] | 09:24 | — | — | ✅ |
| 2 | ORD-CL-202612-000234_217198247 | 6.9 min | 09:41 | [13:00, 15:00] | 13:00 | 198 min | — | ⏳ |
| 3 | ORD-CL-202612-000303_22692685  2 | 2.0 min | 13:12 | [09:00, 21:00] | 13:12 | — | — | ✅ |
| 4 | ORD-CL-202612-000120_73965853 | 6.0 min | 13:28 | [09:00, 21:00] | 13:28 | — | — | ✅ |
| 5 | ORD-CL-202612-000124_204531108 | 8.4 min | 13:46 | [17:00, 19:00] | 17:00 | 194 min | — | ⏳ |
| 6 | ORD-CL-202612-000090_75992709 | 7.7 min | 17:17 | [17:00, 19:00] | 17:17 | — | — | ✅ |
| 7 | ORD-CL-202612-000131_174462588 | 9.6 min | 17:37 | [09:00, 21:00] | 17:37 | — | — | ✅ |
| 8 | ORD-CL-202612-000225_229042840 | 5.3 min | 17:52 | [19:00, 21:00] | 19:00 | 67 min | — | ⏳ |
| 9 | ORD-CL-202612-000146_137522388 | 6.4 min | 19:16 | [19:00, 21:00] | 19:16 | — | — | ✅ |
| 10 | DEPOT_01_BASE | — | 17:56 | — | — | — | — | 🏠 |

### Camión 3 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000171_17328690  8 | 24.9 min | 09:24 | [09:00, 21:00] | 09:24 | — | — | ✅ |
| 2 | ORD-CL-202612-000058_11129072  4 | 0.0 min | 09:34 | [09:00, 21:00] | 09:34 | — | — | ✅ |
| 3 | ORD-CL-202612-000168_80591482 | 21.0 min | 10:05 | [09:00, 21:00] | 10:05 | — | — | ✅ |
| 4 | ORD-CL-202612-000154_19779462  2 | 8.7 min | 10:24 | [17:00, 19:00] | 17:00 | 395 min | — | ⏳ |
| 5 | ORD-CL-202612-000243_50530242 | 10.7 min | 17:20 | [09:00, 21:00] | 17:20 | — | — | ✅ |
| 6 | DEPOT_01_BASE | — | 17:56 | — | — | — | — | 🏠 |


---
## Cluster 6

### Resumen Operativo
| Métrica | Valor |
| :--- | :--- |
| Distancia Total | 59,200.7 m (59.20 km) |
| Costo Ruta (F = dist × S) | 71,040.82 |
| Hora Salida Depósito | 09:00 |
| Hora Retorno Depósito | 17:45 |
| Duración Total | 8h 45min |
| Vehículos Asignados | 2 |

### Restricción 14: Cumplimiento de Ventanas de Tiempo
| Indicador | Valor |
| :--- | :--- |
| Clientes atendidos en ventana | 11/11 |
| Clientes con espera (llegada anticipada) | 5 |
| Clientes con violación (llegada tardía) | 0 |
| Tiempo de espera acumulado | 909.4 min |
| Violación acumulada (G) | 0.0 min |

### Desglose de Tiempos por Camión
| Camión | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 09:00 | 19:44 | 69.9 min | 504.7 min | 70.0 min | 29.43 km | 7 |
| 2 | 09:00 | 17:45 | 81.2 min | 404.8 min | 40.0 min | 29.77 km | 4 |

### Camión 1 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000214_92456335 | 22.8 min | 09:22 | [13:00, 15:00] | 13:00 | 217 min | — | ⏳ |
| 2 | ORD-CL-202612-000097_110443192 | 5.2 min | 13:15 | [15:00, 17:00] | 15:00 | 105 min | — | ⏳ |
| 3 | ORD-CL-202612-000128_97639700 | 0.0 min | 15:10 | [09:00, 21:00] | 15:10 | — | — | ✅ |
| 4 | ORD-CL-202612-000034_18190145  8 | 8.7 min | 15:28 | [15:00, 17:00] | 15:28 | — | — | ✅ |
| 5 | ORD-CL-202612-000041_58842814 | 6.9 min | 15:45 | [09:00, 21:00] | 15:45 | — | — | ✅ |
| 6 | ORD-CL-202612-000138_6343287  3 | 1.7 min | 15:57 | [19:00, 21:00] | 19:00 | 183 min | — | ⏳ |
| 7 | ORD-CL-202612-000065_125088177 | 5.4 min | 19:15 | [19:00, 21:00] | 19:15 | — | — | ✅ |
| 8 | DEPOT_01_BASE | — | 17:45 | — | — | — | — | 🏠 |

### Camión 2 — Detalle de Paradas
| # | Nodo | T. Viaje | Llegada Real | Ventana [a, b] | Inicio Servicio | Espera | Violación | Estado |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | DEPOT_01_BASE | — | 09:00 | — | 09:00 | — | — | 🏠 |
| 1 | ORD-CL-202612-000362_123561909 | 22.7 min | 09:22 | [09:00, 21:00] | 09:22 | — | — | ✅ |
| 2 | ORD-CL-202612-000246_8738877  8 | 5.0 min | 09:37 | [09:00, 21:00] | 09:37 | — | — | ✅ |
| 3 | ORD-CL-202612-000129_22759622  2 | 11.1 min | 09:58 | [11:00, 13:00] | 11:00 | 61 min | — | ⏳ |
| 4 | ORD-CL-202612-000231_16753214  7 | 6.4 min | 11:16 | [17:00, 19:00] | 17:00 | 344 min | — | ⏳ |
| 5 | DEPOT_01_BASE | — | 17:45 | — | — | — | — | 🏠 |


---
