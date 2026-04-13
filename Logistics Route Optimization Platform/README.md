# Logistics Route Optimization Platform (Frontend + Integración)

Frontend React/Vite para visualizar y operar la optimización logística TDVRPTW, integrado con el backend Python del repositorio.

## Resumen

- Framework: `React 18 + Vite 6`
- UI: componentes `Radix` + `Tailwind`
- Mapa:
  - Modo UI (`react-leaflet`, líneas simples)
  - Modo Backend (HTML Folium con calles reales)
- Integración API vía proxy Vite:
  - `/api/*` -> `http://127.0.0.1:8000`

## Estructura relevante

- `src/app/pages/Planning.tsx`
  - Configuración de corrida
  - Upload manual de CSV
  - Lanzamiento de optimización
  - Barra de progreso por etapas
  - Persistencia de parámetros en `localStorage`
- `src/app/pages/FleetMap.tsx`
  - Visualización de rutas en UI o mapa backend
  - Auto-fit a rutas visibles en modo UI
- `src/app/data/api.ts`
  - Cliente API y tipado de payloads
  - Parseo robusto de respuestas JSON
- `src/app/data/AppDataContext.tsx`
  - Carga global de datos del dashboard
  - Sin fallback automático a mocks

## Levantar el proyecto

### Opción recomendada (todo en un comando, desde raíz del repo)

```bash
./scripts/dev_full.sh
```

Este script:

1. Libera puertos `8000` y `5173` si están ocupados.
2. Levanta backend en `127.0.0.1:8000`.
3. Espera `GET /api/v1/health`.
4. Levanta frontend en `127.0.0.1:5173`.

### Opción manual

Terminal 1 (raíz repo):

```bash
source .venv/bin/activate
python backend/api_server.py
```

Terminal 2:

```bash
cd "Logistics Route Optimization Platform"
npm install
npm run dev
```

## Verificación rápida de integración

```bash
curl http://127.0.0.1:8000/api/v1/health
curl http://127.0.0.1:8000/api/v1/optimize-status
curl http://127.0.0.1:5173/api/v1/health
```

Si el frontend muestra `ECONNREFUSED 127.0.0.1:8000`, el backend no está corriendo.

## Endpoints usados por el frontend

- `GET /api/v1/data`
  - Dataset principal del dashboard (run actual, órdenes, flota, histórico)
- `GET /api/v1/optimize-config`
  - Defaults de parámetros de optimización
- `GET /api/v1/optimize-status`
  - Estado de corrida y progreso (`progressPct`, `stage`, `stageMessage`, etc.)
- `POST /api/v1/optimize`
  - Inicia optimización asíncrona
- `POST /api/v1/upload-orders`
  - Carga CSV de pedidos al backend
- `GET /api/v1/map`
  - Mapa HTML backend con calles reales

## Flujo operativo en Planning

1. Cargar CSV (manual).
2. Seleccionar fecha de entrega.
3. Ajustar parámetros efectivos:
   - `clustering_eps`
   - `clustering_min_samples`
   - `ga_n_gen`
   - `ga_pop_size`
   - `d_max_min`
   - `max_vehiculos_globales`
4. Ejecutar optimización.
5. Monitorear barra de progreso por etapa.

### Persistencia de estado de UI

- Se guardan en `localStorage` los parámetros de Planning (`planning_state_v1`).
- Al volver a la página:
  - se recuperan parámetros,
  - si el backend sigue `running`, se retoma polling automáticamente.
- Nota: el `input` de archivo (`type=file`) **no puede** persistirse por restricciones del navegador.

## Mapa y trazado de rutas

### Modo Backend (recomendado para operación)

- Fuente: `GET /api/v1/map`
- Renderiza HTML Folium generado por backend.
- Incluye calles reales de OSMnx + secuencias de camiones.
- Ajustado para enfocar Santiago.

### Modo UI

- Usa coordenadas de órdenes en Leaflet.
- Útil para inspección rápida.
- Ahora auto-centra/auto-zoom según rutas visibles y ordena paradas por `sequence`.

## Estado actual de consistencia Front-Back

- Objetivo mostrado en UI: **Minimizar distancia total**.
- No se muestran controles visuales no conectados al backend.
- Mensajería de error unificada cuando backend no está disponible.
- Parseo API endurecido: si backend responde vacío/corrupto, se muestra error legible.

## Troubleshooting

### 1) `Backend no disponible` en frontend

- Verifica backend:
  ```bash
  curl http://127.0.0.1:8000/api/v1/health
  ```
- Si falla, relanza backend.

### 2) `JSON.parse ... unexpected end of data`

- Suele ocurrir cuando el backend se cae durante request.
- La capa API actual ya maneja esto con errores claros, pero la causa base sigue siendo backend inestable/no activo.

### 3) Proceso backend termina con `killed`

- Es típico de presión de memoria.
- Usa hardware con más RAM o ejecuta modo estable (menos workers de ruteo):
  ```bash
  ROUTING_MAX_WORKERS=1 python backend/api_server.py
  ```

### 4) Error XML `no element found: line 1, column 0` en grafo

- Se da por `.graphml` vacío/corrupto.
- El backend ya tiene manejo para regenerar automáticamente.

### 5) `/api/v1/data` devuelve 500 después de una corrida

- Puede deberse a artefactos históricos incompletos.
- El backend actual omite corridas incompletas y usa la última válida.

## Scripts útiles (raíz repo)

- `scripts/dev_full.sh`: levanta backend + frontend (desarrollo).
- `scripts/dev_verify_full.sh`: smoke checks de integración.

## Build de frontend

```bash
cd "Logistics Route Optimization Platform"
npm run build
```

## Nota de origen visual

El diseño base proviene de Figma:
`https://www.figma.com/design/9QUqhBbg6Is42zO2eZSvmH/Logistics-Route-Optimization-Platform`
  
