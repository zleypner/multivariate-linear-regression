"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useApp } from "@/context/AppContext";
import { getModelStatus, getResults } from "@/lib/api";
import { MetricsGrid } from "@/components/MetricsCard";
import FeatureImportance from "@/components/FeatureImportance";
import ResultsChart from "@/components/ResultsChart";
import { LoadingCard } from "@/components/LoadingSpinner";
import { DataPoint, ResultsResponse } from "@/lib/types";

export default function DashboardPage() {
  const { modelStatus, setModelStatus, error, setError } = useApp();
  const [results, setResults] = useState<ResultsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

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
        // Model not trained yet is expected, not an error
        console.log("No model trained yet");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [setModelStatus, setError]);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
              Dashboard
            </h1>
            <p className="text-slate-500 dark:text-slate-400">
              Campaign analytics overview
            </p>
          </div>
        </div>
        <LoadingCard text="Loading dashboard..." />
      </div>
    );
  }

  // Show welcome screen if no model is trained
  if (!modelStatus?.is_trained) {
    return (
      <div className="space-y-8">
        <div className="text-center py-12">
          <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-primary-700 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-xl">
            <svg
              className="w-12 h-12 text-white"
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
          </div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
            Welcome to Campaign Analytics
          </h1>
          <p className="text-lg text-slate-500 dark:text-slate-400 max-w-2xl mx-auto mb-8">
            Predict campaign performance using machine learning. Upload your data,
            train a model, and start making accurate predictions.
          </p>
        </div>

        {/* Getting Started Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link href="/upload" className="card-hover p-6 group">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-xl group-hover:scale-110 transition-transform">
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
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
              <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                1
              </span>
            </div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
              Upload Data
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Upload your campaign CSV data with historical performance metrics
            </p>
          </Link>

          <Link href="/train" className="card-hover p-6 group">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-success-50 dark:bg-success-900/30 rounded-xl group-hover:scale-110 transition-transform">
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
                    d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
                  />
                </svg>
              </div>
              <span className="text-2xl font-bold text-success-600 dark:text-success-400">
                2
              </span>
            </div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
              Train Model
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Train a multivariate linear regression model on your data
            </p>
          </Link>

          <Link href="/predict" className="card-hover p-6 group">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-warning-50 dark:bg-warning-900/30 rounded-xl group-hover:scale-110 transition-transform">
                <svg
                  className="w-6 h-6 text-warning-600 dark:text-warning-400"
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
              </div>
              <span className="text-2xl font-bold text-warning-600 dark:text-warning-400">
                3
              </span>
            </div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
              Make Predictions
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Use the trained model to predict outcomes for new campaigns
            </p>
          </Link>
        </div>

        {/* Feature Highlights */}
        <div className="card p-8 mt-8">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-6">
            Key Features
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                <svg
                  className="w-5 h-5 text-primary-600 dark:text-primary-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-slate-900 dark:text-white">
                  Easy Data Import
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Drag and drop CSV files
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 bg-success-50 dark:bg-success-900/30 rounded-lg">
                <svg
                  className="w-5 h-5 text-success-600 dark:text-success-400"
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
              </div>
              <div>
                <h3 className="font-medium text-slate-900 dark:text-white">
                  Real-time Metrics
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  R-squared, MSE, RMSE, MAE
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 bg-warning-50 dark:bg-warning-900/30 rounded-lg">
                <svg
                  className="w-5 h-5 text-warning-600 dark:text-warning-400"
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
              </div>
              <div>
                <h3 className="font-medium text-slate-900 dark:text-white">
                  Visual Analytics
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Interactive charts and graphs
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 bg-error-50 dark:bg-error-900/30 rounded-lg">
                <svg
                  className="w-5 h-5 text-error-600 dark:text-error-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-slate-900 dark:text-white">
                  Instant Predictions
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Fast ML inference
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show dashboard with model results
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Dashboard
          </h1>
          <p className="text-slate-500 dark:text-slate-400">
            Model trained and ready for predictions
          </p>
        </div>
        <div className="flex gap-3">
          <Link href="/predict" className="btn-primary">
            Make Prediction
          </Link>
          <Link href="/results" className="btn-secondary">
            View Details
          </Link>
        </div>
      </div>

      {/* Metrics */}
      {modelStatus.metrics && <MetricsGrid metrics={modelStatus.metrics} />}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Feature Importance */}
        {modelStatus.feature_weights && modelStatus.feature_weights.length > 0 && (
          <FeatureImportance features={modelStatus.feature_weights} />
        )}

        {/* Actual vs Predicted */}
        {results?.data_points && results.data_points.length > 0 && (
          <ResultsChart data={results.data_points} />
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Link
          href="/upload"
          className="card p-4 flex items-center gap-4 hover:shadow-lg transition-shadow"
        >
          <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-xl">
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
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
          </div>
          <div>
            <h3 className="font-medium text-slate-900 dark:text-white">
              Upload New Data
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Update training dataset
            </p>
          </div>
        </Link>

        <Link
          href="/train"
          className="card p-4 flex items-center gap-4 hover:shadow-lg transition-shadow"
        >
          <div className="p-3 bg-success-50 dark:bg-success-900/30 rounded-xl">
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
                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
              />
            </svg>
          </div>
          <div>
            <h3 className="font-medium text-slate-900 dark:text-white">
              Retrain Model
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Update model parameters
            </p>
          </div>
        </Link>

        <Link
          href="/results"
          className="card p-4 flex items-center gap-4 hover:shadow-lg transition-shadow"
        >
          <div className="p-3 bg-warning-50 dark:bg-warning-900/30 rounded-xl">
            <svg
              className="w-6 h-6 text-warning-600 dark:text-warning-400"
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
          </div>
          <div>
            <h3 className="font-medium text-slate-900 dark:text-white">
              View Full Results
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Detailed analysis
            </p>
          </div>
        </Link>
      </div>
    </div>
  );
}
