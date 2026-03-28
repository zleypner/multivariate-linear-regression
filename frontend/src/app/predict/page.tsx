"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/context/AppContext";
import { getModelStatus } from "@/lib/api";
import PredictionForm from "@/components/PredictionForm";
import { LoadingCard } from "@/components/LoadingSpinner";
import { PredictResponse } from "@/lib/types";
import { formatNumber, capitalizeWords } from "@/lib/utils";

export default function PredictPage() {
  const { modelStatus, setModelStatus, error } = useApp();
  const [isLoading, setIsLoading] = useState(true);
  const [predictions, setPredictions] = useState<PredictResponse[]>([]);

  useEffect(() => {
    const fetchStatus = async () => {
      setIsLoading(true);
      try {
        const status = await getModelStatus();
        setModelStatus(status);
      } catch (err) {
        console.log("No model trained yet");
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatus();
  }, [setModelStatus]);

  const handlePrediction = (result: PredictResponse) => {
    setPredictions((prev) => [result, ...prev].slice(0, 10)); // Keep last 10 predictions
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Prediction Simulator
          </h1>
          <p className="text-slate-500 dark:text-slate-400">
            Test your model with new campaign data
          </p>
        </div>
        <LoadingCard text="Loading model..." />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Prediction Simulator
        </h1>
        <p className="text-slate-500 dark:text-slate-400">
          Test your model with new campaign data
        </p>
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

      {/* Model Info Banner */}
      {modelStatus?.is_trained && (
        <div className="card p-4 bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 border-primary-200 dark:border-primary-800">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary-200 dark:bg-primary-800 rounded-lg">
                <svg
                  className="w-5 h-5 text-primary-700 dark:text-primary-300"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
                  />
                </svg>
              </div>
              <div>
                <p className="font-medium text-primary-900 dark:text-primary-100">
                  Model Ready
                </p>
                <p className="text-sm text-primary-700 dark:text-primary-300">
                  Predicting{" "}
                  <span className="font-semibold">
                    {capitalizeWords(modelStatus.target_column)}
                  </span>{" "}
                  using {modelStatus.feature_columns.length} features
                </p>
              </div>
            </div>
            {modelStatus.metrics && (
              <div className="flex items-center gap-4 text-sm">
                <div className="text-center">
                  <p className="text-primary-600 dark:text-primary-400">
                    R-Squared
                  </p>
                  <p className="font-bold text-primary-900 dark:text-primary-100">
                    {(modelStatus.metrics.r2_score * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="w-px h-8 bg-primary-300 dark:bg-primary-700" />
                <div className="text-center">
                  <p className="text-primary-600 dark:text-primary-400">RMSE</p>
                  <p className="font-bold text-primary-900 dark:text-primary-100">
                    {formatNumber(modelStatus.metrics.rmse, 2)}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Prediction Form */}
      <PredictionForm onPrediction={handlePrediction} />

      {/* Prediction History */}
      {predictions.length > 0 && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
              Prediction History
            </h2>
            <button
              onClick={() => setPredictions([])}
              className="text-sm text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
            >
              Clear All
            </button>
          </div>

          <div className="space-y-3">
            {predictions.map((pred, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg"
              >
                <div className="flex items-center gap-4">
                  <span className="w-8 h-8 flex items-center justify-center bg-primary-100 dark:bg-primary-900/30 rounded-full text-sm font-semibold text-primary-700 dark:text-primary-300">
                    {predictions.length - index}
                  </span>
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">
                      Prediction: {formatNumber(pred.prediction, 2)}
                    </p>
                    {pred.confidence_interval && (
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        95% CI: [{formatNumber(pred.confidence_interval.lower, 2)}{" "}
                        - {formatNumber(pred.confidence_interval.upper, 2)}]
                      </p>
                    )}
                  </div>
                </div>
                <div className="text-right text-sm text-slate-500 dark:text-slate-400">
                  {new Date().toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="card p-6 bg-slate-50 dark:bg-slate-800/50">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
          <svg
            className="w-5 h-5 text-primary-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          Tips for Better Predictions
        </h3>
        <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-slate-600 dark:text-slate-400">
          <li className="flex items-start gap-2">
            <svg
              className="w-4 h-4 text-success-500 mt-0.5 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            Use values within the range of your training data
          </li>
          <li className="flex items-start gap-2">
            <svg
              className="w-4 h-4 text-success-500 mt-0.5 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            Consider realistic combinations of feature values
          </li>
          <li className="flex items-start gap-2">
            <svg
              className="w-4 h-4 text-success-500 mt-0.5 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            Check feature contributions to understand the prediction
          </li>
          <li className="flex items-start gap-2">
            <svg
              className="w-4 h-4 text-success-500 mt-0.5 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            Use confidence intervals to gauge prediction uncertainty
          </li>
        </ul>
      </div>
    </div>
  );
}
