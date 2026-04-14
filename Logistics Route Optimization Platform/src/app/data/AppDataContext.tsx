import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { fetchDashboardData, type FetchDashboardDataOptions } from './api';
import type { OptimizationRun, Order, Vehicle } from './mockData';

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
  refresh: async () => undefined,
});

export function AppDataProvider({ children }: { children: ReactNode }) {
  const [run, setRun] = useState<OptimizationRun>(emptyRun);
  const [orders, setOrders] = useState<Order[]>([]);
  const [fleet, setFleet] = useState<Vehicle[]>([]);
  const [historicalRuns, setHistoricalRuns] = useState<OptimizationRun[]>([]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [activeDate, setActiveDate] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async (options?: RefreshOptions) => {
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
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido al cargar datos del backend';
      setError(message);
      // Conservamos el último estado válido en memoria.
      // Si no existe estado previo, quedan valores vacíos por defecto.
    } finally {
      if (!background) {
        setLoading(false);
      }
    }
  }, [activeDate, activeRunId]);

  useEffect(() => {
    void refresh({ background: false });
  }, [refresh]);

  useEffect(() => {
    const onFocus = () => {
      void refresh({ background: true });
    };
    window.addEventListener('focus', onFocus);

    return () => {
      window.removeEventListener('focus', onFocus);
    };
  }, [refresh]);

  const value = useMemo(
    () => ({ run, orders, fleet, historicalRuns, activeRunId, loading, error, refresh }),
    [run, orders, fleet, historicalRuns, activeRunId, loading, error, refresh],
  );

  return <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>;
}

export function useAppData() {
  return useContext(AppDataContext);
}
