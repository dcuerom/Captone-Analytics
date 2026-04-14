import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { useAppData } from "../data/AppDataContext";
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  BarChart,
  Bar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from "recharts";
import { TrendingUp, TrendingDown, Calendar, ArrowRight } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";

export function KPIs() {
  const { historicalRuns, loading, error } = useAppData();
  const runs = historicalRuns.length >= 2 ? historicalRuns : historicalRuns.concat(historicalRuns[0] ? [historicalRuns[0]] : []);
  const [compareRuns, setCompareRuns] = useState([
    runs[0]?.id ?? "",
    runs[1]?.id ?? runs[0]?.id ?? ""
  ]);

  if (loading) {
    return <div className="p-8 text-slate-600">Cargando datos de backend...</div>;
  }

  // Trend data
  const trendData = runs.map(run => ({
    date: run.date,
    cost: run.totalCost,
    onTime: run.onTimePercentage,
    distance: run.totalDistanceKm,
    vehicles: run.totalVehiclesUsed,
    utilization: run.averageUtilization
  })).reverse();

  // Comparison data
  const run1 = runs.find(r => r.id === compareRuns[0]) ?? runs[0];
  const run2 = runs.find(r => r.id === compareRuns[1]) ?? runs[0];
  if (!run1 || !run2) {
    return <div className="p-8 text-slate-600">No hay corridas históricas disponibles.</div>;
  }

  const comparisonData = [
    {
      metric: 'Costo Total',
      run1: run1.totalCost,
      run2: run2.totalCost,
    },
    {
      metric: 'Distancia',
      run1: run1.totalDistanceKm,
      run2: run2.totalDistanceKm,
    },
    {
      metric: 'Cumplimiento %',
      run1: run1.onTimePercentage,
      run2: run2.onTimePercentage,
    },
    {
      metric: 'Vehículos',
      run1: run1.totalVehiclesUsed,
      run2: run2.totalVehiclesUsed,
    },
    {
      metric: 'Utilización %',
      run1: run1.averageUtilization,
      run2: run2.averageUtilization,
    }
  ];

  // Radar comparison
  const radarData = [
    {
      metric: 'Cumplimiento',
      run1: run1.onTimePercentage,
      run2: run2.onTimePercentage,
      fullMark: 100,
    },
    {
      metric: 'Utilización',
      run1: run1.averageUtilization,
      run2: run2.averageUtilization,
      fullMark: 100,
    },
    {
      metric: 'Eficiencia',
      run1: (run1.assignedOrders / run1.totalOrders) * 100,
      run2: (run2.assignedOrders / run2.totalOrders) * 100,
      fullMark: 100,
    },
    {
      metric: 'Cobertura',
      run1: ((run1.totalVehiclesAvailable - run1.totalVehiclesUsed) / run1.totalVehiclesAvailable) * 100,
      run2: ((run2.totalVehiclesAvailable - run2.totalVehiclesUsed) / run2.totalVehiclesAvailable) * 100,
      fullMark: 100,
    },
  ];

  const calculateChange = (current: number, previous: number) => {
    const change = ((current - previous) / previous) * 100;
    return change;
  };

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold text-slate-900 mb-2">KPIs y Análisis Comparativo</h1>
        <p className="text-slate-600">Seguimiento de métricas operativas y comparación de escenarios</p>
        {error && <p className="text-xs text-amber-600 mt-1">Backend no disponible. Verifica python backend/api_server.py y npm run dev.</p>}
      </div>

      <Tabs defaultValue="trends">
        <TabsList>
          <TabsTrigger value="trends">Tendencias Históricas</TabsTrigger>
          <TabsTrigger value="comparison">Comparación de Escenarios</TabsTrigger>
          <TabsTrigger value="trade-offs">Trade-offs</TabsTrigger>
        </TabsList>

        {/* Trends Tab */}
        <TabsContent value="trends" className="space-y-6 mt-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-slate-600">Costo Promedio</p>
                  <TrendingDown className="size-4 text-green-600" />
                </div>
                <p className="text-2xl font-semibold text-slate-900 mb-1">
                  ${(trendData.reduce((sum, d) => sum + d.cost, 0) / trendData.length).toFixed(0)}
                </p>
                <div className="flex items-center gap-1 text-xs text-green-600">
                  <TrendingDown className="size-3" />
                  <span>-5.2% últimos 7 días</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-slate-600">Cumplimiento Promedio</p>
                  <TrendingUp className="size-4 text-green-600" />
                </div>
                <p className="text-2xl font-semibold text-slate-900 mb-1">
                  {(trendData.reduce((sum, d) => sum + d.onTime, 0) / trendData.length).toFixed(1)}%
                </p>
                <div className="flex items-center gap-1 text-xs text-green-600">
                  <TrendingUp className="size-3" />
                  <span>+2.8% últimos 7 días</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-slate-600">Distancia Promedio</p>
                  <TrendingDown className="size-4 text-green-600" />
                </div>
                <p className="text-2xl font-semibold text-slate-900 mb-1">
                  {(trendData.reduce((sum, d) => sum + d.distance, 0) / trendData.length).toFixed(0)} km
                </p>
                <div className="flex items-center gap-1 text-xs text-green-600">
                  <TrendingDown className="size-3" />
                  <span>-3.1% últimos 7 días</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-slate-600">Utilización Promedio</p>
                  <TrendingUp className="size-4 text-blue-600" />
                </div>
                <p className="text-2xl font-semibold text-slate-900 mb-1">
                  {(trendData.reduce((sum, d) => sum + d.utilization, 0) / trendData.length).toFixed(1)}%
                </p>
                <div className="flex items-center gap-1 text-xs text-blue-600">
                  <TrendingUp className="size-3" />
                  <span>+4.2% últimos 7 días</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Costo y Cumplimiento</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Line 
                      yAxisId="left"
                      type="monotone" 
                      dataKey="cost" 
                      stroke="#3b82f6" 
                      name="Costo ($)"
                      strokeWidth={2}
                    />
                    <Line 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="onTime" 
                      stroke="#10b981" 
                      name="Cumplimiento (%)"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Distancia y Vehículos Utilizados</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Line 
                      yAxisId="left"
                      type="monotone" 
                      dataKey="distance" 
                      stroke="#f59e0b" 
                      name="Distancia (km)"
                      strokeWidth={2}
                    />
                    <Line 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="vehicles" 
                      stroke="#8b5cf6" 
                      name="Vehículos"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Comparison Tab */}
        <TabsContent value="comparison" className="space-y-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Seleccionar Escenarios a Comparar</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                <div>
                  <label className="text-sm text-slate-600 mb-2 block">Escenario 1</label>
                  <select 
                    className="w-full p-2 border border-slate-300 rounded-lg"
                    value={compareRuns[0]}
                    onChange={(e) => setCompareRuns([e.target.value, compareRuns[1]])}
                  >
                    {runs.map(run => (
                      <option key={run.id} value={run.id}>{run.name}</option>
                    ))}
                  </select>
                </div>

                <div className="flex justify-center">
                  <ArrowRight className="size-6 text-slate-400" />
                </div>

                <div>
                  <label className="text-sm text-slate-600 mb-2 block">Escenario 2</label>
                  <select 
                    className="w-full p-2 border border-slate-300 rounded-lg"
                    value={compareRuns[1]}
                    onChange={(e) => setCompareRuns([compareRuns[0], e.target.value])}
                  >
                    {runs.map(run => (
                      <option key={run.id} value={run.id}>{run.name}</option>
                    ))}
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Comparison Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <Card>
              <CardContent className="p-4">
                <p className="text-xs text-slate-600 mb-1">Costo Total</p>
                <p className="text-xl font-semibold text-slate-900">${run1.totalCost.toFixed(0)}</p>
                <div className="mt-2 pt-2 border-t">
                  <p className="text-xl font-semibold text-slate-900">${run2.totalCost.toFixed(0)}</p>
                  <div className={`text-xs mt-1 flex items-center gap-1 ${
                    run2.totalCost < run1.totalCost ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {run2.totalCost < run1.totalCost ? <TrendingDown className="size-3" /> : <TrendingUp className="size-3" />}
                    <span>{Math.abs(calculateChange(run2.totalCost, run1.totalCost)).toFixed(1)}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <p className="text-xs text-slate-600 mb-1">Cumplimiento</p>
                <p className="text-xl font-semibold text-slate-900">{run1.onTimePercentage}%</p>
                <div className="mt-2 pt-2 border-t">
                  <p className="text-xl font-semibold text-slate-900">{run2.onTimePercentage}%</p>
                  <div className={`text-xs mt-1 flex items-center gap-1 ${
                    run2.onTimePercentage > run1.onTimePercentage ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {run2.onTimePercentage > run1.onTimePercentage ? <TrendingUp className="size-3" /> : <TrendingDown className="size-3" />}
                    <span>{Math.abs(calculateChange(run2.onTimePercentage, run1.onTimePercentage)).toFixed(1)}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <p className="text-xs text-slate-600 mb-1">Distancia</p>
                <p className="text-xl font-semibold text-slate-900">{run1.totalDistanceKm.toFixed(0)} km</p>
                <div className="mt-2 pt-2 border-t">
                  <p className="text-xl font-semibold text-slate-900">{run2.totalDistanceKm.toFixed(0)} km</p>
                  <div className={`text-xs mt-1 flex items-center gap-1 ${
                    run2.totalDistanceKm < run1.totalDistanceKm ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {run2.totalDistanceKm < run1.totalDistanceKm ? <TrendingDown className="size-3" /> : <TrendingUp className="size-3" />}
                    <span>{Math.abs(calculateChange(run2.totalDistanceKm, run1.totalDistanceKm)).toFixed(1)}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <p className="text-xs text-slate-600 mb-1">Vehículos</p>
                <p className="text-xl font-semibold text-slate-900">{run1.totalVehiclesUsed}</p>
                <div className="mt-2 pt-2 border-t">
                  <p className="text-xl font-semibold text-slate-900">{run2.totalVehiclesUsed}</p>
                  <div className={`text-xs mt-1 flex items-center gap-1 ${
                    run2.totalVehiclesUsed < run1.totalVehiclesUsed ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {run2.totalVehiclesUsed < run1.totalVehiclesUsed ? <TrendingDown className="size-3" /> : <TrendingUp className="size-3" />}
                    <span>{Math.abs(run2.totalVehiclesUsed - run1.totalVehiclesUsed)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <p className="text-xs text-slate-600 mb-1">Utilización</p>
                <p className="text-xl font-semibold text-slate-900">{run1.averageUtilization}%</p>
                <div className="mt-2 pt-2 border-t">
                  <p className="text-xl font-semibold text-slate-900">{run2.averageUtilization}%</p>
                  <div className={`text-xs mt-1 flex items-center gap-1 ${
                    run2.averageUtilization > run1.averageUtilization ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {run2.averageUtilization > run1.averageUtilization ? <TrendingUp className="size-3" /> : <TrendingDown className="size-3" />}
                    <span>{Math.abs(calculateChange(run2.averageUtilization, run1.averageUtilization)).toFixed(1)}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Comparison Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Comparación de Métricas</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="metric" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="run1" fill="#3b82f6" name={run1.date} />
                    <Bar dataKey="run2" fill="#10b981" name={run2.date} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Análisis Multidimensional</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="metric" />
                    <PolarRadiusAxis domain={[0, 100]} />
                    <Radar name={run1.date} dataKey="run1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                    <Radar name={run2.date} dataKey="run2" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                    <Legend />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Trade-offs Tab */}
        <TabsContent value="trade-offs" className="space-y-6 mt-6">
          <Card className="border-l-4 border-l-blue-500 bg-blue-50">
            <CardContent className="p-6">
              <h3 className="font-semibold text-blue-900 mb-2">Trade-off Clave: Costo vs Cumplimiento</h3>
              <p className="text-sm text-blue-800">
                La optimización busca balancear dos objetivos principales: minimizar el costo operativo total
                y maximizar el cumplimiento de ventanas horarias. Estos objetivos a menudo están en conflicto.
              </p>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Escenario: Priorizar Costo</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <span className="text-sm text-slate-900">✓ Menor distancia total</span>
                    <span className="text-sm font-medium text-green-600">-15%</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <span className="text-sm text-slate-900">✓ Menos vehículos usados</span>
                    <span className="text-sm font-medium text-green-600">-1 vehículo</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <span className="text-sm text-slate-900">✗ Más violaciones de ventanas</span>
                    <span className="text-sm font-medium text-red-600">-12%</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <span className="text-sm text-slate-900">✗ Mayor espera acumulada</span>
                    <span className="text-sm font-medium text-red-600">+45min</span>
                  </div>
                </div>
                <Button variant="outline" className="w-full">Aplicar configuración</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Escenario: Priorizar Cumplimiento</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <span className="text-sm text-slate-900">✓ Mayor cumplimiento de ventanas</span>
                    <span className="text-sm font-medium text-green-600">+18%</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <span className="text-sm text-slate-900">✓ Menor espera total</span>
                    <span className="text-sm font-medium text-green-600">-30min</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <span className="text-sm text-slate-900">✗ Mayor distancia recorrida</span>
                    <span className="text-sm font-medium text-red-600">+22%</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <span className="text-sm text-slate-900">✗ Más vehículos necesarios</span>
                    <span className="text-sm font-medium text-red-600">+2 vehículos</span>
                  </div>
                </div>
                <Button variant="outline" className="w-full">Aplicar configuración</Button>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recomendaciones del Sistema</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-start gap-3 p-3 border rounded-lg">
                <div className="p-2 bg-blue-100 rounded">
                  <Calendar className="size-4 text-blue-600" />
                </div>
                <div>
                  <p className="font-medium text-slate-900 text-sm">Configuración Balanceada (Actual)</p>
                  <p className="text-xs text-slate-600 mt-1">
                    88.24% cumplimiento con $1,847 de costo. Balance óptimo para operación diaria.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-3 border rounded-lg">
                <div className="p-2 bg-green-100 rounded">
                  <TrendingUp className="size-4 text-green-600" />
                </div>
                <div>
                  <p className="font-medium text-slate-900 text-sm">Mejora Sugerida</p>
                  <p className="text-xs text-slate-600 mt-1">
                    Adelantar 2 entregas del cluster 3 al turno mañana podría mejorar cumplimiento en +5% con costo similar.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
