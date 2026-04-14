import { 
  TrendingUp, 
  Truck, 
  MapPin, 
  DollarSign, 
  Clock, 
  AlertTriangle,
  Package,
  CheckCircle2
} from "lucide-react";
import { KPICard } from "../components/shared/KPICard";
import { StatusBadge } from "../components/shared/StatusBadge";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { useAppData } from "../data/AppDataContext";
import { Link } from "react-router";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from "recharts";

export function Dashboard() {
  const { run, fleet, loading, error, backendAvailable } = useAppData();
  const availableFleet = fleet.filter(v => v.available).length;

  if (loading) {
    return <div className="p-8 text-slate-600">Cargando datos de backend...</div>;
  }

  // Datos para gráficos
  const utilizationData = run.routes.map(route => ({
    vehicle: route.vehicleName,
    volume: route.utilizationVolume,
    weight: route.utilizationWeight,
  }));

  const complianceData = [
    { name: 'A tiempo', value: run.onTimePercentage, color: '#10b981' },
    { name: 'Con retrasos', value: 100 - run.onTimePercentage, color: '#ef4444' },
  ];

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold text-slate-900 mb-2">Dashboard Ejecutivo</h1>
        <p className="text-slate-600">Resumen operativo</p>
        {!backendAvailable && <p className="text-xs text-amber-600 mt-1">Backend no disponible. Verifica python backend/api_server.py y npm run dev.</p>}
        {backendAvailable && error && <p className="text-xs text-slate-500 mt-1">No se pudieron refrescar algunos datos.</p>}
      </div>

      {/* Run Status Alert */}
      <Card className="border-l-4 border-l-green-500 bg-green-50">
        <CardContent className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="size-5 text-green-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-green-900">Corrida completada</h3>
                <p className="text-sm text-green-700 mt-1">
                  {run.name} - Ejecutada en {run.executionTimeSeconds}s
                </p>
                {run.warnings.length > 0 && (
                  <p className="text-sm text-green-700 mt-2">
                    {run.warnings.length} advertencias registradas
                  </p>
                )}
              </div>
            </div>
            <div className="flex gap-2">
              <Link to="/optimization-results">
                <Button size="sm" variant="outline">Ver detalles</Button>
              </Link>
              <Link to="/fleet-map">
                <Button size="sm">Ver mapa</Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Entregas a Tiempo"
          value={`${run.onTimePercentage}%`}
          subtitle={`${Math.round(run.assignedOrders * run.onTimePercentage / 100)} de ${run.assignedOrders} pedidos`}
          icon={Clock}
          variant={run.onTimePercentage >= 90 ? "success" : run.onTimePercentage >= 75 ? "warning" : "danger"}
          trend={{ value: 2.3, label: "vs. ayer" }}
        />
        
        <KPICard
          title="Costo Total"
          value={`$${run.totalCost.toLocaleString('es-CL')}`}
          subtitle={`${run.totalDistanceKm.toFixed(1)} km recorridos`}
          icon={DollarSign}
          variant="default"
          trend={{ value: -5.2, label: "vs. ayer" }}
        />
        
        <KPICard
          title="Flota Utilizada"
          value={`${run.totalVehiclesUsed}/${availableFleet}`}
          subtitle={`${((run.totalVehiclesUsed / availableFleet) * 100).toFixed(0)}% utilización`}
          icon={Truck}
          variant={run.totalVehiclesUsed === availableFleet ? "warning" : "success"}
        />
        
        <KPICard
          title="Pedidos Asignados"
          value={`${run.assignedOrders}/${run.totalOrders}`}
          subtitle={`${run.unassignedOrders} sin asignar, ${run.splitOrders} divididos`}
          icon={Package}
          variant={run.unassignedOrders > 0 ? "warning" : "success"}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Utilization Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Utilización por Vehículo</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={utilizationData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="vehicle" angle={-45} textAnchor="end" height={80} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="volume" fill="#3b82f6" name="Volumen %" />
                <Bar dataKey="weight" fill="#8b5cf6" name="Peso %" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Compliance Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Cumplimiento de Ventanas Horarias</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={complianceData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {complianceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Routes Summary */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Resumen de Rutas</CardTitle>
            <Link to="/optimization-results">
              <Button variant="outline" size="sm">Ver todas las rutas</Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b text-left text-sm text-slate-600">
                  <th className="pb-3 font-medium">Vehículo</th>
                  <th className="pb-3 font-medium">Cluster</th>
                  <th className="pb-3 font-medium">Paradas</th>
                  <th className="pb-3 font-medium">Distancia</th>
                  <th className="pb-3 font-medium">Tiempo</th>
                  <th className="pb-3 font-medium">Utilización</th>
                  <th className="pb-3 font-medium">Cumplimiento</th>
                  <th className="pb-3 font-medium">Costo</th>
                  <th className="pb-3 font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {run.routes.map((route) => (
                  <tr key={route.vehicleId} className="border-b last:border-0 hover:bg-slate-50">
                    <td className="py-3">
                      <div className="flex items-center gap-2">
                        <Truck className="size-4 text-slate-400" />
                        <span className="font-medium text-slate-900">{route.vehicleName}</span>
                      </div>
                    </td>
                    <td className="py-3 text-sm text-slate-600">Cluster {route.cluster}</td>
                    <td className="py-3 text-sm text-slate-900">{route.ordersDelivered} pedidos</td>
                    <td className="py-3 text-sm text-slate-900">{route.totalDistanceKm.toFixed(1)} km</td>
                    <td className="py-3 text-sm text-slate-900">{Math.round(route.totalTimeMinutes / 60)}h {route.totalTimeMinutes % 60}m</td>
                    <td className="py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${route.utilizationVolume}%` }}
                          />
                        </div>
                        <span className="text-sm text-slate-600">{route.utilizationVolume.toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="py-3">
                      <StatusBadge 
                        status={route.onTimeDeliveries === route.ordersDelivered ? 'on-time' : 'violation'} 
                        label={`${route.onTimeDeliveries}/${route.ordersDelivered}`}
                      />
                    </td>
                    <td className="py-3 text-sm font-medium text-slate-900">
                      ${route.totalCost.toFixed(2)}
                    </td>
                    <td className="py-3">
                      <Link to={`/vehicle/${route.vehicleId}`}>
                        <Button variant="ghost" size="sm">Ver detalle</Button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Warnings */}
      {run.warnings.length > 0 && (
        <Card className="border-l-4 border-l-amber-500">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertTriangle className="size-5 text-amber-600" />
              <CardTitle>Advertencias Operativas</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {run.warnings.map((warning, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-slate-700">
                  <span className="text-amber-600 mt-0.5">•</span>
                  <span>{warning}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
