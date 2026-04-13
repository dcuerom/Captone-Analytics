import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { fetchDashboardData, mockDashboardData } from './api';
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

const fallback = mockDashboardData();

const AppDataContext = createContext<AppDataContextValue>({
  run: fallback.optimizationRun,
  orders: fallback.orders,
  fleet: fallback.fleet,
  historicalRuns: fallback.historicalRuns,
  loading: true,
  error: null,
  refresh: async () => undefined,
});

export function AppDataProvider({ children }: { children: ReactNode }) {
  const [run, setRun] = useState<OptimizationRun>(fallback.optimizationRun);
  const [orders, setOrders] = useState<Order[]>(fallback.orders);
  const [fleet, setFleet] = useState<Vehicle[]>(fallback.fleet);
  const [historicalRuns, setHistoricalRuns] = useState<OptimizationRun[]>(fallback.historicalRuns);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async (background = false) => {
    if (!background) {
      setLoading(true);
    }
    try {
      const data = await fetchDashboardData();
      setRun(data.optimizationRun ?? fallback.optimizationRun);
      setOrders(data.orders ?? fallback.orders);
      setFleet(data.fleet ?? fallback.fleet);
      setHistoricalRuns(data.historicalRuns?.length ? data.historicalRuns : fallback.historicalRuns);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error desconocido al cargar datos del backend';
      setError(message);
      setRun(fallback.optimizationRun);
      setOrders(fallback.orders);
      setFleet(fallback.fleet);
      setHistoricalRuns(fallback.historicalRuns);
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
