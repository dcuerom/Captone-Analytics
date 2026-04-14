import { useEffect, useState } from "react";
import { Upload, Play, Truck, Package } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Progress } from "../components/ui/progress";
import { useAppData } from "../data/AppDataContext";
import { getOptimizationDefaults, getOptimizationStatus, getPreflightStatus, startOptimization, uploadOrdersCsv } from "../data/api";

export function Planning() {
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationMessage, setOptimizationMessage] = useState<string | null>(null);
  const [optimizationError, setOptimizationError] = useState<string | null>(null);
  const [latestRunId, setLatestRunId] = useState<string | null>(null);
  const [preflightSummary, setPreflightSummary] = useState<string | null>(null);
  const [deliveryDate, setDeliveryDate] = useState("2026-04-08");
  const [depotAddress, setDepotAddress] = useState("Santa Elena, Santiago, Chile");
  const [clusteringEps, setClusteringEps] = useState(0.3);
  const [clusteringMinSamples, setClusteringMinSamples] = useState(3);
  const [gaGenerations, setGaGenerations] = useState(200);
  const [gaPopulation, setGaPopulation] = useState(100);
  const [maxRouteHours, setMaxRouteHours] = useState(5);
  const [maxVehicles, setMaxVehicles] = useState(20);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [optimizationProgressPct, setOptimizationProgressPct] = useState(0);
  const [optimizationStageMessage, setOptimizationStageMessage] = useState<string | null>(null);
  const [optimizationStepCurrent, setOptimizationStepCurrent] = useState<number | null>(null);
  const [optimizationStepTotal, setOptimizationStepTotal] = useState<number | null>(null);
  const { fleet, orders, loading, error, refresh, activeRunId } = useAppData();

  useEffect(() => {
    const loadDefaults = async () => {
      try {
        const defaults = await getOptimizationDefaults();
        setClusteringEps(Number(defaults.clustering_eps ?? 0.3));
        setClusteringMinSamples(Number(defaults.clustering_min_samples ?? 3));
        setGaGenerations(Number(defaults.ga_n_gen ?? 200));
        setGaPopulation(Number(defaults.ga_pop_size ?? 100));
        setMaxRouteHours(Number((defaults.d_max_min ?? 300) / 60));
        setMaxVehicles(Number(defaults.max_vehiculos_globales ?? 20));
        setDepotAddress(String(defaults.depot_address ?? "Santa Elena, Santiago, Chile"));
      } catch {
        // Si el backend no esta disponible, dejamos defaults locales.
      }
    };
    void loadDefaults();
  }, []);

  useEffect(() => {
    const loadPreflight = async () => {
      try {
        const preflight = await getPreflightStatus();
        if (preflight.status === "ok") {
          setPreflightSummary("Preflight OK");
          return;
        }
        setPreflightSummary(`Preflight con fallas: ${preflight.failedCount}`);
      } catch {
        setPreflightSummary("Preflight no disponible");
      }
    };
    void loadPreflight();
  }, []);

  const handleOptimize = async () => {
    try {
      const generatedRunId = `run-${new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14)}-${Math.random().toString(16).slice(2, 10)}`;
      setIsOptimizing(true);
      setOptimizationError(null);
      setOptimizationMessage("Iniciando optimizacion en backend...");
      setOptimizationProgressPct(0);
      setOptimizationStageMessage("Preparando optimizacion...");
      setOptimizationStepCurrent(null);
      setOptimizationStepTotal(null);
      setLatestRunId(generatedRunId);

      const startResponse = await startOptimization(
        deliveryDate,
        {
          clustering_eps: Number(clusteringEps),
          clustering_min_samples: Number(clusteringMinSamples),
          ga_n_gen: Number(gaGenerations),
          ga_pop_size: Number(gaPopulation),
          d_max_min: Number(maxRouteHours) * 60,
          max_vehiculos_globales: Number(maxVehicles),
        },
        {
          runId: generatedRunId,
          depotAddress: depotAddress.trim(),
        },
      );

      if (startResponse.runId) {
        setLatestRunId(startResponse.runId);
      }
      if (typeof startResponse.progressPct === "number") {
        setOptimizationProgressPct(Math.max(0, Math.min(100, Number(startResponse.progressPct))));
      }
      if (startResponse.stageMessage) {
        setOptimizationStageMessage(startResponse.stageMessage);
      }
      if (typeof startResponse.currentStep === "number") {
        setOptimizationStepCurrent(startResponse.currentStep);
      }
      if (typeof startResponse.totalSteps === "number") {
        setOptimizationStepTotal(startResponse.totalSteps);
      }

      const timeoutMs = 15 * 60 * 1000;
      const pollEveryMs = 3000;
      const startTs = Date.now();

      while (Date.now() - startTs < timeoutMs) {
        const status = await getOptimizationStatus();
        if (status.status === "running") {
          if (status.runId) {
            setLatestRunId(status.runId);
          }
          const nextProgress =
            typeof status.progressPct === "number"
              ? Math.max(0, Math.min(100, Number(status.progressPct)))
              : optimizationProgressPct;
          setOptimizationProgressPct(nextProgress);
          setOptimizationMessage(status.stageMessage ?? "Optimizando rutas con modelo TDVRPTW...");
          setOptimizationStageMessage(status.stageMessage ?? "Procesando optimizacion...");
          if (typeof status.currentStep === "number") {
            setOptimizationStepCurrent(status.currentStep);
          }
          if (typeof status.totalSteps === "number") {
            setOptimizationStepTotal(status.totalSteps);
          }
          await new Promise((resolve) => setTimeout(resolve, pollEveryMs));
          continue;
        }
        if (status.status === "completed") {
          const completedRunId = status.runId ?? latestRunId ?? generatedRunId;
          setLatestRunId(completedRunId);
          setOptimizationProgressPct(100);
          setOptimizationMessage("Optimizacion completada. Actualizando resultados...");
          setOptimizationStageMessage(status.stageMessage ?? "Optimizacion finalizada.");
          await refresh({ runId: completedRunId });
          setOptimizationMessage("Resultados actualizados desde backend.");
          setIsOptimizing(false);
          return;
        }
        if (status.status === "failed") {
          throw new Error(status.error ?? "La optimizacion fallo en backend.");
        }
        await new Promise((resolve) => setTimeout(resolve, pollEveryMs));
      }

      throw new Error("Timeout esperando la optimizacion. Revisa logs del backend.");
    } catch (err) {
      const message = err instanceof Error ? err.message : "No se pudo ejecutar la optimizacion.";
      setOptimizationError(message);
      setOptimizationMessage(null);
      setOptimizationStageMessage(null);
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
      await refresh({ runId: activeRunId ?? undefined });
    } catch (err) {
      const message = err instanceof Error ? err.message : "No se pudo cargar el CSV.";
      setUploadError(message);
    } finally {
      setIsUploading(false);
    }
  };

  const availableVehicles = fleet.filter((v) => v.available);

  if (loading) {
    return <div className="p-8 text-slate-600">Cargando datos de backend...</div>;
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-semibold text-slate-900 mb-2">Planificacion de Corrida</h1>
        <p className="text-slate-600">Configure y ejecute una nueva optimizacion de rutas TDVRPTW</p>
        {error && (
          <p className="text-xs text-amber-700 mt-1">
            Backend no disponible. Verifica <code>python backend/api_server.py</code> y <code>npm run dev</code>.
          </p>
        )}
        {preflightSummary && <p className="text-xs text-slate-600 mt-1">{preflightSummary}</p>}
        {(latestRunId || activeRunId) && (
          <p className="text-xs text-slate-600 mt-1">
            Run activo: <code>{latestRunId ?? activeRunId}</code>
          </p>
        )}
        {optimizationMessage && <p className="text-xs text-blue-700 mt-1">{optimizationMessage}</p>}
        {isOptimizing && (
          <div className="mt-3 space-y-2 max-w-xl">
            <div className="flex items-center justify-between text-xs text-slate-600">
              <span>{optimizationStageMessage ?? "Optimizando..."}</span>
              <span>{Math.round(optimizationProgressPct)}%</span>
            </div>
            <Progress value={optimizationProgressPct} className="h-2" />
            {typeof optimizationStepCurrent === "number" && typeof optimizationStepTotal === "number" && optimizationStepTotal > 0 && (
              <p className="text-xs text-slate-500">
                Progreso de clusters: {optimizationStepCurrent}/{optimizationStepTotal}
              </p>
            )}
          </div>
        )}
        {optimizationError && <p className="text-xs text-red-700 mt-1">{optimizationError}</p>}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Parametros de Optimizacion</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="basic">
                <TabsList>
                  <TabsTrigger value="basic">Basicos</TabsTrigger>
                  <TabsTrigger value="advanced">Parametros efectivos</TabsTrigger>
                </TabsList>

                <TabsContent value="basic" className="space-y-4 mt-4">
                  <div>
                    <Label htmlFor="delivery-date">Fecha de Entrega</Label>
                    <Input id="delivery-date" type="date" value={deliveryDate} onChange={(e) => setDeliveryDate(e.target.value)} />
                  </div>

                  <div>
                    <Label htmlFor="depot-address">Direccion de Deposito</Label>
                    <Input id="depot-address" type="text" value={depotAddress} onChange={(e) => setDepotAddress(e.target.value)} />
                    <p className="text-xs text-slate-500 mt-1">
                      Se envia al backend como <code>depotAddress</code> en la corrida.
                    </p>
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

                  <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
                    <p className="text-sm font-medium text-slate-900">Objetivo activo: Minimizar distancia total</p>
                    <p className="text-xs text-slate-600 mt-1">La version actual del backend opera con este objetivo.</p>
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
                      <p className="text-xs text-slate-500 mt-1">DBSCAN de produccion (espacio lat/lon/tiempo estandarizado)</p>
                    </div>
                    <div>
                      <Label htmlFor="clustering-min-samples">Min Samples</Label>
                      <Input
                        id="clustering-min-samples"
                        type="number"
                        value={clusteringMinSamples}
                        onChange={(e) => setClusteringMinSamples(Number(e.target.value))}
                      />
                      <p className="text-xs text-slate-500 mt-1">Minimo de nodos por cluster (pipeline actual)</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="ga-generations">Generaciones GA</Label>
                      <Input id="ga-generations" type="number" value={gaGenerations} onChange={(e) => setGaGenerations(Number(e.target.value))} />
                    </div>
                    <div>
                      <Label htmlFor="ga-population">Poblacion GA</Label>
                      <Input id="ga-population" type="number" value={gaPopulation} onChange={(e) => setGaPopulation(Number(e.target.value))} />
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="max-route-time">Tiempo Maximo por Ruta (horas)</Label>
                    <Input
                      id="max-route-time"
                      type="number"
                      value={maxRouteHours}
                      step="0.5"
                      onChange={(e) => setMaxRouteHours(Number(e.target.value))}
                    />
                  </div>

                  <div>
                    <Label htmlFor="max-vehicles">Maximo de Vehiculos Globales</Label>
                    <Input
                      id="max-vehicles"
                      type="number"
                      min="1"
                      value={maxVehicles}
                      onChange={(e) => setMaxVehicles(Number(e.target.value))}
                    />
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          <div className="flex gap-3">
            <Button size="lg" className="flex-1" onClick={handleOptimize} disabled={isOptimizing}>
              {isOptimizing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                  Optimizando...
                </>
              ) : (
                <>
                  <Play className="size-5 mr-2" />
                  Ejecutar Optimizacion
                </>
              )}
            </Button>
          </div>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Flota Disponible</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Total vehiculos</span>
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
                {availableVehicles.slice(0, 5).map((vehicle) => (
                  <div key={vehicle.id} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <Truck className="size-4 text-slate-400" />
                      <span className="text-slate-700">{vehicle.name}</span>
                    </div>
                    <span className="text-xs text-slate-500">{vehicle.capacityM3}m3</span>
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
                  <span className="font-medium">{orders.filter((o) => o.status !== "pending").length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Con errores</span>
                  <span className="font-medium">{orders.filter((o) => !o.lat || !o.lng).length}</span>
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
                <li>1. Ingesta y validacion de pedidos</li>
                <li>2. Geocodificacion de direcciones</li>
                <li>3. Clustering DBSCAN 3D (lat,lon,tiempo)</li>
                <li>4. Matriz de distancias sobre red vial real (A*/Dijkstra)</li>
                <li>5. Optimizacion TDVRPTW (PyMoo + restricciones duras)</li>
                <li>6. Asignacion global de flota</li>
                <li>7. Exportacion de resultados</li>
              </ol>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
