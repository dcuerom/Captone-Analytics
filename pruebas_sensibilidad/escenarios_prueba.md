# Escenarios de Evaluación para Pruebas de Sensibilidad

Este documento detalla las configuraciones específicas aplicadas a cuatro días distintos del conjunto de datos de validación (`df_despacho.csv`). Estas configuraciones fueron diseñadas para evaluar el comportamiento, la factibilidad y la robustez del algoritmo genético bajo diferentes situaciones de estrés logístico y distribución temporal de las restricciones de ventanas de tiempo.

Todas las ventanas de tiempo rigurosas tienen una duración de 2 horas (120 minutos). Adicionalmente, los clientes sin ventana específica (`Tipo_vivienda = False`) tienen una ventana de operación completa desde las 9:00 hasta las 21:00 (540 a 1260 minutos desde las 00:00).

---

## 1. Escenario 1: Alta Demanda Matutina Restringida (Día 04)

**Fecha Objetivo:** 2026-12-04
**Objetivo de Prueba:** Evaluar la capacidad de asignación y ruteo del algoritmo cuando la operación exige una fuerte concentración de entregas en los primeros bloques horarios del día.

**Configuración:**
- Se saturaron las ventanas correspondientes a los tres primeros bloques de la mañana.
- Exactamente **20 clientes** fueron asignados a cada uno de los siguientes intervalos:
  - 09:00 a 11:00 (540 - 660)
  - 11:00 a 13:00 (660 - 780)
  - 13:00 a 15:00 (780 - 900)
- El resto de los clientes del día operaron sin restricciones ajustadas, asumiendo la ventana de la jornada completa (09:00 a 21:00).

---

## 2. Escenario 2: Distribución Totalmente Uniforme Diurna (Día 05)

**Fecha Objetivo:** 2026-12-05
**Objetivo de Prueba:** Analizar la carga computacional y la factibilidad del modelo cuando todos los clientes exigen cumplimiento estricto de intervalos cerrados y la demanda horaria es regular durante toda la jornada.

**Configuración:**
- El **100%** de los clientes del día tienen restricción de ventana de tiempo (`Tipo_vivienda = True`).
- Se aplicó una dispersión uniforme entre todos los clientes para agruparlos equitativamente en los **seis intervalos posibles** del día:
  - 09:00 a 11:00, 11:00 a 13:00, 13:00 a 15:00
  - 15:00 a 17:00, 17:00 a 19:00, 19:00 a 21:00

---

## 3. Escenario 3: Alta Demanda Vespertina Restringida (Día 06)

**Fecha Objetivo:** 2026-12-06
**Objetivo de Prueba:** Contrastar con el Escenario 1 evaluando la planificación cuando el cuello de botella (concentración de compromisos) ocurre en la segunda mitad del día. Esto pone a prueba las lógicas de las ventanas relajadas y el manejo de esperas u holguras matutinas en las secuencias de ruteo.

**Configuración:**
- Se saturaron las ventanas correspondientes a los tres últimos bloques de la tarde.
- Exactamente **20 clientes** fueron asignados a cada uno de los siguientes intervalos:
  - 15:00 a 17:00 (900 - 1020)
  - 17:00 a 19:00 (1020 - 1140)
  - 19:00 a 21:00 (1140 - 1260)
- El resto de los clientes del día fue configurado con ventana libre (09:00 a 21:00).

---

## 4. Escenario 4: Matriz Estocástica Mixta (Día 07)

**Fecha Objetivo:** 2026-12-07
**Objetivo de Prueba:** Simular un escenario de operación intermedia y realista, evaluando la robustez para intercalar entregas prioritarias (TWR rígidas) entre solicitudes flexibles (TWR amplias) dentro de la misma optimización.

**Configuración:**
- La cartera de clientes se dividió intencionalmente al **50%**.
- La primera mitad actúa como reguladora (`Tipo_vivienda = False`), recibiendo la ventana base completa de la jornada (09:00 a 21:00).
- La segunda mitad actúa con restricción de servicio (`Tipo_vivienda = True`) y fue distribuida equitativamente entre las 6 ventanas de 2 horas existentes.
