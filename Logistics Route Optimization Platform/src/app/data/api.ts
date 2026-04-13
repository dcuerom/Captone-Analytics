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

export async function fetchDashboardData(): Promise<DashboardDataPayload> {
  const response = await fetch(`${API_BASE_URL}/data`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Error API ${response.status}: ${response.statusText}`);
  }

  const payload = (await response.json()) as DashboardDataPayload;
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

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.error ?? `Error API ${response.status}`);
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
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.error ?? `Error API ${response.status}`);
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

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.error ?? `Error API ${response.status}`);
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
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.error ?? `Error API ${response.status}`);
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
