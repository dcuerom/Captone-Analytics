import { useState } from "react";
import { Link } from "react-router";
import { 
  Truck, 
  MapPin, 
  Clock, 
  TrendingUp, 
  AlertTriangle,
  Filter,
  Eye
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { StatusBadge } from "../components/shared/StatusBadge";
import { useAppData } from "../data/AppDataContext";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";

export function OptimizationResults() {
  const { run, orders, loading, error, backendAvailable } = useAppData();
  const [selectedCluster, setSelectedCluster] = useState<string>("all");
  const [selectedVehicle, setSelectedVehicle] = useState<string>("all");

  const clusters = Array.from(new Set(run.routes.map(r => r.cluster)));
  
  const filteredRoutes = run.routes.filter(route => {
    if (selectedCluster !== "all" && route.cluster !== parseInt(selectedCluster)) return false;
    if (selectedVehicle !== "all" && route.vehicleId !== selectedVehicle) return false;
    return true;
  });

  if (loading) {
    return <div className="p-8 text-slate-600">Cargando datos de backend...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-slate-900 mb-2">Resultados</h1>
          <p className="text-slate-600">{run.name} · {run.date}</p>
          {!backendAvailable && <p className="text-xs text-amber-600 mt-1">Backend no disponible. Verifica python backend/api_server.py y npm run dev.</p>}
          {backendAvailable && error && <p className="text-xs text-slate-500 mt-1">No se pudieron refrescar algunos datos.</p>}
        </div>
        <div className="flex gap-2">
          <Link to="/fleet-map">
            <Button>
              <MapPin className="size-4 mr-2" />
              Ver en Mapa
            </Button>
          </Link>
          <Link to="/exports">
            <Button variant="outline">Exportar Resultados</Button>
          </Link>
        </div>
      </div>

      {/* Global KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-slate-600 mb-1">Entregas a Tiempo</p>
            <p className="text-2xl font-semibold text-green-600 mb-1">{run.onTimePercentage}%</p>
            <p className="text-xs text-slate-500">{Math.round(run.assignedOrders * run.onTimePercentage / 100)}/{run.assignedOrders} pedidos</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-slate-600 mb-1">Costo Total</p>
            <p className="text-2xl font-semibold text-slate-900 mb-1">${run.totalCost.toFixed(0)}</p>
            <p className="text-xs text-slate-500">{run.totalDistanceKm.toFixed(1)} km</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-slate-600 mb-1">Flota Utilizada</p>
            <p className="text-2xl font-semibold text-slate-900 mb-1">{run.totalVehiclesUsed}/{run.totalVehiclesAvailable}</p>
            <p className="text-xs text-slate-500">{((run.totalVehiclesUsed / run.totalVehiclesAvailable) * 100).toFixed(0)}% utilización</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-slate-600 mb-1">Utilización Promedio</p>
            <p className="text-2xl font-semibold text-blue-600 mb-1">{run.averageUtilization}%</p>
            <p className="text-xs text-slate-500">Volumen/capacidad</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <p className="text-xs text-slate-600 mb-1">Tiempo de Ejecución</p>
            <p className="text-2xl font-semibold text-slate-900 mb-1">{run.executionTimeSeconds}s</p>
            <p className="text-xs text-slate-500">Pipeline completo</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <Filter className="size-5 text-slate-600" />
            <div className="flex items-center gap-3 flex-1">
              <div className="w-48">
                <Select value={selectedCluster} onValueChange={setSelectedCluster}>
                  <SelectTrigger>
                    <SelectValue placeholder="Cluster" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los clusters</SelectItem>
                    {clusters.map(cluster => (
                      <SelectItem key={cluster} value={cluster.toString()}>
                        Cluster {cluster}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="w-48">
                <Select value={selectedVehicle} onValueChange={setSelectedVehicle}>
                  <SelectTrigger>
                    <SelectValue placeholder="Vehículo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los vehículos</SelectItem>
                    {run.routes.map(route => (
                      <SelectItem key={route.vehicleId} value={route.vehicleId}>
                        {route.vehicleName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {(selectedCluster !== "all" || selectedVehicle !== "all") && (
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => {
                    setSelectedCluster("all");
                    setSelectedVehicle("all");
                  }}
                >
                  Limpiar filtros
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Routes */}
      <Card>
        <CardHeader>
          <CardTitle>Rutas Asignadas ({filteredRoutes.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="summary">
            <TabsList>
              <TabsTrigger value="summary">Resumen</TabsTrigger>
              <TabsTrigger value="detailed">Detalle de Paradas</TabsTrigger>
            </TabsList>

            <TabsContent value="summary" className="mt-4">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b text-left text-sm text-slate-600">
                      <th className="pb-3 font-medium">Vehículo</th>
                      <th className="pb-3 font-medium">Cluster</th>
                      <th className="pb-3 font-medium">Paradas</th>
                      <th className="pb-3 font-medium">Distancia Total</th>
                      <th className="pb-3 font-medium">Tiempo Total</th>
                      <th className="pb-3 font-medium">Espera Acumulada</th>
                      <th className="pb-3 font-medium">Utilización Vol.</th>
                      <th className="pb-3 font-medium">Cumplimiento</th>
                      <th className="pb-3 font-medium">Costo</th>
                      <th className="pb-3 font-medium"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredRoutes.map((route) => (
                      <tr key={route.vehicleId} className="border-b last:border-0 hover:bg-slate-50">
                        <td className="py-4">
                          <div className="flex items-center gap-2">
                            <Truck className="size-4 text-slate-400" />
                            <span className="font-medium text-slate-900">{route.vehicleName}</span>
                          </div>
                        </td>
                        <td className="py-4">
                          <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800">
                            Cluster {route.cluster}
                          </span>
                        </td>
                        <td className="py-4 text-sm text-slate-900">{route.stops.length} paradas</td>
                        <td className="py-4 text-sm text-slate-900">{route.totalDistanceKm.toFixed(1)} km</td>
                        <td className="py-4 text-sm text-slate-900">
                          {Math.floor(route.totalTimeMinutes / 60)}h {route.totalTimeMinutes % 60}m
                        </td>
                        <td className="py-4">
                          <span className={`text-sm font-medium ${route.totalWaitTimeMinutes > 30 ? 'text-amber-600' : 'text-slate-900'}`}>
                            {route.totalWaitTimeMinutes} min
                          </span>
                          {route.totalWaitTimeMinutes > 30 && (
                            <AlertTriangle className="inline size-3 ml-1 text-amber-600" />
                          )}
                        </td>
                        <td className="py-4">
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-slate-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${
                                  route.utilizationVolume >= 90 ? 'bg-green-600' :
                                  route.utilizationVolume >= 70 ? 'bg-blue-600' :
                                  'bg-amber-600'
                                }`}
                                style={{ width: `${route.utilizationVolume}%` }}
                              />
                            </div>
                            <span className="text-sm text-slate-600">{route.utilizationVolume.toFixed(0)}%</span>
                          </div>
                        </td>
                        <td className="py-4">
                          <StatusBadge 
                            status={route.onTimeDeliveries === route.ordersDelivered ? 'on-time' : 'violation'}
                            label={`${route.onTimeDeliveries}/${route.ordersDelivered}`}
                          />
                        </td>
                        <td className="py-4 text-sm font-medium text-slate-900">
                          ${route.totalCost.toFixed(2)}
                        </td>
                        <td className="py-4">
                          <Link to={`/vehicle/${route.vehicleId}`}>
                            <Button variant="ghost" size="sm">
                              <Eye className="size-4 mr-1" />
                              Ver
                            </Button>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </TabsContent>

            <TabsContent value="detailed" className="mt-4">
              <div className="space-y-6">
                {filteredRoutes.map((route) => (
                  <Card key={route.vehicleId}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Truck className="size-5 text-slate-600" />
                          <div>
                            <CardTitle className="text-lg">{route.vehicleName}</CardTitle>
                            <p className="text-sm text-slate-600">Cluster {route.cluster} - {route.stops.length} paradas</p>
                          </div>
                        </div>
                        <Link to={`/vehicle/${route.vehicleId}`}>
                          <Button size="sm" variant="outline">Ver detalle completo</Button>
                        </Link>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {route.stops.map((stop, index) => {
                          const order = orders.find(o => o.id === stop.orderId);
                          return (
                            <div 
                              key={stop.orderId} 
                              className="flex items-start gap-4 p-3 rounded-lg border border-slate-200 hover:bg-slate-50"
                            >
                              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600 font-semibold text-sm flex-shrink-0">
                                {stop.sequence}
                              </div>
                              
                              <div className="flex-1 min-w-0">
                                <div className="flex items-start justify-between mb-1">
                                  <div>
                                    <p className="font-medium text-slate-900">{order?.customerName}</p>
                                    <p className="text-sm text-slate-600">{order?.address}</p>
                                  </div>
                                  <StatusBadge status={stop.isOnTime ? 'on-time' : 'violation'} />
                                </div>
                                
                                <div className="grid grid-cols-5 gap-4 mt-2 text-xs">
                                  <div>
                                    <p className="text-slate-500">Llegada</p>
                                    <p className="font-medium text-slate-900">{stop.arrivalTime}</p>
                                  </div>
                                  <div>
                                    <p className="text-slate-500">Salida</p>
                                    <p className="font-medium text-slate-900">{stop.departureTime}</p>
                                  </div>
                                  <div>
                                    <p className="text-slate-500">Espera</p>
                                    <p className={`font-medium ${stop.waitTimeMinutes > 0 ? 'text-amber-600' : 'text-slate-900'}`}>
                                      {stop.waitTimeMinutes} min
                                    </p>
                                  </div>
                                  <div>
                                    <p className="text-slate-500">Distancia</p>
                                    <p className="font-medium text-slate-900">{stop.distanceFromPreviousKm.toFixed(1)} km</p>
                                  </div>
                                  <div>
                                    <p className="text-slate-500">Ventana</p>
                                    <p className="font-medium text-slate-900">{order?.timeWindowStart} - {order?.timeWindowEnd}</p>
                                  </div>
                                </div>

                                {stop.timeWindowViolationMinutes > 0 && (
                                  <div className="mt-2 p-2 bg-red-50 rounded text-xs text-red-800">
                                    ⚠️ Violación de ventana: {stop.timeWindowViolationMinutes} minutos de retraso
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Unassigned Orders */}
      {run.unassignedOrders > 0 && (
        <Card className="border-l-4 border-l-red-500 bg-red-50">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertTriangle className="size-5 text-red-600" />
              <CardTitle>Pedidos No Asignados</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-red-900 mb-3">
              {run.unassignedOrders} pedido(s) no pudo(eron) ser asignado(s) para esta fecha.
            </p>
            <div className="space-y-2">
              {orders.filter(o => o.status === 'unassigned').map(order => (
                <div key={order.id} className="flex items-center justify-between p-2 bg-white rounded border border-red-200">
                  <div>
                    <p className="font-medium text-sm text-slate-900">{order.id}</p>
                    <p className="text-xs text-slate-600">{order.customerName} - {order.comuna}</p>
                  </div>
                  <div className="text-xs text-red-700">
                    Sin vehículo disponible en turno requerido
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
