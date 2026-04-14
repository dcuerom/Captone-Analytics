import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { fetchDashboardData, getBackendHealth, type FetchDashboardDataOptions } from './api';
import type { OptimizationRun, Order, Vehicle } from './mockData';
import { useAuth } from './AuthContext';

interface RefreshOptions extends FetchDashboardDataOptions {
  background?: boolean;
}

interface AppDataContextValue {
  run: OptimizationRun;
  orders: Order[];
  fleet: Vehicle[];
  historicalRuns: OptimizationRun[];
  activeRunId: string | null;
  loading: boolean;
  error: string | null;
  backendAvailable: boolean;
  refresh: (options?: RefreshOptions) => Promise<void>;
}

const emptyRun: OptimizationRun = {
  id: '',
  name: 'Sin datos de optimización',
  date: '',
  status: 'failed',
  totalOrders: 0,
  assignedOrders: 0,
  unassignedOrders: 0,
  splitOrders: 0,
  totalVehiclesUsed: 0,
  totalVehiclesAvailable: 0,
  totalDistanceKm: 0,
  totalCost: 0,
  totalWaitTimeMinutes: 0,
  onTimePercentage: 0,
  averageUtilization: 0,
  executionTimeSeconds: 0,
  warnings: [],
  routes: [],
};

const AppDataContext = createContext<AppDataContextValue>({
  run: emptyRun,
  orders: [],
  fleet: [],
  historicalRuns: [],
  activeRunId: null,
  loading: true,
  error: null,
  backendAvailable: true,
  refresh: async () => undefined,
});

export function AppDataProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [run, setRun] = useState<OptimizationRun>(emptyRun);
  const [orders, setOrders] = useState<Order[]>([]);
  const [fleet, setFleet] = useState<Vehicle[]>([]);
  const [historicalRuns, setHistoricalRuns] = useState<OptimizationRun[]>([]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [activeDate, setActiveDate] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [backendAvailable, setBackendAvailable] = useState<boolean>(true);

  const refresh = useCallback(async (options?: RefreshOptions) => {
    if (!isAuthenticated) {
      setLoading(false);
      setError(null);
      setBackendAvailable(true);
      return;
    }
    const background = Boolean(options?.background);
    const runId = options?.runId ?? activeRunId ?? undefined;
    const date = options?.date ?? activeDate ?? undefined;

    if (!background) {
      setLoading(true);
    }
    try {
      const data = await fetchDashboardData({ runId, date });
      setRun(data.optimizationRun ?? emptyRun);
      setOrders(data.orders ?? []);
      setFleet(data.fleet ?? []);
      setHistoricalRuns(data.historicalRuns ?? []);
      setActiveRunId(data.optimizationRun?.id ?? runId ?? null);
      setActiveDate(data.optimizationRun?.date ?? date ?? null);
      setError(null);
      setBackendAvailable(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido al cargar datos del backend';
      setError(message);
      try {
        const health = await getBackendHealth();
        setBackendAvailable(health.status === "ok");
      } catch {
        setBackendAvailable(false);
      }
      // Conservamos el último estado válido en memoria.
      // Si no existe estado previo, quedan valores vacíos por defecto.
    } finally {
      if (!background) {
        setLoading(false);
      }
    }
  }, [activeDate, activeRunId, isAuthenticated]);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }
    void refresh({ background: false });
  }, [isAuthenticated, refresh]);

  useEffect(() => {
    if (!isAuthenticated) {
      return;
    }
    const onFocus = () => {
      void refresh({ background: true });
    };
    window.addEventListener('focus', onFocus);

    return () => {
      window.removeEventListener('focus', onFocus);
    };
  }, [isAuthenticated, refresh]);

  const value = useMemo(
    () => ({ run, orders, fleet, historicalRuns, activeRunId, loading, error, backendAvailable, refresh }),
    [run, orders, fleet, historicalRuns, activeRunId, loading, error, backendAvailable, refresh],
  );

  return <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>;
}

export function useAppData() {
  return useContext(AppDataContext);
}
