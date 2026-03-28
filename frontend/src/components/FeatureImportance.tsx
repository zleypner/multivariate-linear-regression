"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { FeatureWeight } from "@/lib/types";
import { generateChartColors, capitalizeWords } from "@/lib/utils";

interface FeatureImportanceProps {
  features: FeatureWeight[];
  showWeights?: boolean;
}

export default function FeatureImportance({
  features,
  showWeights = false,
}: FeatureImportanceProps) {
  const sortedFeatures = [...features].sort(
    (a, b) => Math.abs(b.importance) - Math.abs(a.importance)
  );

  const chartData = sortedFeatures.map((f) => ({
    name: capitalizeWords(f.feature),
    value: showWeights ? f.weight : Math.abs(f.importance) * 100,
    weight: f.weight,
    importance: f.importance,
    isPositive: f.weight >= 0,
  }));

  const colors = generateChartColors(chartData.length);

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: { payload: typeof chartData[0] }[] }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white dark:bg-slate-800 p-4 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700">
          <p className="font-semibold text-slate-900 dark:text-white mb-2">
            {data.name}
          </p>
          <div className="space-y-1 text-sm">
            <p className="text-slate-600 dark:text-slate-300">
              <span className="font-medium">Weight:</span>{" "}
              <span className={data.weight >= 0 ? "text-success-500" : "text-error-500"}>
                {data.weight >= 0 ? "+" : ""}
                {data.weight.toFixed(4)}
              </span>
            </p>
            <p className="text-slate-600 dark:text-slate-300">
              <span className="font-medium">Importance:</span>{" "}
              {(Math.abs(data.importance) * 100).toFixed(1)}%
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
            Feature Importance
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Impact of each feature on predictions
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-success-500" />
            <span className="text-slate-600 dark:text-slate-400">Positive</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-error-500" />
            <span className="text-slate-600 dark:text-slate-400">Negative</span>
          </div>
        </div>
      </div>

      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="currentColor"
              className="text-slate-200 dark:text-slate-700"
            />
            <XAxis
              type="number"
              tick={{ fill: "currentColor" }}
              className="text-slate-600 dark:text-slate-400 text-xs"
              tickFormatter={(value) =>
                showWeights ? value.toFixed(2) : `${value.toFixed(0)}%`
              }
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ fill: "currentColor" }}
              className="text-slate-600 dark:text-slate-400 text-xs"
              width={90}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey="value"
              radius={[0, 4, 4, 0]}
              maxBarSize={30}
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.isPositive ? "#22c55e" : "#ef4444"}
                  className="hover:opacity-80 transition-opacity"
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Feature List */}
      <div className="mt-6 space-y-2">
        {sortedFeatures.slice(0, 5).map((feature, index) => (
          <div
            key={feature.feature}
            className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg"
          >
            <div className="flex items-center gap-3">
              <span className="w-6 h-6 flex items-center justify-center bg-primary-100 dark:bg-primary-900/30 rounded-full text-xs font-semibold text-primary-700 dark:text-primary-300">
                {index + 1}
              </span>
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                {capitalizeWords(feature.feature)}
              </span>
            </div>
            <div className="flex items-center gap-4">
              <span
                className={`text-sm font-medium ${
                  feature.weight >= 0 ? "text-success-500" : "text-error-500"
                }`}
              >
                {feature.weight >= 0 ? "+" : ""}
                {feature.weight.toFixed(4)}
              </span>
              <span className="text-xs text-slate-500 dark:text-slate-400 bg-slate-200 dark:bg-slate-700 px-2 py-1 rounded">
                {(Math.abs(feature.importance) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
