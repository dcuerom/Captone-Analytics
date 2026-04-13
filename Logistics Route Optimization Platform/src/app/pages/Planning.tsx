import { useEffect, useState } from "react";
import { Calendar, Upload, Play, Settings, Truck, Package } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { useAppData } from "../data/AppDataContext";
import { Switch } from "../components/ui/switch";
import { getOptimizationDefaults, getOptimizationStatus, startOptimization, uploadOrdersCsv } from "../data/api";

export function Planning() {
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationMessage, setOptimizationMessage] = useState<string | null>(null);
  const [optimizationError, setOptimizationError] = useState<string | null>(null);
  const [deliveryDate, setDeliveryDate] = useState('2026-04-08');
  const [clusteringEps, setClusteringEps] = useState(0.3);
  const [clusteringMinSamples, setClusteringMinSamples] = useState(3);
  const [gaGenerations, setGaGenerations] = useState(200);
  const [gaPopulation, setGaPopulation] = useState(100);
  const [maxRouteHours, setMaxRouteHours] = useState(5);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const { fleet, orders, loading, error, refresh } = useAppData();

  useEffect(() => {
    const loadDefaults = async () => {
      try {
        const defaults = await getOptimizationDefaults();
        setClusteringEps(Number(defaults.clustering_eps ?? 0.3));
        setClusteringMinSamples(Number(defaults.clustering_min_samples ?? 3));
        setGaGenerations(Number(defaults.ga_n_gen ?? 200));
        setGaPopulation(Number(defaults.ga_pop_size ?? 100));
        setMaxRouteHours(Number((defaults.d_max_min ?? 300) / 60));
      } catch {
        // Si el backend no está disponible, dejamos defaults locales.
      }
    };
    void loadDefaults();
  }, []);
  
  const handleOptimize = async () => {
    try {
      setIsOptimizing(true);
      setOptimizationError(null);
      setOptimizationMessage("Iniciando optimización en backend...");
      await startOptimization(deliveryDate, {
        clustering_eps: Number(clusteringEps),
        clustering_min_samples: Number(clusteringMinSamples),
        ga_n_gen: Number(gaGenerations),
        ga_pop_size: Number(gaPopulation),
        d_max_min: Number(maxRouteHours) * 60,
        max_vehiculos_globales: Number(fleet.length || 20),
      });

      const timeoutMs = 15 * 60 * 1000;
      const pollEveryMs = 3000;
      const startTs = Date.now();

      while (Date.now() - startTs < timeoutMs) {
        const status = await getOptimizationStatus();
        if (status.status === "running") {
          setOptimizationMessage("Optimizando rutas con modelo TDVRPTW...");
          await new Promise((resolve) => setTimeout(resolve, pollEveryMs));
          continue;
        }
        if (status.status === "completed") {
          setOptimizationMessage("Optimización completada. Actualizando resultados...");
          await refresh();
          setOptimizationMessage("Resultados actualizados desde backend.");
          setIsOptimizing(false);
          return;
        }
        if (status.status === "failed") {
          throw new Error(status.error ?? "La optimización falló en backend.");
        }
        await new Promise((resolve) => setTimeout(resolve, pollEveryMs));
      }

      throw new Error("Timeout esperando la optimización. Revisa logs del backend.");
    } catch (err) {
      const message = err instanceof Error ? err.message : "No se pudo ejecutar la optimización.";
      setOptimizationError(message);
      setOptimizationMessage(null);
      setIsOptimizing(false);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError("Selecciona un archivo CSV primero.");
      return;
    }
    try {
      setIsUploading(true);
      setUploadError(null);
      setUploadMessage(null);
      const csvText = await selectedFile.text();
      const result = await uploadOrdersCsv(selectedFile.name, csvText);
      setUploadMessage(`CSV cargado: ${result.rows} filas (${result.columns.length} columnas).`);
      await refresh();
    } catch (err) {
      const message = err instanceof Error ? err.message : "No se pudo cargar el CSV.";
      setUploadError(message);
    } finally {
      setIsUploading(false);
    }
  };

  const availableVehicles = fleet.filter(v => v.available);

  if (loading) {
    return <div className="p-8 text-slate-600">Cargando datos de backend...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold text-slate-900 mb-2">Planificación de Corrida</h1>
        <p className="text-slate-600">Configure y ejecute una nueva optimización de rutas TDVRPTW</p>
        {error && <p className="text-xs text-amber-600 mt-1">Backend no disponible, usando datos mock.</p>}
        {optimizationMessage && <p className="text-xs text-blue-700 mt-1">{optimizationMessage}</p>}
        {optimizationError && <p className="text-xs text-red-700 mt-1">{optimizationError}</p>}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Parámetros de Optimización</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="basic">
                <TabsList>
                  <TabsTrigger value="basic">Básicos</TabsTrigger>
                  <TabsTrigger value="advanced">Avanzados</TabsTrigger>
                  <TabsTrigger value="constraints">Restricciones</TabsTrigger>
                </TabsList>

                <TabsContent value="basic" className="space-y-4 mt-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="run-name">Nombre de Corrida</Label>
                      <Input 
                        id="run-name" 
                        placeholder="Ej: Optimización Despacho 08-04-2026"
                        defaultValue={`Optimización ${deliveryDate}`}
                      />
                    </div>
                    <div>
                      <Label htmlFor="delivery-date">Fecha de Entrega</Label>
                      <Input 
                        id="delivery-date" 
                        type="date" 
                        value={deliveryDate}
                        onChange={(e) => setDeliveryDate(e.target.value)}
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="orders-file">Archivo de Pedidos (CSV)</Label>
                    <div className="flex gap-2 mt-1">
                      <Input
                        id="orders-file"
                        type="file"
                        accept=".csv,text/csv"
                        onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
                      />
                      <Button variant="outline" onClick={handleUpload} disabled={isUploading}>
                        <Upload className="size-4 mr-2" />
                        {isUploading ? "Subiendo..." : "Cargar"}
                      </Button>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      Formato recomendado (modelo real): id_pedido,id_cliente,direccion_ruteo,Comuna,latitud,longitud,fecha_entrega,a_ventana,b_ventana,peso_pedido,volumen_pedido
                    </p>
                    {uploadMessage && <p className="text-xs text-green-700 mt-1">{uploadMessage}</p>}
                    {uploadError && <p className="text-xs text-red-700 mt-1">{uploadError}</p>}
                  </div>

                  <div>
                    <Label htmlFor="objective">Función Objetivo</Label>
                    <Select defaultValue="balanced">
                      <SelectTrigger id="objective">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="balanced">Balanceado: Costo + Cumplimiento</SelectItem>
                        <SelectItem value="cost">Minimizar Costo Total</SelectItem>
                        <SelectItem value="compliance">Maximizar Cumplimiento</SelectItem>
                        <SelectItem value="distance">Minimizar Distancia</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </TabsContent>

                <TabsContent value="advanced" className="space-y-4 mt-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="clustering-epsilon">DBSCAN Epsilon (km)</Label>
                      <Input
                        id="clustering-epsilon"
                        type="number"
                        value={clusteringEps}
                        step="0.1"
                        onChange={(e) => setClusteringEps(Number(e.target.value))}
                      />
                      <p className="text-xs text-slate-500 mt-1">DBSCAN de producción (espacio lat/lon/tiempo estandarizado)</p>
                    </div>
                    <div>
                      <Label htmlFor="clustering-min-samples">Min Samples</Label>
                      <Input
                        id="clustering-min-samples"
                        type="number"
                        value={clusteringMinSamples}
                        onChange={(e) => setClusteringMinSamples(Number(e.target.value))}
                      />
                      <p className="text-xs text-slate-500 mt-1">Mínimo de nodos por cluster (pipeline actual)</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="ga-generations">Generaciones GA</Label>
                      <Input
                        id="ga-generations"
                        type="number"
                        value={gaGenerations}
                        onChange={(e) => setGaGenerations(Number(e.target.value))}
                      />
                    </div>
                    <div>
                      <Label htmlFor="ga-population">Población GA</Label>
                      <Input
                        id="ga-population"
                        type="number"
                        value={gaPopulation}
                        onChange={(e) => setGaPopulation(Number(e.target.value))}
                      />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="time-dependency">Dependencia Temporal</Label>
                    <Select defaultValue="traffic">
                      <SelectTrigger id="time-dependency">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="traffic">TDVRPTW τ_ij(t) (hora/día)</SelectItem>
                        <SelectItem value="static">Estático (promedio)</SelectItem>
                        <SelectItem value="historical">Histórico ML</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </TabsContent>

                <TabsContent value="constraints" className="space-y-4 mt-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Permitir División de Pedidos</Label>
                        <p className="text-xs text-slate-500">Si pedido excede capacidad, dividir automáticamente</p>
                      </div>
                      <Switch defaultChecked />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Respetar Ventanas Horarias Estrictas</Label>
                        <p className="text-xs text-slate-500">No permitir violaciones de tiempo</p>
                      </div>
                      <Switch defaultChecked />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Habilitar Retornos a Depot</Label>
                        <p className="text-xs text-slate-500">Permitir retornos intermedios para reabastecimiento</p>
                      </div>
                      <Switch />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Considerar Turnos de Vehículos</Label>
                        <p className="text-xs text-slate-500">Asignar según turno (mañana/tarde/noche)</p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="max-route-time">Tiempo Máximo por Ruta (horas)</Label>
                    <Input
                      id="max-route-time"
                      type="number"
                      value={maxRouteHours}
                      step="0.5"
                      onChange={(e) => setMaxRouteHours(Number(e.target.value))}
                    />
                  </div>

                  <div>
                    <Label htmlFor="max-wait-time">Espera Máxima Permitida (min)</Label>
                    <Input id="max-wait-time" type="number" defaultValue="60" />
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button 
              size="lg" 
              className="flex-1"
              onClick={handleOptimize}
              disabled={isOptimizing}
            >
              {isOptimizing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                  Optimizando...
                </>
              ) : (
                <>
                  <Play className="size-5 mr-2" />
                  Ejecutar Optimización
                </>
              )}
            </Button>
            <Button variant="outline" size="lg">
              <Settings className="size-5 mr-2" />
              Guardar Config
            </Button>
          </div>
        </div>

        {/* Summary Panel */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Flota Disponible</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Total vehículos</span>
                  <span className="font-medium">{fleet.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Disponibles</span>
                  <span className="font-medium text-green-600">{availableVehicles.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">No disponibles</span>
                  <span className="font-medium text-red-600">{fleet.length - availableVehicles.length}</span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t space-y-2">
                {availableVehicles.slice(0, 5).map(vehicle => (
                  <div key={vehicle.id} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <Truck className="size-4 text-slate-400" />
                      <span className="text-slate-700">{vehicle.name}</span>
                    </div>
                    <span className="text-xs text-slate-500">{vehicle.capacityM3}m³</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Pedidos Ingresados</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Total pedidos</span>
                  <span className="font-medium">{orders.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Validados</span>
                  <span className="font-medium">{orders.filter(o => o.status !== "pending").length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Con errores</span>
                  <span className="font-medium">{orders.filter(o => !o.lat || !o.lng).length}</span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t">
                <Button variant="outline" className="w-full" size="sm" onClick={handleUpload} disabled={!selectedFile || isUploading}>
                  <Package className="size-4 mr-2" />
                  {isUploading ? "Subiendo..." : "Cargar pedidos"}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-blue-50 border-blue-200">
            <CardContent className="p-4">
                <h4 className="font-medium text-blue-900 mb-2">Pipeline Backend</h4>
              <ol className="text-xs text-blue-800 space-y-1">
                <li>1. Ingesta y validación de pedidos</li>
                <li>2. Geocodificación de direcciones</li>
                <li>3. Clustering DBSCAN 3D (lat,lon,tiempo)</li>
                <li>4. Matriz de distancias sobre red vial real (A*/Dijkstra)</li>
                <li>5. Optimización TDVRPTW (PyMoo + restricciones duras)</li>
                <li>6. Asignación global de flota</li>
                <li>7. Exportación de resultados</li>
              </ol>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
