import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router";
import { ArrowRight, ShieldCheck, Truck } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { useAuth } from "../data/AuthContext";

export function Login() {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("bruno@routeoptimizer.ai");
  const [password, setPassword] = useState("demo123");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (isAuthenticated) {
    const redirectTo = (location.state as { from?: string } | null)?.from ?? "/";
    return <Navigate to={redirectTo} replace />;
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setSubmitting(true);
      setError(null);
      await login(email, password);
      const redirectTo = (location.state as { from?: string } | null)?.from ?? "/";
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo iniciar sesion.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(14,116,144,0.18),_transparent_35%),linear-gradient(135deg,#f8fafc_0%,#e2e8f0_44%,#cbd5e1_100%)] text-slate-950">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-10 px-6 py-8 lg:flex-row lg:items-center lg:px-10">
        <div className="flex-1 space-y-6">
          <div className="inline-flex items-center gap-3 rounded-full border border-sky-200 bg-white/80 px-4 py-2 text-sm text-slate-700 shadow-sm backdrop-blur">
            <Truck className="size-4 text-sky-700" />
            RouteOptimizer Cloud
          </div>

          <div className="max-w-xl space-y-4">
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-sky-800">Urban routing workspace</p>
            <h1 className="font-serif text-5xl leading-tight text-slate-950">
              Optimización y control operativo.
            </h1>
            <p className="text-base leading-7 text-slate-700">
              Acceso al workspace operativo.
            </p>
          </div>

          <Card className="max-w-md border-white/70 bg-white/75 shadow-lg shadow-slate-200/70 backdrop-blur">
            <CardContent className="flex items-center gap-4 p-5">
              <ShieldCheck className="size-6 text-emerald-600" />
              <div>
                <p className="text-sm font-semibold text-slate-900">Acceso por roles</p>
                <p className="mt-1 text-sm text-slate-600">Operación, planificación y supervisión en un mismo entorno.</p>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="w-full max-w-md">
          <Card className="overflow-hidden border-slate-200/80 bg-white/90 shadow-2xl shadow-slate-300/40 backdrop-blur">
            <CardContent className="space-y-6 p-8">
              <div className="space-y-2">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">Workspace access</p>
                <h2 className="font-serif text-3xl text-slate-950">Iniciar sesión</h2>
                <p className="text-sm text-slate-600">Acceso local.</p>
              </div>

              <form className="space-y-5" onSubmit={handleSubmit}>
                <div className="space-y-2">
                  <Label htmlFor="login-email">Correo</Label>
                  <Input
                    id="login-email"
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    placeholder="bruno@routeoptimizer.ai"
                    className="h-11 bg-slate-50"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="login-password">Contraseña</Label>
                    <span className="text-xs text-slate-500">Local</span>
                  </div>
                  <Input
                    id="login-password"
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="demo123"
                    className="h-11 bg-slate-50"
                  />
                </div>

                {error && <p className="text-sm text-red-600">{error}</p>}

                <Button type="submit" className="h-11 w-full bg-slate-950 text-white hover:bg-slate-800" disabled={submitting}>
                  {submitting ? "Ingresando..." : "Entrar al workspace"}
                  <ArrowRight className="ml-2 size-4" />
                </Button>
              </form>

              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                Usuario sugerido: <span className="font-medium text-slate-900">bruno@routeoptimizer.ai</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
