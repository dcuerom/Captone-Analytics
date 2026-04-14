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
  Truck
} from "lucide-react";
import { cn } from "../ui/utils";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/planning", icon: CalendarClock, label: "Planificación" },
  { to: "/data-quality", icon: ClipboardCheck, label: "Calidad de Datos" },
  { to: "/optimization-results", icon: Route, label: "Resultados" },
  { to: "/fleet-map", icon: Map, label: "Mapa de Flota" },
  { to: "/kpis", icon: BarChart3, label: "KPIs" },
  { to: "/alerts", icon: AlertTriangle, label: "Alertas" },
  { to: "/exports", icon: Download, label: "Exportar" },
];

export function MainLayout() {
  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <Truck className="size-8 text-blue-400" />
            <div>
              <h1 className="font-semibold text-lg">RouteOptimizer</h1>
              <p className="text-xs text-slate-400">TDVRPTW Platform</p>
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
                        ? "bg-blue-600 text-white"
                        : "text-slate-300 hover:bg-slate-800 hover:text-white"
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

        <div className="p-4 border-t border-slate-700 text-xs text-slate-400">
          <p>Backend: DBSCAN + GA (PyMoo)</p>
          <p className="mt-1">Pipeline activo</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
