import { mockFleet, mockHistoricalRuns, mockOptimizationRun, mockOrders, type OptimizationRun, type Order, type Vehicle } from './mockData';

export interface DashboardDataPayload {
  optimizationRun: OptimizationRun;
  orders: Order[];
  fleet: Vehicle[];
  historicalRuns: OptimizationRun[];
}

export interface OptimizationStatusPayload {
  status: 'idle' | 'running' | 'completed' | 'failed';
  startedAt: string | null;
  finishedAt: string | null;
  error: string | null;
  result: Record<string, unknown> | null;
  requestedDate: string | null;
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
}

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL ?? '/api/v1';

async function readJsonSafe(response: Response): Promise<any> {
  const raw = await response.text();
  if (!raw || !raw.trim()) {
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch {
    throw new Error('Respuesta inválida del backend (JSON incompleto o corrupto).');
  }
}

export async function fetchDashboardData(): Promise<DashboardDataPayload> {
  const response = await fetch(`${API_BASE_URL}/data`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });
  const payload = (await readJsonSafe(response)) as DashboardDataPayload | null;

  if (!response.ok) {
    throw new Error((payload as any)?.error ?? `Error API ${response.status}: ${response.statusText}`);
  }
  if (!payload) {
    throw new Error('Backend no disponible o respuesta vacía en /api/v1/data.');
  }
  return payload;
}

export function getBackendMapUrl(): string {
  return `${API_BASE_URL}/map`;
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

  const data = await readJsonSafe(response);
  if (!response.ok) {
    throw new Error(data?.error ?? `Error API ${response.status}`);
  }
  if (!data) {
    throw new Error('Backend no disponible o respuesta vacía en /api/v1/upload-orders.');
  }
  return data as { status: string; message: string; rows: number; columns: string[] };
}

export async function getOptimizationDefaults(): Promise<OptimizationConfigPayload> {
  const response = await fetch(`${API_BASE_URL}/optimize-config`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });
  const data = await readJsonSafe(response);
  if (!response.ok) {
    throw new Error(data?.error ?? `Error API ${response.status}`);
  }
  if (!data?.defaults) {
    throw new Error('Backend no disponible o respuesta vacía en /api/v1/optimize-config.');
  }
  return data.defaults as OptimizationConfigPayload;
}

export async function startOptimization(
  date?: string,
  config?: Partial<OptimizationConfigPayload>,
): Promise<OptimizationStatusPayload> {
  const response = await fetch(`${API_BASE_URL}/optimize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify({ date, config }),
  });

  const data = await readJsonSafe(response);
  if (!response.ok) {
    throw new Error(data?.error ?? `Error API ${response.status}`);
  }
  if (!data) {
    throw new Error('Backend no disponible o respuesta vacía en /api/v1/optimize.');
  }
  return data as OptimizationStatusPayload;
}

export async function getOptimizationStatus(): Promise<OptimizationStatusPayload> {
  const response = await fetch(`${API_BASE_URL}/optimize-status`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });
  const data = await readJsonSafe(response);
  if (!response.ok) {
    throw new Error(data?.error ?? `Error API ${response.status}`);
  }
  if (!data) {
    throw new Error('Backend no disponible o respuesta vacía en /api/v1/optimize-status.');
  }
  return data as OptimizationStatusPayload;
}

export function mockDashboardData(): DashboardDataPayload {
  return {
    optimizationRun: mockOptimizationRun,
    orders: mockOrders,
    fleet: mockFleet,
    historicalRuns: mockHistoricalRuns,
  };
}
