import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { mockUsers, type SaaSUser } from "./mockUsers";

interface AuthSession {
  email: string;
}

interface AuthContextValue {
  isAuthenticated: boolean;
  currentUser: SaaSUser | null;
  users: SaaSUser[];
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const STORAGE_KEY = "route-optimizer-auth";

const AuthContext = createContext<AuthContextValue>({
  isAuthenticated: false,
  currentUser: null,
  users: mockUsers,
  login: async () => undefined,
  logout: () => undefined,
});

function resolveUser(email: string): SaaSUser {
  const normalized = email.trim().toLowerCase();
  const existing = mockUsers.find((user) => user.email.toLowerCase() === normalized);
  if (existing) {
    return existing;
  }
  return {
    id: "usr-demo",
    name: "Demo Account",
    email: normalized || "demo@routeoptimizer.ai",
    role: "Owner",
    status: "active",
    team: "Capstone Analytics",
    region: "Santiago",
    lastAccess: "Ahora",
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(null);

  useEffect(() => {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return;
    }
    try {
      const parsed = JSON.parse(raw) as AuthSession;
      if (parsed?.email) {
        setSession(parsed);
      }
    } catch {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }, []);

  const currentUser = useMemo(() => {
    if (!session?.email) {
      return null;
    }
    return resolveUser(session.email);
  }, [session]);

  const value = useMemo<AuthContextValue>(() => ({
    isAuthenticated: Boolean(currentUser),
    currentUser,
    users: mockUsers,
    login: async (email: string, password: string) => {
      const normalizedEmail = email.trim().toLowerCase();
      if (!normalizedEmail) {
        throw new Error("Ingresa un correo de acceso.");
      }
      if (!password.trim()) {
        throw new Error("Ingresa una contraseña.");
      }
      const nextSession = { email: normalizedEmail };
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
      setSession(nextSession);
    },
    logout: () => {
      window.localStorage.removeItem(STORAGE_KEY);
      setSession(null);
    },
  }), [currentUser]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
