# Reporte Gestión Flota Inter-Cluster - Genético PyMoo - 2026-12-03

### KPIs Globales de Utilización
| Métrica | Valor |
| :--- | :--- |
| Total Clientes Atendidos | 85 |
| Total Nodos con Violación (Hard Constr.) | 0 |
| Distancia Global Consolidada | 669,038.1 m (669.04 km) |
| Capacidad Flota Fija | 20 Camiones Homogéneos |
| Flota Utilizada | 17 Camiones (85.0%) |
| Rutas Tercerizadas (Exceso Flota) | 0 Subrutas |

---

## Vehículo Físico GLOBAL 1

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 3 | K11 | Mañana | 09:00 | 09:42 | 32.0 m | 0.0 m | 10.0 m | 11.2 km | 2 |
| 3 | K12 | Tarde | 15:00 | 15:44 | 29.3 m | 0.0 m | 15.0 m | 11.9 km | 3 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 3 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 09:00 | — | 09:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 3 | K11 | ORD-CL-202612-000197_12172627  6 | calle san diego 9161, Recoleta, Santiago, Chile | (-33.4441, -70.6517) | 4.92 km | 09:14 | [09:00, 11:00] | 09:14 | 5.0 m | 2704.0 | 358.4 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 3 | K11 | ORD-CL-202612-000088_79249631 | calle monjitas 7974, Recoleta, Santiago, Chile | (-33.4359, -70.6420) | 1.68 km | 09:23 | [09:00, 11:00] | 09:23 | 5.0 m | 940.8 | 161.2 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 3 | 3 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 4.62 km | 09:42 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |
| 4 | 3 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 15:00 | — | 15:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 5 | 3 | K12 | ORD-CL-202612-000160_108505650 | avenida. providencia 178, Providencia, Santiago, Chile | (-33.4283, -70.6191) | 6.08 km | 15:14 | [15:00, 17:00] | 15:14 | 5.0 m | 245.4 | 52.4 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 6 | 3 | K12 | ORD-CL-202612-000209_163993586 | avenida. providencia 4275, Las Condes, Santiago, Chile | (-33.4283, -70.6191) | 0.00 km | 15:19 | [15:00, 17:00] | 15:19 | 5.0 m | 276.9 | 36.7 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 7 | 3 | K12 | ORD-CL-202612-000013_9933788  8 | avenida. manuel montt 401, Vitacura, Santiago, Chile | (-33.4319, -70.6183) | 0.47 km | 15:25 | [09:00, 21:00] | 15:25 | 5.0 m | 262.6 | 34.5 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 8 | 3 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 5.37 km | 15:44 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 2

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 3 | K11 | Mañana | 09:00 | 11:25 | 40.3 m | 85.6 m | 20.0 m | 14.7 km | 4 |
| 0 | K12 | Tarde | 15:00 | 16:10 | 65.3 m | 0.0 m | 5.0 m | 26.3 km | 1 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 3 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 09:00 | — | 09:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 3 | K11 | ORD-CL-202612-000166_9709625  6 | calle arturo prat 2589, Peñalolén, Santiago, Chile | (-33.4783, -70.6465) | 2.80 km | 09:08 | [09:00, 11:00] | 09:08 | 5.0 m | 1056.7 | 190.9 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 3 | K11 | ORD-CL-202612-000116_73802946 | avenida. libertador bernardo o'higgins 4192, Providencia, Santiago, Chile | (-33.4441, -70.6511) | 4.25 km | 09:25 | [09:00, 21:00] | 09:25 | 5.0 m | 409.0 | 59.3 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 3 | 3 | K11 | ORD-CL-202612-000085_15236104    9 | calle teatinos 975, San Miguel, Santiago, Chile | (-33.4324, -70.6557) | 1.48 km | 09:34 | [11:00, 13:00] | 11:00 | 5.0 m | 1445.3 | 206.3 | 86 m | 0.0 | 0.0 | 0 m | ⏳ |
| 4 | 3 | K11 | ORD-CL-202612-000155_22116046  1 | calle monjitas 4798, Independencia, Santiago, Chile | (-33.4359, -70.6420) | 1.50 km | 11:08 | [09:00, 21:00] | 11:08 | 5.0 m | 400.4 | 60.1 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 5 | 3 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 4.62 km | 11:25 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |
| 6 | 0 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 15:00 | — | 15:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 7 | 0 | K12 | ORD-CL-202612-000020_10263868  8 | avenida. manuel montt 3031, Maipú, Santiago, Chile | (-33.5616, -70.5632) | 13.07 km | 15:31 | [15:00, 17:00] | 15:31 | 5.0 m | 3905.5 | 441.5 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 8 | 0 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 13.22 km | 16:10 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 3

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2 | K11 | Mañana | 09:00 | 11:30 | 123.3 m | 7.3 m | 20.0 m | 45.2 km | 4 |
| 4 | K12 | Tarde | 15:00 | 16:18 | 68.4 m | 0.0 m | 10.0 m | 27.1 km | 2 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 2 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 09:00 | — | 09:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 2 | K11 | ORD-CL-202612-000141_140162225 | calle san antonio 2631, La Reina, Santiago, Chile | (-33.5736, -70.8152) | 20.27 km | 09:57 | [09:00, 21:00] | 09:57 | 5.0 m | 84.7 | 24.3 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 2 | K11 | ORD-CL-202612-000111_5802113  4 | avenida. las condes 599, San Miguel, Santiago, Chile | (-33.5187, -70.7654) | 6.01 km | 10:18 | [09:00, 21:00] | 10:18 | 5.0 m | 2018.8 | 255.6 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 3 | 2 | K11 | ORD-CL-202612-000022_169468917 | avenida. pajaritos 7516, Maipú, Santiago, Chile | (-33.4719, -70.7376) | 6.63 km | 10:41 | [09:00, 21:00] | 10:41 | 5.0 m | 929.9 | 130.3 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 4 | 2 | K11 | ORD-CL-202612-000087_17107764  6 | avenida. pajaritos 5796, Independencia, Santiago, Chile | (-33.4603, -70.7147) | 2.46 km | 10:52 | [11:00, 13:00] | 11:00 | 5.0 m | 237.6 | 62.3 | 7 m | 0.0 | 0.0 | 0 m | ⏳ |
| 5 | 2 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 9.81 km | 11:30 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |
| 6 | 4 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 15:00 | — | 15:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 7 | 4 | K12 | ORD-CL-202612-000126_22556099  9 | avenida. kennedy 6395, Recoleta, Santiago, Chile | (-33.4093, -70.6048) | 8.50 km | 15:20 | [09:00, 21:00] | 15:20 | 5.0 m | 866.8 | 120.4 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 8 | 4 | K12 | ORD-CL-202612-000066_96822760 | calle teatinos 5180, Vitacura, Santiago, Chile | (-33.3818, -70.5658) | 5.41 km | 15:38 | [09:00, 21:00] | 15:38 | 5.0 m | 1260.2 | 220.9 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 9 | 4 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 13.23 km | 16:18 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 4

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | K11 | Mañana | 09:00 | 11:58 | 82.7 m | 86.3 m | 10.0 m | 30.6 km | 2 |
| 2 | K12 | Tarde | 15:00 | 16:21 | 56.7 m | 0.0 m | 25.0 m | 22.6 km | 5 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 1 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 09:00 | — | 09:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 1 | K11 | ORD-CL-202612-000091_79104971 | avenida. independencia 4637, Providencia, Santiago, Chile | (-33.3855, -70.6773) | 11.81 km | 09:33 | [11:00, 13:00] | 11:00 | 5.0 m | 848.6 | 167.5 | 86 m | 0.0 | 0.0 | 0 m | ⏳ |
| 2 | 1 | K11 | ORD-CL-202612-000044_145036177 | avenida. tobalaba 5892, Quinta Normal, Santiago, Chile | (-33.4278, -70.7083) | 7.55 km | 11:24 | [09:00, 21:00] | 11:24 | 5.0 m | 855.7 | 127.7 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 3 | 1 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 11.23 km | 11:58 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |
| 4 | 2 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 15:00 | — | 15:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 5 | 2 | K12 | ORD-CL-202612-000150_10411606  1 | calle santo domingo 6777, Vitacura, Santiago, Chile | (-33.4388, -70.6858) | 8.81 km | 15:21 | [09:00, 21:00] | 15:21 | 5.0 m | 1086.9 | 173.4 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 6 | 2 | K12 | ORD-CL-202612-000071_212196364 | avenida. pajaritos 3626, Estación Central, Santiago, Chile | (-33.4586, -70.7132) | 4.08 km | 15:36 | [15:00, 17:00] | 15:36 | 5.0 m | 1006.0 | 197.4 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 7 | 2 | K12 | ORD-CL-202612-000015_93475810 | calle morande 6751, Estación Central, Santiago, Chile | (-33.4594, -70.6985) | 1.65 km | 15:45 | [09:00, 21:00] | 15:45 | 5.0 m | 266.4 | 74.4 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 8 | 2 | K12 | ORD-CL-202612-000121_102139227 | calle bandera 3131, Estación Central, Santiago, Chile | (-33.4594, -70.6985) | 0.00 km | 15:50 | [09:00, 21:00] | 15:50 | 5.0 m | 1152.4 | 159.0 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 9 | 2 | K12 | ORD-CL-202612-000143_14358394    1 | avenida. matta 9543, Estación Central, Santiago, Chile | (-33.4594, -70.6985) | 0.00 km | 15:55 | [09:00, 21:00] | 15:55 | 5.0 m | 74.2 | 18.0 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 10 | 2 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 8.10 km | 16:21 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 5

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 5 | K11 | Mañana | 09:00 | 13:25 | 42.5 m | 217.7 m | 5.0 m | 15.5 km | 1 |
| 0 | K12 | Tarde | 15:00 | 16:46 | 86.6 m | 0.0 m | 20.0 m | 33.1 km | 4 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 5 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 09:00 | — | 09:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 5 | K11 | ORD-CL-202612-000049_111101253 | avenida. grecia 7712, Recoleta, Santiago, Chile | (-33.4742, -70.5504) | 7.80 km | 09:22 | [13:00, 15:00] | 13:00 | 5.0 m | 3858.7 | 488.3 | 218 m | 0.0 | 0.0 | 0 m | ⏳ |
| 2 | 5 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 7.74 km | 13:25 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |
| 3 | 0 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 15:00 | — | 15:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 4 | 0 | K12 | ORD-CL-202612-000032_83953104 | gran avenida jose miguel carrera 1084, La Florida, Santiago, Chile | (-33.5504, -70.6006) | 9.65 km | 15:23 | [09:00, 21:00] | 15:23 | 5.0 m | 2217.2 | 261.7 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 5 | 0 | K12 | ORD-CL-202612-000163_215462173 | avenida. pedro de valdivia 8264, Puente Alto, Santiago, Chile | (-33.5821, -70.5901) | 4.59 km | 15:39 | [15:00, 17:00] | 15:39 | 5.0 m | 24.8 | 9.3 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 6 | 0 | K12 | ORD-CL-202612-000010_62835725 | avenida americo vespucio 2389, Independencia, Santiago, Chile | (-33.5399, -70.6512) | 9.35 km | 16:09 | [09:00, 21:00] | 16:09 | 5.0 m | 894.1 | 164.7 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 7 | 0 | K12 | ORD-CL-202612-000122_51491954 | avenida. santa rosa 5626, San Miguel, Santiago, Chile | (-33.5183, -70.6367) | 3.50 km | 16:23 | [15:00, 17:00] | 16:23 | 5.0 m | 322.7 | 73.9 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 8 | 0 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 6.04 km | 16:46 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 6

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 4 | K11 | Mañana | 09:00 | 13:44 | 75.0 m | 194.8 m | 15.0 m | 27.4 km | 3 |
| 5 | K12 | Tarde | 15:00 | 17:15 | 47.2 m | 73.6 m | 15.0 m | 18.2 km | 3 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 4 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 09:00 | — | 09:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 4 | K11 | ORD-CL-202612-000108_9272430  1 | avenida kennedy 3695, La Reina, Santiago, Chile | (-33.3927, -70.5554) | 13.37 km | 09:38 | [09:00, 11:00] | 09:38 | 5.0 m | 230.5 | 31.4 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 4 | K11 | ORD-CL-202612-000009_8823811  3 | avenida. kennedy 7331, Independencia, Santiago, Chile | (-33.3941, -70.5593) | 0.72 km | 09:45 | [13:00, 15:00] | 13:00 | 5.0 m | 2219.0 | 256.8 | 195 m | 0.0 | 0.0 | 0 m | ⏳ |
| 3 | 4 | K11 | ORD-CL-202612-000021_217856993 | avenida. apoquindo 4280, Independencia, Santiago, Chile | (-33.4145, -70.5861) | 4.07 km | 13:15 | [13:00, 15:00] | 13:15 | 5.0 m | 482.8 | 56.6 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 4 | 4 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 9.24 km | 13:44 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |
| 5 | 5 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 15:00 | — | 15:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 6 | 5 | K12 | ORD-CL-202612-000039_64956582 | avenida. tobalaba 9986, Las Condes, Santiago, Chile | (-33.4298, -70.5862) | 7.57 km | 15:18 | [09:00, 21:00] | 15:18 | 5.0 m | 3005.7 | 379.0 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 7 | 5 | K12 | ORD-CL-202612-000079_112922605 | avenida. irarrazaval 6780, Macul, Santiago, Chile | (-33.4534, -70.5709) | 3.29 km | 15:31 | [09:00, 21:00] | 15:31 | 5.0 m | 201.8 | 37.8 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 8 | 5 | K12 | ORD-CL-202612-000148_175474353 | avenida. irarrazaval 2033, Maipú, Santiago, Chile | (-33.4537, -70.6099) | 3.93 km | 15:46 | [17:00, 19:00] | 17:00 | 5.0 m | 75.1 | 20.7 | 74 m | 0.0 | 0.0 | 0 m | ⏳ |
| 9 | 5 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 3.39 km | 17:15 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 7

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | K11 | Mañana | 09:00 | 14:18 | 118.7 m | 179.6 m | 20.0 m | 44.1 km | 4 |
| 3 | K12 | Tarde | 15:00 | 19:29 | 65.8 m | 183.8 m | 20.0 m | 22.6 km | 4 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 0 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 09:00 | — | 09:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 0 | K11 | ORD-CL-202612-000082_198569524 | avenida. departamental 2287, La Florida, Santiago, Chile | (-33.5107, -70.5799) | 7.17 km | 09:20 | [09:00, 11:00] | 09:20 | 5.0 m | 481.1 | 96.3 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 0 | K11 | ORD-CL-202612-000222_64382296 | calle merced 6576, Puente Alto, Santiago, Chile | (-33.6067, -70.5774) | 12.22 km | 10:00 | [13:00, 15:00] | 13:00 | 5.0 m | 1396.1 | 158.3 | 180 m | 0.0 | 0.0 | 0 m | ⏳ |
| 3 | 0 | K11 | ORD-CL-202612-000178_6756635  4 | calle bandera 9187, Vitacura, Santiago, Chile | (-33.5440, -70.6450) | 12.27 km | 13:37 | [09:00, 21:00] | 13:37 | 5.0 m | 363.4 | 89.2 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 4 | 0 | K11 | ORD-CL-202612-000096_52601895 | calle arturo prat 4852, Independencia, Santiago, Chile | (-33.5461, -70.6607) | 1.88 km | 13:46 | [09:00, 21:00] | 13:46 | 5.0 m | 1136.0 | 188.5 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 5 | 0 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 10.59 km | 14:18 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |
| 6 | 3 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 15:00 | — | 15:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 7 | 3 | K12 | ORD-CL-202612-000170_137256512 | calle san antonio 2929, Santiago, Santiago, Chile | (-33.4376, -70.6484) | 5.08 km | 15:12 | [09:00, 21:00] | 15:12 | 5.0 m | 776.8 | 140.6 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 8 | 3 | K12 | ORD-CL-202612-000026_175731263 | calle san antonio 1509, Providencia, Santiago, Chile | (-33.4376, -70.6484) | 0.00 km | 15:17 | [17:00, 19:00] | 17:00 | 5.0 m | 1731.7 | 205.5 | 103 m | 0.0 | 0.0 | 0 m | ⏳ |
| 9 | 3 | K12 | ORD-CL-202612-000061_180518007 | avenida. manuel montt 5734, Independencia, Santiago, Chile | (-33.4255, -70.6662) | 2.85 km | 17:14 | [09:00, 21:00] | 17:14 | 5.0 m | 25.7 | 10.6 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 10 | 3 | K12 | ORD-CL-202612-000118_65054485 | avenida la florida 3026, Santiago, Santiago, Chile | (-33.4000, -70.6268) | 5.74 km | 17:38 | [19:00, 21:00] | 19:00 | 5.0 m | 1214.1 | 215.7 | 81 m | 0.0 | 0.0 | 0 m | ⏳ |
| 11 | 3 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 8.95 km | 19:29 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 8

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 5 | K11 | Mañana | 09:00 | 15:13 | 27.2 m | 330.9 m | 15.0 m | 10.1 km | 3 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 5 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 09:00 | — | 09:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 5 | K11 | ORD-CL-202612-000183_148999950 | avenida. vicuna mackenna 578, Macul, Santiago, Chile | (-33.4946, -70.6166) | 2.84 km | 09:08 | [09:00, 11:00] | 09:08 | 5.0 m | 685.5 | 100.8 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 5 | K11 | ORD-CL-202612-000069_143319312 | avenida. pedro de valdivia 8517, Lo Prado, Santiago, Chile | (-33.4800, -70.6059) | 2.94 km | 09:21 | [09:00, 21:00] | 09:21 | 5.0 m | 400.4 | 79.2 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 3 | 5 | K11 | ORD-CL-202612-000112_208275613 | avenida. macul 2508, La Reina, Santiago, Chile | (-33.4776, -70.5988) | 0.90 km | 09:29 | [15:00, 17:00] | 15:00 | 5.0 m | 1409.6 | 246.7 | 331 m | 0.0 | 0.0 | 0 m | ⏳ |
| 4 | 5 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 3.38 km | 15:13 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 9

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | K11 | Mañana | 09:00 | 19:50 | 169.3 m | 446.6 m | 35.0 m | 61.6 km | 7 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 0 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 09:00 | — | 09:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 0 | K11 | ORD-CL-202612-000144_210301989 | avenida vitacura 713, Quinta Normal, Santiago, Chile | (-33.5774, -70.6537) | 14.10 km | 09:40 | [09:00, 11:00] | 09:40 | 5.0 m | 196.0 | 24.5 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 0 | K11 | ORD-CL-202612-000133_55387737 | calle teatinos 4659, La Florida, Santiago, Chile | (-33.5342, -70.5835) | 11.34 km | 10:17 | [11:00, 13:00] | 11:00 | 5.0 m | 379.5 | 55.8 | 43 m | 0.0 | 0.0 | 0 m | ⏳ |
| 3 | 0 | K11 | ORD-CL-202612-000187_5138738  6 | avenida. independencia 4810, Puente Alto, Santiago, Chile | (-33.6024, -70.5818) | 9.10 km | 11:28 | [13:00, 15:00] | 13:00 | 5.0 m | 222.3 | 37.4 | 91 m | 0.0 | 0.0 | 0 m | ⏳ |
| 4 | 0 | K11 | ORD-CL-202612-000006_207417262 | calle catedral 9181, Puente Alto, Santiago, Chile | (-33.6042, -70.5551) | 3.19 km | 13:13 | [17:00, 19:00] | 17:00 | 5.0 m | 639.5 | 113.7 | 227 m | 0.0 | 0.0 | 0 m | ⏳ |
| 5 | 0 | K11 | ORD-CL-202612-000024_53351852 | avenida. apoquindo 5706, La Florida, Santiago, Chile | (-33.5531, -70.6104) | 9.14 km | 17:34 | [19:00, 21:00] | 19:00 | 5.0 m | 168.8 | 34.9 | 86 m | 0.0 | 0.0 | 0 m | ⏳ |
| 6 | 0 | K11 | ORD-CL-202612-000135_153012165 | avenida. vicuna mackenna 8405, Peñalolén, Santiago, Chile | (-33.5345, -70.5939) | 3.53 km | 19:14 | [19:00, 21:00] | 19:14 | 5.0 m | 644.2 | 128.1 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 7 | 0 | K11 | ORD-CL-202612-000139_162296701 | avenida. pajaritos 9174, La Florida, Santiago, Chile | (-33.5203, -70.5784) | 3.20 km | 19:27 | [09:00, 21:00] | 19:27 | 5.0 m | 614.9 | 114.0 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 8 | 0 | K11 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 8.01 km | 19:50 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 10

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 3 | K21 | Mañana | 11:00 | 11:43 | 28.6 m | 0.0 m | 15.0 m | 11.0 km | 3 |
| 5 | K22 | Tarde | 17:00 | 17:47 | 37.3 m | 0.0 m | 10.0 m | 10.8 km | 2 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 3 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 11:00 | — | 11:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 3 | K21 | ORD-CL-202612-000089_172068824 | calle san diego 6019, Macul, Santiago, Chile | (-33.4441, -70.6517) | 4.92 km | 11:12 | [11:00, 13:00] | 11:12 | 5.0 m | 653.9 | 144.7 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 3 | K21 | ORD-CL-202612-000027_7499276  7 | calle compania de jesus 5241, Providencia, Santiago, Chile | (-33.4386, -70.6517) | 0.66 km | 11:19 | [11:00, 13:00] | 11:19 | 5.0 m | 1718.7 | 278.7 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 3 | 3 | K21 | ORD-CL-202612-000119_6466103  7 | calle san antonio 7911, Santiago, Santiago, Chile | (-33.4376, -70.6484) | 0.38 km | 11:25 | [11:00, 13:00] | 11:25 | 5.0 m | 728.8 | 123.9 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 4 | 3 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 4.99 km | 11:43 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |
| 5 | 5 | K22 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 17:00 | — | 17:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 6 | 5 | K22 | ORD-CL-202612-000179_121067557 | avenida. pedro de valdivia 4433, Peñalolén, Santiago, Chile | (-33.4638, -70.6065) | 2.87 km | 17:09 | [09:00, 21:00] | 17:09 | 5.0 m | 716.4 | 154.0 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 7 | 5 | K22 | ORD-CL-202612-000180_135550036 | avenida. grecia 4946, Santiago, Santiago, Chile | (-33.4676, -70.5801) | 2.97 km | 17:24 | [09:00, 21:00] | 17:24 | 5.0 m | 1259.6 | 232.8 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 8 | 5 | K22 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 4.98 km | 17:47 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 11

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 5 | K21 | Mañana | 11:00 | 13:13 | 32.7 m | 86.0 m | 15.0 m | 12.5 km | 3 |
| 0 | K22 | Tarde | 17:00 | 18:02 | 57.3 m | 0.0 m | 5.0 m | 16.7 km | 1 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 5 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 11:00 | — | 11:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 5 | K21 | ORD-CL-202612-000094_84473640 | avenida. irarrazaval 640, Lo Prado, Santiago, Chile | (-33.4529, -70.6238) | 2.78 km | 11:07 | [09:00, 21:00] | 11:07 | 5.0 m | 745.5 | 121.3 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 5 | K21 | ORD-CL-202612-000025_224766177 | calle teatinos 6266, Providencia, Santiago, Chile | (-33.4324, -70.6098) | 3.63 km | 11:21 | [09:00, 21:00] | 11:21 | 5.0 m | 1343.6 | 132.4 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 3 | 5 | K21 | ORD-CL-202612-000052_14976779    6 | avenida. irarrazaval 8302, Ñuñoa, Santiago, Chile | (-33.4536, -70.6093) | 2.78 km | 11:33 | [13:00, 15:00] | 13:00 | 5.0 m | 1652.6 | 231.9 | 86 m | 0.0 | 0.0 | 0 m | ⏳ |
| 4 | 5 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 3.34 km | 13:13 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |
| 5 | 0 | K22 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 17:00 | — | 17:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 6 | 0 | K22 | ORD-CL-202612-000002_173134031 | avenida. la florida 7678, Macul, Santiago, Chile | (-33.5231, -70.5782) | 8.29 km | 17:26 | [09:00, 21:00] | 17:26 | 5.0 m | 4239.4 | 505.6 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 7 | 0 | K22 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 8.39 km | 18:02 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 12

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2 | K21 | Mañana | 11:00 | 13:35 | 61.1 m | 89.5 m | 5.0 m | 23.4 km | 1 |
| 3 | K22 | Tarde | 17:00 | 18:25 | 65.1 m | 0.0 m | 20.0 m | 18.1 km | 4 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 2 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 11:00 | — | 11:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 2 | K21 | ORD-CL-202612-000011_18195149  6 | avenida. pajaritos 5435, Ñuñoa, Santiago, Chile | (-33.4732, -70.7379) | 11.70 km | 11:30 | [13:00, 15:00] | 13:00 | 5.0 m | 4252.7 | 550.2 | 89 m | 0.0 | 0.0 | 0 m | ⏳ |
| 2 | 2 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 11.71 km | 13:35 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |
| 3 | 3 | K22 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 17:00 | — | 17:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 4 | 3 | K22 | ORD-CL-202612-000196_204415159 | calle arturo prat 1187, Ñuñoa, Santiago, Chile | (-33.4595, -70.6472) | 3.25 km | 17:10 | [09:00, 21:00] | 17:10 | 5.0 m | 1895.3 | 289.6 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 5 | 3 | K22 | ORD-CL-202612-000093_134538869 | calle catedral 2615, Providencia, Santiago, Chile | (-33.4376, -70.6541) | 2.80 km | 17:24 | [09:00, 21:00] | 17:24 | 5.0 m | 937.2 | 124.3 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 6 | 3 | K22 | ORD-CL-202612-000169_15815165  1 | calle santo domingo 9121, Recoleta, Santiago, Chile | (-33.4370, -70.6586) | 0.52 km | 17:31 | [17:00, 19:00] | 17:31 | 5.0 m | 682.2 | 97.5 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 7 | 3 | K22 | ORD-CL-202612-000095_140053537 | calle morande 3761, Quinta Normal, Santiago, Chile | (-33.4346, -70.6826) | 2.66 km | 17:46 | [09:00, 21:00] | 17:46 | 5.0 m | 76.0 | 23.9 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 8 | 3 | K22 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 8.92 km | 18:25 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 13

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 3 | K21 | Mañana | 11:00 | 15:15 | 27.7 m | 213.2 m | 15.0 m | 11.0 km | 3 |
| 2 | K22 | Tarde | 17:00 | 18:50 | 105.5 m | 0.0 m | 5.0 m | 30.5 km | 1 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 3 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 11:00 | — | 11:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 3 | K21 | ORD-CL-202612-000188_146386625 | avenida. libertador bernardo o'higgins 9819, Macul, Santiago, Chile | (-33.4451, -70.6574) | 5.42 km | 11:14 | [09:00, 21:00] | 11:14 | 5.0 m | 3169.8 | 425.3 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 3 | K21 | ORD-CL-202612-000103_22242242  0 | calle teatinos 7628, Macul, Santiago, Chile | (-33.4447, -70.6542) | 0.37 km | 11:20 | [09:00, 21:00] | 11:20 | 5.0 m | 208.2 | 28.5 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 3 | 3 | K21 | ORD-CL-202612-000184_21805102  0 | calle arturo prat 175, Peñalolén, Santiago, Chile | (-33.4464, -70.6498) | 0.65 km | 11:26 | [15:00, 17:00] | 15:00 | 5.0 m | 226.3 | 29.0 | 213 m | 0.0 | 0.0 | 0 m | ⏳ |
| 4 | 3 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 4.57 km | 15:15 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |
| 5 | 2 | K22 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 17:00 | — | 17:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 6 | 2 | K22 | ORD-CL-202612-000208_107728946 | avenida. pajaritos 1016, San Miguel, Santiago, Chile | (-33.5178, -70.7575) | 15.12 km | 17:47 | [09:00, 21:00] | 17:47 | 5.0 m | 4894.5 | 609.0 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 7 | 2 | K22 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 15.41 km | 18:50 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 14

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | K21 | Mañana | 11:00 | 15:27 | 50.3 m | 202.4 m | 15.0 m | 20.0 km | 3 |
| 3 | K22 | Tarde | 17:00 | 19:21 | 35.5 m | 101.1 m | 5.0 m | 12.0 km | 1 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 0 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 11:00 | — | 11:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 0 | K21 | ORD-CL-202612-000060_199941644 | avenida. macul 7795, Maipú, Santiago, Chile | (-33.5085, -70.5618) | 8.62 km | 11:22 | [09:00, 21:00] | 11:22 | 5.0 m | 577.7 | 83.3 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 0 | K21 | ORD-CL-202612-000019_156820915 | avenida. tobalaba 3402, Macul, Santiago, Chile | (-33.5193, -70.5577) | 1.35 km | 11:31 | [09:00, 21:00] | 11:31 | 5.0 m | 2163.4 | 238.1 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 3 | 0 | K21 | ORD-CL-202612-000092_162059956 | avenida. providencia 4727, La Florida, Santiago, Chile | (-33.5150, -70.5605) | 0.62 km | 11:37 | [15:00, 17:00] | 15:00 | 5.0 m | 892.8 | 131.5 | 202 m | 0.0 | 0.0 | 0 m | ⏳ |
| 4 | 0 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 9.44 km | 15:27 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |
| 5 | 3 | K22 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 17:00 | — | 17:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 6 | 3 | K22 | ORD-CL-202612-000107_158151651 | calle santo domingo 9121, Recoleta, Santiago, Chile | (-33.4370, -70.6586) | 5.97 km | 17:18 | [19:00, 21:00] | 19:00 | 5.0 m | 2219.2 | 319.8 | 101 m | 0.0 | 0.0 | 0 m | ⏳ |
| 7 | 3 | K22 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 6.06 km | 19:21 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 15

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 4 | K21 | Mañana | 11:00 | 17:39 | 105.8 m | 268.7 m | 25.0 m | 38.3 km | 5 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 4 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 11:00 | — | 11:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 4 | K21 | ORD-CL-202612-000210_11704104  4 | calle estado 8684, Vitacura, Santiago, Chile | (-33.3818, -70.5658) | 13.32 km | 11:34 | [11:00, 13:00] | 11:34 | 5.0 m | 1707.5 | 294.1 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 4 | K21 | ORD-CL-202612-000195_16543282  2 | avenida. las condes 180, Independencia, Santiago, Chile | (-33.3714, -70.5091) | 6.10 km | 11:55 | [13:00, 15:00] | 13:00 | 5.0 m | 1450.2 | 222.2 | 64 m | 0.0 | 0.0 | 0 m | ⏳ |
| 3 | 4 | K21 | ORD-CL-202612-000140_98108348 | avenida. apoquindo 8832, Lo Prado, Santiago, Chile | (-33.4081, -70.5492) | 6.63 km | 13:22 | [09:00, 21:00] | 13:22 | 5.0 m | 74.7 | 16.7 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 4 | 4 | K21 | ORD-CL-202612-000045_74983175 | avenida. apoquindo 7097, Vitacura, Santiago, Chile | (-33.4081, -70.5492) | 0.00 km | 13:27 | [15:00, 17:00] | 15:00 | 5.0 m | 31.4 | 10.2 | 93 m | 0.0 | 0.0 | 0 m | ⏳ |
| 5 | 4 | K21 | ORD-CL-202612-000017_149456125 | avenida. matta 4672, Las Condes, Santiago, Chile | (-33.4144, -70.5570) | 1.39 km | 15:08 | [17:00, 19:00] | 17:00 | 5.0 m | 22.7 | 6.4 | 112 m | 0.0 | 0.0 | 0 m | ⏳ |
| 6 | 4 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 10.83 km | 17:39 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 16

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | K21 | Mañana | 11:00 | 19:33 | 40.2 m | 463.3 m | 10.0 m | 15.5 km | 2 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 0 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 11:00 | — | 11:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 0 | K21 | ORD-CL-202612-000031_14317726  4 | avenida. la florida 1002, Peñalolén, Santiago, Chile | (-33.5101, -70.5885) | 6.38 km | 11:16 | [19:00, 21:00] | 19:00 | 5.0 m | 2786.0 | 391.8 | 463 m | 0.0 | 0.0 | 0 m | ⏳ |
| 2 | 0 | K21 | ORD-CL-202612-000177_19337908  6 | avenida. la florida 2133, Macul, Santiago, Chile | (-33.5195, -70.5807) | 1.36 km | 19:08 | [09:00, 21:00] | 19:08 | 5.0 m | 905.8 | 185.3 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 3 | 0 | K21 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 7.75 km | 19:33 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
## Vehículo Físico GLOBAL 17

### Tiempos de Turnos
| Cluster | Clase K | Turno | Salida CD | Retorno CD | Viaje Efectivo | Espera | Serv. | Dist. | Clientes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | K12 | Tarde | 15:00 | 19:49 | 65.6 m | 203.7 m | 20.0 m | 26.8 km | 4 |

### Desglose Completo de Paradas
| # | Cluster visitado | clase k | Nodo | dirección | coordenadas | Distancia recorrida | Hora de llegada | Ventana | Inicio de servicio | Tiempo de servicio | vol (L) | peso (kg) | tiempo de espera | violación en vol | violación en peso | violación en ventana | Est |
| :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 1 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 0.00 km | 15:00 | — | 15:00 | — | — | — | — | 0.0 | 0.0 | — | 🚗 |
| 1 | 1 | K12 | ORD-CL-202612-000004_183059669 | calle san antonio 8832, Lo Prado, Santiago, Chile | (-33.4270, -70.7253) | 13.04 km | 15:31 | [09:00, 21:00] | 15:31 | 5.0 m | 2514.1 | 317.4 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 2 | 1 | K12 | ORD-CL-202612-000062_7640094    3 | calle san antonio 9379, Lo Prado, Santiago, Chile | (-33.4270, -70.7253) | 0.00 km | 15:36 | [19:00, 21:00] | 19:00 | 5.0 m | 634.5 | 101.6 | 204 m | 0.0 | 0.0 | 0 m | ⏳ |
| 3 | 1 | K12 | ORD-CL-202612-000115_198154752 | calle san antonio 6514, La Reina, Santiago, Chile | (-33.4273, -70.7239) | 0.13 km | 19:05 | [19:00, 21:00] | 19:05 | 5.0 m | 371.8 | 100.9 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 4 | 1 | K12 | ORD-CL-202612-000055_203179717 | avenida. mapocho 6648, Macul, Santiago, Chile | (-33.4238, -70.7263) | 0.59 km | 19:11 | [09:00, 21:00] | 19:11 | 5.0 m | 224.5 | 56.1 | 0 m | 0.0 | 0.0 | 0 m | ✅ |
| 5 | 1 | K12 | DEPOT_01_BASE | Base Depósito | (-33.4489, -70.6693) | 13.07 km | 19:49 | — | — | — | — | — | — | 0.0 | 0.0 | — | 🏠 |

---
