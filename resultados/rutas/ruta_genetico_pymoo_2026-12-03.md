# Reporte GA (PyMoo Problem) - 2026-12-03

## Cluster 0

### Desglose de Tiempos por Camión
| ID Ruta | ID Vehículo | Clase K | Turno | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Vehículo 1 | K11 | Mañana | 09:00 | 15:46 | 144.1 min | 232.5 min | 30.0 min | 54.04 km | 6 |
| 2 | Vehículo 1 | K12 | Tarde | 15:00 | 16:41 | 86.9 min | 0.0 min | 15.0 min | 34.37 km | 3 |
| 3 | Vehículo 2 | K21 | Mañana | 11:00 | 16:10 | 121.8 min | 164.2 min | 25.0 min | 47.52 km | 5 |
| 4 | Vehículo 2 | K22 | Tarde | 17:00 | 18:37 | 92.6 min | 0.0 min | 5.0 min | 26.82 km | 1 |
| 5 | Vehículo 3 | K11 | Mañana | 09:00 | 15:48 | 95.7 min | 308.0 min | 5.0 min | 36.40 km | 1 |
| 6 | Vehículo 3 | K12 | Tarde | 15:00 | 19:55 | 140.6 min | 134.5 min | 20.0 min | 54.00 km | 4 |
| 7 | Vehículo 4 | K21 | Mañana | 11:00 | 19:36 | 70.2 min | 436.5 min | 10.0 min | 26.30 km | 2 |

### Vehículo Físico 1
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 1 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 1 | K11 | Mañana | ORD-CL-202612-000144_210301989 | avenida vitacura 713, Quinta Normal, Santiago, Chile | 16.94 | 48.4 m | 21.0 | 09:48 | [09:00,11:00] | 09:48 | 5.0 m | 196.0 L | 24.5 kg | — | — | ✅ |
| 2 | 1 | K11 | Mañana | ORD-CL-202612-000082_198569524 | avenida. departamental 2287, La Florida, Santiago, Chile | 12.73 | 35.0 m | 21.8 | 10:28 | [09:00,11:00] | 10:28 | 5.0 m | 481.1 L | 96.3 kg | — | — | ✅ |
| 3 | 1 | K11 | Mañana | ORD-CL-202612-000133_55387737 | calle teatinos 4659, La Florida, Santiago, Chile | 3.94 | 10.3 m | 23.0 | 10:43 | [11:00,13:00] | 11:00 | 5.0 m | 379.5 L | 55.8 kg | 16 m | — | ⏳ |
| 4 | 1 | K11 | Mañana | ORD-CL-202612-000060_199941644 | avenida. macul 7795, Maipú, Santiago, Chile | 4.41 | 11.5 m | 23.0 | 11:16 | [09:00,21:00] | 11:16 | 5.0 m | 577.7 L | 83.3 kg | — | — | ✅ |
| 5 | 1 | K11 | Mañana | ORD-CL-202612-000092_162059956 | avenida. providencia 4727, La Florida, Santiago, Chile | 0.89 | 2.3 m | 23.0 | 11:23 | [15:00,17:00] | 15:00 | 5.0 m | 892.8 L | 131.5 kg | 216 m | — | ⏳ |
| 6 | 1 | K11 | Mañana | ORD-CL-202612-000177_19337908  6 | avenida. la florida 2133, Macul, Santiago, Chile | 2.39 | 5.7 m | 25.0 | 15:10 | [09:00,21:00] | 15:10 | 5.0 m | 905.8 L | 185.3 kg | — | — | ✅ |
| 7 | 1 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | 12.74 | 30.8 m | 24.8 | 15:46 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 1
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 2 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 2 | K12 | Tarde | ORD-CL-202612-000096_52601895 | calle arturo prat 4852, Independencia, Santiago, Chile | 13.00 | 31.2 m | 25.0 | 15:31 | [09:00,21:00] | 15:31 | 5.0 m | 1136.0 L | 188.5 kg | — | — | ✅ |
| 2 | 2 | K12 | Tarde | ORD-CL-202612-000178_6756635  4 | calle bandera 9187, Vitacura, Santiago, Chile | 1.88 | 4.8 m | 23.4 | 15:41 | [09:00,21:00] | 15:41 | 5.0 m | 363.4 L | 89.2 kg | — | — | ✅ |
| 3 | 2 | K12 | Tarde | ORD-CL-202612-000032_83953104 | gran avenida jose miguel carrera 1084, La Florida, Santiago, Chile | 4.64 | 12.1 m | 23.0 | 15:58 | [09:00,21:00] | 15:58 | 5.0 m | 2217.2 L | 261.7 kg | — | — | ✅ |
| 4 | 2 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | 14.86 | 38.8 m | 23.0 | 16:41 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 2
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 3 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 3 | K21 | Mañana | ORD-CL-202612-000222_64382296 | calle merced 6576, Puente Alto, Santiago, Chile | 21.35 | 55.7 m | 23.0 | 11:55 | [13:00,15:00] | 13:00 | 5.0 m | 1396.1 L | 158.3 kg | 64 m | — | ⏳ |
| 2 | 3 | K21 | Mañana | ORD-CL-202612-000187_5138738  6 | avenida. independencia 4810, Puente Alto, Santiago, Chile | 1.11 | 2.9 m | 23.0 | 13:07 | [13:00,15:00] | 13:07 | 5.0 m | 222.3 L | 37.4 kg | — | — | ✅ |
| 3 | 3 | K21 | Mañana | ORD-CL-202612-000163_215462173 | avenida. pedro de valdivia 8264, Puente Alto, Santiago, Chile | 2.77 | 7.2 m | 23.0 | 13:20 | [15:00,17:00] | 15:00 | 5.0 m | 24.8 L | 9.3 kg | 100 m | — | ⏳ |
| 4 | 3 | K21 | Mañana | ORD-CL-202612-000010_62835725 | avenida americo vespucio 2389, Independencia, Santiago, Chile | 9.35 | 22.4 m | 25.0 | 15:27 | [09:00,21:00] | 15:27 | 5.0 m | 894.1 L | 164.7 kg | — | — | ✅ |
| 5 | 3 | K21 | Mañana | ORD-CL-202612-000122_51491954 | avenida. santa rosa 5626, San Miguel, Santiago, Chile | 3.50 | 8.9 m | 23.6 | 15:41 | [15:00,17:00] | 15:41 | 5.0 m | 322.7 L | 73.9 kg | — | — | ✅ |
| 6 | 3 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | 9.44 | 24.6 m | 23.0 | 16:10 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 2
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 4 | K22 | Tarde | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 4 | K22 | Tarde | ORD-CL-202612-000002_173134031 | avenida. la florida 7678, Macul, Santiago, Chile | 13.43 | 42.4 m | 19.0 | 17:42 | [09:00,21:00] | 17:42 | 5.0 m | 4239.4 L | 505.6 kg | — | — | ✅ |
| 2 | 4 | K22 | Tarde | DEPOT_01_BASE | Base Depósito | 13.38 | 50.2 m | 16.0 | 18:37 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 3
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 5 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 5 | K11 | Mañana | ORD-CL-202612-000020_10263868  8 | avenida. manuel montt 3031, Maipú, Santiago, Chile | 18.18 | 52.0 m | 21.0 | 09:51 | [15:00,17:00] | 15:00 | 5.0 m | 3905.5 L | 441.5 kg | 308 m | — | ⏳ |
| 2 | 5 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | 18.21 | 43.7 m | 25.0 | 15:48 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 3
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 6 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 6 | K12 | Tarde | ORD-CL-202612-000019_156820915 | avenida. tobalaba 3402, Macul, Santiago, Chile | 15.00 | 36.0 m | 25.0 | 15:36 | [09:00,21:00] | 15:36 | 5.0 m | 2163.4 L | 238.1 kg | — | — | ✅ |
| 2 | 6 | K12 | Tarde | ORD-CL-202612-000006_207417262 | calle catedral 9181, Puente Alto, Santiago, Chile | 11.47 | 29.8 m | 23.1 | 16:10 | [17:00,19:00] | 17:00 | 5.0 m | 639.5 L | 113.7 kg | 49 m | — | ⏳ |
| 3 | 6 | K12 | Tarde | ORD-CL-202612-000135_153012165 | avenida. vicuna mackenna 8405, Peñalolén, Santiago, Chile | 9.31 | 29.7 m | 18.8 | 17:34 | [19:00,21:00] | 19:00 | 5.0 m | 644.2 L | 128.1 kg | 85 m | — | ⏳ |
| 4 | 6 | K12 | Tarde | ORD-CL-202612-000024_53351852 | avenida. apoquindo 5706, La Florida, Santiago, Chile | 3.52 | 9.7 m | 21.8 | 19:14 | [19:00,21:00] | 19:14 | 5.0 m | 168.8 L | 34.9 kg | — | — | ✅ |
| 5 | 6 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | 14.69 | 35.4 m | 24.9 | 19:55 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 4
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 7 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 7 | K21 | Mañana | ORD-CL-202612-000139_162296701 | avenida. pajaritos 9174, La Florida, Santiago, Chile | 13.24 | 34.5 m | 23.0 | 11:34 | [09:00,21:00] | 11:34 | 5.0 m | 614.9 L | 114.0 kg | — | — | ✅ |
| 2 | 7 | K21 | Mañana | ORD-CL-202612-000031_14317726  4 | avenida. la florida 1002, Peñalolén, Santiago, Chile | 1.53 | 4.0 m | 23.0 | 11:43 | [19:00,21:00] | 19:00 | 5.0 m | 2786.0 L | 391.8 kg | 436 m | — | ⏳ |
| 3 | 7 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | 11.52 | 31.7 m | 21.8 | 19:36 | — | — | — | — | — | — | — | 🏠 |


---
## Cluster 1

### Desglose de Tiempos por Camión
| ID Ruta | ID Vehículo | Clase K | Turno | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Vehículo 1 | K11 | Mañana | 09:00 | 11:45 | 55.8 min | 99.6 min | 10.0 min | 20.70 km | 2 |
| 2 | Vehículo 1 | K12 | Tarde | 15:00 | 19:36 | 40.5 min | 215.9 min | 20.0 min | 16.54 km | 4 |

### Vehículo Físico 1
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 1 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 1 | K11 | Mañana | ORD-CL-202612-000091_79104971 | avenida. independencia 4637, Providencia, Santiago, Chile | 7.15 | 20.4 m | 21.0 | 09:20 | [11:00,13:00] | 11:00 | 5.0 m | 848.6 L | 167.5 kg | 100 m | — | ⏳ |
| 2 | 1 | K11 | Mañana | ORD-CL-202612-000044_145036177 | avenida. tobalaba 5892, Quinta Normal, Santiago, Chile | 7.55 | 19.7 m | 23.0 | 11:24 | [09:00,21:00] | 11:24 | 5.0 m | 855.7 L | 127.7 kg | — | — | ✅ |
| 3 | 1 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | 6.01 | 15.7 m | 23.0 | 11:45 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 1
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 2 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 2 | K12 | Tarde | ORD-CL-202612-000004_183059669 | calle san antonio 8832, Lo Prado, Santiago, Chile | 7.97 | 19.1 m | 25.0 | 15:19 | [09:00,21:00] | 15:19 | 5.0 m | 2514.1 L | 317.4 kg | — | — | ✅ |
| 2 | 2 | K12 | Tarde | ORD-CL-202612-000062_7640094    3 | calle san antonio 9379, Lo Prado, Santiago, Chile | 0.00 | 0.0 m | — | 15:24 | [19:00,21:00] | 19:00 | 5.0 m | 634.5 L | 101.6 kg | 216 m | — | ⏳ |
| 3 | 2 | K12 | Tarde | ORD-CL-202612-000115_198154752 | calle san antonio 6514, La Reina, Santiago, Chile | 0.13 | 0.4 m | 21.8 | 19:05 | [19:00,21:00] | 19:05 | 5.0 m | 371.8 L | 100.9 kg | — | — | ✅ |
| 4 | 2 | K12 | Tarde | ORD-CL-202612-000055_203179717 | avenida. mapocho 6648, Macul, Santiago, Chile | 0.59 | 1.6 m | 22.8 | 19:11 | [09:00,21:00] | 19:11 | 5.0 m | 224.5 L | 56.1 kg | — | — | ✅ |
| 5 | 2 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | 7.85 | 19.4 m | 24.2 | 19:36 | — | — | — | — | — | — | — | 🏠 |


---
## Cluster 2

### Desglose de Tiempos por Camión
| ID Ruta | ID Vehículo | Clase K | Turno | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Vehículo 1 | K11 | Mañana | 09:00 | 11:23 | 117.0 min | 6.1 min | 20.0 min | 42.75 km | 4 |
| 2 | Vehículo 1 | K12 | Tarde | 15:00 | 16:02 | 37.8 min | 0.0 min | 25.0 min | 15.17 km | 5 |
| 3 | Vehículo 2 | K21 | Mañana | 11:00 | 13:29 | 50.7 min | 94.3 min | 5.0 min | 19.43 km | 1 |
| 4 | Vehículo 2 | K22 | Tarde | 17:00 | 18:50 | 105.9 min | 0.0 min | 5.0 min | 30.65 km | 1 |

### Vehículo Físico 1
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 1 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 1 | K11 | Mañana | ORD-CL-202612-000141_140162225 | calle san antonio 2631, La Reina, Santiago, Chile | 20.73 | 59.2 m | 21.0 | 09:59 | [09:00,21:00] | 09:59 | 5.0 m | 84.7 L | 24.3 kg | — | — | ✅ |
| 2 | 1 | K11 | Mañana | ORD-CL-202612-000111_5802113  4 | avenida. las condes 599, San Miguel, Santiago, Chile | 6.01 | 16.0 m | 22.6 | 10:20 | [09:00,21:00] | 10:20 | 5.0 m | 2018.8 L | 255.6 kg | — | — | ✅ |
| 3 | 1 | K11 | Mañana | ORD-CL-202612-000022_169468917 | avenida. pajaritos 7516, Maipú, Santiago, Chile | 6.63 | 17.3 m | 23.0 | 10:42 | [09:00,21:00] | 10:42 | 5.0 m | 929.9 L | 130.3 kg | — | — | ✅ |
| 4 | 1 | K11 | Mañana | ORD-CL-202612-000087_17107764  6 | avenida. pajaritos 5796, Independencia, Santiago, Chile | 2.46 | 6.4 m | 23.0 | 10:53 | [11:00,13:00] | 11:00 | 5.0 m | 237.6 L | 62.3 kg | 6 m | — | ⏳ |
| 5 | 1 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | 6.92 | 18.0 m | 23.0 | 11:23 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 1
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 2 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 2 | K12 | Tarde | ORD-CL-202612-000150_10411606  1 | calle santo domingo 6777, Vitacura, Santiago, Chile | 3.63 | 8.7 m | 25.0 | 15:08 | [09:00,21:00] | 15:08 | 5.0 m | 1086.9 L | 173.4 kg | — | — | ✅ |
| 2 | 2 | K12 | Tarde | ORD-CL-202612-000071_212196364 | avenida. pajaritos 3626, Estación Central, Santiago, Chile | 4.08 | 9.8 m | 24.9 | 15:23 | [15:00,17:00] | 15:23 | 5.0 m | 1006.0 L | 197.4 kg | — | — | ✅ |
| 3 | 2 | K12 | Tarde | ORD-CL-202612-000143_14358394    1 | avenida. matta 9543, Estación Central, Santiago, Chile | 1.65 | 4.1 m | 23.9 | 15:32 | [09:00,21:00] | 15:32 | 5.0 m | 74.2 L | 18.0 kg | — | — | ✅ |
| 4 | 2 | K12 | Tarde | ORD-CL-202612-000015_93475810 | calle morande 6751, Estación Central, Santiago, Chile | 0.00 | 0.0 m | — | 15:37 | [09:00,21:00] | 15:37 | 5.0 m | 266.4 L | 74.4 kg | — | — | ✅ |
| 5 | 2 | K12 | Tarde | ORD-CL-202612-000121_102139227 | calle bandera 3131, Estación Central, Santiago, Chile | 0.00 | 0.0 m | — | 15:42 | [09:00,21:00] | 15:42 | 5.0 m | 1152.4 L | 159.0 kg | — | — | ✅ |
| 6 | 2 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | 5.81 | 15.2 m | 23.0 | 16:02 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 2
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 3 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 3 | K21 | Mañana | ORD-CL-202612-000011_18195149  6 | avenida. pajaritos 5435, Ñuñoa, Santiago, Chile | 9.86 | 25.7 m | 23.0 | 11:25 | [13:00,15:00] | 13:00 | 5.0 m | 4252.7 L | 550.2 kg | 94 m | — | ⏳ |
| 2 | 3 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | 9.57 | 25.0 m | 23.0 | 13:29 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 2
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 4 | K22 | Tarde | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 4 | K22 | Tarde | ORD-CL-202612-000208_107728946 | avenida. pajaritos 1016, San Miguel, Santiago, Chile | 15.29 | 48.3 m | 19.0 | 17:48 | [09:00,21:00] | 17:48 | 5.0 m | 4894.5 L | 609.0 kg | — | — | ✅ |
| 2 | 4 | K22 | Tarde | DEPOT_01_BASE | Base Depósito | 15.36 | 57.6 m | 16.0 | 18:50 | — | — | — | — | — | — | — | 🏠 |


---
## Cluster 3

### Desglose de Tiempos por Camión
| ID Ruta | ID Vehículo | Clase K | Turno | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Vehículo 1 | K11 | Mañana | 09:00 | 15:13 | 27.7 min | 321.1 min | 25.0 min | 9.96 km | 5 |
| 2 | Vehículo 1 | K12 | Tarde | 15:00 | 17:06 | 22.2 min | 79.0 min | 25.0 min | 8.91 km | 5 |
| 3 | Vehículo 2 | K21 | Mañana | 11:00 | 19:31 | 40.5 min | 446.2 min | 25.0 min | 15.53 km | 5 |
| 4 | Vehículo 2 | K22 | Tarde | 17:00 | 17:45 | 30.5 min | 0.0 min | 15.0 min | 8.79 km | 3 |
| 5 | Vehículo 3 | K11 | Mañana | 09:00 | 11:05 | 33.7 min | 76.6 min | 15.0 min | 11.81 km | 3 |
| 6 | Vehículo 3 | K12 | Tarde | 15:00 | 15:11 | 6.9 min | 0.0 min | 5.0 min | 2.86 km | 1 |
| 7 | Vehículo 4 | K21 | Mañana | 11:00 | 19:07 | 7.1 min | 470.6 min | 10.0 min | 2.66 km | 2 |

### Vehículo Físico 1
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 1 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 1 | K11 | Mañana | ORD-CL-202612-000095_140053537 | calle morande 3761, Quinta Normal, Santiago, Chile | 3.48 | 10.0 m | 21.0 | 09:09 | [09:00,21:00] | 09:09 | 5.0 m | 76.0 L | 23.9 kg | — | — | ✅ |
| 2 | 1 | K11 | Mañana | ORD-CL-202612-000103_22242242  0 | calle teatinos 7628, Macul, Santiago, Chile | 4.07 | 11.6 m | 21.0 | 09:26 | [09:00,21:00] | 09:26 | 5.0 m | 208.2 L | 28.5 kg | — | — | ✅ |
| 3 | 1 | K11 | Mañana | ORD-CL-202612-000197_12172627  6 | calle san diego 9161, Recoleta, Santiago, Chile | 0.29 | 0.8 m | 21.0 | 09:32 | [09:00,11:00] | 09:32 | 5.0 m | 2704.0 L | 358.4 kg | — | — | ✅ |
| 4 | 1 | K11 | Mañana | ORD-CL-202612-000184_21805102  0 | calle arturo prat 175, Peñalolén, Santiago, Chile | 0.53 | 1.5 m | 21.0 | 09:38 | [15:00,17:00] | 15:00 | 5.0 m | 226.3 L | 29.0 kg | 321 m | — | ⏳ |
| 5 | 1 | K11 | Mañana | ORD-CL-202612-000116_73802946 | avenida. libertador bernardo o'higgins 4192, Providencia, Santiago, Chile | 0.78 | 1.9 m | 25.0 | 15:06 | [09:00,21:00] | 15:06 | 5.0 m | 409.0 L | 59.3 kg | — | — | ✅ |
| 6 | 1 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | 0.80 | 1.9 m | 25.0 | 15:13 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 1
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 2 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 2 | K12 | Tarde | ORD-CL-202612-000093_134538869 | calle catedral 2615, Providencia, Santiago, Chile | 0.32 | 0.8 m | 25.0 | 15:00 | [09:00,21:00] | 15:00 | 5.0 m | 937.2 L | 124.3 kg | — | — | ✅ |
| 2 | 2 | K12 | Tarde | ORD-CL-202612-000013_9933788  8 | avenida. manuel montt 401, Vitacura, Santiago, Chile | 4.16 | 10.0 m | 25.0 | 15:15 | [09:00,21:00] | 15:15 | 5.0 m | 262.6 L | 34.5 kg | — | — | ✅ |
| 3 | 2 | K12 | Tarde | ORD-CL-202612-000209_163993586 | avenida. providencia 4275, Las Condes, Santiago, Chile | 0.92 | 2.3 m | 24.4 | 15:23 | [15:00,17:00] | 15:23 | 5.0 m | 276.9 L | 36.7 kg | — | — | ✅ |
| 4 | 2 | K12 | Tarde | ORD-CL-202612-000160_108505650 | avenida. providencia 178, Providencia, Santiago, Chile | 0.00 | 0.0 m | — | 15:28 | [15:00,17:00] | 15:28 | 5.0 m | 245.4 L | 52.4 kg | — | — | ✅ |
| 5 | 2 | K12 | Tarde | ORD-CL-202612-000026_175731263 | calle san antonio 1509, Providencia, Santiago, Chile | 3.14 | 8.0 m | 23.6 | 15:41 | [17:00,19:00] | 17:00 | 5.0 m | 1731.7 L | 205.5 kg | 79 m | — | ⏳ |
| 6 | 2 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | 0.36 | 1.2 m | 18.8 | 17:06 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 2
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 3 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 3 | K21 | Mañana | ORD-CL-202612-000089_172068824 | calle san diego 6019, Macul, Santiago, Chile | 0.99 | 2.6 m | 23.0 | 11:02 | [11:00,13:00] | 11:02 | 5.0 m | 653.9 L | 144.7 kg | — | — | ✅ |
| 2 | 3 | K21 | Mañana | ORD-CL-202612-000119_6466103  7 | calle san antonio 7911, Santiago, Santiago, Chile | 1.00 | 2.6 m | 23.0 | 11:10 | [11:00,13:00] | 11:10 | 5.0 m | 728.8 L | 123.9 kg | — | — | ✅ |
| 3 | 3 | K21 | Mañana | ORD-CL-202612-000170_137256512 | calle san antonio 2929, Santiago, Santiago, Chile | 0.00 | 0.0 m | — | 11:15 | [09:00,21:00] | 11:15 | 5.0 m | 776.8 L | 140.6 kg | — | — | ✅ |
| 4 | 3 | K21 | Mañana | ORD-CL-202612-000118_65054485 | avenida la florida 3026, Santiago, Santiago, Chile | 5.20 | 13.6 m | 23.0 | 11:33 | [19:00,21:00] | 19:00 | 5.0 m | 1214.1 L | 215.7 kg | 446 m | — | ⏳ |
| 5 | 3 | K21 | Mañana | ORD-CL-202612-000061_180518007 | avenida. manuel montt 5734, Independencia, Santiago, Chile | 5.55 | 15.3 m | 21.8 | 19:20 | [09:00,21:00] | 19:20 | 5.0 m | 25.7 L | 10.6 kg | — | — | ✅ |
| 6 | 3 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | 2.79 | 6.4 m | 26.0 | 19:31 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 2
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 4 | K22 | Tarde | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 4 | K22 | Tarde | ORD-CL-202612-000169_15815165  1 | calle santo domingo 9121, Recoleta, Santiago, Chile | 0.84 | 2.7 m | 19.0 | 17:02 | [17:00,19:00] | 17:02 | 5.0 m | 682.2 L | 97.5 kg | — | — | ✅ |
| 2 | 4 | K22 | Tarde | ORD-CL-202612-000155_22116046  1 | calle monjitas 4798, Independencia, Santiago, Chile | 1.97 | 6.4 m | 18.5 | 17:14 | [09:00,21:00] | 17:14 | 5.0 m | 400.4 L | 60.1 kg | — | — | ✅ |
| 3 | 4 | K22 | Tarde | ORD-CL-202612-000196_204415159 | calle arturo prat 1187, Ñuñoa, Santiago, Chile | 3.31 | 11.5 m | 17.3 | 17:30 | [09:00,21:00] | 17:30 | 5.0 m | 1895.3 L | 289.6 kg | — | — | ✅ |
| 4 | 4 | K22 | Tarde | DEPOT_01_BASE | Base Depósito | 2.67 | 10.0 m | 16.0 | 17:45 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 3
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 5 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 5 | K11 | Mañana | ORD-CL-202612-000088_79249631 | calle monjitas 7974, Recoleta, Santiago, Chile | 1.13 | 3.2 m | 21.0 | 09:03 | [09:00,11:00] | 09:03 | 5.0 m | 940.8 L | 161.2 kg | — | — | ✅ |
| 2 | 5 | K11 | Mañana | ORD-CL-202612-000166_9709625  6 | calle arturo prat 2589, Peñalolén, Santiago, Chile | 5.80 | 16.6 m | 21.0 | 09:24 | [09:00,11:00] | 09:24 | 5.0 m | 1056.7 L | 190.9 kg | — | — | ✅ |
| 3 | 5 | K11 | Mañana | ORD-CL-202612-000027_7499276  7 | calle compania de jesus 5241, Providencia, Santiago, Chile | 4.76 | 13.6 m | 21.0 | 09:43 | [11:00,13:00] | 11:00 | 5.0 m | 1718.7 L | 278.7 kg | 77 m | — | ⏳ |
| 4 | 5 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | 0.12 | 0.3 m | 23.0 | 11:05 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 3
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 6 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 6 | K12 | Tarde | ORD-CL-202612-000188_146386625 | avenida. libertador bernardo o'higgins 9819, Macul, Santiago, Chile | 1.51 | 3.6 m | 25.0 | 15:03 | [09:00,21:00] | 15:03 | 5.0 m | 3169.8 L | 425.3 kg | — | — | ✅ |
| 2 | 6 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | 1.36 | 3.3 m | 25.0 | 15:11 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 4
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 7 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 7 | K21 | Mañana | ORD-CL-202612-000085_15236104    9 | calle teatinos 975, San Miguel, Santiago, Chile | 0.93 | 2.4 m | 23.0 | 11:02 | [11:00,13:00] | 11:02 | 5.0 m | 1445.3 L | 206.3 kg | — | — | ✅ |
| 2 | 7 | K21 | Mañana | ORD-CL-202612-000107_158151651 | calle santo domingo 9121, Recoleta, Santiago, Chile | 0.76 | 2.0 m | 23.0 | 11:09 | [19:00,21:00] | 19:00 | 5.0 m | 2219.2 L | 319.8 kg | 471 m | — | ⏳ |
| 3 | 7 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | 0.97 | 2.7 m | 21.8 | 19:07 | — | — | — | — | — | — | — | 🏠 |


---
## Cluster 4

### Desglose de Tiempos por Camión
| ID Ruta | ID Vehículo | Clase K | Turno | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Vehículo 1 | K11 | Mañana | 09:00 | 17:36 | 106.1 min | 380.0 min | 30.0 min | 37.35 km | 6 |
| 2 | Vehículo 1 | K12 | Tarde | 15:00 | 16:05 | 55.9 min | 0.0 min | 10.0 min | 22.37 km | 2 |
| 3 | Vehículo 2 | K21 | Mañana | 11:00 | 13:38 | 56.9 min | 91.9 min | 10.0 min | 21.81 km | 2 |

### Vehículo Físico 1
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 1 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 1 | K11 | Mañana | ORD-CL-202612-000108_9272430  1 | avenida kennedy 3695, La Reina, Santiago, Chile | 11.07 | 31.6 m | 21.0 | 09:31 | [09:00,11:00] | 09:31 | 5.0 m | 230.5 L | 31.4 kg | — | — | ✅ |
| 2 | 1 | K11 | Mañana | ORD-CL-202612-000210_11704104  4 | calle estado 8684, Vitacura, Santiago, Chile | 2.37 | 6.8 m | 21.0 | 09:43 | [11:00,13:00] | 11:00 | 5.0 m | 1707.5 L | 294.1 kg | 77 m | — | ⏳ |
| 3 | 1 | K11 | Mañana | ORD-CL-202612-000195_16543282  2 | avenida. las condes 180, Independencia, Santiago, Chile | 6.10 | 15.9 m | 23.0 | 11:20 | [13:00,15:00] | 13:00 | 5.0 m | 1450.2 L | 222.2 kg | 99 m | — | ⏳ |
| 4 | 1 | K11 | Mañana | ORD-CL-202612-000045_74983175 | avenida. apoquindo 7097, Vitacura, Santiago, Chile | 6.63 | 17.3 m | 23.0 | 13:22 | [15:00,17:00] | 15:00 | 5.0 m | 31.4 L | 10.2 kg | 98 m | — | ⏳ |
| 5 | 1 | K11 | Mañana | ORD-CL-202612-000140_98108348 | avenida. apoquindo 8832, Lo Prado, Santiago, Chile | 0.00 | 0.0 m | — | 15:05 | [09:00,21:00] | 15:05 | 5.0 m | 74.7 L | 16.7 kg | — | — | ✅ |
| 6 | 1 | K11 | Mañana | ORD-CL-202612-000017_149456125 | avenida. matta 4672, Las Condes, Santiago, Chile | 1.39 | 3.3 m | 25.0 | 15:13 | [17:00,19:00] | 17:00 | 5.0 m | 22.7 L | 6.4 kg | 107 m | — | ⏳ |
| 7 | 1 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | 9.78 | 31.2 m | 18.8 | 17:36 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 1
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 2 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 2 | K12 | Tarde | ORD-CL-202612-000126_22556099  9 | avenida. kennedy 6395, Recoleta, Santiago, Chile | 6.08 | 14.6 m | 25.0 | 15:14 | [09:00,21:00] | 15:14 | 5.0 m | 866.8 L | 120.4 kg | — | — | ✅ |
| 2 | 2 | K12 | Tarde | ORD-CL-202612-000066_96822760 | calle teatinos 5180, Vitacura, Santiago, Chile | 5.41 | 13.3 m | 24.5 | 15:32 | [09:00,21:00] | 15:32 | 5.0 m | 1260.2 L | 220.9 kg | — | — | ✅ |
| 3 | 2 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | 10.88 | 28.0 m | 23.3 | 16:05 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 2
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 3 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 3 | K21 | Mañana | ORD-CL-202612-000009_8823811  3 | avenida. kennedy 7331, Independencia, Santiago, Chile | 10.78 | 28.1 m | 23.0 | 11:28 | [13:00,15:00] | 13:00 | 5.0 m | 2219.0 L | 256.8 kg | 92 m | — | ⏳ |
| 2 | 3 | K21 | Mañana | ORD-CL-202612-000021_217856993 | avenida. apoquindo 4280, Independencia, Santiago, Chile | 4.07 | 10.6 m | 23.0 | 13:15 | [13:00,15:00] | 13:15 | 5.0 m | 482.8 L | 56.6 kg | — | — | ✅ |
| 3 | 3 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | 6.95 | 18.1 m | 23.0 | 13:38 | — | — | — | — | — | — | — | 🏠 |


---
## Cluster 5

### Desglose de Tiempos por Camión
| ID Ruta | ID Vehículo | Clase K | Turno | Salida | Retorno | Viaje Efectivo | Espera | Servicio | Dist. (km) | Clientes |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Vehículo 1 | K11 | Mañana | 09:00 | 15:30 | 54.6 min | 316.3 min | 20.0 min | 20.44 km | 4 |
| 2 | Vehículo 1 | K12 | Tarde | 15:00 | 15:37 | 32.8 min | 0.0 min | 5.0 min | 13.49 km | 1 |
| 3 | Vehículo 2 | K21 | Mañana | 11:00 | 13:34 | 59.6 min | 90.3 min | 5.0 min | 22.85 km | 1 |
| 4 | Vehículo 2 | K22 | Tarde | 17:00 | 18:31 | 71.9 min | 0.0 min | 20.0 min | 20.77 km | 4 |
| 5 | Vehículo 3 | K11 | Mañana | 09:00 | 13:23 | 28.6 min | 225.3 min | 10.0 min | 10.47 km | 2 |

### Vehículo Físico 1
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 1 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 1 | K11 | Mañana | ORD-CL-202612-000183_148999950 | avenida. vicuna mackenna 578, Macul, Santiago, Chile | 7.96 | 22.7 m | 21.0 | 09:22 | [09:00,11:00] | 09:22 | 5.0 m | 685.5 L | 100.8 kg | — | — | ✅ |
| 2 | 1 | K11 | Mañana | ORD-CL-202612-000069_143319312 | avenida. pedro de valdivia 8517, Lo Prado, Santiago, Chile | 2.94 | 8.4 m | 21.0 | 09:36 | [09:00,21:00] | 09:36 | 5.0 m | 400.4 L | 79.2 kg | — | — | ✅ |
| 3 | 1 | K11 | Mañana | ORD-CL-202612-000112_208275613 | avenida. macul 2508, La Reina, Santiago, Chile | 0.90 | 2.6 m | 21.0 | 09:43 | [15:00,17:00] | 15:00 | 5.0 m | 1409.6 L | 246.7 kg | 316 m | — | ⏳ |
| 4 | 1 | K11 | Mañana | ORD-CL-202612-000179_121067557 | avenida. pedro de valdivia 4433, Peñalolén, Santiago, Chile | 2.34 | 5.6 m | 25.0 | 15:10 | [09:00,21:00] | 15:10 | 5.0 m | 716.4 L | 154.0 kg | — | — | ✅ |
| 5 | 1 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | 6.29 | 15.2 m | 24.8 | 15:30 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 1
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 2 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 2 | K12 | Tarde | ORD-CL-202612-000039_64956582 | avenida. tobalaba 9986, Las Condes, Santiago, Chile | 6.84 | 16.4 m | 25.0 | 15:16 | [09:00,21:00] | 15:16 | 5.0 m | 3005.7 L | 379.0 kg | — | — | ✅ |
| 2 | 2 | K12 | Tarde | DEPOT_01_BASE | Base Depósito | 6.65 | 16.4 m | 24.4 | 15:37 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 2
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 3 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 3 | K21 | Mañana | ORD-CL-202612-000049_111101253 | avenida. grecia 7712, Recoleta, Santiago, Chile | 11.39 | 29.7 m | 23.0 | 11:29 | [13:00,15:00] | 13:00 | 5.0 m | 3858.7 L | 488.3 kg | 90 m | — | ⏳ |
| 2 | 3 | K21 | Mañana | DEPOT_01_BASE | Base Depósito | 11.46 | 29.9 m | 23.0 | 13:34 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 2
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 4 | K22 | Tarde | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 4 | K22 | Tarde | ORD-CL-202612-000148_175474353 | avenida. irarrazaval 2033, Maipú, Santiago, Chile | 5.08 | 16.1 m | 19.0 | 17:16 | [17:00,19:00] | 17:16 | 5.0 m | 75.1 L | 20.7 kg | — | — | ✅ |
| 2 | 4 | K22 | Tarde | ORD-CL-202612-000180_135550036 | avenida. grecia 4946, Santiago, Santiago, Chile | 3.90 | 13.7 m | 17.1 | 17:34 | [09:00,21:00] | 17:34 | 5.0 m | 1259.6 L | 232.8 kg | — | — | ✅ |
| 3 | 4 | K22 | Tarde | ORD-CL-202612-000079_112922605 | avenida. irarrazaval 6780, Macul, Santiago, Chile | 2.45 | 9.2 m | 16.0 | 17:48 | [09:00,21:00] | 17:48 | 5.0 m | 201.8 L | 37.8 kg | — | — | ✅ |
| 4 | 4 | K22 | Tarde | ORD-CL-202612-000025_224766177 | calle teatinos 6266, Providencia, Santiago, Chile | 5.10 | 19.1 m | 16.0 | 18:13 | [09:00,21:00] | 18:13 | 5.0 m | 1343.6 L | 132.4 kg | — | — | ✅ |
| 5 | 4 | K22 | Tarde | DEPOT_01_BASE | Base Depósito | 4.24 | 13.9 m | 18.3 | 18:31 | — | — | — | — | — | — | — | 🏠 |

### Vehículo Físico 3
| # | Ruta | Clase K | Turno | Nodo | Dirección | Dist. (km) | T. Viaje | Vel. (h) | Llegada | Ventana | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 5 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | — | — | — | 09:00 | — | 09:00 | — | — | — | — | — | 🏠 |
| 1 | 5 | K11 | Mañana | ORD-CL-202612-000052_14976779    6 | avenida. irarrazaval 8302, Ñuñoa, Santiago, Chile | 5.14 | 14.7 m | 21.0 | 09:14 | [13:00,15:00] | 13:00 | 5.0 m | 1652.6 L | 231.9 kg | 225 m | — | ⏳ |
| 2 | 5 | K11 | Mañana | ORD-CL-202612-000094_84473640 | avenida. irarrazaval 640, Lo Prado, Santiago, Chile | 1.43 | 3.7 m | 23.0 | 13:08 | [09:00,21:00] | 13:08 | 5.0 m | 745.5 L | 121.3 kg | — | — | ✅ |
| 3 | 5 | K11 | Mañana | DEPOT_01_BASE | Base Depósito | 3.90 | 10.2 m | 23.0 | 13:23 | — | — | — | — | — | — | — | 🏠 |


---
