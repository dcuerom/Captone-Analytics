import { LucideIcon } from "lucide-react";
import { Card } from "../ui/card";
import { cn } from "../ui/utils";

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: number;
    label: string;
  };
  variant?: "default" | "success" | "warning" | "danger";
}

export function KPICard({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  trend, 
  variant = "default" 
}: KPICardProps) {
  const variantStyles = {
    default: "bg-blue-50 text-blue-600",
    success: "bg-green-50 text-green-600",
    warning: "bg-amber-50 text-amber-600",
    danger: "bg-red-50 text-red-600",
  };

  return (
    <Card className="p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-slate-600 mb-1">{title}</p>
          <p className="text-3xl font-semibold text-slate-900 mb-1">{value}</p>
          {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
          {trend && (
            <div className="mt-2 flex items-center gap-1">
              <span className={cn(
                "text-xs font-medium",
                trend.value > 0 ? "text-green-600" : trend.value < 0 ? "text-red-600" : "text-slate-600"
              )}>
                {trend.value > 0 ? "+" : ""}{trend.value}%
              </span>
              <span className="text-xs text-slate-500">{trend.label}</span>
            </div>
          )}
        </div>
        <div className={cn("p-3 rounded-lg", variantStyles[variant])}>
          <Icon className="size-6" />
        </div>
      </div>
    </Card>
  );
}
