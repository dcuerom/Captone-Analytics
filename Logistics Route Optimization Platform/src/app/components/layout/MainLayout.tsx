import { Outlet, NavLink } from "react-router";
import { 
  LayoutDashboard, 
  CalendarClock, 
  ClipboardCheck, 
  Route, 
  Map, 
  BarChart3, 
  AlertTriangle, 
  Download,
  Truck,
  Users,
  LogOut,
  ShieldCheck,
} from "lucide-react";
import { cn } from "../ui/utils";
import { useAuth } from "../../data/AuthContext";
import { useAppData } from "../../data/AppDataContext";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/planning", icon: CalendarClock, label: "Planificación" },
  { to: "/data-quality", icon: ClipboardCheck, label: "Calidad de Datos" },
  { to: "/optimization-results", icon: Route, label: "Resultados" },
  { to: "/fleet-map", icon: Map, label: "Mapa de Flota" },
  { to: "/kpis", icon: BarChart3, label: "KPIs" },
  { to: "/alerts", icon: AlertTriangle, label: "Alertas" },
  { to: "/exports", icon: Download, label: "Exportar" },
  { to: "/users", icon: Users, label: "Usuarios" },
];

export function MainLayout() {
  const { currentUser, logout } = useAuth();
  const { error, backendAvailable } = useAppData();

  return (
    <div className="flex h-screen bg-slate-100">
      {/* Sidebar */}
      <aside className="w-72 bg-[linear-gradient(180deg,#020617_0%,#0f172a_52%,#0f766e_100%)] text-white flex flex-col">
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="flex size-12 items-center justify-center rounded-2xl bg-white/10 shadow-lg shadow-sky-950/30 backdrop-blur">
              <Truck className="size-7 text-sky-300" />
            </div>
            <div>
              <h1 className="font-semibold text-lg">RouteOptimizer Cloud</h1>
              <p className="text-xs text-slate-300">Routing SaaS for urban logistics</p>
            </div>
          </div>
        </div>
        
        <nav className="flex-1 p-4 overflow-y-auto">
          <ul className="space-y-1">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) =>
                    cn(
                      "flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors",
                      isActive
                        ? "bg-white text-slate-950 shadow-sm"
                        : "text-slate-200 hover:bg-white/10 hover:text-white"
                    )
                  }
                >
                  <item.icon className="size-5" />
                  <span className="text-sm font-medium">{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="p-4 space-y-4 border-t border-white/10">
          <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-medium text-white">{currentUser?.name ?? "Demo Account"}</p>
                <p className="mt-1 text-xs text-slate-300">{currentUser?.email ?? "demo@routeoptimizer.ai"}</p>
              </div>
              <div className="inline-flex items-center gap-1 rounded-full bg-emerald-400/15 px-2 py-1 text-[11px] font-medium text-emerald-200">
                <ShieldCheck className="size-3" />
                {currentUser?.role ?? "Owner"}
              </div>
            </div>
            <button
              type="button"
              onClick={logout}
              className="mt-4 inline-flex items-center gap-2 text-xs text-slate-200 transition hover:text-white"
            >
              <LogOut className="size-3.5" />
              Cerrar sesión demo
            </button>
          </div>

          <div className="text-xs text-slate-300">
            <p>Backend: DBSCAN + GA + red vial OSMnx</p>
            <p className="mt-1">
              {!backendAvailable ? "Sin conexión con backend" : error ? "Datos no actualizados" : "Pipeline conectado"}
            </p>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto bg-[linear-gradient(180deg,#f8fafc_0%,#eef2ff_100%)]">
        <Outlet />
      </main>
    </div>
  );
}
