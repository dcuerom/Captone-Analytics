import { Download, FileText, FileSpreadsheet, FileCode, Eye } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { useAppData } from "../data/AppDataContext";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { StatusBadge } from "../components/shared/StatusBadge";

export function Exports() {
  const { run, historicalRuns, loading, error } = useAppData();

  if (loading) {
    return <div className="p-8 text-slate-600">Cargando datos de backend...</div>;
  }

  const handleExport = (format: string, type: string) => {
    alert(`Exportando ${type} en formato ${format}...\nEn producción, esto generaría y descargaría el archivo.`);
  };

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold text-slate-900 mb-2">Exportación y Trazabilidad</h1>
        <p className="text-slate-600">Descargue resultados y audite el historial de optimizaciones</p>
        {error && <p className="text-xs text-amber-600 mt-1">Backend no disponible. Verifica python backend/api_server.py y npm run dev.</p>}
      </div>

      <Tabs defaultValue="exports">
        <TabsList>
          <TabsTrigger value="exports">Exportar Resultados</TabsTrigger>
          <TabsTrigger value="traceability">Trazabilidad de Corrida</TabsTrigger>
          <TabsTrigger value="history">Historial</TabsTrigger>
        </TabsList>

        {/* Exports Tab */}
        <TabsContent value="exports" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Rutas Completas */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Rutas Completas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-slate-600">
                  Exporta todas las rutas con detalle de paradas, horarios, distancias y costos.
                </p>
                <div className="flex flex-col gap-2">
                  <Button 
                    variant="outline" 
                    className="justify-start"
                    onClick={() => handleExport('CSV', 'Rutas Completas')}
                  >
                    <FileSpreadsheet className="size-4 mr-2" />
                    Descargar CSV
                  </Button>
                  <Button 
                    variant="outline" 
                    className="justify-start"
                    onClick={() => handleExport('JSON', 'Rutas Completas')}
                  >
                    <FileCode className="size-4 mr-2" />
                    Descargar JSON
                  </Button>
                  <Button 
                    variant="outline" 
                    className="justify-start"
                    onClick={() => handleExport('Excel', 'Rutas Completas')}
                  >
                    <FileSpreadsheet className="size-4 mr-2" />
                    Descargar Excel
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Resumen por Vehículo */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Resumen por Vehículo</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-slate-600">
                  Resumen ejecutivo con KPIs por vehículo: distancia, tiempo, costo, utilización.
                </p>
                <div className="flex flex-col gap-2">
                  <Button 
                    variant="outline" 
                    className="justify-start"
                    onClick={() => handleExport('CSV', 'Resumen por Vehículo')}
                  >
                    <FileSpreadsheet className="size-4 mr-2" />
                    Descargar CSV
                  </Button>
                  <Button 
                    variant="outline" 
                    className="justify-start"
                    onClick={() => handleExport('PDF', 'Resumen por Vehículo')}
                  >
                    <FileText className="size-4 mr-2" />
                    Descargar PDF
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Detalle de Paradas */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Detalle de Paradas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-slate-600">
                  Lista secuencial de todas las paradas con horarios, direcciones y estado de cumplimiento.
                </p>
                <div className="flex flex-col gap-2">
                  <Button 
                    variant="outline" 
                    className="justify-start"
                    onClick={() => handleExport('CSV', 'Detalle de Paradas')}
                  >
                    <FileSpreadsheet className="size-4 mr-2" />
                    Descargar CSV
                  </Button>
                  <Button 
                    variant="outline" 
                    className="justify-start"
                    onClick={() => handleExport('Excel', 'Detalle de Paradas')}
                  >
                    <FileSpreadsheet className="size-4 mr-2" />
                    Descargar Excel con Hojas por Vehículo
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* KPIs Globales */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">KPIs Globales</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-slate-600">
                  Métricas agregadas: costo total, cumplimiento, distancia, utilización de flota.
                </p>
                <div className="flex flex-col gap-2">
                  <Button 
                    variant="outline" 
                    className="justify-start"
                    onClick={() => handleExport('JSON', 'KPIs Globales')}
                  >
                    <FileCode className="size-4 mr-2" />
                    Descargar JSON
                  </Button>
                  <Button 
                    variant="outline" 
                    className="justify-start"
                    onClick={() => handleExport('PDF', 'KPIs Globales')}
                  >
                    <FileText className="size-4 mr-2" />
                    Reporte PDF Ejecutivo
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Pedidos Asignados */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Pedidos Asignados</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-slate-600">
                  Lista de pedidos con vehículo asignado, horario de entrega y estado.
                </p>
                <div className="flex flex-col gap-2">
                  <Button 
                    variant="outline" 
                    className="justify-start"
                    onClick={() => handleExport('CSV', 'Pedidos Asignados')}
                  >
                    <FileSpreadsheet className="size-4 mr-2" />
                    Descargar CSV
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Mapa de Rutas */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Mapa de Rutas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-slate-600">
                  Visualización geográfica de todas las rutas en formato interactivo o estático.
                </p>
                <div className="flex flex-col gap-2">
                  <Button 
                    variant="outline" 
                    className="justify-start"
                    onClick={() => handleExport('HTML', 'Mapa Interactivo')}
                  >
                    <FileCode className="size-4 mr-2" />
                    Descargar HTML Interactivo
                  </Button>
                  <Button 
                    variant="outline" 
                    className="justify-start"
                    onClick={() => handleExport('GeoJSON', 'Geometrías de Rutas')}
                  >
                    <FileCode className="size-4 mr-2" />
                    Descargar GeoJSON
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Export All */}
          <Card className="border-blue-200 bg-blue-50">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-blue-900 mb-1">Exportación Completa</h3>
                  <p className="text-sm text-blue-800">
                    Descarga un paquete ZIP con todos los formatos disponibles
                  </p>
                </div>
                <Button onClick={() => handleExport('ZIP', 'Paquete Completo')}>
                  <Download className="size-4 mr-2" />
                  Descargar Todo
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Traceability Tab */}
        <TabsContent value="traceability" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Información de Corrida</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-600 mb-1">ID de Corrida</p>
                  <p className="font-mono text-slate-900">{run.id}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600 mb-1">Fecha de Ejecución</p>
                  <p className="text-slate-900">{run.date}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600 mb-1">Estado</p>
                  <StatusBadge status={run.status} />
                </div>
                <div>
                  <p className="text-sm text-slate-600 mb-1">Tiempo de Ejecución</p>
                  <p className="text-slate-900">{run.executionTimeSeconds} segundos</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600 mb-1">Pedidos Totales</p>
                  <p className="text-slate-900">{run.totalOrders}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600 mb-1">Pedidos Asignados</p>
                  <p className="text-slate-900">{run.assignedOrders}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Pipeline de Procesamiento</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { step: 1, name: 'Ingesta de Pedidos', status: 'completed', time: '0.2s', details: `${run.totalOrders} pedidos cargados` },
                  { step: 2, name: 'Geocodificación', status: 'completed', time: '1.8s', details: `${run.totalOrders} direcciones geocodificadas` },
                  { step: 3, name: 'Clustering DBSCAN', status: 'completed', time: '0.5s', details: `${Math.max(...run.routes.map(r => r.cluster))} clusters identificados` },
                  { step: 4, name: 'Matriz de Distancias', status: 'completed', time: '2.1s', details: 'Red vial real con dependencia temporal' },
                  { step: 5, name: 'Optimización GA (PyMoo)', status: 'completed', time: '6.8s', details: '100 generaciones, población 50' },
                  { step: 6, name: 'Asignación Global de Flota', status: 'completed', time: '0.7s', details: `${run.totalVehiclesUsed} vehículos asignados` },
                  { step: 7, name: 'Exportación de Resultados', status: 'completed', time: '0.3s', details: 'KPIs, rutas y mapas generados' },
                ].map(step => (
                  <div key={step.step} className="flex items-start gap-4 p-4 bg-slate-50 rounded-lg border">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-100 text-green-700 font-semibold text-sm flex-shrink-0">
                      {step.step}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-medium text-slate-900">{step.name}</h4>
                        <div className="flex items-center gap-2">
                          <StatusBadge status="completed" />
                          <span className="text-xs text-slate-600">{step.time}</span>
                        </div>
                      </div>
                      <p className="text-sm text-slate-600">{step.details}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Decisiones del Algoritmo</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                  <p className="text-sm font-medium text-purple-900 mb-1">División de Pedidos</p>
                  <p className="text-sm text-purple-800">
                    Pedido ORD003 (18m³, 3200kg) dividido en 2 subpedidos: ORD003-A (14.5m³, 2500kg) y ORD003-B (3.5m³, 700kg) 
                    por exceder capacidad máxima de vehículo disponible (15m³).
                  </p>
                </div>

                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                  <p className="text-sm font-medium text-amber-900 mb-1">Espera Programada</p>
                  <p className="text-sm text-amber-800">
                    Ruta V003 tiene 45 minutos de espera distribuidos en 2 paradas para cumplir ventanas horarias. 
                    Alternativa sin espera violaría restricciones de tiempo.
                  </p>
                </div>

                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm font-medium text-blue-900 mb-1">Asignación de Clusters</p>
                  <p className="text-sm text-blue-800">
                    DBSCAN identificó 4 clusters geográficos. Cluster 2 (centro de Santiago) asignado a 3 vehículos 
                    por alta densidad de pedidos.
                  </p>
                </div>

                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm font-medium text-red-900 mb-1">Pedidos No Asignados</p>
                  <p className="text-sm text-red-800">
                    Pedido ORD015 (turno tarde, 16:00-20:00) no asignado: V006 no disponible y otros vehículos 
                    del turno tarde ya comprometidos con rutas que excederían jornada máxima.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Parámetros de Configuración</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-xs text-slate-600 mb-1">Función Objetivo</p>
                  <p className="text-sm font-medium text-slate-900">Balanceado (Costo + Cumplimiento)</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-xs text-slate-600 mb-1">DBSCAN Epsilon</p>
                  <p className="text-sm font-medium text-slate-900">5.0 km</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-xs text-slate-600 mb-1">Min Samples</p>
                  <p className="text-sm font-medium text-slate-900">2</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-xs text-slate-600 mb-1">Generaciones GA</p>
                  <p className="text-sm font-medium text-slate-900">100</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-xs text-slate-600 mb-1">Población GA</p>
                  <p className="text-sm font-medium text-slate-900">50</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <p className="text-xs text-slate-600 mb-1">División Automática</p>
                  <p className="text-sm font-medium text-slate-900">Habilitada</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Historial de Corridas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b text-left text-sm text-slate-600">
                      <th className="pb-3 font-medium">Fecha</th>
                      <th className="pb-3 font-medium">ID Corrida</th>
                      <th className="pb-3 font-medium">Estado</th>
                      <th className="pb-3 font-medium">Pedidos</th>
                      <th className="pb-3 font-medium">Vehículos</th>
                      <th className="pb-3 font-medium">Cumplimiento</th>
                      <th className="pb-3 font-medium">Costo</th>
                      <th className="pb-3 font-medium">Distancia</th>
                      <th className="pb-3 font-medium"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {historicalRuns.map(histRun => (
                      <tr key={histRun.id} className="border-b last:border-0 hover:bg-slate-50">
                        <td className="py-3 text-sm text-slate-900">{histRun.date}</td>
                        <td className="py-3 text-sm font-mono text-slate-600">{histRun.id}</td>
                        <td className="py-3">
                          <StatusBadge status={histRun.status} />
                        </td>
                        <td className="py-3 text-sm text-slate-900">
                          {histRun.assignedOrders}/{histRun.totalOrders}
                        </td>
                        <td className="py-3 text-sm text-slate-900">
                          {histRun.totalVehiclesUsed}/{histRun.totalVehiclesAvailable}
                        </td>
                        <td className="py-3 text-sm font-medium text-slate-900">
                          {histRun.onTimePercentage}%
                        </td>
                        <td className="py-3 text-sm text-slate-900">
                          ${histRun.totalCost.toFixed(0)}
                        </td>
                        <td className="py-3 text-sm text-slate-900">
                          {histRun.totalDistanceKm.toFixed(1)} km
                        </td>
                        <td className="py-3">
                          <Button variant="ghost" size="sm">
                            <Eye className="size-4 mr-1" />
                            Ver
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
