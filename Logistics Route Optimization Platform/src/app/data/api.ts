import { mockFleet, mockHistoricalRuns, mockOptimizationRun, mockOrders, type OptimizationRun, type Order, type Vehicle } from './mockData';

export interface DashboardDataPayload {
  schemaVersion?: string;
  generatedAt?: string;
  optimizationRun: OptimizationRun;
  orders: Order[];
  fleet: Vehicle[];
  historicalRuns: OptimizationRun[];
}

export interface OptimizationStatusPayload {
  runId?: string | null;
  status: 'idle' | 'running' | 'completed' | 'failed';
  startedAt: string | null;
  finishedAt: string | null;
  error: string | null;
  result: Record<string, unknown> | null;
  requestedDate: string | null;
  depotAddress?: string | null;
  progressPct?: number;
  stage?: string;
  stageMessage?: string;
  currentStep?: number;
  totalSteps?: number;
  updatedAt?: string | null;
}

export interface OptimizationConfigPayload {
  t_inicio: number;
  cap_vol_cm3: number;
  cap_peso_g: number;
  factor_s: number;
  alpha_espera: number;
  costo_fijo_camion: number;
  ga_pop_size: number;
  ga_n_gen: number;
  ga_seed: number;
  d_max_min: number;
  max_vehiculos_globales: number;
  clustering_time_column: string;
  clustering_default_window_start_hour: number;
  clustering_alpha_time: number;
  clustering_eps: number;
  clustering_min_samples: number;
  clustering_rescue_threshold: number;
  force_outlier_rescue: boolean;
  depot_address?: string;
}

export interface RoutesGeometryPayload {
  runId: string;
  date: string;
  generatedAt: string;
  depot: {
    id: string;
    address?: string | null;
    coordinates?: [number, number] | null;
  };
  routes: Array<{
    vehicleId: string;
    vehiclePhysicalId: number;
    cluster: number | string;
    blockIndex: number;
    stopOrderIds: string[];
    coordinates: [number, number][];
  }>;
}

export interface PreflightCheckItem {
  name: string;
  ok: boolean;
  detail: string;
}

export interface PreflightPayload {
  status: "ok" | "failed";
  generatedAt: string;
  failedCount: number;
  checks: PreflightCheckItem[];
}

export interface FetchDashboardDataOptions {
  runId?: string;
  date?: string;
}

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL ?? '/api/v1';

async function readApiPayload<T>(response: Response): Promise<T> {
  const raw = await response.text();
  const trimmed = raw.trim();

  let data: unknown = null;
  if (trimmed) {
    try {
      data = JSON.parse(trimmed);
    } catch {
      if (!response.ok) {
        throw new Error(`Error API ${response.status}: respuesta no JSON del backend`);
      }
      throw new Error("Respuesta invalida del backend");
    }
  }

  if (!response.ok) {
    let message =
      typeof data === "object" && data !== null && "error" in data && typeof (data as { error?: unknown }).error === "string"
        ? (data as { error: string }).error
        : `Error API ${response.status}: ${response.statusText || "backend no disponible"}`;
    const firstRowError =
      typeof data === "object" &&
      data !== null &&
      "errors" in data &&
      Array.isArray((data as { errors?: Array<{ row?: number; errors?: string[] }> }).errors) &&
      (data as { errors?: Array<{ row?: number; errors?: string[] }> }).errors![0]
        ? (data as { errors: Array<{ row?: number; errors?: string[] }> }).errors[0]
        : null;
    if (firstRowError) {
      message += ` Primera fila invalida: ${firstRowError.row ?? "?"} (${(firstRowError.errors ?? []).join(", ")})`;
    }
    throw new Error(message);
  }

  if (data === null) {
    throw new Error("Respuesta vacia del backend");
  }

  return data as T;
}

export async function fetchDashboardData(options?: FetchDashboardDataOptions): Promise<DashboardDataPayload> {
  const params = new URLSearchParams();
  if (options?.runId) {
    params.set("runId", options.runId);
  }
  if (options?.date) {
    params.set("date", options.date);
  }
  const query = params.toString();

  const response = await fetch(`${API_BASE_URL}/data${query ? `?${query}` : ""}`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  return readApiPayload<DashboardDataPayload>(response);
}

export async function getBackendHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });
  return readApiPayload<{ status: string }>(response);
}

export function getBackendMapUrl(): string {
  return `${API_BASE_URL}/map`;
}

export function getBackendMapUrlForRun(runId?: string | null): string {
  if (!runId) return getBackendMapUrl();
  return `${API_BASE_URL}/map?runId=${encodeURIComponent(runId)}`;
}

export async function getPreflightStatus(): Promise<PreflightPayload> {
  const response = await fetch(`${API_BASE_URL}/preflight`, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });
  return readApiPayload<PreflightPayload>(response);
}

export async function uploadOrdersCsv(filename: string, csvText: string) {
  const response = await fetch(`${API_BASE_URL}/upload-orders`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({
      filename,
      csv: csvText,
    }),
  });

  return readApiPayload<{
    status: string;
    message: string;
    rows: number;
    columns: string[];
    detectedDeliveryDates?: string[];
    defaultDeliveryDate?: string | null;
  }>(response);
}

export async function getOptimizationDefaults(): Promise<OptimizationConfigPayload> {
  const response = await fetch(`${API_BASE_URL}/optimize-config`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });
  const data = await readApiPayload<{ defaults: OptimizationConfigPayload }>(response);
  return data.defaults;
}

export async function startOptimization(
  date?: string,
  config?: Partial<OptimizationConfigPayload>,
  options?: { runId?: string; depotAddress?: string },
): Promise<OptimizationStatusPayload> {
  const response = await fetch(`${API_BASE_URL}/optimize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({ date, config, runId: options?.runId, depotAddress: options?.depotAddress }),
  });

  return readApiPayload<OptimizationStatusPayload>(response);
}

export async function getRoutesGeometry(runId?: string): Promise<RoutesGeometryPayload> {
  const url = runId ? `${API_BASE_URL}/routes-geometry?runId=${encodeURIComponent(runId)}` : `${API_BASE_URL}/routes-geometry`;
  const response = await fetch(url, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  });
  return readApiPayload<RoutesGeometryPayload>(response);
}

export async function getOptimizationStatus(): Promise<OptimizationStatusPayload> {
  const response = await fetch(`${API_BASE_URL}/optimize-status`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });
  return readApiPayload<OptimizationStatusPayload>(response);
}

export function mockDashboardData(): DashboardDataPayload {
  return {
    optimizationRun: mockOptimizationRun,
    orders: mockOrders,
    fleet: mockFleet,
    historicalRuns: mockHistoricalRuns,
  };
}
