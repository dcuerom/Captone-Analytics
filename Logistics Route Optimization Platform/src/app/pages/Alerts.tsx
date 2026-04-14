import { AlertTriangle, AlertCircle, Clock, Truck, Package, XCircle, Filter } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { StatusBadge } from "../components/shared/StatusBadge";
import { useAppData } from "../data/AppDataContext";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { useState } from "react";

interface Alert {
  id: string;
  type: 'critical' | 'warning' | 'info';
  category: 'capacity' | 'time' | 'assignment' | 'geocode' | 'split';
  title: string;
  description: string;
  affectedOrders?: string[];
  affectedVehicles?: string[];
  timestamp: string;
}

export function Alerts() {
  const [filterType, setFilterType] = useState<string>("all");
  const [filterCategory, setFilterCategory] = useState<string>("all");

  const { run, orders, loading, error, backendAvailable } = useAppData();
  if (loading) {
    return <div className="p-8 text-slate-600">Cargando datos de backend...</div>;
  }

  // Generate alerts from run data
  const alerts: Alert[] = [];

  // Pedidos no asignados
  const unassignedOrders = orders.filter(o => o.status === 'unassigned');
  if (unassignedOrders.length > 0) {
    alerts.push({
      id: 'alert-001',
      type: 'critical',
      category: 'assignment',
      title: 'Pedidos sin asignar',
      description: `${unassignedOrders.length} pedido(s) no pudieron ser asignados por falta de vehículos disponibles en el turno requerido.`,
      affectedOrders: unassignedOrders.map(o => o.id),
      timestamp: '2026-04-06T10:30:00'
    });
  }

  // Pedidos divididos por capacidad
  const splitOrders = orders.filter(o => o.status === 'split');
  if (splitOrders.length > 0) {
    alerts.push({
      id: 'alert-002',
      type: 'warning',
      category: 'split',
      title: 'Pedidos divididos por capacidad',
      description: `${splitOrders.length} pedido(s) fueron divididos en subpedidos porque exceden la capacidad máxima de los vehículos disponibles (15m³).`,
      affectedOrders: splitOrders.map(o => o.id),
      timestamp: '2026-04-06T10:25:00'
    });
  }

  // Rutas con alta espera
  const routesWithHighWait = run.routes.filter(r => r.totalWaitTimeMinutes > 30);
  if (routesWithHighWait.length > 0) {
    routesWithHighWait.forEach((route, index) => {
      alerts.push({
        id: `alert-wait-${index}`,
        type: 'warning',
        category: 'time',
        title: 'Espera excesiva en ruta',
        description: `${route.vehicleName} tiene ${route.totalWaitTimeMinutes} minutos de espera acumulada para cumplir ventanas horarias. Considere re-secuenciar paradas.`,
        affectedVehicles: [route.vehicleId],
        timestamp: '2026-04-06T10:28:00'
      });
    });
  }

  // Violaciones de ventana horaria
  run.routes.forEach(route => {
    const violatedStops = route.stops.filter(s => !s.isOnTime);
    if (violatedStops.length > 0) {
      alerts.push({
        id: `alert-violation-${route.vehicleId}`,
        type: 'critical',
        category: 'time',
        title: 'Violaciones de ventana horaria',
        description: `${route.vehicleName} tiene ${violatedStops.length} parada(s) fuera de ventana horaria con retrasos de hasta ${Math.max(...violatedStops.map(s => s.timeWindowViolationMinutes))} minutos.`,
        affectedVehicles: [route.vehicleId],
        affectedOrders: violatedStops.map(s => s.orderId),
        timestamp: '2026-04-06T10:32:00'
      });
    }
  });

  // Baja utilización
  const lowUtilizationRoutes = run.routes.filter(r => r.utilizationVolume < 60);
  if (lowUtilizationRoutes.length > 0) {
    lowUtilizationRoutes.forEach((route, index) => {
      alerts.push({
        id: `alert-util-${index}`,
        type: 'info',
        category: 'capacity',
        title: 'Baja utilización de capacidad',
        description: `${route.vehicleName} opera con solo ${route.utilizationVolume.toFixed(0)}% de utilización. Considere consolidar con otra ruta.`,
        affectedVehicles: [route.vehicleId],
        timestamp: '2026-04-06T10:35:00'
      });
    });
  }

  // Filtrar alertas
  const filteredAlerts = alerts.filter(alert => {
    if (filterType !== "all" && alert.type !== filterType) return false;
    if (filterCategory !== "all" && alert.category !== filterCategory) return false;
    return true;
  });

  const criticalCount = alerts.filter(a => a.type === 'critical').length;
  const warningCount = alerts.filter(a => a.type === 'warning').length;
  const infoCount = alerts.filter(a => a.type === 'info').length;

  const getAlertIcon = (type: Alert['type']) => {
    switch (type) {
      case 'critical': return XCircle;
      case 'warning': return AlertTriangle;
      case 'info': return AlertCircle;
    }
  };

  const getAlertColor = (type: Alert['type']) => {
    switch (type) {
      case 'critical': return 'border-red-500 bg-red-50';
      case 'warning': return 'border-amber-500 bg-amber-50';
      case 'info': return 'border-blue-500 bg-blue-50';
    }
  };

  const getCategoryLabel = (category: Alert['category']) => {
    switch (category) {
      case 'capacity': return 'Capacidad';
      case 'time': return 'Tiempo';
      case 'assignment': return 'Asignación';
      case 'geocode': return 'Geocodificación';
      case 'split': return 'División';
    }
  };

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold text-slate-900 mb-2">Alertas y Excepciones Operativas</h1>
        <p className="text-slate-600">Monitor de advertencias, violaciones y oportunidades de mejora</p>
        {!backendAvailable && <p className="text-xs text-amber-600 mt-1">Backend no disponible. Verifica python backend/api_server.py y npm run dev.</p>}
        {backendAvailable && error && <p className="text-xs text-slate-500 mt-1">No se pudieron refrescar algunos datos.</p>}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Total Alertas</p>
                <p className="text-3xl font-semibold text-slate-900">{alerts.length}</p>
              </div>
              <div className="p-3 bg-slate-100 rounded-lg">
                <AlertCircle className="size-6 text-slate-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Críticas</p>
                <p className="text-3xl font-semibold text-red-600">{criticalCount}</p>
              </div>
              <div className="p-3 bg-red-100 rounded-lg">
                <XCircle className="size-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Advertencias</p>
                <p className="text-3xl font-semibold text-amber-600">{warningCount}</p>
              </div>
              <div className="p-3 bg-amber-100 rounded-lg">
                <AlertTriangle className="size-6 text-amber-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600 mb-1">Informativas</p>
                <p className="text-3xl font-semibold text-blue-600">{infoCount}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <AlertCircle className="size-6 text-blue-600" />
              </div>
            </div>
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
                <Select value={filterType} onValueChange={setFilterType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos los tipos</SelectItem>
                    <SelectItem value="critical">Críticas</SelectItem>
                    <SelectItem value="warning">Advertencias</SelectItem>
                    <SelectItem value="info">Informativas</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="w-48">
                <Select value={filterCategory} onValueChange={setFilterCategory}>
                  <SelectTrigger>
                    <SelectValue placeholder="Categoría" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todas las categorías</SelectItem>
                    <SelectItem value="capacity">Capacidad</SelectItem>
                    <SelectItem value="time">Tiempo</SelectItem>
                    <SelectItem value="assignment">Asignación</SelectItem>
                    <SelectItem value="split">División</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {(filterType !== "all" || filterCategory !== "all") && (
                <button
                  className="text-sm text-slate-600 hover:text-slate-900"
                  onClick={() => {
                    setFilterType("all");
                    setFilterCategory("all");
                  }}
                >
                  Limpiar filtros
                </button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Alerts List */}
      <Tabs defaultValue="all">
        <TabsList>
          <TabsTrigger value="all">Todas ({filteredAlerts.length})</TabsTrigger>
          <TabsTrigger value="critical">Críticas ({criticalCount})</TabsTrigger>
          <TabsTrigger value="warning">Advertencias ({warningCount})</TabsTrigger>
          <TabsTrigger value="info">Informativas ({infoCount})</TabsTrigger>
        </TabsList>

        {['all', 'critical', 'warning', 'info'].map(tab => (
          <TabsContent key={tab} value={tab} className="space-y-4 mt-6">
            {filteredAlerts
              .filter(alert => tab === 'all' || alert.type === tab)
              .map(alert => {
                const Icon = getAlertIcon(alert.type);
                return (
                  <Card key={alert.id} className={`border-l-4 ${getAlertColor(alert.type)}`}>
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        <div className={`p-2 rounded-lg ${
                          alert.type === 'critical' ? 'bg-red-200' :
                          alert.type === 'warning' ? 'bg-amber-200' :
                          'bg-blue-200'
                        }`}>
                          <Icon className={`size-5 ${
                            alert.type === 'critical' ? 'text-red-700' :
                            alert.type === 'warning' ? 'text-amber-700' :
                            'text-blue-700'
                          }`} />
                        </div>

                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h3 className={`font-semibold ${
                                alert.type === 'critical' ? 'text-red-900' :
                                alert.type === 'warning' ? 'text-amber-900' :
                                'text-blue-900'
                              }`}>
                                {alert.title}
                              </h3>
                              <p className="text-xs text-slate-500 mt-1">
                                {new Date(alert.timestamp).toLocaleString('es-CL')}
                              </p>
                            </div>
                            <StatusBadge
                              status={
                                alert.type === 'critical' ? 'violation' :
                                alert.type === 'warning' ? 'waiting' :
                                'assigned'
                              }
                              label={getCategoryLabel(alert.category)}
                            />
                          </div>

                          <p className={`text-sm mb-3 ${
                            alert.type === 'critical' ? 'text-red-800' :
                            alert.type === 'warning' ? 'text-amber-800' :
                            'text-blue-800'
                          }`}>
                            {alert.description}
                          </p>

                          <div className="flex items-center gap-4 text-xs">
                            {alert.affectedOrders && alert.affectedOrders.length > 0 && (
                              <div className="flex items-center gap-2">
                                <Package className="size-3 text-slate-500" />
                                <span className="text-slate-600">
                                  Pedidos afectados: {alert.affectedOrders.join(', ')}
                                </span>
                              </div>
                            )}
                            {alert.affectedVehicles && alert.affectedVehicles.length > 0 && (
                              <div className="flex items-center gap-2">
                                <Truck className="size-3 text-slate-500" />
                                <span className="text-slate-600">
                                  Vehículos: {alert.affectedVehicles.join(', ')}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}

            {filteredAlerts.filter(alert => tab === 'all' || alert.type === tab).length === 0 && (
              <div className="text-center py-12">
                <AlertCircle className="size-12 text-slate-300 mx-auto mb-3" />
                <p className="text-slate-600">No hay alertas de este tipo</p>
              </div>
            )}
          </TabsContent>
        ))}
      </Tabs>

      {/* Recommendations */}
      <Card className="border-l-4 border-l-green-500 bg-green-50">
        <CardHeader>
          <CardTitle className="text-green-900">Recomendaciones del Sistema</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            <li className="flex items-start gap-2 text-sm text-green-800">
              <span className="text-green-600 mt-0.5">✓</span>
              <span>
                Habilite vehículo V006 (actualmente no disponible) para asignar pedido ORD015 pendiente.
              </span>
            </li>
            <li className="flex items-start gap-2 text-sm text-green-800">
              <span className="text-green-600 mt-0.5">✓</span>
              <span>
                Considere negociar ventanas horarias más flexibles con clientes del cluster 2 para reducir espera.
              </span>
            </li>
            <li className="flex items-start gap-2 text-sm text-green-800">
              <span className="text-green-600 mt-0.5">✓</span>
              <span>
                Consolide rutas V001 y V004 (ambas con baja utilización) para optimizar costos.
              </span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
