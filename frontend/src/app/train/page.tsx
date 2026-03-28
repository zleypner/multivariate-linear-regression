"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/context/AppContext";
import { trainModel, getDataPreview, getModelStatus } from "@/lib/api";
import { TrainRequest } from "@/lib/types";
import { MetricsGrid } from "@/components/MetricsCard";
import FeatureImportance from "@/components/FeatureImportance";
import LoadingSpinner, { LoadingCard } from "@/components/LoadingSpinner";
import { cn } from "@/lib/utils";

export default function TrainPage() {
  const router = useRouter();
  const {
    uploadedData,
    trainingResults,
    setTrainingResults,
    setModelStatus,
    setError,
    error,
  } = useApp();

  const [columns, setColumns] = useState<string[]>([]);
  const [targetColumn, setTargetColumn] = useState<string>("");
  const [featureColumns, setFeatureColumns] = useState<string[]>([]);
  const [testSize, setTestSize] = useState<number>(0.2);
  const [normalize, setNormalize] = useState<boolean>(true);
  const [isTraining, setIsTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [isLoadingColumns, setIsLoadingColumns] = useState(true);

  // Load columns from uploaded data or fetch from API
  useEffect(() => {
    const loadColumns = async () => {
      setIsLoadingColumns(true);
      try {
        if (uploadedData?.columns) {
          setColumns(uploadedData.columns);
        } else {
          const preview = await getDataPreview();
          setColumns(preview.columns);
        }
      } catch (err) {
        // No data uploaded yet
        setColumns([]);
      } finally {
        setIsLoadingColumns(false);
      }
    };
    loadColumns();
  }, [uploadedData]);

  // Auto-select features when target changes
  useEffect(() => {
    if (targetColumn && columns.length > 0) {
      setFeatureColumns(columns.filter((col) => col !== targetColumn));
    }
  }, [targetColumn, columns]);

  const handleFeatureToggle = (column: string) => {
    setFeatureColumns((prev) =>
      prev.includes(column)
        ? prev.filter((c) => c !== column)
        : [...prev, column]
    );
  };

  const handleSelectAllFeatures = () => {
    setFeatureColumns(columns.filter((col) => col !== targetColumn));
  };

  const handleDeselectAllFeatures = () => {
    setFeatureColumns([]);
  };

  const handleTrain = async () => {
    if (!targetColumn) {
      setError("Please select a target column");
      return;
    }
    if (featureColumns.length === 0) {
      setError("Please select at least one feature column");
      return;
    }

    setIsTraining(true);
    setTrainingProgress(0);
    setError(null);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setTrainingProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + Math.random() * 15;
      });
    }, 200);

    try {
      const params: TrainRequest = {
        target_column: targetColumn,
        feature_columns: featureColumns,
        test_size: testSize,
        normalize,
      };

      const results = await trainModel(params);
      clearInterval(progressInterval);
      setTrainingProgress(100);
      setTrainingResults(results);

      // Update model status
      const status = await getModelStatus();
      setModelStatus(status);
    } catch (err) {
      clearInterval(progressInterval);
      setError(err instanceof Error ? err.message : "Training failed");
    } finally {
      setIsTraining(false);
    }
  };

  if (isLoadingColumns) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Train Model
          </h1>
          <p className="text-slate-500 dark:text-slate-400">
            Configure and train your regression model
          </p>
        </div>
        <LoadingCard text="Loading data..." />
      </div>
    );
  }

  if (columns.length === 0) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Train Model
          </h1>
          <p className="text-slate-500 dark:text-slate-400">
            Configure and train your regression model
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
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            No Data Uploaded
          </h3>
          <p className="text-slate-500 dark:text-slate-400 mb-4">
            Please upload a CSV file first to train the model
          </p>
          <button
            onClick={() => router.push("/upload")}
            className="btn-primary"
          >
            Go to Upload
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Train Model
        </h1>
        <p className="text-slate-500 dark:text-slate-400">
          Configure and train your regression model
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration */}
        <div className="lg:col-span-2 space-y-6">
          {/* Target Selection */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Target Variable
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
              Select the column you want to predict
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {columns.map((column) => (
                <button
                  key={column}
                  onClick={() => setTargetColumn(column)}
                  disabled={isTraining}
                  className={cn(
                    "px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all",
                    targetColumn === column
                      ? "border-primary-500 bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300"
                      : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300"
                  )}
                >
                  {column}
                </button>
              ))}
            </div>
          </div>

          {/* Feature Selection */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                  Feature Variables
                </h2>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Select the columns to use as predictors ({featureColumns.length}{" "}
                  selected)
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleSelectAllFeatures}
                  disabled={isTraining || !targetColumn}
                  className="text-xs text-primary-600 dark:text-primary-400 hover:underline disabled:opacity-50"
                >
                  Select All
                </button>
                <span className="text-slate-300 dark:text-slate-600">|</span>
                <button
                  onClick={handleDeselectAllFeatures}
                  disabled={isTraining}
                  className="text-xs text-slate-600 dark:text-slate-400 hover:underline disabled:opacity-50"
                >
                  Clear
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              {columns
                .filter((col) => col !== targetColumn)
                .map((column) => (
                  <button
                    key={column}
                    onClick={() => handleFeatureToggle(column)}
                    disabled={isTraining || !targetColumn}
                    className={cn(
                      "px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all flex items-center justify-between",
                      featureColumns.includes(column)
                        ? "border-success-500 bg-success-50 dark:bg-success-900/30 text-success-700 dark:text-success-300"
                        : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 text-slate-700 dark:text-slate-300",
                      !targetColumn && "opacity-50 cursor-not-allowed"
                    )}
                  >
                    <span className="truncate">{column}</span>
                    {featureColumns.includes(column) && (
                      <svg
                        className="w-4 h-4 flex-shrink-0 ml-2"
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
                    )}
                  </button>
                ))}
            </div>
          </div>

          {/* Advanced Settings */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Training Settings
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label className="label">Test Split Ratio</label>
                <div className="flex items-center gap-4">
                  <input
                    type="range"
                    min="0.1"
                    max="0.4"
                    step="0.05"
                    value={testSize}
                    onChange={(e) => setTestSize(parseFloat(e.target.value))}
                    disabled={isTraining}
                    className="flex-1"
                  />
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300 w-12">
                    {(testSize * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Percentage of data used for testing
                </p>
              </div>

              <div>
                <label className="label">Data Normalization</label>
                <button
                  onClick={() => setNormalize(!normalize)}
                  disabled={isTraining}
                  className={cn(
                    "w-full px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all flex items-center justify-between",
                    normalize
                      ? "border-success-500 bg-success-50 dark:bg-success-900/30 text-success-700 dark:text-success-300"
                      : "border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300"
                  )}
                >
                  <span>Normalize Features</span>
                  <div
                    className={cn(
                      "w-10 h-6 rounded-full transition-colors relative",
                      normalize
                        ? "bg-success-500"
                        : "bg-slate-300 dark:bg-slate-600"
                    )}
                  >
                    <div
                      className={cn(
                        "w-4 h-4 bg-white rounded-full absolute top-1 transition-transform",
                        normalize ? "translate-x-5" : "translate-x-1"
                      )}
                    />
                  </div>
                </button>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Scale features to similar ranges
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Training Panel */}
        <div className="space-y-6">
          {/* Train Button */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Training
            </h2>

            {isTraining ? (
              <div className="space-y-4">
                <div className="flex items-center justify-center py-8">
                  <LoadingSpinner size="lg" text="Training model..." />
                </div>
                <div>
                  <div className="flex justify-between text-sm text-slate-600 dark:text-slate-400 mb-2">
                    <span>Progress</span>
                    <span>{Math.round(trainingProgress)}%</span>
                  </div>
                  <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-500 transition-all duration-300 rounded-full"
                      style={{ width: `${trainingProgress}%` }}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">
                      Target
                    </span>
                    <span className="font-medium text-slate-900 dark:text-white">
                      {targetColumn || "Not selected"}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">
                      Features
                    </span>
                    <span className="font-medium text-slate-900 dark:text-white">
                      {featureColumns.length}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500 dark:text-slate-400">
                      Test Size
                    </span>
                    <span className="font-medium text-slate-900 dark:text-white">
                      {(testSize * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                <button
                  onClick={handleTrain}
                  disabled={!targetColumn || featureColumns.length === 0}
                  className="btn-primary w-full flex items-center justify-center gap-2"
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
                      d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Start Training
                </button>
              </div>
            )}
          </div>

          {/* Tips */}
          <div className="card p-6">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">
              Tips
            </h3>
            <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
              <li className="flex items-start gap-2">
                <svg
                  className="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Choose a continuous numerical column as target
              </li>
              <li className="flex items-start gap-2">
                <svg
                  className="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Include relevant features that influence the target
              </li>
              <li className="flex items-start gap-2">
                <svg
                  className="w-4 h-4 text-primary-500 mt-0.5 flex-shrink-0"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                A 20% test split is usually a good starting point
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Results */}
      {trainingResults && (
        <div className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-success-100 dark:bg-success-900/30 rounded-full flex items-center justify-center">
              <svg
                className="w-6 h-6 text-success-600 dark:text-success-400"
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
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">
                Training Complete
              </h2>
              <p className="text-slate-500 dark:text-slate-400">
                {trainingResults.message}
              </p>
            </div>
          </div>

          <MetricsGrid metrics={trainingResults.metrics} />

          {trainingResults.feature_weights && (
            <FeatureImportance features={trainingResults.feature_weights} />
          )}

          <div className="flex justify-end gap-4">
            <button
              onClick={() => router.push("/predict")}
              className="btn-primary flex items-center gap-2"
            >
              Make Predictions
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
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>
            <button
              onClick={() => router.push("/results")}
              className="btn-secondary"
            >
              View Full Results
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
