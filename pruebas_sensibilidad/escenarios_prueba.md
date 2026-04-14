# Escenarios de Evaluación y Pruebas de Sensibilidad

## 1. Metodología de Generación de Instancias

Las instancias operativas empleadas en la presente fase de validación y pruebas de sensibilidad fueron sintetizadas a partir de los registros brutos contenidos en el archivo de origen `vrp_orders.xlsx`. Posteriormente, estos datos fueron procesados, depurados y consolidados formativamente en el conjunto de datos de validación `df_despacho.csv` (ubicado en el directorio de `DatosSimulados`). Este diseño experimental persigue la evaluación empírica del comportamiento, factibilidad matemática y resiliencia computacional del algoritmo genético híbrido frente a configuraciones de estrés logístico y distribución temporal de restricciones (ventanas de tiempo).

La parametrización base de las instancias se rige bajo los siguientes supuestos operativos estructurales:
- **Restricciones Estrictas (Hard Windows):** Todas las ventanas de tiempo impuestas por los clientes con alta prioridad poseen una duración invariable de 2 horas (120 minutos).
- **Ventanas Globales (Holgura Extendida):** Los clientes que carecen de especificación horaria preferente (`Tipo_vivienda = False`) operan bajo un marco de asignación continua a lo largo de la jornada laboral oficial, configurado entre las 09:00 y las 21:00 horas (equivalente al intervalo [540, 1260] medido en minutos desde las 00:00).

Para representar fielmente la heterogeneidad de la casuística de entrega, la generación de las configuraciones de prueba fue gobernada por dos aproximaciones estocásticas fundamentales:
1. **Asignación de Distribución Uniforme:** Se implementó una lógica determinística y equitativa para agrupar nodos restringidos. En esta formulación, se impone un reparto homogéneo de clientes a través de los múltiples intervalos horarios disponibles, lo cual somete al modelo algorítmico a una saturación global plana, permitiendo evaluar la eficiencia computacional basal y el manejo de carga sostenida sin picos locales.
2. **Asignación Aleatoria y Distribución Híbrida Estocástica:** Se introdujo variabilidad sistémica incorporando selección aleatoria y saturación intencional de clústeres temporales. Mediante generadores de variables pseudoaleatorias, se simularon desbalances operacionales agudos (p. ej., alta concentración matutina o vespertina y matrices probabilísticas combinadas). Este enfoque es crítico para determinar la robustez de las heurísticas de cruce inter-clúster (intra-ruta) y la flexibilidad adaptativa del modelo frente a picos probabilísticos abruptos interactuando con nodos de holgura extendida.

---

## 2. Descripción Paramétrica de los Escenarios Simulados

A continuación, se documenta la estructura analítica de los cuatro escenarios de modelamiento evaluativos construidos para medir la sensibilidad de las heurísticas del enrutador:

### 2.1 Escenario 1: Alta Demanda Matutina Restringida (Día 04)

**Fecha Objetivo:** 2026-12-04
**Objetivo de Prueba:** Evaluar empíricamente la capacidad de asignación, factibilidad de ruteo y penalización sistémica del algoritmo bajo una exigencia logística donde la densidad de entregas exhibe un sesgo estadístico marcado hacia los deciles iniciales de la jornada laboral.

**Configuración Metodológica:**
- Se procedió a la saturación forzada de los intervalos correspondientes a los tres primeros clústeres horarios de la mañana.
- Exactamente **20 nodos clientes** fueron asignados estáticamente a cada uno de los siguientes intervalos cerrados:
  - 09:00 a 11:00 (540 - 660)
  - 11:00 a 13:00 (660 - 780)
  - 13:00 a 15:00 (780 - 900)
- El complemento de la demanda diaria operó sin restricciones ajustadas, recayendo en la ventana global del sistema operativo continuo (09:00 a 21:00).

### 2.2 Escenario 2: Distribución Totalmente Uniforme Diurna (Día 05)

**Fecha Objetivo:** 2026-12-05
**Objetivo de Prueba:** Cuantificar el esfuerzo computacional, la convergencia del vector genético y la factibilidad teórica del modelo cuando la totalidad de los vértices exige cumplimiento estricto y la función de densidad de demanda es perfectamente constante durante la jornada.

**Configuración Metodológica:**
- El **100%** del grafo de clientes para este día operativo cuenta con vector de restricción temporal activo (`Tipo_vivienda = True`).
- Se aplicó un algoritmo de dispersión uniforme sobre la matriz de requerimientos, fraccionando la demanda de manera estrictamente equitativa a lo largo de los **seis intervalos posibles** del modelo:
  - 09:00 a 11:00, 11:00 a 13:00, 13:00 a 15:00
  - 15:00 a 17:00, 17:00 a 19:00, 19:00 a 21:00

### 2.3 Escenario 3: Alta Demanda Vespertina Restringida (Día 06)

**Fecha Objetivo:** 2026-12-06
**Objetivo de Prueba:** Contrastar estructuralmente con el diseño del Escenario 1 (Día 04). Busca evaluar la mitigación de cuellos de botella mediante las holguras (waiting times) previas y la asimilación del estrés operativo cuando la concentración crítica de compromisos es decantada probabilísticamente hacia la segunda mitad del horizonte de planificación.

**Configuración Metodológica:**
- Se indujo asimetría en la distribución de requerimientos al saturar directamente los tres bloques finales de la tarde-noche.
- Exactamente **20 nodos clientes** fueron forzados bajo las siguientes ventanas estáticas:
  - 15:00 a 17:00 (900 - 1020)
  - 17:00 a 19:00 (1020 - 1140)
  - 19:00 a 21:00 (1140 - 1260)
- Simétricamente al escenario matinal, el saldo residual recayó aleatoriamente sobre ventanas libres (09:00 a 21:00).

### 2.4 Escenario 4: Matriz Estocástica Mixta (Día 07)

**Fecha Objetivo:** 2026-12-07
**Objetivo de Prueba:** Simular un gradiente estocástico realista como elemento de control base. La prueba busca validar la integración y superposición de nodos con restricciones duras y nodos con requerimientos holgados, maximizando el nivel de aleatoriedad operativa.

**Configuración Metodológica:**
- La topología de la cartera fue particionada aleatoria y uniformemente al **50%**.
- La primera subpoblación cumple el rol de amortiguador de rutas (`Tipo_vivienda = False`), recibiendo la parametrización base completa (09:00 a 21:00).
- La subpoblación complementaria actúa como vector de carga (nodos rígidos, `Tipo_vivienda = True`) y fue expuesta a una asignación pseudoaleatoria, distribuyéndose equitativamente de forma probabilística entre todo el espectro de ventanas bihorarias habilitadas.
