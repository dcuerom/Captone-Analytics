import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { fetchDashboardData } from './api';
import type { OptimizationRun, Order, Vehicle } from './mockData';

interface AppDataContextValue {
  run: OptimizationRun;
  orders: Order[];
  fleet: Vehicle[];
  historicalRuns: OptimizationRun[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
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
  loading: true,
  error: null,
  refresh: async () => undefined,
});

export function AppDataProvider({ children }: { children: ReactNode }) {
  const [run, setRun] = useState<OptimizationRun>(emptyRun);
  const [orders, setOrders] = useState<Order[]>([]);
  const [fleet, setFleet] = useState<Vehicle[]>([]);
  const [historicalRuns, setHistoricalRuns] = useState<OptimizationRun[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async (background = false) => {
    if (!background) {
      setLoading(true);
    }
    try {
      const data = await fetchDashboardData();
      setRun(data.optimizationRun ?? emptyRun);
      setOrders(data.orders ?? []);
      setFleet(data.fleet ?? []);
      setHistoricalRuns(data.historicalRuns ?? []);
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
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  useEffect(() => {
    const onFocus = () => {
      void refresh(true);
    };
    window.addEventListener('focus', onFocus);

    return () => {
      window.removeEventListener('focus', onFocus);
    };
  }, [refresh]);

  const value = useMemo(
    () => ({ run, orders, fleet, historicalRuns, loading, error, refresh }),
    [run, orders, fleet, historicalRuns, loading, error],
  );

  return <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>;
}

export function useAppData() {
  return useContext(AppDataContext);
}
