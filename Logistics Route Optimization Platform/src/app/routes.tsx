import { Navigate, createBrowserRouter, useLocation } from "react-router";
import { MainLayout } from "./components/layout/MainLayout";
import { Dashboard } from "./pages/Dashboard";
import { Planning } from "./pages/Planning";
import { DataQuality } from "./pages/DataQuality";
import { OptimizationResults } from "./pages/OptimizationResults";
import { FleetMap } from "./pages/FleetMap";
import { VehicleDetail } from "./pages/VehicleDetail";
import { KPIs } from "./pages/KPIs";
import { Alerts } from "./pages/Alerts";
import { Exports } from "./pages/Exports";
import { NotFound } from "./pages/NotFound";
import { Login } from "./pages/Login";
import { Users } from "./pages/Users";
import { useAuth } from "./data/AuthContext";

function ProtectedLayout() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <MainLayout />;
}

export const router = createBrowserRouter([
  { path: "/login", Component: Login },
  {
    path: "/",
    Component: ProtectedLayout,
    children: [
      { index: true, Component: Dashboard },
      { path: "planning", Component: Planning },
      { path: "data-quality", Component: DataQuality },
      { path: "optimization-results", Component: OptimizationResults },
      { path: "fleet-map", Component: FleetMap },
      { path: "vehicle/:id", Component: VehicleDetail },
      { path: "kpis", Component: KPIs },
      { path: "alerts", Component: Alerts },
      { path: "exports", Component: Exports },
      { path: "users", Component: Users },
      { path: "*", Component: NotFound },
    ],
  },
]);
