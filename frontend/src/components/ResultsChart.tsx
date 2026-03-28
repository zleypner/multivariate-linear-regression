"use client";

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Line,
  ComposedChart,
} from "recharts";
import { DataPoint } from "@/lib/types";
import { formatNumber } from "@/lib/utils";

interface ResultsChartProps {
  data: DataPoint[];
  title?: string;
}

export default function ResultsChart({ data, title }: ResultsChartProps) {
  const chartData = data.map((point, index) => ({
    ...point,
    name: `Point ${index + 1}`,
  }));

  // Calculate min and max for axis range
  const allValues = data.flatMap((d) => [d.actual, d.predicted]);
  const minValue = Math.min(...allValues);
  const maxValue = Math.max(...allValues);
  const padding = (maxValue - minValue) * 0.1;

  // Perfect prediction line data
  const lineData = [
    { actual: minValue - padding, predicted: minValue - padding },
    { actual: maxValue + padding, predicted: maxValue + padding },
  ];

  const CustomTooltip = ({
    active,
    payload,
  }: {
    active?: boolean;
    payload?: { payload: typeof chartData[0] }[];
  }) => {
    if (active && payload && payload.length) {
      const point = payload[0].payload;
      return (
        <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700">
          <div className="space-y-2 text-sm">
            <p className="text-slate-600 dark:text-slate-300">
              <span className="font-medium">Actual:</span>{" "}
              {formatNumber(point.actual, 2)}
            </p>
            <p className="text-slate-600 dark:text-slate-300">
              <span className="font-medium">Predicted:</span>{" "}
              {formatNumber(point.predicted, 2)}
            </p>
            <p
              className={`font-medium ${
                Math.abs(point.residual) < (maxValue - minValue) * 0.1
                  ? "text-success-500"
                  : "text-warning-500"
              }`}
            >
              <span className="text-slate-600 dark:text-slate-300">Error:</span>{" "}
              {point.residual >= 0 ? "+" : ""}
              {formatNumber(point.residual, 2)}
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
            {title || "Actual vs Predicted"}
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Points closer to the diagonal line indicate better predictions
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-primary-500" />
            <span className="text-slate-600 dark:text-slate-400">
              Data Points
            </span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-8 h-0.5 bg-success-500" />
            <span className="text-slate-600 dark:text-slate-400">
              Perfect Fit
            </span>
          </div>
        </div>
      </div>

      <div className="h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="currentColor"
              className="text-slate-200 dark:text-slate-700"
            />
            <XAxis
              type="number"
              dataKey="actual"
              name="Actual"
              domain={[minValue - padding, maxValue + padding]}
              tick={{ fill: "currentColor" }}
              className="text-slate-600 dark:text-slate-400 text-xs"
              tickFormatter={(value) => formatNumber(value, 0)}
              label={{
                value: "Actual Values",
                position: "insideBottom",
                offset: -10,
                fill: "currentColor",
                className: "text-slate-600 dark:text-slate-400 text-xs",
              }}
            />
            <YAxis
              type="number"
              dataKey="predicted"
              name="Predicted"
              domain={[minValue - padding, maxValue + padding]}
              tick={{ fill: "currentColor" }}
              className="text-slate-600 dark:text-slate-400 text-xs"
              tickFormatter={(value) => formatNumber(value, 0)}
              label={{
                value: "Predicted Values",
                angle: -90,
                position: "insideLeft",
                fill: "currentColor",
                className: "text-slate-600 dark:text-slate-400 text-xs",
              }}
            />
            <Tooltip content={<CustomTooltip />} />

            {/* Perfect prediction line */}
            <Line
              data={lineData}
              type="linear"
              dataKey="predicted"
              stroke="#22c55e"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              legendType="none"
            />

            {/* Data points */}
            <Scatter
              data={chartData}
              fill="#0ea5e9"
              shape={(props: unknown) => {
                const { cx, cy } = props as { cx: number; cy: number };
                return (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={6}
                    fill="#0ea5e9"
                    fillOpacity={0.6}
                    stroke="#0284c7"
                    strokeWidth={2}
                    className="hover:fill-primary-400 transition-colors"
                  />
                );
              }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Stats */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="text-center p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">
            Data Points
          </p>
          <p className="text-lg font-semibold text-slate-900 dark:text-white">
            {data.length}
          </p>
        </div>
        <div className="text-center p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">
            Avg Error
          </p>
          <p className="text-lg font-semibold text-slate-900 dark:text-white">
            {formatNumber(
              data.reduce((sum, d) => sum + Math.abs(d.residual), 0) /
                data.length,
              2
            )}
          </p>
        </div>
        <div className="text-center p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">
            Max Error
          </p>
          <p className="text-lg font-semibold text-slate-900 dark:text-white">
            {formatNumber(Math.max(...data.map((d) => Math.abs(d.residual))), 2)}
          </p>
        </div>
      </div>
    </div>
  );
}

// Residuals histogram component
export function ResidualsChart({ data }: { data: DataPoint[] }) {
  // Create histogram bins
  const residuals = data.map((d) => d.residual);
  const minResidual = Math.min(...residuals);
  const maxResidual = Math.max(...residuals);
  const range = maxResidual - minResidual;
  const binCount = 10;
  const binSize = range / binCount;

  const bins: { range: string; count: number; midpoint: number }[] = [];
  for (let i = 0; i < binCount; i++) {
    const binStart = minResidual + i * binSize;
    const binEnd = binStart + binSize;
    const count = residuals.filter((r) => r >= binStart && r < binEnd).length;
    bins.push({
      range: `${formatNumber(binStart, 1)} - ${formatNumber(binEnd, 1)}`,
      count,
      midpoint: (binStart + binEnd) / 2,
    });
  }

  return (
    <div className="card p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
          Residuals Distribution
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Distribution of prediction errors
        </p>
      </div>

      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={bins} margin={{ top: 20, right: 20, bottom: 60, left: 20 }}>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="currentColor"
              className="text-slate-200 dark:text-slate-700"
            />
            <XAxis
              dataKey="midpoint"
              tick={{ fill: "currentColor" }}
              className="text-slate-600 dark:text-slate-400 text-xs"
              tickFormatter={(value) => formatNumber(value, 1)}
              label={{
                value: "Residual Value",
                position: "insideBottom",
                offset: -10,
                fill: "currentColor",
                className: "text-slate-600 dark:text-slate-400 text-xs",
              }}
            />
            <YAxis
              tick={{ fill: "currentColor" }}
              className="text-slate-600 dark:text-slate-400 text-xs"
              label={{
                value: "Frequency",
                angle: -90,
                position: "insideLeft",
                fill: "currentColor",
                className: "text-slate-600 dark:text-slate-400 text-xs",
              }}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white dark:bg-slate-800 p-3 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700">
                      <p className="text-sm text-slate-600 dark:text-slate-300">
                        <span className="font-medium">Range:</span> {data.range}
                      </p>
                      <p className="text-sm text-slate-600 dark:text-slate-300">
                        <span className="font-medium">Count:</span> {data.count}
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <ReferenceLine x={0} stroke="#ef4444" strokeDasharray="3 3" />
            <Scatter
              dataKey="count"
              fill="#0ea5e9"
              shape={(props: unknown) => {
                const { cx, cy, payload } = props as { cx: number; cy: number; payload: { count: number } };
                const width = 30;
                const height = (payload.count / Math.max(...bins.map((b) => b.count))) * 200;
                return (
                  <rect
                    x={cx - width / 2}
                    y={cy}
                    width={width}
                    height={Math.max(height, 2)}
                    fill="#0ea5e9"
                    fillOpacity={0.7}
                    rx={2}
                  />
                );
              }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
