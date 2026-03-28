"use client";

import { useState, useEffect } from "react";
import { useApp } from "@/context/AppContext";
import { predict } from "@/lib/api";
import { PredictResponse } from "@/lib/types";
import { capitalizeWords, formatNumber } from "@/lib/utils";
import LoadingSpinner from "./LoadingSpinner";

interface PredictionFormProps {
  onPrediction?: (result: PredictResponse) => void;
}

export default function PredictionForm({ onPrediction }: PredictionFormProps) {
  const { modelStatus, setError } = useApp();
  const [features, setFeatures] = useState<Record<string, number>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<PredictResponse | null>(null);

  // Initialize features from model status
  useEffect(() => {
    if (modelStatus?.feature_columns) {
      const initialFeatures: Record<string, number> = {};
      modelStatus.feature_columns.forEach((col) => {
        initialFeatures[col] = 0;
      });
      setFeatures(initialFeatures);
    }
  }, [modelStatus]);

  const handleInputChange = (feature: string, value: string) => {
    const numValue = parseFloat(value) || 0;
    setFeatures((prev) => ({
      ...prev,
      [feature]: numValue,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await predict({ features });
      setResult(response);
      onPrediction?.(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    if (modelStatus?.feature_columns) {
      const resetFeatures: Record<string, number> = {};
      modelStatus.feature_columns.forEach((col) => {
        resetFeatures[col] = 0;
      });
      setFeatures(resetFeatures);
    }
    setResult(null);
  };

  if (!modelStatus?.is_trained) {
    return (
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
            d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
          />
        </svg>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
          No Model Available
        </h3>
        <p className="text-slate-500 dark:text-slate-400 mb-4">
          Please train a model first to make predictions
        </p>
        <a href="/train" className="btn-primary inline-block">
          Go to Training
        </a>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Input Form */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
          Campaign Parameters
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
          Enter values for each feature to predict {modelStatus.target_column}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {modelStatus.feature_columns.map((feature) => (
              <div key={feature}>
                <label className="label">{capitalizeWords(feature)}</label>
                <input
                  type="number"
                  step="any"
                  value={features[feature] || ""}
                  onChange={(e) => handleInputChange(feature, e.target.value)}
                  className="input"
                  placeholder={`Enter ${feature}`}
                />
              </div>
            ))}
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary flex-1 flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <LoadingSpinner size="sm" />
                  Predicting...
                </>
              ) : (
                <>
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
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                  Predict
                </>
              )}
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="btn-secondary"
            >
              Reset
            </button>
          </div>
        </form>
      </div>

      {/* Results */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
          Prediction Result
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
          Predicted {capitalizeWords(modelStatus.target_column)}
        </p>

        {result ? (
          <div className="space-y-6">
            {/* Main Prediction */}
            <div className="text-center p-6 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/30 dark:to-primary-800/30 rounded-xl">
              <p className="text-sm text-primary-600 dark:text-primary-400 font-medium mb-2">
                Predicted Value
              </p>
              <p className="text-4xl font-bold text-primary-700 dark:text-primary-300">
                {formatNumber(result.prediction, 2)}
              </p>
              {result.confidence_interval && (
                <p className="text-sm text-primary-600 dark:text-primary-400 mt-2">
                  95% CI: [{formatNumber(result.confidence_interval.lower, 2)} -{" "}
                  {formatNumber(result.confidence_interval.upper, 2)}]
                </p>
              )}
            </div>

            {/* Feature Contributions */}
            {result.feature_contributions && (
              <div>
                <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                  Feature Contributions
                </h4>
                <div className="space-y-2">
                  {Object.entries(result.feature_contributions)
                    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
                    .map(([feature, contribution]) => (
                      <div
                        key={feature}
                        className="flex items-center justify-between p-2 bg-slate-50 dark:bg-slate-800/50 rounded-lg"
                      >
                        <span className="text-sm text-slate-600 dark:text-slate-400">
                          {capitalizeWords(feature)}
                        </span>
                        <span
                          className={`text-sm font-medium ${
                            contribution >= 0
                              ? "text-success-500"
                              : "text-error-500"
                          }`}
                        >
                          {contribution >= 0 ? "+" : ""}
                          {formatNumber(contribution, 2)}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-48 text-slate-400 dark:text-slate-500">
            <svg
              className="w-12 h-12 mb-3"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
              />
            </svg>
            <p className="text-sm">Enter values and click Predict</p>
          </div>
        )}
      </div>
    </div>
  );
}
