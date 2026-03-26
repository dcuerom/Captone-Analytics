# Reporte GA (PyMoo Problem) - 2026-12-03

## Cluster 0

### Resumen Operativo

| Métrica                   | Valor                 |
| :------------------------- | :-------------------- |
| Distancia Total            | 98,997.1 m (99.00 km) |
| Costo Ruta (F = dist × S) | 118,796.50            |
| Hora Salida Depósito      | 09:00                 |
| Hora Retorno Depósito     | 19:58                 |
| Duración Total            | 10h 58min             |
| Vehículos Asignados       | 2                     |

### Restricción 14: Cumplimiento de Ventanas de Tiempo

| Indicador                                 | Valor     |
| :---------------------------------------- | :-------- |
| Clientes atendidos en ventana             | 14/14     |
| Clientes con espera (llegada anticipada)  | 5         |
| Clientes con violación (llegada tardía) | 0         |
| Tiempo de espera acumulado                | 500.9 min |
| Violación acumulada (G)                  | 0.0 min   |

### Desglose de Tiempos por Camión

| Camión | Salida | Retorno | Viaje Efectivo |  Espera  | Servicio | Dist. (km) | Clientes |
| :-----: | :----: | :-----: | :------------: | :-------: | :------: | :--------: | :------: |
|    1    | 09:00 |  11:59  |    99.5 min    | 50.0 min | 30.0 min |  36.70 km  |    6    |
|    2    | 09:00 |  19:58  |   167.8 min   | 450.9 min | 40.0 min |  62.30 km  |    8    |

### Camión 1 — Detalle de Paradas

| # | Nodo                             | Dirección                                                         | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :------------------------------- | :----------------------------------------------------------------- | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :------: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                    | Base Depósito                                                     |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |    —    |    —    |   —   |  —  | 🏠 |
| 1 | ORD-CL-202612-000082_198569524   | avenida. departamental 2287, La Florida, Santiago, Chile           |   12.32   |  35.2 m  |   21.0   |  09:35  | [09:00,11:00] |    09:35    |  5.0 m  | 481.1 L |  96.3 kg  |   —   |  —  | ✅ |
| 2 | ORD-CL-202612-000139_162296701   | avenida. pajaritos 9174, La Florida, Santiago, Chile               |    1.16    |  3.3 m  |   21.0   |  09:43  | [09:00,21:00] |    09:43    |  5.0 m  | 614.9 L | 114.0 kg |   —   |  —  | ✅ |
| 3 | ORD-CL-202612-000002_173134031   | avenida. la florida 7678, Macul, Santiago, Chile                   |    0.72    |  2.0 m  |   21.5   |  09:50  | [09:00,21:00] |    09:50    |  5.0 m  | 4239.4 L | 505.6 kg |   —   |  —  | ✅ |
| 4 | ORD-CL-202612-000177_19337908  6 | avenida. la florida 2133, Macul, Santiago, Chile                   |    0.64    |  1.8 m  |   22.0   |  09:57  | [09:00,21:00] |    09:57    |  5.0 m  | 905.8 L | 185.3 kg |   —   |  —  | ✅ |
| 5 | ORD-CL-202612-000133_55387737    | calle teatinos 4659, La Florida, Santiago, Chile                   |    2.88    |  7.7 m  |   22.4   |  10:10  | [11:00,13:00] |    11:00    |  5.0 m  | 379.5 L |  55.8 kg  |  50 m  |  —  | ⏳ |
| 6 | ORD-CL-202612-000032_83953104    | gran avenida jose miguel carrera 1084, La Florida, Santiago, Chile |    4.12    |  10.7 m  |   23.0   |  11:15  | [09:00,21:00] |    11:15    |  5.0 m  | 2217.2 L | 261.7 kg |   —   |  —  | ✅ |
| 7 | DEPOT_01_BASE                    | Base Depósito                                                     |   14.85   |  38.7 m  |   23.0   |  11:59  |      —      |     —     |   —   |    —    |    —    |   —   |  —  | 🏠 |

### Camión 2 — Detalle de Paradas

| # | Nodo                             | Dirección                                                    | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :------------------------------- | :------------------------------------------------------------ | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :------: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                    | Base Depósito                                                |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |    —    |    —    |   —   |  —  | 🏠 |
| 1 | ORD-CL-202612-000222_64382296    | calle merced 6576, Puente Alto, Santiago, Chile               |   21.36   |  61.0 m  |   21.0   |  10:01  | [13:00,15:00] |    13:00    |  5.0 m  | 1396.1 L | 158.3 kg | 179 m |  —  | ⏳ |
| 2 | ORD-CL-202612-000187_5138738  6  | avenida. independencia 4810, Puente Alto, Santiago, Chile     |    1.11    |  2.9 m  |   23.0   |  13:07  | [13:00,15:00] |    13:07    |  5.0 m  | 222.3 L |  37.4 kg  |   —   |  —  | ✅ |
| 3 | ORD-CL-202612-000163_215462173   | avenida. pedro de valdivia 8264, Puente Alto, Santiago, Chile |    2.77    |  7.2 m  |   23.0   |  13:20  | [15:00,17:00] |    15:00    |  5.0 m  |  24.8 L  |  9.3 kg  | 100 m |  —  | ⏳ |
| 4 | ORD-CL-202612-000020_10263868  8 | avenida. manuel montt 3031, Maipú, Santiago, Chile           |    4.52    |  10.9 m  |   25.0   |  15:15  | [15:00,17:00] |    15:15    |  5.0 m  | 3905.5 L | 441.5 kg |   —   |  —  | ✅ |
| 5 | ORD-CL-202612-000006_207417262   | calle catedral 9181, Puente Alto, Santiago, Chile             |    5.26    |  12.9 m  |   24.4   |  15:33  | [17:00,19:00] |    17:00    |  5.0 m  | 639.5 L | 113.7 kg |  86 m  |  —  | ⏳ |
| 6 | ORD-CL-202612-000024_53351852    | avenida. apoquindo 5706, La Florida, Santiago, Chile          |    9.14    |  29.1 m  |   18.8   |  17:34  | [19:00,21:00] |    19:00    |  5.0 m  | 168.8 L |  34.9 kg  |  86 m  |  —  | ⏳ |
| 7 | ORD-CL-202612-000135_153012165   | avenida. vicuna mackenna 8405, Peñalolén, Santiago, Chile   |    3.53    |  9.7 m  |   21.8   |  19:14  | [19:00,21:00] |    19:14    |  5.0 m  | 644.2 L | 128.1 kg |   —   |  —  | ✅ |
| 8 | ORD-CL-202612-000031_14317726  4 | avenida. la florida 1002, Peñalolén, Santiago, Chile        |    3.09    |  7.5 m  |   24.9   |  19:27  | [19:00,21:00] |    19:27    |  5.0 m  | 2786.0 L | 391.8 kg |   —   |  —  | ✅ |
| 9 | DEPOT_01_BASE                    | Base Depósito                                                |   11.51   |  26.6 m  |   26.0   |  19:58  |      —      |     —     |   —   |    —    |    —    |   —   |  —  | 🏠 |

---

## Cluster 1

### Resumen Operativo

| Métrica                   | Valor                 |
| :------------------------- | :-------------------- |
| Distancia Total            | 23,430.6 m (23.43 km) |
| Costo Ruta (F = dist × S) | 28,116.73             |
| Hora Salida Depósito      | 09:00                 |
| Hora Retorno Depósito     | 19:38                 |
| Duración Total            | 10h 38min             |
| Vehículos Asignados       | 1                     |

### Restricción 14: Cumplimiento de Ventanas de Tiempo

| Indicador                                 | Valor     |
| :---------------------------------------- | :-------- |
| Clientes atendidos en ventana             | 6/6       |
| Clientes con espera (llegada anticipada)  | 2         |
| Clientes con violación (llegada tardía) | 0         |
| Tiempo de espera acumulado                | 547.8 min |
| Violación acumulada (G)                  | 0.0 min   |

### Desglose de Tiempos por Camión

| Camión | Salida | Retorno | Viaje Efectivo |  Espera  | Servicio | Dist. (km) | Clientes |
| :-----: | :----: | :-----: | :------------: | :-------: | :------: | :--------: | :------: |
|    1    | 09:00 |  19:38  |    60.9 min    | 547.8 min | 30.0 min |  23.43 km  |    6    |

### Camión 1 — Detalle de Paradas

| # | Nodo                              | Dirección                                                | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :-------------------------------- | :-------------------------------------------------------- | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :------: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                     | Base Depósito                                            |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |    —    |    —    |   —   |  —  | 🏠 |
| 1 | ORD-CL-202612-000091_79104971     | avenida. independencia 4637, Providencia, Santiago, Chile |    7.16    |  20.4 m  |   21.0   |  09:20  | [11:00,13:00] |    11:00    |  5.0 m  | 848.6 L | 167.5 kg | 100 m |  —  | ⏳ |
| 2 | ORD-CL-202612-000055_203179717    | avenida. mapocho 6648, Macul, Santiago, Chile             |    7.87    |  20.5 m  |   23.0   |  11:25  | [09:00,21:00] |    11:25    |  5.0 m  | 224.5 L |  56.1 kg  |   —   |  —  | ✅ |
| 3 | ORD-CL-202612-000062_7640094    3 | calle san antonio 9379, Lo Prado, Santiago, Chile         |    0.49    |  1.3 m  |   23.0   |  11:31  | [19:00,21:00] |    19:00    |  5.0 m  | 634.5 L | 101.6 kg | 448 m |  —  | ⏳ |
| 4 | ORD-CL-202612-000004_183059669    | calle san antonio 8832, Lo Prado, Santiago, Chile         |    0.00    |  0.0 m  |    —    |  19:05  | [09:00,21:00] |    19:05    |  5.0 m  | 2514.1 L | 317.4 kg |   —   |  —  | ✅ |
| 5 | ORD-CL-202612-000115_198154752    | calle san antonio 6514, La Reina, Santiago, Chile         |    0.13    |  0.3 m  |   22.8   |  19:10  | [19:00,21:00] |    19:10    |  5.0 m  | 371.8 L | 100.9 kg |   —   |  —  | ✅ |
| 6 | ORD-CL-202612-000044_145036177    | avenida. tobalaba 5892, Quinta Normal, Santiago, Chile    |    1.77    |  4.4 m  |   23.9   |  19:19  | [09:00,21:00] |    19:19    |  5.0 m  | 855.7 L | 127.7 kg |   —   |  —  | ✅ |
| 7 | DEPOT_01_BASE                     | Base Depósito                                            |    6.02    |  13.9 m  |   26.0   |  19:38  |      —      |     —     |   —   |    —    |    —    |   —   |  —  | 🏠 |

---

## Cluster 2

### Resumen Operativo

| Métrica                   | Valor                 |
| :------------------------- | :-------------------- |
| Distancia Total            | 44,245.5 m (44.25 km) |
| Costo Ruta (F = dist × S) | 53,094.55             |
| Hora Salida Depósito      | 09:00                 |
| Hora Retorno Depósito     | 17:35                 |
| Duración Total            | 8h 35min              |
| Vehículos Asignados       | 1                     |

### Restricción 14: Cumplimiento de Ventanas de Tiempo

| Indicador                                 | Valor     |
| :---------------------------------------- | :-------- |
| Clientes atendidos en ventana             | 9/9       |
| Clientes con espera (llegada anticipada)  | 4         |
| Clientes con violación (llegada tardía) | 0         |
| Tiempo de espera acumulado                | 347.1 min |
| Violación acumulada (G)                  | 0.0 min   |

### Desglose de Tiempos por Camión

| Camión | Salida | Retorno | Viaje Efectivo |  Espera  | Servicio | Dist. (km) | Clientes |
| :-----: | :----: | :-----: | :------------: | :-------: | :------: | :--------: | :------: |
|    1    | 09:00 |  17:35  |   123.8 min   | 347.1 min | 45.0 min |  44.25 km  |    9    |

### Camión 1 — Detalle de Paradas

| # | Nodo                                | Dirección                                              | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :---------------------------------- | :------------------------------------------------------ | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :------: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                       | Base Depósito                                          |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |    —    |    —    |   —   |  —  | 🏠 |
| 1 | *ORD-CL-202612-000108_9272430  1*  | avenida kennedy 3695, La Reina, Santiago, Chile         |   11.05   |  31.6 m  |   21.0   |  09:31  | [09:00,11:00] |    09:31    |  5.0 m  | 230.5 L |  31.4 kg  |   —   |  —  | ✅ |
| 2 | *ORD-CL-202612-000210_11704104  4* | calle estado 8684, Vitacura, Santiago, Chile            |    2.37    |  6.8 m  |   21.0   |  09:43  | [11:00,13:00] |    11:00    |  5.0 m  | 1707.5 L | 294.1 kg |  77 m  |  —  | ⏳ |
| 3 | ORD-CL-202612-000066_96822760       | calle teatinos 5180, Vitacura, Santiago, Chile          |    0.00    |  0.0 m  |    —    |  11:05  | [09:00,21:00] |    11:05    |  5.0 m  | 1260.2 L | 220.9 kg |   —   |  —  | ✅ |
| 4 | *ORD-CL-202612-000195_16543282  2* | avenida. las condes 180, Independencia, Santiago, Chile |    6.10    |  15.9 m  |   23.0   |  11:25  | [13:00,15:00] |    13:00    |  5.0 m  | 1450.2 L | 222.2 kg |  94 m  |  —  | ⏳ |
| 5 | *ORD-CL-202612-000009_8823811  3*  | avenida. kennedy 7331, Independencia, Santiago, Chile   |    6.01    |  15.7 m  |   23.0   |  13:20  | [13:00,15:00] |    13:20    |  5.0 m  | 2219.0 L | 256.8 kg |   —   |  —  | ✅ |
| 6 | *ORD-CL-202612-000021_217856993*   | avenida. apoquindo 4280, Independencia, Santiago, Chile |    4.07    |  10.6 m  |   23.1   |  13:36  | [13:00,15:00] |    13:36    |  5.0 m  | 482.8 L |  56.6 kg  |   —   |  —  | ✅ |
| 7 | ORD-CL-202612-000045_74983175       | avenida. apoquindo 7097, Vitacura, Santiago, Chile      |    3.57    |  9.1 m  |   23.6   |  13:50  | [15:00,17:00] |    15:00    |  5.0 m  |  31.4 L  |  10.2 kg  |  70 m  |  —  | ⏳ |
| 8 | *ORD-CL-202612-000140_98108348*    | avenida. apoquindo 8832, Lo Prado, Santiago, Chile      |    0.00    |  0.0 m  |    —    |  15:05  | [09:00,21:00] |    15:05    |  5.0 m  |  74.7 L  |  16.7 kg  |   —   |  —  | ✅ |
| 9 | *ORD-CL-202612-000017_149456125*   | avenida. matta 4672, Las Condes, Santiago, Chile        |    1.39    |  3.3 m  |   25.0   |  15:13  | [17:00,19:00] |    17:00    |  5.0 m  |  22.7 L  |  6.4 kg  | 107 m |  —  | ⏳ |
| 10 | DEPOT_01_BASE                       | Base Depósito                                          |    9.67    |  30.8 m  |   18.8   |  17:35  |      —      |     —     |   —   |    —    |    —    |   —   |  —  | 🏠 |

---

## Cluster 3

### Resumen Operativo

| Métrica                   | Valor                 |
| :------------------------- | :-------------------- |
| Distancia Total            | 36,265.9 m (36.27 km) |
| Costo Ruta (F = dist × S) | 43,519.08             |
| Hora Salida Depósito      | 09:00                 |
| Hora Retorno Depósito     | 15:27                 |
| Duración Total            | 6h 27min              |
| Vehículos Asignados       | 1                     |

### Restricción 14: Cumplimiento de Ventanas de Tiempo

| Indicador                                 | Valor     |
| :---------------------------------------- | :-------- |
| Clientes atendidos en ventana             | 5/5       |
| Clientes con espera (llegada anticipada)  | 1         |
| Clientes con violación (llegada tardía) | 0         |
| Tiempo de espera acumulado                | 265.7 min |
| Violación acumulada (G)                  | 0.0 min   |

### Desglose de Tiempos por Camión

| Camión | Salida | Retorno | Viaje Efectivo |  Espera  | Servicio | Dist. (km) | Clientes |
| :-----: | :----: | :-----: | :------------: | :-------: | :------: | :--------: | :------: |
|    1    | 09:00 |  15:27  |    97.0 min    | 265.7 min | 25.0 min |  36.27 km  |    5    |

### Camión 1 — Detalle de Paradas

| # | Nodo                            | Dirección                                                    | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :------------------------------ | :------------------------------------------------------------ | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :------: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                   | Base Depósito                                                |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |    —    |    —    |   —   |  —  | 🏠 |
| 1 | ORD-CL-202612-000010_62835725   | avenida americo vespucio 2389, Independencia, Santiago, Chile |   12.29   |  35.1 m  |   21.0   |  09:35  | [09:00,21:00] |    09:35    |  5.0 m  | 894.1 L | 164.7 kg |   —   |  —  | ✅ |
| 2 | ORD-CL-202612-000096_52601895   | calle arturo prat 4852, Independencia, Santiago, Chile        |    1.63    |  4.7 m  |   21.0   |  09:44  | [09:00,21:00] |    09:44    |  5.0 m  | 1136.0 L | 188.5 kg |   —   |  —  | ✅ |
| 3 | ORD-CL-202612-000144_210301989  | avenida vitacura 713, Quinta Normal, Santiago, Chile          |    4.44    |  12.3 m  |   21.6   |  10:02  | [09:00,11:00] |    10:02    |  5.0 m  | 196.0 L |  24.5 kg  |   —   |  —  | ✅ |
| 4 | ORD-CL-202612-000178_6756635  4 | calle bandera 9187, Vitacura, Santiago, Chile                 |    4.74    |  12.5 m  |   22.8   |  10:19  | [09:00,21:00] |    10:19    |  5.0 m  | 363.4 L |  89.2 kg  |   —   |  —  | ✅ |
| 5 | ORD-CL-202612-000122_51491954   | avenida. santa rosa 5626, San Miguel, Santiago, Chile         |    3.73    |  9.7 m  |   23.0   |  10:34  | [15:00,17:00] |    15:00    |  5.0 m  | 322.7 L |  73.9 kg  | 266 m |  —  | ⏳ |
| 6 | DEPOT_01_BASE                   | Base Depósito                                                |    9.43    |  22.6 m  |   25.0   |  15:27  |      —      |     —     |   —   |    —    |    —    |   —   |  —  | 🏠 |

---

## Cluster 4

### Resumen Operativo

| Métrica                   | Valor                 |
| :------------------------- | :-------------------- |
| Distancia Total            | 21,723.2 m (21.72 km) |
| Costo Ruta (F = dist × S) | 26,067.85             |
| Hora Salida Depósito      | 09:00                 |
| Hora Retorno Depósito     | 19:19                 |
| Duración Total            | 10h 19min             |
| Vehículos Asignados       | 1                     |

### Restricción 14: Cumplimiento de Ventanas de Tiempo

| Indicador                                 | Valor     |
| :---------------------------------------- | :-------- |
| Clientes atendidos en ventana             | 7/7       |
| Clientes con espera (llegada anticipada)  | 2         |
| Clientes con violación (llegada tardía) | 0         |
| Tiempo de espera acumulado                | 526.5 min |
| Violación acumulada (G)                  | 0.0 min   |

### Desglose de Tiempos por Camión

| Camión | Salida | Retorno | Viaje Efectivo |  Espera  | Servicio | Dist. (km) | Clientes |
| :-----: | :----: | :-----: | :------------: | :-------: | :------: | :--------: | :------: |
|    1    | 09:00 |  19:19  |    57.5 min    | 526.5 min | 35.0 min |  21.72 km  |    7    |

### Camión 1 — Detalle de Paradas

| # | Nodo                             | Dirección                                             | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :------------------------------- | :----------------------------------------------------- | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :------: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                    | Base Depósito                                         |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |    —    |    —    |   —   |  —  | 🏠 |
| 1 | ORD-CL-202612-000209_163993586   | avenida. providencia 4275, Las Condes, Santiago, Chile |    3.75    |  10.7 m  |   21.0   |  09:10  | [15:00,17:00] |    15:00    |  5.0 m  | 276.9 L |  36.7 kg  | 349 m |  —  | ⏳ |
| 2 | ORD-CL-202612-000160_108505650   | avenida. providencia 178, Providencia, Santiago, Chile |    0.00    |  0.0 m  |    —    |  15:05  | [15:00,17:00] |    15:05    |  5.0 m  | 245.4 L |  52.4 kg  |   —   |  —  | ✅ |
| 3 | ORD-CL-202612-000013_9933788  8  | avenida. manuel montt 401, Vitacura, Santiago, Chile   |    0.47    |  1.1 m  |   25.0   |  15:11  | [09:00,21:00] |    15:11    |  5.0 m  | 262.6 L |  34.5 kg  |   —   |  —  | ✅ |
| 4 | ORD-CL-202612-000025_224766177   | calle teatinos 6266, Providencia, Santiago, Chile      |    1.00    |  2.4 m  |   24.8   |  15:18  | [09:00,21:00] |    15:18    |  5.0 m  | 1343.6 L | 132.4 kg |   —   |  —  | ✅ |
| 5 | ORD-CL-202612-000039_64956582    | avenida. tobalaba 9986, Las Condes, Santiago, Chile    |    2.58    |  6.4 m  |   24.2   |  15:29  | [09:00,21:00] |    15:29    |  5.0 m  | 3005.7 L | 379.0 kg |   —   |  —  | ✅ |
| 6 | ORD-CL-202612-000126_22556099  9 | avenida. kennedy 6395, Recoleta, Santiago, Chile       |    3.19    |  8.1 m  |   23.5   |  15:43  | [09:00,21:00] |    15:43    |  5.0 m  | 866.8 L | 120.4 kg |   —   |  —  | ✅ |
| 7 | ORD-CL-202612-000118_65054485    | avenida la florida 3026, Santiago, Santiago, Chile     |    5.62    |  14.7 m  |   23.0   |  16:02  | [19:00,21:00] |    19:00    |  5.0 m  | 1214.1 L | 215.7 kg | 177 m |  —  | ⏳ |
| 8 | DEPOT_01_BASE                    | Base Depósito                                         |    5.12    |  14.1 m  |   21.8   |  19:19  |      —      |     —     |   —   |    —    |    —    |   —   |  —  | 🏠 |

---

## Cluster 5

### Resumen Operativo

| Métrica                   | Valor                 |
| :------------------------- | :-------------------- |
| Distancia Total            | 64,713.4 m (64.71 km) |
| Costo Ruta (F = dist × S) | 77,656.07             |
| Hora Salida Depósito      | 09:00                 |
| Hora Retorno Depósito     | 15:21                 |
| Duración Total            | 6h 21min              |
| Vehículos Asignados       | 2                     |

### Restricción 14: Cumplimiento de Ventanas de Tiempo

| Indicador                                 | Valor     |
| :---------------------------------------- | :-------- |
| Clientes atendidos en ventana             | 11/11     |
| Clientes con espera (llegada anticipada)  | 2         |
| Clientes con violación (llegada tardía) | 0         |
| Tiempo de espera acumulado                | 311.6 min |
| Violación acumulada (G)                  | 0.0 min   |

### Desglose de Tiempos por Camión

| Camión | Salida | Retorno | Viaje Efectivo |  Espera  | Servicio | Dist. (km) | Clientes |
| :-----: | :----: | :-----: | :------------: | :-------: | :------: | :--------: | :------: |
|    1    | 09:00 |  11:40  |   120.6 min   |  0.0 min  | 40.0 min |  44.12 km  |    8    |
|    2    | 09:00 |  15:21  |    54.9 min    | 311.6 min | 15.0 min |  20.59 km  |    3    |

### Camión 1 — Detalle de Paradas

| # | Nodo                               | Dirección                                              | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :--------------------------------- | :------------------------------------------------------ | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :------: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                      | Base Depósito                                          |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |    —    |    —    |   —   |  —  | 🏠 |
| 1 | ORD-CL-202612-000141_140162225     | calle san antonio 2631, La Reina, Santiago, Chile       |   20.74   |  59.3 m  |   21.0   |  09:59  | [09:00,21:00] |    09:59    |  5.0 m  |  84.7 L  |  24.3 kg  |   —   |  —  | ✅ |
| 2 | ORD-CL-202612-000111_5802113  4    | avenida. las condes 599, San Miguel, Santiago, Chile    |    6.01    |  16.0 m  |   22.6   |  10:20  | [09:00,21:00] |    10:20    |  5.0 m  | 2018.8 L | 255.6 kg |   —   |  —  | ✅ |
| 3 | ORD-CL-202612-000208_107728946     | avenida. pajaritos 1016, San Miguel, Santiago, Chile    |    1.13    |  3.0 m  |   23.0   |  10:28  | [09:00,21:00] |    10:28    |  5.0 m  | 4894.5 L | 609.0 kg |   —   |  —  | ✅ |
| 4 | ORD-CL-202612-000022_169468917     | avenida. pajaritos 7516, Maipú, Santiago, Chile        |    6.07    |  15.8 m  |   23.0   |  10:49  | [09:00,21:00] |    10:49    |  5.0 m  | 929.9 L | 130.3 kg |   —   |  —  | ✅ |
| 5 | ORD-CL-202612-000087_17107764  6   | avenida. pajaritos 5796, Independencia, Santiago, Chile |    2.46    |  6.4 m  |   23.0   |  11:00  | [11:00,13:00] |    11:00    |  5.0 m  | 237.6 L |  62.3 kg  |   —   |  —  | ✅ |
| 6 | ORD-CL-202612-000121_102139227     | calle bandera 3131, Estación Central, Santiago, Chile  |    1.78    |  4.6 m  |   23.0   |  11:10  | [09:00,21:00] |    11:10    |  5.0 m  | 1152.4 L | 159.0 kg |   —   |  —  | ✅ |
| 7 | ORD-CL-202612-000143_14358394    1 | avenida. matta 9543, Estación Central, Santiago, Chile |    0.00    |  0.0 m  |    —    |  11:15  | [09:00,21:00] |    11:15    |  5.0 m  |  74.2 L  |  18.0 kg  |   —   |  —  | ✅ |
| 8 | ORD-CL-202612-000015_93475810      | calle morande 6751, Estación Central, Santiago, Chile  |    0.00    |  0.0 m  |    —    |  11:20  | [09:00,21:00] |    11:20    |  5.0 m  | 266.4 L |  74.4 kg  |   —   |  —  | ✅ |
| 9 | DEPOT_01_BASE                      | Base Depósito                                          |    5.93    |  15.5 m  |   23.0   |  11:40  |      —      |     —     |   —   |    —    |    —    |   —   |  —  | 🏠 |

### Camión 2 — Detalle de Paradas

| # | Nodo                             | Dirección                                                  | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :------------------------------- | :---------------------------------------------------------- | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :------: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                    | Base Depósito                                              |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |    —    |    —    |   —   |  —  | 🏠 |
| 1 | ORD-CL-202612-000150_10411606  1 | calle santo domingo 6777, Vitacura, Santiago, Chile         |    3.64    |  10.4 m  |   21.0   |  09:10  | [09:00,21:00] |    09:10    |  5.0 m  | 1086.9 L | 173.4 kg |   —   |  —  | ✅ |
| 2 | ORD-CL-202612-000011_18195149  6 | avenida. pajaritos 5435, Ñuñoa, Santiago, Chile           |    7.13    |  20.4 m  |   21.0   |  09:35  | [13:00,15:00] |    13:00    |  5.0 m  | 4252.7 L | 550.2 kg | 204 m |  —  | ⏳ |
| 3 | ORD-CL-202612-000071_212196364   | avenida. pajaritos 3626, Estación Central, Santiago, Chile |    2.92    |  7.6 m  |   23.0   |  13:12  | [15:00,17:00] |    15:00    |  5.0 m  | 1006.0 L | 197.4 kg | 107 m |  —  | ⏳ |
| 4 | DEPOT_01_BASE                    | Base Depósito                                              |    6.90    |  16.6 m  |   25.0   |  15:21  |      —      |     —     |   —   |    —    |    —    |   —   |  —  | 🏠 |

---

## Cluster 6

### Resumen Operativo

| Métrica                   | Valor                 |
| :------------------------- | :-------------------- |
| Distancia Total            | 32,272.8 m (32.27 km) |
| Costo Ruta (F = dist × S) | 38,727.33             |
| Hora Salida Depósito      | 09:00                 |
| Hora Retorno Depósito     | 15:39                 |
| Duración Total            | 6h 39min              |
| Vehículos Asignados       | 1                     |

### Restricción 14: Cumplimiento de Ventanas de Tiempo

| Indicador                                 | Valor     |
| :---------------------------------------- | :-------- |
| Clientes atendidos en ventana             | 4/4       |
| Clientes con espera (llegada anticipada)  | 2         |
| Clientes con violación (llegada tardía) | 0         |
| Tiempo de espera acumulado                | 295.6 min |
| Violación acumulada (G)                  | 0.0 min   |

### Desglose de Tiempos por Camión

| Camión | Salida | Retorno | Viaje Efectivo |  Espera  | Servicio | Dist. (km) | Clientes |
| :-----: | :----: | :-----: | :------------: | :-------: | :------: | :--------: | :------: |
|    1    | 09:00 |  15:39  |    84.0 min    | 295.6 min | 20.0 min |  32.27 km  |    4    |

### Camión 1 — Detalle de Paradas

| # | Nodo                           | Dirección                                             | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :----------------------------- | :----------------------------------------------------- | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :------: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                  | Base Depósito                                         |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |    —    |    —    |   —   |  —  | 🏠 |
| 1 | ORD-CL-202612-000049_111101253 | avenida. grecia 7712, Recoleta, Santiago, Chile        |   11.40   |  32.6 m  |   21.0   |  09:32  | [13:00,15:00] |    13:00    |  5.0 m  | 3858.7 L | 488.3 kg | 207 m |  —  | ⏳ |
| 2 | ORD-CL-202612-000060_199941644 | avenida. macul 7795, Maipú, Santiago, Chile           |    4.48    |  11.7 m  |   23.0   |  13:16  | [09:00,21:00] |    13:16    |  5.0 m  | 577.7 L |  83.3 kg  |   —   |  —  | ✅ |
| 3 | ORD-CL-202612-000019_156820915 | avenida. tobalaba 3402, Macul, Santiago, Chile         |    1.35    |  3.5 m  |   23.0   |  13:25  | [09:00,21:00] |    13:25    |  5.0 m  | 2163.4 L | 238.1 kg |   —   |  —  | ✅ |
| 4 | ORD-CL-202612-000092_162059956 | avenida. providencia 4727, La Florida, Santiago, Chile |    0.62    |  1.6 m  |   23.3   |  13:31  | [15:00,17:00] |    15:00    |  5.0 m  | 892.8 L | 131.5 kg |  88 m  |  —  | ⏳ |
| 5 | DEPOT_01_BASE                  | Base Depósito                                         |   14.42   |  34.6 m  |   25.0   |  15:39  |      —      |     —     |   —   |    —    |    —    |   —   |  —  | 🏠 |

---

## Cluster 7

### Resumen Operativo

| Métrica                   | Valor                 |
| :------------------------- | :-------------------- |
| Distancia Total            | 24,333.1 m (24.33 km) |
| Costo Ruta (F = dist × S) | 29,199.77             |
| Hora Salida Depósito      | 09:00                 |
| Hora Retorno Depósito     | 15:08                 |
| Duración Total            | 6h 8min               |
| Vehículos Asignados       | 3                     |

### Restricción 14: Cumplimiento de Ventanas de Tiempo

| Indicador                                 | Valor     |
| :---------------------------------------- | :-------- |
| Clientes atendidos en ventana             | 19/19     |
| Clientes con espera (llegada anticipada)  | 4         |
| Clientes con violación (llegada tardía) | 0         |
| Tiempo de espera acumulado                | 990.6 min |
| Violación acumulada (G)                  | 0.0 min   |

### Desglose de Tiempos por Camión

| Camión | Salida | Retorno | Viaje Efectivo |  Espera  | Servicio | Dist. (km) | Clientes |
| :-----: | :----: | :-----: | :------------: | :-------: | :------: | :--------: | :------: |
|    1    | 09:00 |  19:07  |    14.5 min    | 558.5 min | 35.0 min |  4.40 km  |    7    |
|    2    | 09:00 |  11:57  |    41.1 min    | 91.0 min | 45.0 min |  15.30 km  |    9    |
|    3    | 09:00 |  15:08  |    12.5 min    | 341.1 min | 15.0 min |  4.64 km  |    3    |

### Camión 1 — Detalle de Paradas

| # | Nodo                             | Dirección                                                          | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :------------------------------- | :------------------------------------------------------------------ | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :------: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                    | Base Depósito                                                      |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |    —    |    —    |   —   |  —  | 🏠 |
| 1 | ORD-CL-202612-000026_175731263   | calle san antonio 1509, Providencia, Santiago, Chile                |    0.27    |  0.8 m  |   21.0   |  09:00  | [17:00,19:00] |    17:00    |  5.0 m  | 1731.7 L | 205.5 kg | 479 m |  —  | ⏳ |
| 2 | ORD-CL-202612-000170_137256512   | calle san antonio 2929, Santiago, Santiago, Chile                   |    0.00    |  0.0 m  |    —    |  17:05  | [09:00,21:00] |    17:05    |  5.0 m  | 776.8 L | 140.6 kg |   —   |  —  | ✅ |
| 3 | ORD-CL-202612-000093_134538869   | calle catedral 2615, Providencia, Santiago, Chile                   |    0.58    |  1.9 m  |   18.3   |  17:11  | [09:00,21:00] |    17:11    |  5.0 m  | 937.2 L | 124.3 kg |   —   |  —  | ✅ |
| 4 | ORD-CL-202612-000103_22242242  0 | calle teatinos 7628, Macul, Santiago, Chile                         |    0.93    |  3.2 m  |   17.5   |  17:20  | [09:00,21:00] |    17:20    |  5.0 m  | 208.2 L |  28.5 kg  |   —   |  —  | ✅ |
| 5 | ORD-CL-202612-000188_146386625   | avenida. libertador bernardo o'higgins 9819, Macul, Santiago, Chile |    0.31    |  1.1 m  |   16.7   |  17:26  | [09:00,21:00] |    17:26    |  5.0 m  | 3169.8 L | 425.3 kg |   —   |  —  | ✅ |
| 6 | ORD-CL-202612-000169_15815165  1 | calle santo domingo 9121, Recoleta, Santiago, Chile                 |    1.21    |  4.5 m  |   16.2   |  17:35  | [17:00,19:00] |    17:35    |  5.0 m  | 682.2 L |  97.5 kg  |   —   |  —  | ✅ |
| 7 | ORD-CL-202612-000107_158151651   | calle santo domingo 9121, Recoleta, Santiago, Chile                 |    0.00    |  0.0 m  |    —    |  17:40  | [19:00,21:00] |    19:00    |  5.0 m  | 2219.2 L | 319.8 kg |  79 m  |  —  | ⏳ |
| 8 | DEPOT_01_BASE                    | Base Depósito                                                      |    1.08    |  3.0 m  |   21.8   |  19:07  |      —      |     —     |   —   |    —    |    —    |   —   |  —  | 🏠 |

### Camión 2 — Detalle de Paradas

| # | Nodo                               | Dirección                                                                | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :--------------------------------- | :------------------------------------------------------------------------ | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :------: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                      | Base Depósito                                                            |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |    —    |    —    |   —   |  —  | 🏠 |
| 1 | ORD-CL-202612-000196_204415159     | calle arturo prat 1187, Ñuñoa, Santiago, Chile                          |    2.64    |  7.6 m  |   21.0   |  09:07  | [09:00,21:00] |    09:07    |  5.0 m  | 1895.3 L | 289.6 kg |   —   |  —  | ✅ |
| 2 | ORD-CL-202612-000197_12172627  6   | calle san diego 9161, Recoleta, Santiago, Chile                           |    2.08    |  6.0 m  |   21.0   |  09:18  | [09:00,11:00] |    09:18    |  5.0 m  | 2704.0 L | 358.4 kg |   —   |  —  | ✅ |
| 3 | ORD-CL-202612-000116_73802946      | avenida. libertador bernardo o'higgins 4192, Providencia, Santiago, Chile |    0.09    |  0.3 m  |   21.0   |  09:23  | [09:00,21:00] |    09:23    |  5.0 m  | 409.0 L |  59.3 kg  |   —   |  —  | ✅ |
| 4 | ORD-CL-202612-000089_172068824     | calle san diego 6019, Macul, Santiago, Chile                              |    0.09    |  0.3 m  |   21.0   |  09:29  | [11:00,13:00] |    11:00    |  5.0 m  | 653.9 L | 144.7 kg |  91 m  |  —  | ⏳ |
| 5 | ORD-CL-202612-000119_6466103  7    | calle san antonio 7911, Santiago, Santiago, Chile                         |    1.00    |  2.6 m  |   23.0   |  11:07  | [11:00,13:00] |    11:07    |  5.0 m  | 728.8 L | 123.9 kg |   —   |  —  | ✅ |
| 6 | ORD-CL-202612-000085_15236104    9 | calle teatinos 975, San Miguel, Santiago, Chile                           |    1.19    |  3.1 m  |   23.0   |  11:15  | [11:00,13:00] |    11:15    |  5.0 m  | 1445.3 L | 206.3 kg |   —   |  —  | ✅ |
| 7 | ORD-CL-202612-000061_180518007     | avenida. manuel montt 5734, Independencia, Santiago, Chile                |    1.66    |  4.3 m  |   23.0   |  11:25  | [09:00,21:00] |    11:25    |  5.0 m  |  25.7 L  |  10.6 kg  |   —   |  —  | ✅ |
| 8 | ORD-CL-202612-000095_140053537     | calle morande 3761, Quinta Normal, Santiago, Chile                        |    2.57    |  6.7 m  |   23.0   |  11:36  | [09:00,21:00] |    11:36    |  5.0 m  |  76.0 L  |  23.9 kg  |   —   |  —  | ✅ |
| 9 | ORD-CL-202612-000027_7499276  7    | calle compania de jesus 5241, Providencia, Santiago, Chile                |    3.74    |  9.8 m  |   23.0   |  11:51  | [11:00,13:00] |    11:51    |  5.0 m  | 1718.7 L | 278.7 kg |   —   |  —  | ✅ |
| 10 | DEPOT_01_BASE                      | Base Depósito                                                            |    0.24    |  0.6 m  |   23.0   |  11:57  |      —      |     —     |   —   |    —    |    —    |   —   |  —  | 🏠 |

### Camión 3 — Detalle de Paradas

| # | Nodo                             | Dirección                                          | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :------------------------------- | :-------------------------------------------------- | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :-----: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                    | Base Depósito                                      |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |   —   |    —    |   —   |  —  | 🏠 |
| 1 | ORD-CL-202612-000088_79249631    | calle monjitas 7974, Recoleta, Santiago, Chile      |    1.12    |  3.2 m  |   21.0   |  09:03  | [09:00,11:00] |    09:03    |  5.0 m  | 940.8 L | 161.2 kg |   —   |  —  | ✅ |
| 2 | ORD-CL-202612-000155_22116046  1 | calle monjitas 4798, Independencia, Santiago, Chile |    0.00    |  0.0 m  |    —    |  09:08  | [09:00,21:00] |    09:08    |  5.0 m  | 400.4 L |  60.1 kg  |   —   |  —  | ✅ |
| 3 | ORD-CL-202612-000184_21805102  0 | calle arturo prat 175, Peñalolén, Santiago, Chile |    1.99    |  5.7 m  |   21.0   |  09:18  | [15:00,17:00] |    15:00    |  5.0 m  | 226.3 L |  29.0 kg  | 341 m |  —  | ⏳ |
| 4 | DEPOT_01_BASE                    | Base Depósito                                      |    1.53    |  3.7 m  |   25.0   |  15:08  |      —      |     —     |   —   |   —   |    —    |   —   |  —  | 🏠 |

---

## Cluster 8

### Resumen Operativo

| Métrica                   | Valor                 |
| :------------------------- | :-------------------- |
| Distancia Total            | 33,224.2 m (33.22 km) |
| Costo Ruta (F = dist × S) | 39,869.03             |
| Hora Salida Depósito      | 09:00                 |
| Hora Retorno Depósito     | 17:27                 |
| Duración Total            | 8h 27min              |
| Vehículos Asignados       | 1                     |

### Restricción 14: Cumplimiento de Ventanas de Tiempo

| Indicador                                 | Valor     |
| :---------------------------------------- | :-------- |
| Clientes atendidos en ventana             | 10/10     |
| Clientes con espera (llegada anticipada)  | 3         |
| Clientes con violación (llegada tardía) | 0         |
| Tiempo de espera acumulado                | 365.0 min |
| Violación acumulada (G)                  | 0.0 min   |

### Desglose de Tiempos por Camión

| Camión | Salida | Retorno | Viaje Efectivo |  Espera  | Servicio | Dist. (km) | Clientes |
| :-----: | :----: | :-----: | :------------: | :-------: | :------: | :--------: | :------: |
|    1    | 09:00 |  17:27  |    92.6 min    | 365.0 min | 50.0 min |  33.22 km  |    10    |

### Camión 1 — Detalle de Paradas

| # | Nodo                               | Dirección                                                    | Dist. (km) | T. Viaje | Vel. (h) | Llegada |    Ventana    | Inic. Serv. | T. Serv | Vol (L) | Peso (kg) | Espera | Viol. | Est |
| :-: | :--------------------------------- | :------------------------------------------------------------ | :--------: | :------: | :------: | :-----: | :-----------: | :---------: | :-----: | :------: | :-------: | :----: | :---: | :-: |
| 0 | DEPOT_01_BASE                      | Base Depósito                                                |     —     |    —    |    —    |  09:00  |      —      |    09:00    |   —   |    —    |    —    |   —   |  —  | 🏠 |
| 1 | ORD-CL-202612-000166_9709625  6    | calle arturo prat 2589, Peñalolén, Santiago, Chile          |    5.14    |  14.7 m  |   21.0   |  09:14  | [09:00,11:00] |    09:14    |  5.0 m  | 1056.7 L | 190.9 kg |   —   |  —  | ✅ |
| 2 | ORD-CL-202612-000183_148999950     | avenida. vicuna mackenna 578, Macul, Santiago, Chile          |    3.68    |  10.5 m  |   21.0   |  09:30  | [09:00,11:00] |    09:30    |  5.0 m  | 685.5 L | 100.8 kg |   —   |  —  | ✅ |
| 3 | ORD-CL-202612-000052_14976779    6 | avenida. irarrazaval 8302, Ñuñoa, Santiago, Chile           |    5.63    |  16.1 m  |   21.0   |  09:51  | [13:00,15:00] |    13:00    |  5.0 m  | 1652.6 L | 231.9 kg | 189 m |  —  | ⏳ |
| 4 | ORD-CL-202612-000179_121067557     | avenida. pedro de valdivia 4433, Peñalolén, Santiago, Chile |    1.55    |  4.0 m  |   23.0   |  13:09  | [09:00,21:00] |    13:09    |  5.0 m  | 716.4 L | 154.0 kg |   —   |  —  | ✅ |
| 5 | ORD-CL-202612-000069_143319312     | avenida. pedro de valdivia 8517, Lo Prado, Santiago, Chile    |    1.91    |  5.0 m  |   23.0   |  13:19  | [09:00,21:00] |    13:19    |  5.0 m  | 400.4 L |  79.2 kg  |   —   |  —  | ✅ |
| 6 | ORD-CL-202612-000112_208275613     | avenida. macul 2508, La Reina, Santiago, Chile                |    0.90    |  2.3 m  |   23.1   |  13:26  | [15:00,17:00] |    15:00    |  5.0 m  | 1409.6 L | 246.7 kg |  94 m  |  —  | ⏳ |
| 7 | ORD-CL-202612-000180_135550036     | avenida. grecia 4946, Santiago, Santiago, Chile               |    2.74    |  6.6 m  |   25.0   |  15:11  | [09:00,21:00] |    15:11    |  5.0 m  | 1259.6 L | 232.8 kg |   —   |  —  | ✅ |
| 8 | ORD-CL-202612-000079_112922605     | avenida. irarrazaval 6780, Macul, Santiago, Chile             |    2.45    |  5.9 m  |   24.7   |  15:22  | [09:00,21:00] |    15:22    |  5.0 m  | 201.8 L |  37.8 kg  |   —   |  —  | ✅ |
| 9 | ORD-CL-202612-000148_175474353     | avenida. irarrazaval 2033, Maipú, Santiago, Chile            |    3.93    |  9.8 m  |   24.0   |  15:37  | [17:00,19:00] |    17:00    |  5.0 m  |  75.1 L  |  20.7 kg  |  83 m  |  —  | ⏳ |
| 10 | ORD-CL-202612-000094_84473640      | avenida. irarrazaval 640, Lo Prado, Santiago, Chile           |    1.51    |  4.8 m  |   18.8   |  17:09  | [09:00,21:00] |    17:09    |  5.0 m  | 745.5 L | 121.3 kg |   —   |  —  | ✅ |
| 11 | DEPOT_01_BASE                      | Base Depósito                                                |    3.78    |  12.8 m  |   17.7   |  17:27  |      —      |     —     |   —   |    —    |    —    |   —   |  —  | 🏠 |

---
