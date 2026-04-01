# 🚚 Módulo `gestion_flota/` — Orquestación Global de Turnos

Este módulo es la **fase final del negocio** dentro del pipeline. Aborda el problema de la logística abstracta versus la vida real temporal de los camiones de reparto limitados de una empresa.

## Archivos y su Contribución al Pipeline

### `gestor.py`
**Rol:** Administrador de Empaquetamiento de Flota (Multiplexación Temporal).
**Funcionalidad Detallada:**
El archivo principal de optimización (`genetic_algorithm.py`) encuentra "rutas perfectas" por agrupamiento de zonas en paralelo, pero asume que posee un número infinito de vehículos abstractos libres.

El script `gestor.py` contribuye cerrando este vacío de infactibilidad abstracta:
1. Agrupa todos los turnos abstractos y los encapsula en variables de bloque (`BloqueRuta`).
2. Implementa directrices *Earliest Departure First*: aplanando bloques temporalmente para asignar tareas en base a cronologías estrictas.
3. Empaqueta sub-rutas dentro de un pool fijo (Ej: 20 camiones reales `VehiculoGlobal`). Se asegura de que un conductor que sale al Clúster 1 a las 09:00 AM, vuelva a base y pueda ser reaprovechado en otra ruta a las 14:00 PM sin solaparse (turnos mañana/tarde).
4. **Genera los Reportes Consolidados Markdown:** Mapea el formato tabular visual para los "Dashboards" o análisis de supervisor, levantando alarmas explícitamente en el documento final si un bloque no puede ser ejecutado porque superó la Capacidad Estática Global (indicando que requerirá servicio externalizado).
