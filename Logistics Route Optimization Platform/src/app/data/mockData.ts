// Mock data que refleja la salida del backend TDVRPTW
// Pipeline: ingesta -> geocodificación -> clustering DBSCAN -> matriz distancias -> GA -> asignación flota

export interface Order {
  id: string;
  customerId: string;
  customerName: string;
  address: string;
  comuna: string;
  lat: number;
  lng: number;
  volumeM3: number;
  weightKg: number;
  timeWindowStart: string; // HH:MM
  timeWindowEnd: string; // HH:MM
  deliveryDate: string; // YYYY-MM-DD
  cluster?: number;
  status: 'pending' | 'assigned' | 'delivered' | 'split' | 'unassigned';
  splitFromOrderId?: string; // Si fue dividido por capacidad
  serviceTimeMinutes: number;
}

export interface Stop {
  orderId: string;
  sequence: number;
  arrivalTime: string; // HH:MM
  departureTime: string; // HH:MM
  waitTimeMinutes: number;
  distanceFromPreviousKm: number;
  travelTimeMinutes: number;
  isOnTime: boolean;
  timeWindowViolationMinutes: number;
}

export interface Vehicle {
  id: string;
  name: string;
  capacityM3: number;
  capacityKg: number;
  costPerKm: number;
  costPerHour: number;
  shift: 'morning' | 'afternoon' | 'night';
  available: boolean;
}

export interface Route {
  vehicleId: string;
  vehicleName: string;
  stops: Stop[];
  totalDistanceKm: number;
  totalTimeMinutes: number;
  totalWaitTimeMinutes: number;
  loadVolumeM3: number;
  loadWeightKg: number;
  utilizationVolume: number; // %
  utilizationWeight: number; // %
  ordersDelivered: number;
  onTimeDeliveries: number;
  totalCost: number;
  cluster: number;
}

export interface OptimizationRun {
  id: string;
  name: string;
  date: string;
  status: 'running' | 'completed' | 'failed' | 'infeasible';
  totalOrders: number;
  assignedOrders: number;
  unassignedOrders: number;
  splitOrders: number; // Pedidos divididos por capacidad
  totalVehiclesUsed: number;
  totalVehiclesAvailable: number;
  totalDistanceKm: number;
  totalCost: number;
  totalWaitTimeMinutes: number;
  onTimePercentage: number;
  averageUtilization: number;
  executionTimeSeconds: number;
  warnings: string[];
  routes: Route[];
}

// Mock fleet - flota global disponible
export const mockFleet: Vehicle[] = [
  { id: 'V001', name: 'Camión 001', capacityM3: 15, capacityKg: 3000, costPerKm: 0.8, costPerHour: 15, shift: 'morning', available: true },
  { id: 'V002', name: 'Camión 002', capacityM3: 15, capacityKg: 3000, costPerKm: 0.8, costPerHour: 15, shift: 'morning', available: true },
  { id: 'V003', name: 'Camión 003', capacityM3: 20, capacityKg: 4000, costPerKm: 1.0, costPerHour: 18, shift: 'morning', available: true },
  { id: 'V004', name: 'Camión 004', capacityM3: 20, capacityKg: 4000, costPerKm: 1.0, costPerHour: 18, shift: 'afternoon', available: true },
  { id: 'V005', name: 'Camión 005', capacityM3: 25, capacityKg: 5000, costPerKm: 1.2, costPerHour: 20, shift: 'afternoon', available: true },
  { id: 'V006', name: 'Camión 006', capacityM3: 15, capacityKg: 3000, costPerKm: 0.8, costPerHour: 15, shift: 'afternoon', available: false },
  { id: 'V007', name: 'Camión 007', capacityM3: 20, capacityKg: 4000, costPerKm: 1.0, costPerHour: 18, shift: 'night', available: true },
  { id: 'V008', name: 'Camión 008', capacityM3: 15, capacityKg: 3000, costPerKm: 0.8, costPerHour: 15, shift: 'night', available: true },
];

// Mock orders
export const mockOrders: Order[] = [
  { id: 'ORD001', customerId: 'C001', customerName: 'Distribuidora Sur Ltda.', address: 'Av. Apoquindo 3000', comuna: 'Las Condes', lat: -33.4172, lng: -70.5836, volumeM3: 2.5, weightKg: 450, timeWindowStart: '09:00', timeWindowEnd: '12:00', deliveryDate: '2026-04-08', cluster: 1, status: 'assigned', serviceTimeMinutes: 15 },
  { id: 'ORD002', customerId: 'C002', customerName: 'Comercial El Bosque', address: 'Av. Kennedy 5600', comuna: 'Vitacura', lat: -33.3929, lng: -70.5696, volumeM3: 3.2, weightKg: 580, timeWindowStart: '08:00', timeWindowEnd: '11:00', deliveryDate: '2026-04-08', cluster: 1, status: 'assigned', serviceTimeMinutes: 20 },
  { id: 'ORD003', customerId: 'C003', customerName: 'SuperMercado Central', address: 'Av. Libertador 1400', comuna: 'Santiago', lat: -33.4372, lng: -70.6506, volumeM3: 18.0, weightKg: 3200, timeWindowStart: '10:00', timeWindowEnd: '14:00', deliveryDate: '2026-04-08', cluster: 2, status: 'split', serviceTimeMinutes: 25 },
  { id: 'ORD003-A', customerId: 'C003', customerName: 'SuperMercado Central', address: 'Av. Libertador 1400', comuna: 'Santiago', lat: -33.4372, lng: -70.6506, volumeM3: 14.5, weightKg: 2500, timeWindowStart: '10:00', timeWindowEnd: '14:00', deliveryDate: '2026-04-08', cluster: 2, status: 'assigned', splitFromOrderId: 'ORD003', serviceTimeMinutes: 25 },
  { id: 'ORD003-B', customerId: 'C003', customerName: 'SuperMercado Central', address: 'Av. Libertador 1400', comuna: 'Santiago', lat: -33.4372, lng: -70.6506, volumeM3: 3.5, weightKg: 700, timeWindowStart: '10:00', timeWindowEnd: '14:00', deliveryDate: '2026-04-08', cluster: 2, status: 'assigned', splitFromOrderId: 'ORD003', serviceTimeMinutes: 15 },
  { id: 'ORD004', customerId: 'C004', customerName: 'Retail Express SA', address: 'Gran Avenida 3200', comuna: 'San Miguel', lat: -33.4969, lng: -70.6503, volumeM3: 5.8, weightKg: 920, timeWindowStart: '09:00', timeWindowEnd: '13:00', deliveryDate: '2026-04-08', cluster: 2, status: 'assigned', serviceTimeMinutes: 18 },
  { id: 'ORD005', customerId: 'C005', customerName: 'Almacén Don Pedro', address: 'Vicuña Mackenna 4500', comuna: 'La Florida', lat: -33.5242, lng: -70.5956, volumeM3: 1.2, weightKg: 280, timeWindowStart: '14:00', timeWindowEnd: '18:00', deliveryDate: '2026-04-08', cluster: 3, status: 'assigned', serviceTimeMinutes: 10 },
  { id: 'ORD006', customerId: 'C006', customerName: 'Minimarket La Esquina', address: 'Américo Vespucio 1200', comuna: 'Pudahuel', lat: -33.4258, lng: -70.7437, volumeM3: 2.1, weightKg: 380, timeWindowStart: '08:00', timeWindowEnd: '12:00', deliveryDate: '2026-04-08', cluster: 4, status: 'assigned', serviceTimeMinutes: 12 },
  { id: 'ORD007', customerId: 'C007', customerName: 'Distribuidora Norte', address: 'Recoleta 1100', comuna: 'Recoleta', lat: -33.4144, lng: -70.6394, volumeM3: 4.5, weightKg: 750, timeWindowStart: '10:00', timeWindowEnd: '14:00', deliveryDate: '2026-04-08', cluster: 2, status: 'assigned', serviceTimeMinutes: 16 },
  { id: 'ORD008', customerId: 'C008', customerName: 'Cash & Carry Mapocho', address: 'Independencia 2400', comuna: 'Independencia', lat: -33.4089, lng: -70.6569, volumeM3: 8.2, weightKg: 1450, timeWindowStart: '09:00', timeWindowEnd: '12:00', deliveryDate: '2026-04-08', cluster: 2, status: 'assigned', serviceTimeMinutes: 22 },
  { id: 'ORD009', customerId: 'C009', customerName: 'Supermercado El Roble', address: 'Bilbao 1800', comuna: 'Providencia', lat: -33.4258, lng: -70.6165, volumeM3: 6.3, weightKg: 1100, timeWindowStart: '08:00', timeWindowEnd: '11:00', deliveryDate: '2026-04-08', cluster: 1, status: 'assigned', serviceTimeMinutes: 18 },
  { id: 'ORD010', customerId: 'C010', customerName: 'Abarrotes La Familia', address: 'Tobalaba 2200', comuna: 'Ñuñoa', lat: -33.4551, lng: -70.5999, volumeM3: 1.8, weightKg: 320, timeWindowStart: '15:00', timeWindowEnd: '19:00', deliveryDate: '2026-04-08', cluster: 3, status: 'assigned', serviceTimeMinutes: 10 },
  { id: 'ORD011', customerId: 'C011', customerName: 'Mercado Sur SpA', address: 'Santa Rosa 6400', comuna: 'La Pintana', lat: -33.5965, lng: -70.6348, volumeM3: 4.2, weightKg: 680, timeWindowStart: '13:00', timeWindowEnd: '17:00', deliveryDate: '2026-04-08', cluster: 3, status: 'assigned', serviceTimeMinutes: 15 },
  { id: 'ORD012', customerId: 'C012', customerName: 'Retail City', address: 'Los Pajaritos 3100', comuna: 'Maipú', lat: -33.5059, lng: -70.7628, volumeM3: 7.5, weightKg: 1300, timeWindowStart: '09:00', timeWindowEnd: '13:00', deliveryDate: '2026-04-08', cluster: 4, status: 'assigned', serviceTimeMinutes: 20 },
  { id: 'ORD013', customerId: 'C013', customerName: 'Almacenes Unidos', address: 'Pajaritos 1850', comuna: 'Estación Central', lat: -33.4722, lng: -70.7053, volumeM3: 3.1, weightKg: 520, timeWindowStart: '10:00', timeWindowEnd: '14:00', deliveryDate: '2026-04-08', cluster: 4, status: 'assigned', serviceTimeMinutes: 14 },
  { id: 'ORD014', customerId: 'C014', customerName: 'Cash La Reina', address: 'Larraín 8000', comuna: 'La Reina', lat: -33.4522, lng: -70.5437, volumeM3: 5.9, weightKg: 980, timeWindowStart: '08:00', timeWindowEnd: '12:00', deliveryDate: '2026-04-08', cluster: 1, status: 'assigned', serviceTimeMinutes: 17 },
  { id: 'ORD015', customerId: 'C015', customerName: 'Minimarket Express', address: 'Vicuña Mackenna 8200', comuna: 'La Florida', lat: -33.5389, lng: -70.5842, volumeM3: 2.3, weightKg: 410, timeWindowStart: '16:00', timeWindowEnd: '20:00', deliveryDate: '2026-04-08', cluster: 3, status: 'unassigned', serviceTimeMinutes: 12 },
  { id: 'ORD016', customerId: 'C016', customerName: 'Distribuidora Peñalolén', address: 'Grecia 9500', comuna: 'Peñalolén', lat: -33.4947, lng: -70.5207, volumeM3: 4.8, weightKg: 850, timeWindowStart: '09:00', timeWindowEnd: '13:00', deliveryDate: '2026-04-08', cluster: 1, status: 'assigned', serviceTimeMinutes: 16 },
  { id: 'ORD017', customerId: 'C017', customerName: 'Abarrotes San Joaquín', address: 'Vicuña Mackenna 5200', comuna: 'San Joaquín', lat: -33.5011, lng: -70.6194, volumeM3: 2.7, weightKg: 480, timeWindowStart: '11:00', timeWindowEnd: '15:00', deliveryDate: '2026-04-08', cluster: 2, status: 'assigned', serviceTimeMinutes: 13 },
  { id: 'ORD018', customerId: 'C018', customerName: 'Super Quilicura', address: 'Miraflores 8800', comuna: 'Quilicura', lat: -33.3594, lng: -70.7279, volumeM3: 9.2, weightKg: 1650, timeWindowStart: '08:00', timeWindowEnd: '12:00', deliveryDate: '2026-04-08', cluster: 4, status: 'assigned', serviceTimeMinutes: 23 },
];

// Mock optimization run - resultado completo de una corrida
export const mockOptimizationRun: OptimizationRun = {
  id: 'RUN-2026-04-06-001',
  name: 'Optimización Despacho 08-04-2026',
  date: '2026-04-06',
  status: 'completed',
  totalOrders: 18,
  assignedOrders: 17,
  unassignedOrders: 1,
  splitOrders: 1, // ORD003 fue dividido
  totalVehiclesUsed: 5,
  totalVehiclesAvailable: 7, // V006 no disponible
  totalDistanceKm: 342.8,
  totalCost: 1847.50,
  totalWaitTimeMinutes: 85,
  onTimePercentage: 88.24,
  averageUtilization: 76.3,
  executionTimeSeconds: 12.4,
  warnings: [
    'Pedido ORD003 dividido en 2 subpedidos por exceder capacidad máxima de vehículo (18m³ > 15m³)',
    'Pedido ORD015 no asignado: no hay vehículos disponibles en turno tarde con capacidad suficiente',
    'Ruta V003 tiene 45min de espera acumulada para cumplir ventanas horarias'
  ],
  routes: [
    {
      vehicleId: 'V002',
      vehicleName: 'Camión 002',
      cluster: 1,
      totalDistanceKm: 68.5,
      totalTimeMinutes: 245,
      totalWaitTimeMinutes: 12,
      loadVolumeM3: 14.2,
      loadWeightKg: 2510,
      utilizationVolume: 94.7,
      utilizationWeight: 83.7,
      ordersDelivered: 4,
      onTimeDeliveries: 4,
      totalCost: 362.80,
      stops: [
        { orderId: 'ORD009', sequence: 1, arrivalTime: '08:15', departureTime: '08:33', waitTimeMinutes: 0, distanceFromPreviousKm: 12.3, travelTimeMinutes: 18, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD002', sequence: 2, arrivalTime: '08:48', departureTime: '09:08', waitTimeMinutes: 0, distanceFromPreviousKm: 8.7, travelTimeMinutes: 15, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD001', sequence: 3, arrivalTime: '09:22', departureTime: '09:37', waitTimeMinutes: 0, distanceFromPreviousKm: 6.4, travelTimeMinutes: 14, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD014', sequence: 4, arrivalTime: '10:05', departureTime: '10:22', waitTimeMinutes: 12, distanceFromPreviousKm: 18.2, travelTimeMinutes: 28, isOnTime: true, timeWindowViolationMinutes: 0 },
      ]
    },
    {
      vehicleId: 'V003',
      vehicleName: 'Camión 003',
      cluster: 2,
      totalDistanceKm: 82.3,
      totalTimeMinutes: 278,
      totalWaitTimeMinutes: 45,
      loadVolumeM3: 19.5,
      loadWeightKg: 3580,
      utilizationVolume: 97.5,
      utilizationWeight: 89.5,
      ordersDelivered: 5,
      onTimeDeliveries: 4,
      totalCost: 432.20,
      stops: [
        { orderId: 'ORD008', sequence: 1, arrivalTime: '09:22', departureTime: '09:44', waitTimeMinutes: 0, distanceFromPreviousKm: 15.6, travelTimeMinutes: 22, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD007', sequence: 2, arrivalTime: '09:58', departureTime: '10:14', waitTimeMinutes: 0, distanceFromPreviousKm: 6.8, travelTimeMinutes: 14, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD003-A', sequence: 3, arrivalTime: '10:32', departureTime: '10:57', waitTimeMinutes: 0, distanceFromPreviousKm: 9.4, travelTimeMinutes: 18, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD004', sequence: 4, arrivalTime: '11:28', departureTime: '11:46', waitTimeMinutes: 12, distanceFromPreviousKm: 14.2, travelTimeMinutes: 31, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD017', sequence: 5, arrivalTime: '12:18', departureTime: '12:31', waitTimeMinutes: 33, distanceFromPreviousKm: 12.7, travelTimeMinutes: 32, isOnTime: false, timeWindowViolationMinutes: 18 },
      ]
    },
    {
      vehicleId: 'V004',
      vehicleName: 'Camión 004',
      cluster: 3,
      totalDistanceKm: 71.4,
      totalTimeMinutes: 198,
      totalWaitTimeMinutes: 8,
      loadVolumeM3: 8.3,
      loadWeightKg: 1010,
      utilizationVolume: 41.5,
      utilizationWeight: 25.3,
      ordersDelivered: 3,
      onTimeDeliveries: 3,
      totalCost: 327.60,
      stops: [
        { orderId: 'ORD005', sequence: 1, arrivalTime: '14:18', departureTime: '14:28', waitTimeMinutes: 0, distanceFromPreviousKm: 22.3, travelTimeMinutes: 28, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD010', sequence: 2, arrivalTime: '14:52', departureTime: '15:02', waitTimeMinutes: 0, distanceFromPreviousKm: 11.6, travelTimeMinutes: 24, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD011', sequence: 3, arrivalTime: '15:44', departureTime: '15:59', waitTimeMinutes: 8, distanceFromPreviousKm: 24.8, travelTimeMinutes: 42, isOnTime: true, timeWindowViolationMinutes: 0 },
      ]
    },
    {
      vehicleId: 'V005',
      vehicleName: 'Camión 005',
      cluster: 4,
      totalDistanceKm: 84.7,
      totalTimeMinutes: 252,
      totalWaitTimeMinutes: 18,
      loadVolumeM3: 22.8,
      loadWeightKg: 3750,
      utilizationVolume: 91.2,
      utilizationWeight: 75.0,
      ordersDelivered: 4,
      onTimeDeliveries: 4,
      totalCost: 486.40,
      stops: [
        { orderId: 'ORD018', sequence: 1, arrivalTime: '08:35', departureTime: '08:58', waitTimeMinutes: 0, distanceFromPreviousKm: 28.4, travelTimeMinutes: 35, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD006', sequence: 2, arrivalTime: '09:28', departureTime: '09:40', waitTimeMinutes: 0, distanceFromPreviousKm: 15.9, travelTimeMinutes: 30, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD012', sequence: 3, arrivalTime: '10:15', departureTime: '10:35', waitTimeMinutes: 15, distanceFromPreviousKm: 18.6, travelTimeMinutes: 35, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD013', sequence: 4, arrivalTime: '11:08', departureTime: '11:22', waitTimeMinutes: 3, distanceFromPreviousKm: 12.4, travelTimeMinutes: 33, isOnTime: true, timeWindowViolationMinutes: 0 },
      ]
    },
    {
      vehicleId: 'V001',
      vehicleName: 'Camión 001',
      cluster: 2,
      totalDistanceKm: 35.9,
      totalTimeMinutes: 142,
      totalWaitTimeMinutes: 2,
      loadVolumeM3: 8.3,
      loadWeightKg: 1500,
      utilizationVolume: 55.3,
      utilizationWeight: 50.0,
      ordersDelivered: 2,
      onTimeDeliveries: 2,
      totalCost: 238.50,
      stops: [
        { orderId: 'ORD003-B', sequence: 1, arrivalTime: '10:22', departureTime: '10:37', waitTimeMinutes: 0, distanceFromPreviousKm: 14.2, travelTimeMinutes: 22, isOnTime: true, timeWindowViolationMinutes: 0 },
        { orderId: 'ORD016', sequence: 2, arrivalTime: '11:15', departureTime: '11:31', waitTimeMinutes: 2, distanceFromPreviousKm: 21.7, travelTimeMinutes: 38, isOnTime: true, timeWindowViolationMinutes: 0 },
      ]
    }
  ]
};

export const mockHistoricalRuns: OptimizationRun[] = [
  mockOptimizationRun,
  {
    ...mockOptimizationRun,
    id: 'RUN-2026-04-05-001',
    name: 'Optimización Despacho 07-04-2026',
    date: '2026-04-05',
    totalOrders: 22,
    assignedOrders: 22,
    unassignedOrders: 0,
    splitOrders: 2,
    totalVehiclesUsed: 6,
    totalDistanceKm: 412.3,
    totalCost: 2156.80,
    onTimePercentage: 95.45,
    executionTimeSeconds: 15.2,
  },
  {
    ...mockOptimizationRun,
    id: 'RUN-2026-04-04-001',
    name: 'Optimización Despacho 06-04-2026',
    date: '2026-04-04',
    totalOrders: 19,
    assignedOrders: 18,
    unassignedOrders: 1,
    splitOrders: 0,
    totalVehiclesUsed: 5,
    totalDistanceKm: 368.1,
    totalCost: 1923.40,
    onTimePercentage: 83.33,
    executionTimeSeconds: 11.8,
  }
];
