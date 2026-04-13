import { Badge } from "../ui/badge";
import { cn } from "../ui/utils";

interface StatusBadgeProps {
  status: 'on-time' | 'waiting' | 'violation' | 'assigned' | 'unassigned' | 'split' | 'delivered' | 'pending' | 'running' | 'completed' | 'failed' | 'infeasible';
  label?: string;
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const config = {
    'on-time': { 
      label: label || 'A tiempo', 
      className: 'bg-green-100 text-green-800 border-green-200' 
    },
    'waiting': { 
      label: label || 'Esperando', 
      className: 'bg-amber-100 text-amber-800 border-amber-200' 
    },
    'violation': { 
      label: label || 'Violación', 
      className: 'bg-red-100 text-red-800 border-red-200' 
    },
    'assigned': { 
      label: label || 'Asignado', 
      className: 'bg-blue-100 text-blue-800 border-blue-200' 
    },
    'unassigned': { 
      label: label || 'No asignado', 
      className: 'bg-slate-100 text-slate-800 border-slate-200' 
    },
    'split': { 
      label: label || 'Dividido', 
      className: 'bg-purple-100 text-purple-800 border-purple-200' 
    },
    'delivered': { 
      label: label || 'Entregado', 
      className: 'bg-green-100 text-green-800 border-green-200' 
    },
    'pending': { 
      label: label || 'Pendiente', 
      className: 'bg-slate-100 text-slate-800 border-slate-200' 
    },
    'running': { 
      label: label || 'Ejecutando', 
      className: 'bg-blue-100 text-blue-800 border-blue-200' 
    },
    'completed': { 
      label: label || 'Completado', 
      className: 'bg-green-100 text-green-800 border-green-200' 
    },
    'failed': { 
      label: label || 'Fallido', 
      className: 'bg-red-100 text-red-800 border-red-200' 
    },
    'infeasible': { 
      label: label || 'Infactible', 
      className: 'bg-orange-100 text-orange-800 border-orange-200' 
    },
  };

  const { label: displayLabel, className } = config[status];

  return (
    <Badge variant="outline" className={cn("text-xs font-medium", className)}>
      {displayLabel}
    </Badge>
  );
}
