"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/context/AppContext";
import FileUpload from "@/components/FileUpload";
import DataPreview from "@/components/DataPreview";

export default function UploadPage() {
  const router = useRouter();
  const { uploadedData, error } = useApp();
  const [showSuccess, setShowSuccess] = useState(false);

  const handleUploadComplete = () => {
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Upload Data
        </h1>
        <p className="text-slate-500 dark:text-slate-400">
          Upload your campaign CSV data to train the model
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

      {/* Success Alert */}
      {showSuccess && (
        <div className="bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-800 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <svg
              className="w-5 h-5 text-success-500"
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
            <p className="text-success-700 dark:text-success-300">
              File uploaded successfully! You can now proceed to training.
            </p>
          </div>
        </div>
      )}

      {/* Upload Section */}
      <div className="card p-6">
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
            Upload CSV File
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Your CSV should contain numerical columns for features and a target
            variable. The first row should be column headers.
          </p>
        </div>

        <FileUpload onUploadComplete={handleUploadComplete} />

        {/* Expected Format */}
        <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
          <h3 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
            Expected CSV Format
          </h3>
          <div className="overflow-x-auto">
            <table className="text-xs text-slate-600 dark:text-slate-400">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-700">
                  <th className="text-left py-2 px-3 font-medium">budget</th>
                  <th className="text-left py-2 px-3 font-medium">impressions</th>
                  <th className="text-left py-2 px-3 font-medium">clicks</th>
                  <th className="text-left py-2 px-3 font-medium">conversions</th>
                  <th className="text-left py-2 px-3 font-medium">revenue</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="py-2 px-3">5000</td>
                  <td className="py-2 px-3">50000</td>
                  <td className="py-2 px-3">2500</td>
                  <td className="py-2 px-3">125</td>
                  <td className="py-2 px-3">12500</td>
                </tr>
                <tr>
                  <td className="py-2 px-3">10000</td>
                  <td className="py-2 px-3">100000</td>
                  <td className="py-2 px-3">5000</td>
                  <td className="py-2 px-3">250</td>
                  <td className="py-2 px-3">25000</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Data Preview */}
      {uploadedData && (
        <>
          <DataPreview
            columns={uploadedData.columns}
            data={uploadedData.preview}
            totalRows={uploadedData.rows}
            filename={uploadedData.filename}
          />

          {/* Upload Summary */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Upload Summary
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  File Name
                </p>
                <p className="text-lg font-semibold text-slate-900 dark:text-white truncate">
                  {uploadedData.filename}
                </p>
              </div>
              <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Total Rows
                </p>
                <p className="text-lg font-semibold text-slate-900 dark:text-white">
                  {uploadedData.rows.toLocaleString()}
                </p>
              </div>
              <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Columns
                </p>
                <p className="text-lg font-semibold text-slate-900 dark:text-white">
                  {uploadedData.columns.length}
                </p>
              </div>
              <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Status
                </p>
                <p className="text-lg font-semibold text-success-500">Ready</p>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-4">
              <button
                onClick={() => router.push("/train")}
                className="btn-primary flex items-center gap-2"
              >
                Continue to Training
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
            </div>
          </div>
        </>
      )}
    </div>
  );
}
