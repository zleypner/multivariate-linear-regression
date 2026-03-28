"""
Machine Learning service for model training and prediction.

Integrates the enhanced CampaignRegressionModel from the ml module.
Includes persistence for models and training results.
"""

import sys
import uuid
import json
from pathlib import Path
from typing import Any
from datetime import datetime

import pandas as pd
import numpy as np
import joblib
import structlog

# Add ML module to path
ML_MODULE_PATH = Path(__file__).resolve().parent.parent.parent.parent / "ml"
sys.path.insert(0, str(ML_MODULE_PATH.parent))

from ml.model import CampaignRegressionModel
from ml.preprocessing import CampaignDataPreprocessor

from ..config import settings
from ..middleware.error_handler import ModelError, NotFoundError
from ..models.schemas import TrainingResult, TrainingConfig

logger = structlog.get_logger(__name__)


class MLService:
    """Service for ML model operations using CampaignRegressionModel."""

    # Default feature configurations
    DEFAULT_NUMERIC_FEATURES = ["budget", "impressions", "clicks", "ctr", "cpc"]
    DEFAULT_CATEGORICAL_FEATURES = ["audience_type", "creative_type", "channel"]

    # Persistence file names
    MODEL_FILE = "current_model.joblib"
    RESULTS_FILE = "training_results.json"
    STATE_FILE = "ml_state.json"

    def __init__(self) -> None:
        """Initialize ML service and load persisted state."""
        self._model: CampaignRegressionModel | None = None
        self._training_results: dict[str, TrainingResult] = {}
        self._latest_training_id: str | None = None
        self._load_persisted_state()

    def train_model(
        self,
        df: pd.DataFrame,
        config: TrainingConfig,
    ) -> TrainingResult:
        """
        Train a multivariate regression model.

        Args:
            df: Training DataFrame
            config: Training configuration

        Returns:
            TrainingResult with metrics and coefficients

        Raises:
            ModelError: If training fails
        """
        training_id = str(uuid.uuid4())

        try:
            logger.info(
                "Starting model training",
                training_id=training_id,
                model_type=config.model_type,
                target=config.target_column,
                rows=len(df),
            )

            # Validate target column exists
            if config.target_column not in df.columns:
                raise ModelError(
                    f"Target column '{config.target_column}' not found in data",
                    details={
                        "target_column": config.target_column,
                        "available_columns": list(df.columns),
                    },
                )

            # Determine features to use
            numeric_features = config.numerical_features or self.DEFAULT_NUMERIC_FEATURES
            categorical_features = config.categorical_features or self.DEFAULT_CATEGORICAL_FEATURES

            # Filter to available columns
            numeric_features = [f for f in numeric_features if f in df.columns]
            categorical_features = [f for f in categorical_features if f in df.columns]

            # Initialize the enhanced model
            self._model = CampaignRegressionModel(
                target_variable=config.target_column,
                numeric_features=numeric_features,
                categorical_features=categorical_features,
            )

            # Fit the model
            self._model.fit(df, compute_vif=True, cv_folds=config.cv_folds)

            # Get model results
            model_metrics = self._model.metrics
            coefficients = self._model.get_coefficients()
            # The model returns feature_importance with 'importance' key (coefficient value)
            feature_importance = {
                item["feature"]: item["importance"]
                for item in self._model.get_feature_importance()
            }
            feature_names = self._model.preprocessor.get_feature_names()

            # Create result compatible with TrainingResult schema
            result = TrainingResult(
                training_id=training_id,
                trained_at=datetime.utcnow(),
                model_type=config.model_type,
                target_column=config.target_column,
                n_samples=model_metrics.get("n_samples", len(df)),
                n_features=model_metrics.get("n_features", len(feature_names)),
                train_r2=model_metrics.get("r_squared", 0.0),
                test_r2=model_metrics.get("cv_r2_mean", 0.0),
                train_rmse=model_metrics.get("rmse", 0.0),
                test_rmse=model_metrics.get("rmse", 0.0),
                train_mae=model_metrics.get("mae", 0.0),
                test_mae=model_metrics.get("mae", 0.0),
                cv_r2_mean=model_metrics.get("cv_r2_mean", 0.0),
                cv_r2_std=model_metrics.get("cv_r2_std", 0.0),
                intercept=self._model.get_intercept(),
                coefficients=coefficients,
                feature_importance=feature_importance,
                feature_names=feature_names,
            )

            # Store results
            self._training_results[training_id] = result
            self._latest_training_id = training_id

            # Persist to disk
            self._persist_all()

            logger.info(
                "Model training completed",
                training_id=training_id,
                r_squared=model_metrics.get("r_squared", 0.0),
                cv_r2_mean=model_metrics.get("cv_r2_mean", 0.0),
            )

            return result

        except ModelError:
            raise
        except Exception as e:
            logger.error(
                "Model training failed",
                training_id=training_id,
                error=str(e),
            )
            raise ModelError(
                f"Model training failed: {str(e)}",
                details={"error": str(e)},
            )

    def predict(
        self,
        campaigns: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Make predictions for campaign data.

        Args:
            campaigns: List of campaign data dictionaries

        Returns:
            List of predictions with input data

        Raises:
            ModelError: If no model is trained or prediction fails
        """
        if self._model is None or not self._model.is_fitted:
            raise ModelError(
                "No trained model available. Please train a model first.",
                details={"trained": False},
            )

        try:
            results = []
            df = pd.DataFrame(campaigns)

            # Use predict with confidence intervals
            predictions, intervals = self._model.predict(df, return_confidence=True)

            for idx, (campaign, prediction) in enumerate(zip(campaigns, predictions)):
                confidence_interval = None
                if intervals is not None and len(intervals) > idx:
                    confidence_interval = (
                        float(intervals[idx, 0]),
                        float(intervals[idx, 1])
                    )

                results.append({
                    "input_data": campaign,
                    "predicted_value": float(prediction),
                    "confidence_interval": confidence_interval,
                })

            logger.info(
                "Predictions generated",
                count=len(results),
            )

            return results

        except Exception as e:
            logger.error("Prediction failed", error=str(e))
            raise ModelError(
                f"Prediction failed: {str(e)}",
                details={"error": str(e)},
            )

    def get_latest_result(self) -> TrainingResult:
        """
        Get the latest training result.

        Returns:
            Latest TrainingResult

        Raises:
            NotFoundError: If no training has been done
        """
        if self._latest_training_id is None:
            raise NotFoundError(
                "No training results available. Please train a model first.",
            )
        return self._training_results[self._latest_training_id]

    def get_result_by_id(self, training_id: str) -> TrainingResult:
        """
        Get training result by ID.

        Args:
            training_id: Training run identifier

        Returns:
            TrainingResult for the specified run

        Raises:
            NotFoundError: If training ID not found
        """
        if training_id not in self._training_results:
            raise NotFoundError(
                f"Training result with ID '{training_id}' not found",
                details={"training_id": training_id},
            )
        return self._training_results[training_id]

    def list_training_runs(self) -> list[dict[str, Any]]:
        """List all training runs with summary info."""
        return [
            {
                "training_id": tid,
                "model_type": result.model_type,
                "target_column": result.target_column,
                "test_r2": result.test_r2,
                "trained_at": result.trained_at.isoformat(),
            }
            for tid, result in self._training_results.items()
        ]

    def get_model_info(self) -> dict[str, Any]:
        """
        Get information about the current model.

        Returns:
            Dictionary with model information
        """
        if self._model is None or not self._model.is_fitted:
            return {"trained": False}

        return {
            "trained": True,
            "target_column": self._model.target_variable,
            "feature_names": self._model.preprocessor.get_feature_names(),
            "numeric_features": self._model.numeric_features,
            "categorical_features": self._model.categorical_features,
        }

    def is_model_trained(self) -> bool:
        """Check if a model is currently trained."""
        return self._model is not None and self._model.is_fitted

    def get_vif_report(self) -> dict[str, Any]:
        """
        Get Variance Inflation Factor report for multicollinearity analysis.

        Returns:
            VIF report dictionary
        """
        if self._model is None or not self._model.is_fitted:
            raise NotFoundError("No trained model available.")
        return self._model.get_vif_report()

    # -------------------------------------------------------------------------
    # Persistence Methods
    # -------------------------------------------------------------------------

    def _get_model_path(self) -> Path:
        """Get path to model file."""
        return settings.models_path / self.MODEL_FILE

    def _get_results_path(self) -> Path:
        """Get path to results file."""
        return settings.metadata_path / self.RESULTS_FILE

    def _get_state_path(self) -> Path:
        """Get path to state file."""
        return settings.metadata_path / self.STATE_FILE

    def _save_model(self) -> None:
        """Save current model to disk."""
        if self._model is not None and self._model.is_fitted:
            model_path = self._get_model_path()
            joblib.dump(self._model, model_path)
            logger.info("Model saved to disk", path=str(model_path))

    def _load_model(self) -> bool:
        """Load model from disk if exists."""
        model_path = self._get_model_path()
        if model_path.exists():
            try:
                self._model = joblib.load(model_path)
                logger.info("Model loaded from disk", path=str(model_path))
                return True
            except Exception as e:
                logger.warning("Failed to load model", error=str(e))
        return False

    def _save_results(self) -> None:
        """Save training results to disk."""
        results_path = self._get_results_path()
        results_data = {}
        for tid, result in self._training_results.items():
            results_data[tid] = {
                "training_id": result.training_id,
                "trained_at": result.trained_at.isoformat(),
                "model_type": result.model_type,
                "target_column": result.target_column,
                "n_samples": result.n_samples,
                "n_features": result.n_features,
                "train_r2": result.train_r2,
                "test_r2": result.test_r2,
                "train_rmse": result.train_rmse,
                "test_rmse": result.test_rmse,
                "train_mae": result.train_mae,
                "test_mae": result.test_mae,
                "cv_r2_mean": result.cv_r2_mean,
                "cv_r2_std": result.cv_r2_std,
                "intercept": result.intercept,
                "coefficients": result.coefficients,
                "feature_importance": result.feature_importance,
                "feature_names": result.feature_names,
            }
        with open(results_path, "w") as f:
            json.dump(results_data, f, indent=2)
        logger.info("Training results saved", count=len(results_data))

    def _load_results(self) -> bool:
        """Load training results from disk if exists."""
        results_path = self._get_results_path()
        if results_path.exists():
            try:
                with open(results_path, "r") as f:
                    results_data = json.load(f)
                for tid, data in results_data.items():
                    self._training_results[tid] = TrainingResult(
                        training_id=data["training_id"],
                        trained_at=datetime.fromisoformat(data["trained_at"]),
                        model_type=data["model_type"],
                        target_column=data["target_column"],
                        n_samples=data["n_samples"],
                        n_features=data["n_features"],
                        train_r2=data["train_r2"],
                        test_r2=data["test_r2"],
                        train_rmse=data["train_rmse"],
                        test_rmse=data["test_rmse"],
                        train_mae=data["train_mae"],
                        test_mae=data["test_mae"],
                        cv_r2_mean=data["cv_r2_mean"],
                        cv_r2_std=data["cv_r2_std"],
                        intercept=data["intercept"],
                        coefficients=data["coefficients"],
                        feature_importance=data["feature_importance"],
                        feature_names=data["feature_names"],
                    )
                logger.info("Training results loaded", count=len(results_data))
                return True
            except Exception as e:
                logger.warning("Failed to load results", error=str(e))
        return False

    def _save_state(self) -> None:
        """Save service state (latest training ID)."""
        state_path = self._get_state_path()
        state = {"latest_training_id": self._latest_training_id}
        with open(state_path, "w") as f:
            json.dump(state, f)

    def _load_state(self) -> bool:
        """Load service state from disk."""
        state_path = self._get_state_path()
        if state_path.exists():
            try:
                with open(state_path, "r") as f:
                    state = json.load(f)
                self._latest_training_id = state.get("latest_training_id")
                return True
            except Exception as e:
                logger.warning("Failed to load state", error=str(e))
        return False

    def _load_persisted_state(self) -> None:
        """Load all persisted state on initialization."""
        self._load_model()
        self._load_results()
        self._load_state()

    def _persist_all(self) -> None:
        """Save all state to disk."""
        self._save_model()
        self._save_results()
        self._save_state()


# Singleton instance
ml_service = MLService()
