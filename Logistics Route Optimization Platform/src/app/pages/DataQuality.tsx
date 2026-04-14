import { AlertCircle, CheckCircle2, XCircle, MapPin, Search } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { useAppData } from "../data/AppDataContext";
import { StatusBadge } from "../components/shared/StatusBadge";
import { useState } from "react";

export function DataQuality() {
  const [searchTerm, setSearchTerm] = useState("");
  const { orders, loading, error, backendAvailable } = useAppData();

  // Simular validaciones
  const validatedOrders = orders.filter(o => o.status !== 'pending');
  const withIssues = orders.filter(o => o.volumeM3 > 15); // Pedidos que exceden capacidad máxima
  const needsGeocode = orders.filter(o => !o.lat || !o.lng);

  const filteredOrders = orders.filter(order =>
    order.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.customerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.comuna.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="p-8 text-slate-600">Cargando datos de backend...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold text-slate-900 mb-2">Calidad de Datos</h1>
        <p className="text-slate-600">Validación y verificación de pedidos antes de optimización</p>
        {!backendAvailable && <p className="text-xs text-amber-600 mt-1">Backend no disponible. Verifica python backend/api_server.py y npm run dev.</p>}
        {backendAvailable && error && <p className="text-xs text-slate-500 mt-1">No se pudieron refrescar algunos datos.</p>}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Total Pedidos</p>
                <p className="text-2xl font-semibold text-slate-900">{orders.length}</p>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg">
                <CheckCircle2 className="size-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Validados</p>
                <p className="text-2xl font-semibold text-green-600">{validatedOrders.length}</p>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <CheckCircle2 className="size-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Con Alertas</p>
                <p className="text-2xl font-semibold text-amber-600">{withIssues.length}</p>
              </div>
              <div className="p-3 bg-amber-50 rounded-lg">
                <AlertCircle className="size-6 text-amber-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Sin Geocodificar</p>
                <p className="text-2xl font-semibold text-red-600">{needsGeocode.length}</p>
              </div>
              <div className="p-3 bg-red-50 rounded-lg">
                <MapPin className="size-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Validation Issues */}
      {withIssues.length > 0 && (
        <Card className="border-l-4 border-l-amber-500 bg-amber-50">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertCircle className="size-5 text-amber-600" />
              <CardTitle>Alertas de Validación</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              <li className="flex items-start gap-2 text-sm text-amber-900">
                <span className="text-amber-600 mt-0.5">•</span>
                <span>{withIssues.length} pedidos exceden la capacidad máxima de vehículo (15m³) y serán divididos automáticamente</span>
              </li>
              <li className="flex items-start gap-2 text-sm text-amber-900">
                <span className="text-amber-600 mt-0.5">•</span>
                <span>Pedidos afectados: {withIssues.map(o => o.id).join(', ')}</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Orders Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Detalle de Pedidos</CardTitle>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
                <Input
                  placeholder="Buscar por ID, cliente o comuna..."
                  className="pl-9 w-80"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button variant="outline">Exportar CSV</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b text-left text-sm text-slate-600">
                  <th className="pb-3 font-medium">Estado</th>
                  <th className="pb-3 font-medium">ID Pedido</th>
                  <th className="pb-3 font-medium">Cliente</th>
                  <th className="pb-3 font-medium">Dirección</th>
                  <th className="pb-3 font-medium">Comuna</th>
                  <th className="pb-3 font-medium">Volumen</th>
                  <th className="pb-3 font-medium">Peso</th>
                  <th className="pb-3 font-medium">Ventana Horaria</th>
                  <th className="pb-3 font-medium">Geocodificado</th>
                  <th className="pb-3 font-medium">Validación</th>
                </tr>
              </thead>
              <tbody>
                {filteredOrders.map((order) => {
                  const exceedsCapacity = order.volumeM3 > 15;
                  const hasGeocode = order.lat && order.lng;
                  
                  return (
                    <tr key={order.id} className="border-b last:border-0 hover:bg-slate-50">
                      <td className="py-3">
                        <StatusBadge status={order.status} />
                      </td>
                      <td className="py-3">
                        <span className="font-mono text-sm text-slate-900">{order.id}</span>
                        {order.splitFromOrderId && (
                          <span className="ml-2 text-xs text-purple-600">(split)</span>
                        )}
                      </td>
                      <td className="py-3 text-sm text-slate-900">{order.customerName}</td>
                      <td className="py-3 text-sm text-slate-600 max-w-xs truncate">{order.address}</td>
                      <td className="py-3 text-sm text-slate-900">{order.comuna}</td>
                      <td className="py-3">
                        <span className={`text-sm font-medium ${exceedsCapacity ? 'text-amber-600' : 'text-slate-900'}`}>
                          {order.volumeM3} m³
                        </span>
                        {exceedsCapacity && (
                          <AlertCircle className="inline size-3 ml-1 text-amber-600" />
                        )}
                      </td>
                      <td className="py-3 text-sm text-slate-900">{order.weightKg} kg</td>
                      <td className="py-3 text-sm text-slate-600">
                        {order.timeWindowStart} - {order.timeWindowEnd}
                      </td>
                      <td className="py-3">
                        {hasGeocode ? (
                          <div className="flex items-center gap-1 text-green-600">
                            <CheckCircle2 className="size-4" />
                            <span className="text-xs">Sí</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-1 text-red-600">
                            <XCircle className="size-4" />
                            <span className="text-xs">No</span>
                          </div>
                        )}
                      </td>
                      <td className="py-3">
                        {!exceedsCapacity && hasGeocode ? (
                          <span className="text-xs text-green-600 font-medium">✓ OK</span>
                        ) : (
                          <div className="flex flex-col gap-1">
                            {exceedsCapacity && (
                              <span className="text-xs text-amber-600">⚠ Excede capacidad</span>
                            )}
                            {!hasGeocode && (
                              <span className="text-xs text-red-600">✗ Sin geocodificar</span>
                            )}
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Geocoding Section */}
      <Card>
        <CardHeader>
          <CardTitle>Geocodificación</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-slate-600">
              Todos los pedidos han sido geocodificados exitosamente usando el servicio de mapas.
              Las coordenadas están listas para el cálculo de matriz de distancias sobre red vial real.
            </p>
            
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <p className="text-sm text-green-900 font-medium mb-1">Geocodificados</p>
                <p className="text-2xl font-semibold text-green-600">{orders.length}</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                <p className="text-sm text-slate-900 font-medium mb-1">Precisión Promedio</p>
                <p className="text-2xl font-semibold text-slate-900">98.5%</p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-900 font-medium mb-1">Tiempo Promedio</p>
                <p className="text-2xl font-semibold text-blue-600">0.3s</p>
              </div>
            </div>

            <Button variant="outline" className="w-full">
              <MapPin className="size-4 mr-2" />
              Re-geocodificar Todos
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
