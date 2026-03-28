"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { cn } from "@/lib/utils";
import { uploadCSV } from "@/lib/api";
import { useApp } from "@/context/AppContext";
import LoadingSpinner from "./LoadingSpinner";

interface FileUploadProps {
  onUploadComplete?: () => void;
}

export default function FileUpload({ onUploadComplete }: FileUploadProps) {
  const { setUploadedData, setError } = useApp();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file) return;

      // Validate file type
      if (!file.name.endsWith(".csv")) {
        setError("Please upload a CSV file");
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError("File size must be less than 10MB");
        return;
      }

      setIsUploading(true);
      setUploadProgress(0);
      setError(null);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 100);

      try {
        const response = await uploadCSV(file);
        clearInterval(progressInterval);
        setUploadProgress(100);
        setUploadedData(response);
        onUploadComplete?.();
      } catch (err) {
        clearInterval(progressInterval);
        setError(err instanceof Error ? err.message : "Upload failed");
      } finally {
        setIsUploading(false);
        setUploadProgress(0);
      }
    },
    [setUploadedData, setError, onUploadComplete]
  );

  const { getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject } =
    useDropzone({
      onDrop,
      accept: {
        "text/csv": [".csv"],
      },
      maxFiles: 1,
      disabled: isUploading,
    });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={cn(
          "relative border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300",
          "bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800",
          isDragActive && "border-primary-500 bg-primary-50 dark:bg-primary-900/20",
          isDragAccept && "border-success-500 bg-success-50 dark:bg-success-900/20",
          isDragReject && "border-error-500 bg-error-50 dark:bg-error-900/20",
          !isDragActive && "border-slate-300 dark:border-slate-600",
          isUploading && "pointer-events-none opacity-75"
        )}
      >
        <input {...getInputProps()} />

        {isUploading ? (
          <div className="flex flex-col items-center gap-4">
            <LoadingSpinner size="lg" />
            <div className="w-full max-w-xs">
              <div className="flex justify-between text-sm text-slate-600 dark:text-slate-400 mb-2">
                <span>Uploading...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-500 transition-all duration-300 rounded-full"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4">
            <div
              className={cn(
                "p-4 rounded-full transition-colors",
                isDragActive
                  ? "bg-primary-100 dark:bg-primary-900/30"
                  : "bg-slate-200 dark:bg-slate-700"
              )}
            >
              <svg
                className={cn(
                  "w-10 h-10 transition-colors",
                  isDragActive
                    ? "text-primary-600 dark:text-primary-400"
                    : "text-slate-400 dark:text-slate-500"
                )}
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
              <p className="text-lg font-semibold text-slate-700 dark:text-slate-200">
                {isDragActive
                  ? "Drop your file here"
                  : "Drag & drop your CSV file here"}
              </p>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                or click to browse from your computer
              </p>
            </div>

            <div className="flex items-center gap-4 text-xs text-slate-400 dark:text-slate-500">
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                CSV format
              </span>
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                Max 10MB
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
