"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/context/AppContext";
import { getModelStatus, getResults, resetModel } from "@/lib/api";
import { ResultsResponse } from "@/lib/types";
import { MetricsGrid } from "@/components/MetricsCard";
import FeatureImportance from "@/components/FeatureImportance";
import ResultsChart, { ResidualsChart } from "@/components/ResultsChart";
import { LoadingCard } from "@/components/LoadingSpinner";
import { capitalizeWords, formatNumber } from "@/lib/utils";
import { useRouter } from "next/navigation";

export default function ResultsPage() {
  const router = useRouter();
  const { modelStatus, setModelStatus, setError, error, resetState } = useApp();
  const [results, setResults] = useState<ResultsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isResetting, setIsResetting] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "features" | "residuals">(
    "overview"
  );

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const status = await getModelStatus();
        setModelStatus(status);

        if (status.is_trained) {
          const resultsData = await getResults();
          setResults(resultsData);
        }
      } catch (err) {
        console.log("No model trained yet");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [setModelStatus, setError]);

  const handleReset = async () => {
    if (!confirm("Are you sure you want to reset the model? This action cannot be undone.")) {
      return;
    }

    setIsResetting(true);
    try {
      await resetModel();
      resetState();
      router.push("/upload");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reset model");
    } finally {
      setIsResetting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Results & Analysis
          </h1>
          <p className="text-slate-500 dark:text-slate-400">
            Detailed model performance analysis
          </p>
        </div>
        <LoadingCard text="Loading results..." />
      </div>
    );
  }

  if (!modelStatus?.is_trained) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Results & Analysis
          </h1>
          <p className="text-slate-500 dark:text-slate-400">
            Detailed model performance analysis
          </p>
        </div>

        <div className="card p-8 text-center">
          <svg
            className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            No Results Available
          </h3>
          <p className="text-slate-500 dark:text-slate-400 mb-4">
            Train a model first to see detailed results and analysis
          </p>
          <button onClick={() => router.push("/train")} className="btn-primary">
            Go to Training
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Results & Analysis
          </h1>
          <p className="text-slate-500 dark:text-slate-400">
            Detailed model performance analysis for{" "}
            <span className="font-medium">
              {capitalizeWords(modelStatus.target_column)}
            </span>
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => router.push("/predict")}
            className="btn-primary"
          >
            Make Predictions
          </button>
          <button
            onClick={handleReset}
            disabled={isResetting}
            className="btn-secondary text-error-600 dark:text-error-400 hover:bg-error-50 dark:hover:bg-error-900/20"
          >
            {isResetting ? "Resetting..." : "Reset Model"}
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-800 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <svg
              className="w-5 h-5 text-error-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="text-error-700 dark:text-error-300">{error}</p>
          </div>
        </div>
      )}

      {/* Metrics */}
      {modelStatus.metrics && <MetricsGrid metrics={modelStatus.metrics} />}

      {/* Tabs */}
      <div className="border-b border-slate-200 dark:border-slate-700">
        <nav className="flex gap-4">
          {[
            { id: "overview", label: "Overview" },
            { id: "features", label: "Feature Analysis" },
            { id: "residuals", label: "Residuals" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() =>
                setActiveTab(tab.id as "overview" | "features" | "residuals")
              }
              className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-primary-500 text-primary-600 dark:text-primary-400"
                  : "border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Actual vs Predicted */}
          {results?.data_points && results.data_points.length > 0 && (
            <ResultsChart data={results.data_points} />
          )}

          {/* Model Summary */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Model Summary
            </h3>

            <div className="space-y-4">
              <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Model Equation
                </h4>
                <div className="font-mono text-sm text-slate-600 dark:text-slate-400 overflow-x-auto">
                  <span className="text-primary-600 dark:text-primary-400">
                    {capitalizeWords(modelStatus.target_column)}
                  </span>{" "}
                  ={" "}
                  {modelStatus.feature_weights?.map((fw, i) => (
                    <span key={fw.feature}>
                      {i > 0 && (
                        <span className="text-slate-400">
                          {fw.weight >= 0 ? " + " : " - "}
                        </span>
                      )}
                      {i === 0 && fw.weight < 0 && "-"}
                      <span className="text-success-600 dark:text-success-400">
                        {Math.abs(fw.weight).toFixed(4)}
                      </span>
                      <span className="text-slate-500"> * </span>
                      <span className="text-warning-600 dark:text-warning-400">
                        {fw.feature}
                      </span>
                    </span>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Target Variable
                  </p>
                  <p className="text-lg font-semibold text-slate-900 dark:text-white">
                    {capitalizeWords(modelStatus.target_column)}
                  </p>
                </div>
                <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Feature Count
                  </p>
                  <p className="text-lg font-semibold text-slate-900 dark:text-white">
                    {modelStatus.feature_columns.length}
                  </p>
                </div>
              </div>

              {/* Feature List */}
              <div>
                <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Features Used
                </h4>
                <div className="flex flex-wrap gap-2">
                  {modelStatus.feature_columns.map((feature) => (
                    <span
                      key={feature}
                      className="px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-full text-sm"
                    >
                      {capitalizeWords(feature)}
                    </span>
                  ))}
                </div>
              </div>

              {/* Interpretation */}
              <div className="p-4 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg">
                <h4 className="text-sm font-medium text-primary-700 dark:text-primary-300 mb-2">
                  Model Interpretation
                </h4>
                {modelStatus.metrics && (
                  <p className="text-sm text-primary-600 dark:text-primary-400">
                    This model explains{" "}
                    <span className="font-semibold">
                      {(modelStatus.metrics.r2_score * 100).toFixed(1)}%
                    </span>{" "}
                    of the variance in {capitalizeWords(modelStatus.target_column)}.{" "}
                    {modelStatus.metrics.r2_score >= 0.8
                      ? "This is a strong fit, suggesting the features have good predictive power."
                      : modelStatus.metrics.r2_score >= 0.6
                      ? "This is a moderate fit. Consider adding more relevant features."
                      : "This is a weak fit. The features may not adequately explain the target variable."}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "features" && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {modelStatus.feature_weights && (
            <FeatureImportance features={modelStatus.feature_weights} />
          )}

          {/* Feature Details Table */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Feature Coefficients
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <th className="text-left py-3 px-4 text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase">
                      Feature
                    </th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase">
                      Weight
                    </th>
                    <th className="text-right py-3 px-4 text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase">
                      Importance
                    </th>
                    <th className="text-center py-3 px-4 text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase">
                      Direction
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-700">
                  {modelStatus.feature_weights
                    ?.sort((a, b) => Math.abs(b.importance) - Math.abs(a.importance))
                    .map((fw) => (
                      <tr
                        key={fw.feature}
                        className="hover:bg-slate-50 dark:hover:bg-slate-800/50"
                      >
                        <td className="py-3 px-4 text-sm font-medium text-slate-900 dark:text-white">
                          {capitalizeWords(fw.feature)}
                        </td>
                        <td className="py-3 px-4 text-sm text-right font-mono">
                          <span
                            className={
                              fw.weight >= 0
                                ? "text-success-600 dark:text-success-400"
                                : "text-error-600 dark:text-error-400"
                            }
                          >
                            {fw.weight >= 0 ? "+" : ""}
                            {fw.weight.toFixed(4)}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-right">
                          <span className="px-2 py-1 bg-slate-100 dark:bg-slate-700 rounded text-slate-600 dark:text-slate-300">
                            {(Math.abs(fw.importance) * 100).toFixed(1)}%
                          </span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          {fw.weight >= 0 ? (
                            <span className="inline-flex items-center gap-1 text-success-600 dark:text-success-400">
                              <svg
                                className="w-4 h-4"
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
                              Positive
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-error-600 dark:text-error-400">
                              <svg
                                className="w-4 h-4"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M19 14l-7 7m0 0l-7-7m7 7V3"
                                />
                              </svg>
                              Negative
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === "residuals" && results?.data_points && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ResidualsChart data={results.data_points} />

          {/* Residuals Stats */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Residuals Statistics
            </h3>

            <div className="space-y-4">
              {(() => {
                const residuals = results.data_points.map((d) => d.residual);
                const mean =
                  residuals.reduce((a, b) => a + b, 0) / residuals.length;
                const variance =
                  residuals.reduce((a, b) => a + Math.pow(b - mean, 2), 0) /
                  residuals.length;
                const std = Math.sqrt(variance);
                const min = Math.min(...residuals);
                const max = Math.max(...residuals);
                const sortedResiduals = [...residuals].sort((a, b) => a - b);
                const median =
                  sortedResiduals.length % 2 === 0
                    ? (sortedResiduals[sortedResiduals.length / 2 - 1] +
                        sortedResiduals[sortedResiduals.length / 2]) /
                      2
                    : sortedResiduals[Math.floor(sortedResiduals.length / 2)];

                return (
                  <>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                          Mean
                        </p>
                        <p className="text-lg font-semibold text-slate-900 dark:text-white">
                          {formatNumber(mean, 4)}
                        </p>
                      </div>
                      <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                          Median
                        </p>
                        <p className="text-lg font-semibold text-slate-900 dark:text-white">
                          {formatNumber(median, 4)}
                        </p>
                      </div>
                      <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                          Std Dev
                        </p>
                        <p className="text-lg font-semibold text-slate-900 dark:text-white">
                          {formatNumber(std, 4)}
                        </p>
                      </div>
                      <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                        <p className="text-sm text-slate-500 dark:text-slate-400">
                          Range
                        </p>
                        <p className="text-lg font-semibold text-slate-900 dark:text-white">
                          {formatNumber(max - min, 4)}
                        </p>
                      </div>
                    </div>

                    <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-slate-500 dark:text-slate-400">
                          Min: {formatNumber(min, 2)}
                        </span>
                        <span className="text-slate-500 dark:text-slate-400">
                          Max: {formatNumber(max, 2)}
                        </span>
                      </div>
                      <div className="h-4 bg-gradient-to-r from-error-500 via-warning-500 to-success-500 rounded-full relative">
                        <div
                          className="absolute w-4 h-4 bg-white border-2 border-slate-400 rounded-full -top-0 transform -translate-x-1/2"
                          style={{
                            left: `${((0 - min) / (max - min)) * 100}%`,
                          }}
                        />
                      </div>
                      <p className="text-center text-xs text-slate-500 dark:text-slate-400 mt-2">
                        Zero line position
                      </p>
                    </div>

                    <div className="p-4 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg">
                      <h4 className="text-sm font-medium text-primary-700 dark:text-primary-300 mb-2">
                        Interpretation
                      </h4>
                      <p className="text-sm text-primary-600 dark:text-primary-400">
                        {Math.abs(mean) < std * 0.1
                          ? "The residuals are well-centered around zero, indicating no systematic bias in predictions."
                          : mean > 0
                          ? "The model tends to underestimate the target values on average."
                          : "The model tends to overestimate the target values on average."}
                      </p>
                    </div>
                  </>
                );
              })()}
            </div>
          </div>
        </div>
      )}

      {/* Export Section */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          Export & Share
        </h3>
        <div className="flex flex-wrap gap-4">
          <button
            className="btn-secondary flex items-center gap-2"
            onClick={() => {
              const data = {
                model_status: modelStatus,
                results: results,
              };
              const blob = new Blob([JSON.stringify(data, null, 2)], {
                type: "application/json",
              });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "model_results.json";
              a.click();
            }}
          >
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Export JSON
          </button>
          <button
            className="btn-secondary flex items-center gap-2"
            onClick={() => {
              if (!modelStatus.feature_weights) return;
              let csv = "Feature,Weight,Importance\n";
              modelStatus.feature_weights.forEach((fw) => {
                csv += `${fw.feature},${fw.weight},${fw.importance}\n`;
              });
              const blob = new Blob([csv], { type: "text/csv" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "feature_weights.csv";
              a.click();
            }}
          >
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            Export Features CSV
          </button>
        </div>
      </div>
    </div>
  );
}
