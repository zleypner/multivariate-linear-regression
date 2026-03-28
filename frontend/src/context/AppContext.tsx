"use client";

import React, { createContext, useContext, useReducer, useCallback, useEffect, ReactNode } from "react";
import {
  UploadResponse,
  ModelStatus,
  TrainResponse,
  TrainingMetrics,
  FeatureWeight,
} from "@/lib/types";

interface AppState {
  uploadedData: UploadResponse | null;
  modelStatus: ModelStatus | null;
  trainingResults: TrainResponse | null;
  isLoading: boolean;
  error: string | null;
  theme: "light" | "dark";
}

type AppAction =
  | { type: "SET_UPLOADED_DATA"; payload: UploadResponse | null }
  | { type: "SET_MODEL_STATUS"; payload: ModelStatus | null }
  | { type: "SET_TRAINING_RESULTS"; payload: TrainResponse | null }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "TOGGLE_THEME" }
  | { type: "SET_THEME"; payload: "light" | "dark" }
  | { type: "RESET_STATE" };

const initialState: AppState = {
  uploadedData: null,
  modelStatus: null,
  trainingResults: null,
  isLoading: false,
  error: null,
  theme: "light",
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case "SET_UPLOADED_DATA":
      return { ...state, uploadedData: action.payload, error: null };
    case "SET_MODEL_STATUS":
      return { ...state, modelStatus: action.payload };
    case "SET_TRAINING_RESULTS":
      return { ...state, trainingResults: action.payload, error: null };
    case "SET_LOADING":
      return { ...state, isLoading: action.payload };
    case "SET_ERROR":
      return { ...state, error: action.payload, isLoading: false };
    case "TOGGLE_THEME":
      return { ...state, theme: state.theme === "light" ? "dark" : "light" };
    case "SET_THEME":
      return { ...state, theme: action.payload };
    case "RESET_STATE":
      return { ...initialState, theme: state.theme };
    default:
      return state;
  }
}

interface AppContextType extends AppState {
  setUploadedData: (data: UploadResponse | null) => void;
  setModelStatus: (status: ModelStatus | null) => void;
  setTrainingResults: (results: TrainResponse | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  toggleTheme: () => void;
  resetState: () => void;
  getMetrics: () => TrainingMetrics | null;
  getFeatureWeights: () => FeatureWeight[];
}

const AppContext = createContext<AppContextType | undefined>(undefined);

function getInitialTheme(): "light" | "dark" {
  if (typeof window === "undefined") {
    return "light";
  }
  const stored = localStorage.getItem("theme");
  if (stored === "light" || stored === "dark") {
    return stored;
  }
  return "light";
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState, (initial) => ({
    ...initial,
    theme: getInitialTheme(),
  }));

  const setUploadedData = useCallback((data: UploadResponse | null) => {
    dispatch({ type: "SET_UPLOADED_DATA", payload: data });
  }, []);

  const setModelStatus = useCallback((status: ModelStatus | null) => {
    dispatch({ type: "SET_MODEL_STATUS", payload: status });
  }, []);

  const setTrainingResults = useCallback((results: TrainResponse | null) => {
    dispatch({ type: "SET_TRAINING_RESULTS", payload: results });
  }, []);

  const setLoading = useCallback((loading: boolean) => {
    dispatch({ type: "SET_LOADING", payload: loading });
  }, []);

  const setError = useCallback((error: string | null) => {
    dispatch({ type: "SET_ERROR", payload: error });
  }, []);

  const toggleTheme = useCallback(() => {
    dispatch({ type: "TOGGLE_THEME" });
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem("theme", state.theme);
    }
  }, [state.theme]);

  const resetState = useCallback(() => {
    dispatch({ type: "RESET_STATE" });
  }, []);

  const getMetrics = useCallback((): TrainingMetrics | null => {
    return state.trainingResults?.metrics || state.modelStatus?.metrics || null;
  }, [state.trainingResults, state.modelStatus]);

  const getFeatureWeights = useCallback((): FeatureWeight[] => {
    return (
      state.trainingResults?.feature_weights ||
      state.modelStatus?.feature_weights ||
      []
    );
  }, [state.trainingResults, state.modelStatus]);

  const value: AppContextType = {
    ...state,
    setUploadedData,
    setModelStatus,
    setTrainingResults,
    setLoading,
    setError,
    toggleTheme,
    resetState,
    getMetrics,
    getFeatureWeights,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
}
