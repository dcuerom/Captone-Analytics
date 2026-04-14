import { Link } from "react-router";
import { Home } from "lucide-react";
import { Button } from "../components/ui/button";

export function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-screen p-8 bg-slate-50">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-slate-300 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">Página no encontrada</h2>
        <p className="text-slate-600 mb-6">
          La página que estás buscando no existe o ha sido movida.
        </p>
        <Link to="/">
          <Button>
            <Home className="size-4 mr-2" />
            Volver al Dashboard
          </Button>
        </Link>
      </div>
    </div>
  );
}
