"use client";

import { cn } from "@/lib/utils";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
  text?: string;
}

const sizeClasses = {
  sm: "w-4 h-4 border-2",
  md: "w-8 h-8 border-3",
  lg: "w-12 h-12 border-4",
  xl: "w-16 h-16 border-4",
};

export default function LoadingSpinner({
  size = "md",
  className,
  text,
}: LoadingSpinnerProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center gap-3", className)}>
      <div
        className={cn(
          "animate-spin rounded-full border-primary-200 border-t-primary-600",
          sizeClasses[size]
        )}
      />
      {text && (
        <p className="text-sm text-slate-600 dark:text-slate-400 animate-pulse">
          {text}
        </p>
      )}
    </div>
  );
}

export function LoadingOverlay({ text }: { text?: string }) {
  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white dark:bg-slate-800 rounded-xl p-8 shadow-2xl">
        <LoadingSpinner size="xl" text={text} />
      </div>
    </div>
  );
}

export function LoadingCard({ text }: { text?: string }) {
  return (
    <div className="card p-8 flex items-center justify-center min-h-[200px]">
      <LoadingSpinner size="lg" text={text || "Loading..."} />
    </div>
  );
}
