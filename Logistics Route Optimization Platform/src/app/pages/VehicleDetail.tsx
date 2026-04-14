import { useParams, Link } from "react-router";
import { ArrowLeft, Truck, MapPin, Clock, TrendingUp, Package } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { StatusBadge } from "../components/shared/StatusBadge";
import { useAppData } from "../data/AppDataContext";
import { Progress } from "../components/ui/progress";

export function VehicleDetail() {
  const { id } = useParams<{ id: string }>();
  const { run, orders, fleet, loading, error, backendAvailable } = useAppData();

  if (loading) {
    return <div className="p-8 text-slate-600">Cargando datos de backend...</div>;
  }

  const route = run.routes.find(r => r.vehicleId === id);
  const vehicle = fleet.find(v => v.id === id);

  if (!route || !vehicle) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <Truck className="size-16 text-slate-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Vehículo no encontrado</h2>
          <p className="text-slate-600 mb-4">No se encontró información para el vehículo {id}</p>
          <Link to="/optimization-results">
            <Button>Volver a resultados</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to="/optimization-results">
          <Button variant="outline" size="icon">
            <ArrowLeft className="size-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <Truck className="size-6 text-slate-600" />
            <h1 className="text-3xl font-semibold text-slate-900">{route.vehicleName}</h1>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded">
              Cluster {route.cluster}
            </span>
          </div>
          <p className="text-slate-600">Detalle de ruta y paradas asignadas</p>
          {!backendAvailable && <p className="text-xs text-amber-600 mt-1">Backend no disponible. Verifica python backend/api_server.py y npm run dev.</p>}
          {backendAvailable && error && <p className="text-xs text-slate-500 mt-1">No se pudieron refrescar algunos datos.</p>}
        </div>
        <Link to="/fleet-map">
          <Button>
            <MapPin className="size-4 mr-2" />
            Ver en mapa
          </Button>
        </Link>
      </div>

      {/* Vehicle Info & KPIs */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Información del Vehículo</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <p className="text-xs text-slate-600">Capacidad Volumen</p>
              <p className="text-lg font-semibold text-slate-900">{vehicle.capacityM3} m³</p>
            </div>
            <div>
              <p className="text-xs text-slate-600">Capacidad Peso</p>
              <p className="text-lg font-semibold text-slate-900">{vehicle.capacityKg} kg</p>
            </div>
            <div>
              <p className="text-xs text-slate-600">Turno</p>
              <p className="text-sm font-medium text-slate-900 capitalize">{vehicle.shift}</p>
            </div>
            <div>
              <p className="text-xs text-slate-600">Costo por km</p>
              <p className="text-sm font-medium text-slate-900">${vehicle.costPerKm}</p>
            </div>
            <div>
              <p className="text-xs text-slate-600">Costo por hora</p>
              <p className="text-sm font-medium text-slate-900">${vehicle.costPerHour}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-slate-600">Distancia Total</p>
              <TrendingUp className="size-4 text-blue-600" />
            </div>
            <p className="text-3xl font-semibold text-slate-900 mb-1">{route.totalDistanceKm.toFixed(1)}</p>
            <p className="text-sm text-slate-600">kilómetros</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-slate-600">Tiempo Total</p>
              <Clock className="size-4 text-blue-600" />
            </div>
            <p className="text-3xl font-semibold text-slate-900 mb-1">
              {Math.floor(route.totalTimeMinutes / 60)}h {route.totalTimeMinutes % 60}m
            </p>
            <p className="text-sm text-slate-600">incluye {route.totalWaitTimeMinutes}min espera</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-slate-600">Costo Total</p>
              <Package className="size-4 text-blue-600" />
            </div>
            <p className="text-3xl font-semibold text-slate-900 mb-1">${route.totalCost.toFixed(2)}</p>
            <p className="text-sm text-slate-600">{route.ordersDelivered} pedidos</p>
          </CardContent>
        </Card>
      </div>

      {/* Utilization */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Utilización de Capacidad</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-600">Volumen</span>
                <span className="text-sm font-medium text-slate-900">
                  {route.loadVolumeM3.toFixed(1)} / {vehicle.capacityM3} m³ ({route.utilizationVolume.toFixed(1)}%)
                </span>
              </div>
              <Progress value={route.utilizationVolume} className="h-3" />
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-600">Peso</span>
                <span className="text-sm font-medium text-slate-900">
                  {route.loadWeightKg} / {vehicle.capacityKg} kg ({route.utilizationWeight.toFixed(1)}%)
                </span>
              </div>
              <Progress value={route.utilizationWeight} className="h-3" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Cumplimiento de Entregas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-4">
              <div className="inline-flex items-center justify-center w-32 h-32 rounded-full border-8 border-green-100 mb-3">
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-600">
                    {((route.onTimeDeliveries / route.ordersDelivered) * 100).toFixed(0)}%
                  </p>
                  <p className="text-xs text-slate-600">a tiempo</p>
                </div>
              </div>
              <p className="text-sm text-slate-600">
                {route.onTimeDeliveries} de {route.ordersDelivered} entregas cumplieron ventana horaria
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Route Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Cronograma de Ruta</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {route.stops.map((stop, index) => {
              const order = orders.find(o => o.id === stop.orderId);
              const isLast = index === route.stops.length - 1;

              return (
                <div key={stop.orderId} className="relative">
                  <div className="flex gap-4">
                    {/* Timeline */}
                    <div className="flex flex-col items-center">
                      <div className={`flex items-center justify-center w-10 h-10 rounded-full font-semibold text-sm ${
                        stop.isOnTime 
                          ? 'bg-green-100 text-green-700 border-2 border-green-300' 
                          : 'bg-red-100 text-red-700 border-2 border-red-300'
                      }`}>
                        {stop.sequence}
                      </div>
                      {!isLast && (
                        <div className="w-0.5 h-full min-h-16 bg-slate-200 my-1" />
                      )}
                    </div>

                    {/* Stop Content */}
                    <div className="flex-1 pb-8">
                      <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h4 className="font-semibold text-slate-900">{order?.customerName}</h4>
                            <div className="flex items-center gap-2 mt-1">
                              <MapPin className="size-3 text-slate-400" />
                              <p className="text-sm text-slate-600">{order?.address}, {order?.comuna}</p>
                            </div>
                          </div>
                          <StatusBadge status={stop.isOnTime ? 'on-time' : 'violation'} />
                        </div>

                        <div className="grid grid-cols-2 lg:grid-cols-6 gap-3 text-sm">
                          <div>
                            <p className="text-xs text-slate-500 mb-0.5">Llegada</p>
                            <p className="font-medium text-slate-900">{stop.arrivalTime}</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-500 mb-0.5">Salida</p>
                            <p className="font-medium text-slate-900">{stop.departureTime}</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-500 mb-0.5">Ventana</p>
                            <p className="font-medium text-slate-900 text-xs">{order?.timeWindowStart}-{order?.timeWindowEnd}</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-500 mb-0.5">Espera</p>
                            <p className={`font-medium ${stop.waitTimeMinutes > 0 ? 'text-amber-600' : 'text-slate-900'}`}>
                              {stop.waitTimeMinutes} min
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-500 mb-0.5">Distancia</p>
                            <p className="font-medium text-slate-900">{stop.distanceFromPreviousKm.toFixed(1)} km</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-500 mb-0.5">Carga</p>
                            <p className="font-medium text-slate-900 text-xs">{order?.volumeM3}m³ / {order?.weightKg}kg</p>
                          </div>
                        </div>

                        {stop.waitTimeMinutes > 0 && (
                          <div className="mt-3 p-2 bg-amber-50 border border-amber-200 rounded text-xs text-amber-900">
                            <Clock className="inline size-3 mr-1" />
                            Espera de {stop.waitTimeMinutes} minutos para cumplir ventana horaria
                          </div>
                        )}

                        {stop.timeWindowViolationMinutes > 0 && (
                          <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-900">
                            ⚠️ Violación de ventana: llegada {stop.timeWindowViolationMinutes} minutos después del cierre
                          </div>
                        )}

                        {order?.splitFromOrderId && (
                          <div className="mt-3 p-2 bg-purple-50 border border-purple-200 rounded text-xs text-purple-900">
                            📦 Este pedido fue dividido del pedido original {order.splitFromOrderId} por exceder capacidad del vehículo
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Cost Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Desglose de Costos</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-600 mb-1">Costo por Distancia</p>
              <p className="text-2xl font-semibold text-slate-900">
                ${(route.totalDistanceKm * vehicle.costPerKm).toFixed(2)}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {route.totalDistanceKm.toFixed(1)} km × ${vehicle.costPerKm}/km
              </p>
            </div>
            
            <div className="p-4 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-600 mb-1">Costo por Tiempo</p>
              <p className="text-2xl font-semibold text-slate-900">
                ${((route.totalTimeMinutes / 60) * vehicle.costPerHour).toFixed(2)}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {(route.totalTimeMinutes / 60).toFixed(1)} horas × ${vehicle.costPerHour}/hora
              </p>
            </div>
            
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <p className="text-sm text-blue-900 font-medium mb-1">Costo Total</p>
              <p className="text-2xl font-semibold text-blue-600">
                ${route.totalCost.toFixed(2)}
              </p>
              <p className="text-xs text-blue-700 mt-1">
                Costo por pedido: ${(route.totalCost / route.ordersDelivered).toFixed(2)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
