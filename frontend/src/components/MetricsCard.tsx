"use client";

import { cn, formatNumber, formatPercentage, getMetricDescription, capitalizeWords } from "@/lib/utils";

interface MetricsCardProps {
  title: string;
  value: number;
  format?: "number" | "percentage" | "currency";
  decimals?: number;
  description?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  icon?: React.ReactNode;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export default function MetricsCard({
  title,
  value,
  format = "number",
  decimals = 4,
  description,
  trend,
  icon,
  className,
  size = "md",
}: MetricsCardProps) {
  const formattedValue = (() => {
    switch (format) {
      case "percentage":
        return formatPercentage(value, decimals);
      case "currency":
        return new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: "USD",
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(value);
      default:
        return formatNumber(value, decimals);
    }
  })();

  const sizeClasses = {
    sm: "p-4",
    md: "p-6",
    lg: "p-8",
  };

  const valueSizeClasses = {
    sm: "text-xl",
    md: "text-3xl",
    lg: "text-4xl",
  };

  return (
    <div
      className={cn(
        "card transition-all duration-300 hover:shadow-xl group",
        sizeClasses[size],
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            {capitalizeWords(title)}
          </h3>
          <p
            className={cn(
              "font-bold text-slate-900 dark:text-white mt-2",
              valueSizeClasses[size]
            )}
          >
            {formattedValue}
          </p>
          {description && (
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
              {description}
            </p>
          )}
          {trend && (
            <div className="flex items-center gap-1 mt-2">
              <span
                className={cn(
                  "text-sm font-medium",
                  trend.isPositive ? "text-success-500" : "text-error-500"
                )}
              >
                {trend.isPositive ? "+" : "-"}
                {Math.abs(trend.value).toFixed(1)}%
              </span>
              <svg
                className={cn(
                  "w-4 h-4",
                  trend.isPositive ? "text-success-500 rotate-0" : "text-error-500 rotate-180"
                )}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 10l7-7m0 0l7 7m-7-7v18"
                />
              </svg>
            </div>
          )}
        </div>
        {icon && (
          <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-xl group-hover:scale-110 transition-transform">
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}

interface MetricsGridProps {
  metrics: {
    r2_score: number;
    mse: number;
    rmse: number;
    mae: number;
    adjusted_r2?: number;
  };
}

export function MetricsGrid({ metrics }: MetricsGridProps) {
  const metricItems = [
    {
      key: "r2_score",
      title: "R-Squared",
      value: metrics.r2_score,
      format: "percentage" as const,
      icon: (
        <svg
          className="w-6 h-6 text-primary-600 dark:text-primary-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
      ),
    },
    {
      key: "mse",
      title: "MSE",
      value: metrics.mse,
      format: "number" as const,
      icon: (
        <svg
          className="w-6 h-6 text-warning-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
          />
        </svg>
      ),
    },
    {
      key: "rmse",
      title: "RMSE",
      value: metrics.rmse,
      format: "number" as const,
      icon: (
        <svg
          className="w-6 h-6 text-success-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"
          />
        </svg>
      ),
    },
    {
      key: "mae",
      title: "MAE",
      value: metrics.mae,
      format: "number" as const,
      icon: (
        <svg
          className="w-6 h-6 text-error-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 6h16M4 10h16M4 14h16M4 18h16"
          />
        </svg>
      ),
    },
  ];

  if (metrics.adjusted_r2 !== undefined) {
    metricItems.push({
      key: "adjusted_r2",
      title: "Adjusted R-Squared",
      value: metrics.adjusted_r2,
      format: "percentage" as const,
      icon: (
        <svg
          className="w-6 h-6 text-violet-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"
          />
        </svg>
      ),
    });
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      {metricItems.map((item) => (
        <MetricsCard
          key={item.key}
          title={item.title}
          value={item.value}
          format={item.format}
          description={getMetricDescription(item.key)}
          icon={item.icon}
          size="sm"
        />
      ))}
    </div>
  );
}
