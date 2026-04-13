import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from "react-leaflet";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { StatusBadge } from "../components/shared/StatusBadge";
import { useAppData } from "../data/AppDataContext";
import { getBackendMapUrl } from "../data/api";
import { Truck, MapPin, Clock } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import "leaflet/dist/leaflet.css";

// Colores por cluster
const CLUSTER_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export function FleetMap() {
  const [selectedRoute, setSelectedRoute] = useState<string>("all");
  const [mapReady, setMapReady] = useState(false);
  const [useBackendMap, setUseBackendMap] = useState(true);
  const { run, orders, loading, error } = useAppData();
  const centerLat = -33.4489;
  const centerLng = -70.6693;

  useEffect(() => {
    // Fix for Leaflet default marker icons
    setMapReady(true);
  }, []);

  const filteredRoutes = selectedRoute === "all" 
    ? run.routes 
    : run.routes.filter(r => r.vehicleId === selectedRoute);

  if (loading || !mapReady) {
    return (
      <div className="p-8 flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent mx-auto mb-4" />
          <p className="text-slate-600">Cargando mapa...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="p-6 border-b bg-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900 mb-1">Mapa Interactivo de Flota</h1>
            <p className="text-sm text-slate-600">{run.name} - {run.totalVehiclesUsed} vehículos activos</p>
            {error && <p className="text-xs text-amber-600 mt-1">Backend no disponible. Verifica python backend/api_server.py y npm run dev.</p>}
          </div>
          
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={() => setUseBackendMap(v => !v)}>
              {useBackendMap ? "Mapa UI (líneas rectas)" : "Mapa Backend (calles reales)"}
            </Button>
            <div className="w-64">
              <Select value={selectedRoute} onValueChange={setSelectedRoute}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar vehículo" />
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
          </div>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Map */}
        <div className="flex-1 relative">
          {useBackendMap ? (
            <iframe
              src={getBackendMapUrl()}
              title="Mapa Backend Calles Reales"
              className="w-full h-full border-0"
            />
          ) : (
          <MapContainer
            center={[centerLat, centerLng]}
            zoom={11}
            style={{ height: "100%", width: "100%" }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* Draw routes */}
            {filteredRoutes.map((route, routeIndex) => {
              const routeOrders = route.stops.map(stop => 
                orders.find(o => o.id === stop.orderId)
              ).filter(o => o !== undefined);

              const routeColor = CLUSTER_COLORS[route.cluster % CLUSTER_COLORS.length];

              // Polyline connecting all stops
              const coordinates = routeOrders.map(order => [order!.lat, order!.lng] as [number, number]);

              return (
                <div key={route.vehicleId}>
                  {/* Route line */}
                  {coordinates.length > 1 && (
                    <Polyline
                      positions={coordinates}
                      pathOptions={{ color: routeColor, weight: 3, opacity: 0.7 }}
                    />
                  )}

                  {/* Stop markers */}
                  {route.stops.map((stop, stopIndex) => {
                    const order = orders.find(o => o.id === stop.orderId);
                    if (!order) return null;

                    return (
                      <CircleMarker
                        key={stop.orderId}
                        center={[order.lat, order.lng]}
                        radius={8}
                        pathOptions={{
                          fillColor: stop.isOnTime ? '#10b981' : '#ef4444',
                          color: '#fff',
                          weight: 2,
                          fillOpacity: 0.9
                        }}
                      >
                        <Popup>
                          <div className="min-w-64">
                            <div className="flex items-center justify-between mb-2">
                              <p className="font-semibold text-slate-900">Parada {stop.sequence}</p>
                              <StatusBadge status={stop.isOnTime ? 'on-time' : 'violation'} />
                            </div>
                            
                            <div className="space-y-1 text-sm">
                              <div className="flex items-start gap-2">
                                <Truck className="size-4 text-slate-400 mt-0.5" />
                                <div>
                                  <p className="font-medium text-slate-900">{route.vehicleName}</p>
                                  <p className="text-xs text-slate-600">Cluster {route.cluster}</p>
                                </div>
                              </div>

                              <div className="flex items-start gap-2 pt-2 border-t">
                                <MapPin className="size-4 text-slate-400 mt-0.5" />
                                <div>
                                  <p className="font-medium text-slate-900">{order.customerName}</p>
                                  <p className="text-xs text-slate-600">{order.address}</p>
                                  <p className="text-xs text-slate-600">{order.comuna}</p>
                                </div>
                              </div>

                              <div className="flex items-start gap-2 pt-2 border-t">
                                <Clock className="size-4 text-slate-400 mt-0.5" />
                                <div>
                                  <p className="text-xs text-slate-600">
                                    Llegada: <span className="font-medium text-slate-900">{stop.arrivalTime}</span>
                                  </p>
                                  <p className="text-xs text-slate-600">
                                    Ventana: <span className="font-medium text-slate-900">{order.timeWindowStart} - {order.timeWindowEnd}</span>
                                  </p>
                                  {stop.waitTimeMinutes > 0 && (
                                    <p className="text-xs text-amber-600 mt-1">
                                      ⏱️ Espera: {stop.waitTimeMinutes} min
                                    </p>
                                  )}
                                </div>
                              </div>

                              <div className="pt-2 border-t">
                                <p className="text-xs text-slate-600">
                                  Carga: {order.volumeM3}m³ / {order.weightKg}kg
                                </p>
                                <p className="text-xs text-slate-600">
                                  Desde parada anterior: {stop.distanceFromPreviousKm.toFixed(1)}km
                                </p>
                              </div>
                            </div>
                          </div>
                        </Popup>
                      </CircleMarker>
                    );
                  })}
                </div>
              );
            })}
          </MapContainer>
          )}
        </div>

        {/* Right Panel - Route Info */}
        <div className="w-80 border-l bg-white overflow-y-auto">
          <div className="p-4 space-y-4">
            <div>
              <h3 className="font-semibold text-slate-900 mb-2">Leyenda</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-4 h-4 rounded-full bg-green-600" />
                  <span className="text-slate-700">Entrega a tiempo</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <div className="w-4 h-4 rounded-full bg-red-600" />
                  <span className="text-slate-700">Violación de ventana</span>
                </div>
                {CLUSTER_COLORS.slice(0, Math.max(...run.routes.map(r => r.cluster))).map((color, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <div className="w-4 h-1 rounded" style={{ backgroundColor: color }} />
                    <span className="text-slate-700">Ruta Cluster {i + 1}</span>
                  </div>
                ))}
              </div>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Resumen de Rutas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {filteredRoutes.map((route) => (
                  <div 
                    key={route.vehicleId}
                    className="p-3 border rounded-lg hover:bg-slate-50 cursor-pointer"
                    onClick={() => setSelectedRoute(route.vehicleId)}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Truck className="size-4 text-slate-600" />
                        <span className="font-medium text-sm text-slate-900">{route.vehicleName}</span>
                      </div>
                      <span 
                        className="px-2 py-0.5 text-xs font-medium rounded"
                        style={{ 
                          backgroundColor: CLUSTER_COLORS[route.cluster % CLUSTER_COLORS.length] + '20',
                          color: CLUSTER_COLORS[route.cluster % CLUSTER_COLORS.length]
                        }}
                      >
                        C{route.cluster}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <p className="text-slate-500">Paradas</p>
                        <p className="font-medium text-slate-900">{route.stops.length}</p>
                      </div>
                      <div>
                        <p className="text-slate-500">Distancia</p>
                        <p className="font-medium text-slate-900">{route.totalDistanceKm.toFixed(1)} km</p>
                      </div>
                      <div>
                        <p className="text-slate-500">Cumplimiento</p>
                        <p className="font-medium text-slate-900">{route.onTimeDeliveries}/{route.ordersDelivered}</p>
                      </div>
                      <div>
                        <p className="text-slate-500">Utilización</p>
                        <p className="font-medium text-slate-900">{route.utilizationVolume.toFixed(0)}%</p>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="p-4">
                <h4 className="font-medium text-blue-900 text-sm mb-2">Clustering DBSCAN</h4>
                <p className="text-xs text-blue-800">
                  Las rutas fueron agrupadas espacialmente usando DBSCAN antes de la optimización.
                  Cada color representa un cluster geográfico diferente.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
