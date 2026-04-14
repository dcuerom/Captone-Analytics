import { useMemo, useState } from "react";
import { Mail, Plus, Search, Shield, Users as UsersIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { useAuth } from "../data/AuthContext";

function statusTone(status: string) {
  if (status === "active") {
    return "bg-emerald-100 text-emerald-800";
  }
  if (status === "invited") {
    return "bg-amber-100 text-amber-800";
  }
  return "bg-rose-100 text-rose-800";
}

export function Users() {
  const { users, currentUser } = useAuth();
  const [query, setQuery] = useState("");

  const filteredUsers = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) {
      return users;
    }
    return users.filter((user) =>
      [user.name, user.email, user.role, user.team, user.region].some((value) => value.toLowerCase().includes(term)),
    );
  }, [query, users]);

  const activeUsers = users.filter((user) => user.status === "active").length;

  return (
    <div className="space-y-6 p-8">
      <section className="rounded-3xl border border-slate-200 bg-[linear-gradient(135deg,#0f172a_0%,#1e293b_45%,#0f766e_100%)] p-8 text-white shadow-xl">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl space-y-3">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-200">SaaS workspace</p>
            <h1 className="font-serif text-4xl leading-tight">Gestión de usuarios y control de acceso</h1>
            <p className="text-sm leading-7 text-slate-200">
              Gestión de cuentas, roles y acceso del workspace.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <Card className="border-white/10 bg-white/10 text-white shadow-none backdrop-blur">
              <CardContent className="p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Usuarios</p>
                <p className="mt-2 text-3xl font-semibold">{users.length}</p>
              </CardContent>
            </Card>
            <Card className="border-white/10 bg-white/10 text-white shadow-none backdrop-blur">
              <CardContent className="p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Activos</p>
                <p className="mt-2 text-3xl font-semibold">{activeUsers}</p>
              </CardContent>
            </Card>
            <Card className="border-white/10 bg-white/10 text-white shadow-none backdrop-blur">
              <CardContent className="p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Tu rol</p>
                <p className="mt-2 text-3xl font-semibold">{currentUser?.role ?? "Owner"}</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.7fr,0.8fr]">
        <Card className="border-slate-200 shadow-sm">
          <CardHeader className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <CardTitle>Directorio de usuarios</CardTitle>
              <p className="mt-1 text-sm text-slate-600">Directorio y administración de accesos.</p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <div className="relative w-full sm:w-72">
                <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
                <Input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Buscar por nombre, rol o equipo"
                  className="pl-9"
                />
              </div>
              <Button className="bg-slate-950 hover:bg-slate-800">
                <Plus className="mr-2 size-4" />
                Invitar usuario
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-[0.16em] text-slate-500">
                    <th className="px-3 py-3 font-medium">Usuario</th>
                    <th className="px-3 py-3 font-medium">Rol</th>
                    <th className="px-3 py-3 font-medium">Estado</th>
                    <th className="px-3 py-3 font-medium">Equipo</th>
                    <th className="px-3 py-3 font-medium">Región</th>
                    <th className="px-3 py-3 font-medium">Último acceso</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.map((user) => (
                    <tr key={user.id} className="border-b border-slate-100 align-top">
                      <td className="px-3 py-4">
                        <div>
                          <p className="font-medium text-slate-900">{user.name}</p>
                          <p className="mt-1 text-slate-500">{user.email}</p>
                        </div>
                      </td>
                      <td className="px-3 py-4 text-slate-700">{user.role}</td>
                      <td className="px-3 py-4">
                        <Badge className={statusTone(user.status)}>{user.status}</Badge>
                      </td>
                      <td className="px-3 py-4 text-slate-700">{user.team}</td>
                      <td className="px-3 py-4 text-slate-700">{user.region}</td>
                      <td className="px-3 py-4 text-slate-500">{user.lastAccess}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle>Seguridad y governance</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-slate-600">
              <div className="flex items-start gap-3 rounded-2xl bg-slate-50 p-4">
                <Shield className="mt-0.5 size-4 text-sky-700" />
                <div>
                  <p className="font-medium text-slate-900">Roles de acceso</p>
                  <p className="mt-1">Owner, Planner, Operations y Viewer para segmentar permisos del workspace.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 rounded-2xl bg-slate-50 p-4">
                <Mail className="mt-0.5 size-4 text-emerald-700" />
                <div>
                  <p className="font-medium text-slate-900">Invitaciones</p>
                  <p className="mt-1">Flujo de invitación preparado para una futura integración de identidad.</p>
                </div>
              </div>
              <div className="flex items-start gap-3 rounded-2xl bg-slate-50 p-4">
                <UsersIcon className="mt-0.5 size-4 text-amber-600" />
                <div>
                  <p className="font-medium text-slate-900">Sesión local</p>
                  <p className="mt-1">La sesión se conserva localmente para mantener continuidad de navegación.</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
