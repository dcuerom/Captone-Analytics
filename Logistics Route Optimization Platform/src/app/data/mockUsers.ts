export type SaaSUserRole = "Owner" | "Planner" | "Operations" | "Viewer";
export type SaaSUserStatus = "active" | "invited" | "suspended";

export interface SaaSUser {
  id: string;
  name: string;
  email: string;
  role: SaaSUserRole;
  status: SaaSUserStatus;
  team: string;
  region: string;
  lastAccess: string;
}

export const mockUsers: SaaSUser[] = [
  {
    id: "usr-001",
    name: "Bruno Soto",
    email: "bruno@routeoptimizer.ai",
    role: "Owner",
    status: "active",
    team: "Capstone Analytics",
    region: "Santiago",
    lastAccess: "Hoy, 09:14",
  },
  {
    id: "usr-002",
    name: "Camila Fuentes",
    email: "camila@routeoptimizer.ai",
    role: "Planner",
    status: "active",
    team: "Routing Lab",
    region: "Santiago",
    lastAccess: "Hoy, 08:02",
  },
  {
    id: "usr-003",
    name: "Martín Reyes",
    email: "martin@routeoptimizer.ai",
    role: "Operations",
    status: "invited",
    team: "Distribución Urbana",
    region: "Puente Alto",
    lastAccess: "Pendiente",
  },
  {
    id: "usr-004",
    name: "Valentina Díaz",
    email: "valentina@routeoptimizer.ai",
    role: "Viewer",
    status: "active",
    team: "Dirección Comercial",
    region: "San Bernardo",
    lastAccess: "Ayer, 18:37",
  },
  {
    id: "usr-005",
    name: "Ignacio Pérez",
    email: "ignacio@routeoptimizer.ai",
    role: "Operations",
    status: "suspended",
    team: "Flota Externa",
    region: "Santiago",
    lastAccess: "12 Apr, 16:11",
  },
];
